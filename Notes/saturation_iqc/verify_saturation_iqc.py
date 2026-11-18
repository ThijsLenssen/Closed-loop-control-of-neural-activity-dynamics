"""Numerical checks supplementing the proofs in saturation_iqc.tex.

Run with Python and NumPy. No optimization package is required. Sampling
checks algebra and graph constructions, not universal copositivity.
"""

from dataclasses import dataclass
from itertools import product
from pathlib import Path
import json
import numpy as np


@dataclass(frozen=True)
class Saturation:
    lower: float
    upper: float
    slope: float = 1.0
    offset: float = 0.0

    def __call__(self, value):
        return np.clip(self.slope * value + self.offset, self.lower, self.upper)

    @property
    def breaks(self):
        return ((self.lower - self.offset) / self.slope,
                (self.upper - self.offset) / self.slope)


def cartesian_graph_generator(scalar_pieces):
    """Each piece contains scalar (input, output) vertices and rays."""
    dimension = len(scalar_pieces)
    columns = []
    for vertices in product(*(piece[0] for piece in scalar_pieces)):
        values = np.asarray(vertices)
        columns.append(np.r_[values[:, 0], values[:, 1], 1.0])
    for index, (_, rays) in enumerate(scalar_pieces):
        for input_direction, output_direction in rays:
            column = np.zeros(2 * dimension + 1)
            column[index] = input_direction
            column[dimension + index] = output_direction
            columns.append(column)
    return np.column_stack(columns)


def saturation_piece(saturation, mode):
    lower_break, upper_break = saturation.breaks
    if mode == -1:
        return ([(lower_break, saturation.lower)], [(-1.0, 0.0)])
    if mode == 1:
        return ([(upper_break, saturation.upper)], [(1.0, 0.0)])
    return ([(lower_break, saturation.lower),
             (upper_break, saturation.upper)], [])


def envelope_pieces(lower, upper):
    breaks = sorted(set((*lower.breaks, *upper.breaks)))
    bounds = [-np.inf, *breaks, np.inf]
    pieces = []
    for left, right in zip(bounds[:-1], bounds[1:]):
        endpoints = [value for value in (left, right) if np.isfinite(value)]
        vertices = list(dict.fromkeys(
            (value, float(output(value)))
            for value in endpoints for output in (lower, upper)))
        rays = []
        if not np.isfinite(left):
            rays.append((-1.0, 0.0))
        if not np.isfinite(right):
            rays.append((1.0, 0.0))
        pieces.append((vertices, rays))
    return pieces


def paired_generator(first, second):
    """Order is [bar v; hat v; bar w; hat w; common t]."""
    dimension = (first.shape[0] - 1) // 2
    columns = []
    first_vertices = first[:, first[-1] == 1.0].T
    second_vertices = second[:, second[-1] == 1.0].T
    for bar, hat in product(first_vertices, second_vertices):
        columns.append(np.r_[bar[:dimension], hat[:dimension],
                             bar[dimension:-1], hat[dimension:-1], 1.0])
    for factor, copy_index in ((first, 0), (second, 1)):
        for ray in factor[:, factor[-1] == 0.0].T:
            column = np.zeros(4 * dimension + 1)
            column[copy_index * dimension:(copy_index + 1) * dimension] = ray[:dimension]
            column[(copy_index + 2) * dimension:(copy_index + 3) * dimension] = ray[dimension:-1]
            columns.append(column)
    return np.column_stack(columns)


def normalized_points(generator, rng, count=80):
    coefficients = rng.exponential(size=(generator.shape[1], count))
    points = generator @ coefficients
    return points / points[-1]


def amplitude_matrix(saturations):
    dimension = len(saturations)
    multiplier = np.zeros((2 * dimension + 1, 2 * dimension + 1))
    for index, saturation in enumerate(saturations):
        lower_slack = np.zeros(2 * dimension + 1)
        upper_slack = np.zeros_like(lower_slack)
        lower_slack[dimension + index] = 1.0
        lower_slack[-1] = -saturation.lower
        upper_slack[dimension + index] = -1.0
        upper_slack[-1] = saturation.upper
        multiplier += (np.outer(lower_slack, upper_slack)
                       + np.outer(upper_slack, lower_slack)) / 2
    return multiplier


def main():
    rng = np.random.default_rng(17112026)
    report = {}
    saturation_count = 0
    max_graph_error = 0.0
    for dimension in (1, 2, 3):
        saturations = [Saturation(-0.4 - 0.3 * i, 1.1 + i,
                                  0.7 + 0.4 * i, -0.2 + 0.5 * i)
                       for i in range(dimension)]
        multiplier = amplitude_matrix(saturations)
        for modes in product((-1, 0, 1), repeat=dimension):
            generator = cartesian_graph_generator([
                saturation_piece(sat, mode) for sat, mode in zip(saturations, modes)])
            middle_count = modes.count(0)
            assert generator.shape[1] == 2 ** middle_count + dimension - middle_count
            points = normalized_points(generator, rng)
            expected = np.vstack([sat(points[i]) for i, sat in enumerate(saturations)])
            error = float(np.max(np.abs(points[dimension:2 * dimension] - expected)))
            max_graph_error = max(max_graph_error, error)
            assert error < 2e-12
            supplies = np.einsum('ij,ij->j', points, multiplier @ points)
            assert np.min(supplies) > -2e-10
            # Independent scalar formula checks the affine multiplier assembly.
            actual = sum((expected[i] - sat.lower) * (sat.upper - expected[i])
                         for i, sat in enumerate(saturations))
            assert np.max(np.abs(supplies - actual)) < 2e-10
            saturation_count += 1
    report['saturation_graph_pieces_checked'] = saturation_count
    report['maximum_saturation_graph_error'] = max_graph_error

    # Any normalized sector direction is a scaled saturation increment.
    max_increment_error = 0.0
    for _ in range(2500):
        dimension = 4
        lower = rng.uniform(-3.0, 1.0, dimension)
        upper = lower + rng.uniform(0.2, 4.0, dimension)
        slopes = rng.uniform(0.2, 2.5, dimension)
        offsets = rng.normal(size=dimension)
        direction = rng.normal(size=dimension)
        normalized_output = rng.uniform(size=dimension) * direction
        tau = 0.25 * np.min((upper - lower) / slopes / np.maximum(np.abs(direction), 1e-12))
        kink = (lower - offsets) / slopes
        positive = direction >= 0
        bar = kink + tau * np.where(positive, normalized_output, direction - normalized_output)
        hat = kink + tau * np.where(positive, normalized_output - direction, -normalized_output)
        bar_output = np.clip(slopes * bar + offsets, lower, upper)
        hat_output = np.clip(slopes * hat + offsets, lower, upper)
        error = max(float(np.max(np.abs(bar - hat - tau * direction))),
                    float(np.max(np.abs(bar_output - hat_output
                                        - tau * slopes * normalized_output))))
        max_increment_error = max(max_increment_error, error)
        assert error < 2e-12
    report['scaled_increment_witnesses_checked'] = 2500
    report['maximum_scaled_increment_error'] = max_increment_error

    # Global analytic sigmoid envelopes, also yielding scalar strip generators.
    scalar_envelopes = []
    max_envelope_violation = 0.0
    for maximum, midpoint in ((1.0, 0.0), (300.0, -8.0)):
        epsilon = maximum / 2 * (1 - np.tanh(1.0))
        lower = Saturation(0.0, maximum - epsilon, 1.0,
                           -midpoint + maximum / 2 - epsilon)
        upper = Saturation(epsilon, maximum, 1.0,
                           -midpoint + maximum / 2 + epsilon)
        q = midpoint + maximum * np.linspace(-12, 12, 24001)
        sigmoid = maximum / 2 * (1 + np.tanh(2 * (q - midpoint) / maximum))
        violation = max(float(np.max(lower(q) - sigmoid)),
                        float(np.max(sigmoid - upper(q))))
        max_envelope_violation = max(max_envelope_violation, violation)
        assert violation < 2e-12
        p = np.clip(q - midpoint + maximum / 2, 0.0, maximum)
        assert abs(float(np.max(np.abs(sigmoid - p))) - epsilon) < 1e-11
        scalar_envelopes.append((lower, upper))
    report['maximum_sampled_sigmoid_envelope_violation'] = max_envelope_violation

    # Parallel ramps with small vertical margins, as in the user's sketch.
    shifted_cases = 0
    shifted_max_violation = 0.0
    minimum_necessity_violation = np.inf
    for maximum, midpoint in ((1.0, 0.0), (300.0, -8.0)):
        for fraction, slope in product((1e-6, 0.001, 0.01, 0.1192, 0.3, 0.49),
                                       (0.05, 0.5, 1.0)):
            epsilon = fraction * maximum
            quantile = midpoint + maximum / 4 * np.log(epsilon / (maximum - epsilon))
            right_critical = midpoint + maximum / 2 * np.arccosh(1 / np.sqrt(slope))
            right_output = maximum / 2 * (1 + np.sqrt(1 - slope))
            start_upper = min(quantile, right_critical - (right_output - epsilon) / slope)
            start_lower = 2 * midpoint - start_upper - maximum / slope
            lower = Saturation(-epsilon, maximum - epsilon, slope,
                               -slope * start_lower - epsilon)
            upper = Saturation(epsilon, maximum + epsilon, slope,
                               -slope * start_upper + epsilon)
            # Include analytic contact points and breakpoints, not only a grid.
            special = [quantile, 2 * midpoint - quantile, right_critical,
                       2 * midpoint - right_critical, *lower.breaks, *upper.breaks]
            span = 20 * maximum / slope
            q = np.r_[midpoint + np.linspace(-span, span, 20001), special]
            sigmoid = maximum / 2 * (1 + np.tanh(2 * (q - midpoint) / maximum))
            violation = max(float(np.max(lower(q) - sigmoid)),
                            float(np.max(sigmoid - upper(q))),
                            float(np.max(np.maximum(0.0, lower(q)) - sigmoid)))
            shifted_max_violation = max(shifted_max_violation, violation)
            assert violation < 5e-12 * maximum
            clipped_lower = Saturation(0.0, maximum - epsilon, slope,
                                       -slope * start_lower - epsilon)
            assert np.max(np.abs(clipped_lower(q) - np.maximum(0.0, lower(q)))) < 2e-12 * maximum
            assert np.max(np.abs(lower(q) - (maximum - upper(2 * midpoint - q)))) < 2e-12 * maximum
            # Move just beyond either exact shift threshold and exhibit a failure.
            shift_violation = 0.01 * maximum / slope
            invalid_upper = Saturation(epsilon, maximum + epsilon, slope,
                                       -slope * (start_upper + shift_violation) + epsilon)
            if quantile <= right_critical - (right_output - epsilon) / slope:
                witness = quantile + shift_violation / 2
            else:
                witness = right_critical
            sigmoid_witness = maximum / 2 * (1 + np.tanh(2 * (witness - midpoint) / maximum))
            upper_failure = float(sigmoid_witness - invalid_upper(witness))
            invalid_lower = Saturation(-epsilon, maximum - epsilon, slope,
                                       -slope * (start_lower - shift_violation) - epsilon)
            reflected_witness = 2 * midpoint - witness
            reflected_sigmoid = maximum / 2 * (1 + np.tanh(2 * (reflected_witness - midpoint) / maximum))
            lower_failure = float(invalid_lower(reflected_witness) - reflected_sigmoid)
            assert upper_failure > 1e-12 * maximum
            assert lower_failure > 1e-12 * maximum
            minimum_necessity_violation = min(minimum_necessity_violation,
                                              upper_failure / maximum, lower_failure / maximum)
            shifted_cases += 1
            if maximum == 1.0 and fraction == 0.01 and slope == 0.5:
                report['sketch_example_upper_ramp_start'] = float(start_upper)
                report['sketch_example_lower_ramp_start'] = float(start_lower)
    report['shifted_sandwich_cases_checked'] = shifted_cases
    report['maximum_sampled_shifted_sandwich_violation'] = shifted_max_violation
    report['minimum_normalized_shift_threshold_counterexample'] = minimum_necessity_violation

    generators = []
    for pieces in product(*(envelope_pieces(*pair) for pair in scalar_envelopes)):
        generator = cartesian_graph_generator(pieces)
        points = normalized_points(generator, rng)
        for index, (lower, upper) in enumerate(scalar_envelopes):
            assert np.min(points[2 + index] - lower(points[index])) > -2e-11
            assert np.min(upper(points[index]) - points[2 + index]) > -2e-11
        generators.append(generator)
    report['two_channel_envelope_pieces_checked'] = len(generators)

    dimension = 2
    identity = np.eye(dimension)
    zero = np.zeros_like(identity)
    difference = np.block([[identity, -identity, zero, zero],
                           [zero, zero, identity, -identity]])
    pair_count = 0
    max_difference_error = 0.0
    for first, second in product(generators, repeat=2):
        generator = paired_generator(first, second)
        points = normalized_points(generator, rng, count=12)
        mapped = difference @ points[:-1]
        expected = np.vstack([points[:2] - points[2:4], points[4:6] - points[6:8]])
        error = float(np.max(np.abs(mapped - expected)))
        max_difference_error = max(max_difference_error, error)
        assert error < 1e-12
        for copy_index in (0, 1):
            for channel, (lower, upper) in enumerate(scalar_envelopes):
                value = points[copy_index * 2 + channel]
                output = points[(copy_index + 2) * 2 + channel]
                assert np.min(output - lower(value)) > -2e-10
                assert np.min(upper(value) - output) > -2e-10
        pair_count += 1
    report['paired_envelope_pieces_checked'] = pair_count
    report['maximum_difference_map_error'] = max_difference_error

    # A continuous member of the sandwich class can violate the unit slope QC.
    lower, upper = scalar_envelopes[0]
    q = np.array([-1e-5, 1e-5])
    mixing = (1 + np.tanh(100 * q)) / 2
    selected = (1 - mixing) * lower(q) + mixing * upper(q)
    dv = q[1] - q[0]
    dw = selected[1] - selected[0]
    assert dw / dv > 1.0
    assert dw * (dv - dw) < 0.0
    report['continuous_sandwich_selection_secant_slope'] = float(dw / dv)
    report['continuous_sandwich_selection_sector_supply'] = float(dw * (dv - dw))

    # The coupled ReLU incremental QC is valid on independently sampled slopes.
    inputs = rng.normal(size=(2, 20000))
    outputs = rng.uniform(size=inputs.shape) * inputs
    supply = (inputs[0] - inputs[1]) ** 2 + 2 * outputs[0] * outputs[1]
    assert float(np.min(supply)) >= -1e-12
    report['minimum_sampled_coupled_incremental_supply'] = float(np.min(supply))
    report['status'] = 'passed'
    print(json.dumps(report, indent=2))
    Path(__file__).with_name('verification_results.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
