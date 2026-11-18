function validation = validate_cortical_disturbance
%VALIDATE_CORTICAL_DISTURBANCE Check equilibria and DDE solver refinement.
% Uses the saved default run, then repeats without graphics at tighter
% tolerances and half the maximum solver step. The convergence criterion
% is peak-normalized because the populations have different rate scales.
folder = fileparts(mfilename('fullpath'));
saved = load(fullfile(folder,'output','cortex_equilibrium_results.mat'), 'results');
coarse = saved.results;
cfg = coarse.configuration;
cfg.relTol = cfg.relTol/100;
cfg.absTol = cfg.absTol/100;
cfg.maxStep = cfg.maxStep/2;
fine = simulate_cortical_disturbance(cfg, false);
validation.maxAbsoluteDifference = zeros(numel(coarse.cases),2);
validation.maxRelativeDifference = zeros(numel(coarse.cases),2);
for k = 1:numel(coarse.cases)
    c = coarse.cases(k);
    f = fine.cases(k);
    assert(c.maxEquilibriumResidual < 1e-7);
    assert(all(c.rates >= -1e-6 & c.rates <= [300 400]+1e-6, 'all'));
    difference = max(abs(c.rates-f.rates), [], 1);
    rateScale = max(1, max(abs(f.rates), [], 1));
    validation.maxAbsoluteDifference(k,:) = difference;
    validation.maxRelativeDifference(k,:) = difference./rateScale;
end
validation.relativeTolerance = 1e-3;
assert(all(validation.maxRelativeDifference < validation.relativeTolerance, 'all'), ...
    'Solver refinement changed rates by more than 0.1 percent of their peak.');
% Check the known manuscript equilibrium with constant cortex and zero
% perturbation over a short interval, before instability amplifies roundoff.
stationary = simulate_cortical_disturbance(struct('duration',0.05, ...
    'initialPerturbation',[0;0],'cortex',@(t) 27), false);
assert(max(abs(stationary.cases(1).equilibrium(1,:) ...
    -[20.44251554 21.83661841])) < 1e-7);
validation.stationaryDeviation = max(abs(stationary.cases(1).trackingError), [], 'all');
assert(validation.stationaryDeviation < 1e-6);
validation.passed = true;
disp('Maximum default/refined rate differences [STN GPe], spikes/s:');
disp(validation.maxAbsoluteDifference);
disp('Peak-normalized relative differences:');
disp(validation.maxRelativeDifference);
save(fullfile(folder,'output','numerical_validation.mat'), 'validation');
fprintf('VALIDATION_PASSED\n');
end
