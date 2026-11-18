"""Numerical regression of the component equations and device-independent wiring."""
from pathlib import Path
from types import SimpleNamespace
import ast
import sys
import unittest
import tempfile
import json
from unittest.mock import patch
import numpy as np
from scipy import signal

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"model/python"))
from Controllers import standard_PID_Controller, Constant_Controller
from components.base import NeuralModel, Sensor, Biomarker, Controller, Actuator
from components.pi_controller import PIController
from components.constant_controller import ConstantController
from components.beta_arv import BetaARV
from components.lfp_sensor import BipolarLFPSensor
from components.dbs_actuator import pulse_segment
from components.optogenetic_actuator import OptogeneticActuator
from components.closed_loop import ClosedLoop


def source_function(name):
    path=ROOT/"model/python/run_CBG_Model_Amplitude_Modulation_Controller.py"
    tree=ast.parse(path.read_text(encoding="utf-8-sig"))
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    scope={"np":np,"signal":signal}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),"exec"),scope)
    return scope[name]


class NumericalTests(unittest.TestCase):
    def test_pi_matches_supplied_algorithm_with_saturation(self):
        for target,ti in [(1.0414e-4,.2),(0.,.2),(1.0414e-4,0.)]:
            old=standard_PID_Controller(SetPoint=target,Kp=.23,Ti=ti,Td=0,Ts=.02,MinValue=0,MaxValue=3)
            new=PIController(target=target,ti_s=ti)
            values=np.r_[np.full(30,1.),np.full(30,-1.),np.random.RandomState(42).uniform(0,5e-4,100)]
            expected=[old.update(v,i*20.) for i,v in enumerate(values)]
            actual=[new.update(v,i*20.) for i,v in enumerate(values)]
            np.testing.assert_array_equal(actual,expected)
            np.testing.assert_array_equal(new.errors,old.get_error_history())
            np.testing.assert_array_equal(new.times_s,old.get_sample_times())

    def test_trial_noise_preserves_legacy_default_unless_explicitly_selected(self):
        from components.cbg_model import CBGModel
        from unittest.mock import Mock
        for seed in (None,3695):
            with tempfile.TemporaryDirectory() as directory:
                (Path(directory)/"steady_state.bin").write_bytes(b"test checkpoint")
                model=CBGModel(directory,trial_noise_seed=seed)
                noise=Mock()
                model.cortex=[SimpleNamespace(_cell=SimpleNamespace(noise=noise))]
                model.population_size=0
                model.scope={"run_until":Mock()}
                model.h=SimpleNamespace(t=6000.01)
                model.restore()
                if seed is None:noise.seed.assert_not_called()
                else:noise.seed.assert_called_once_with(seed)

    def test_constant_controller_matches_supplied_bounds(self):
        for command in [-1.,0.,2.5,4.]:
            old=Constant_Controller(SetPoint=1.0414e-4,MinValue=0,MaxValue=3,ConstantValue=command,Ts=.02)
            new=ConstantController(command=command)
            for i,v in enumerate([0.,1e-5,2e-4]):
                self.assertEqual(new.update(v,i*20.),old.update(v,i*20.))
            np.testing.assert_array_equal(new.errors,old.get_error_history())

    def test_pulses_match_supplied_waveform_and_phase(self):
        reference=source_function("generate_DBS_Signal")
        start=8020.
        for amplitude in [0.,-.2,-3.,-1.2,0.,-2.5]:
            stop=start+20.
            old,t_old,next_old=reference(start,stop,.01,amplitude,130.,.06,0)
            new,t_new,next_new=pulse_segment(start,stop,.01,amplitude)
            np.testing.assert_array_equal(new,old)
            np.testing.assert_array_equal(t_new,t_old)
            self.assertEqual(next_new,next_old)
            start=next_old

    def test_beta_arv_matches_supplied_filter_for_multiple_windows(self):
        reference=source_function("calculate_avg_beta_power")
        b,a=source_function("make_beta_cheby1_filter")(2000.,4,.5,21,29)
        processor=BetaARV()
        np.testing.assert_array_equal(processor.b,b)
        np.testing.assert_array_equal(processor.a,a)
        t=np.arange(0,2.2,.0005)
        lfp=.001*np.sin(2*np.pi*25*t)+.0002*np.cos(2*np.pi*7*t)
        history=np.array([])
        for chunk in [lfp[:4040],lfp[4040:4080],lfp[4080:]]:
            history=np.hstack((history,chunk))
            expected=reference(history[-4000:],200,b,a)
            self.assertEqual(processor.update(chunk),expected)

    def test_lfp_expression_and_legacy_endpoint_padding(self):
        ampa=np.random.RandomState(7).normal(size=(5,4))
        gabaa=np.random.RandomState(8).normal(size=(5,4))
        times=np.arange(4)*.5  # Five samples including the legacy duplicated endpoint.
        cell=SimpleNamespace(_cell=SimpleNamespace(record_times=SimpleNamespace(as_numpy=lambda:times)))
        class Population:
            def __getitem__(self,index):return cell
            def get_data(self,name,**kwargs):
                values=ampa if name=="AMPA.i" else gabaa
                return SimpleNamespace(segments=[SimpleNamespace(analogsignals=[values])])
        sensor=BipolarLFPSensor()
        sensor.population=Population()
        sensor.distance_1=np.array([[200.],[400.],[800.],[1600.]])
        sensor.distance_2=np.array([[1200.],[900.],[500.],[300.]])
        currents=ampa+gabaa
        expected=(1/(4*np.pi*.27))*np.sum((1/(sensor.distance_1*1e-6))*currents.transpose(),axis=0)*1e-6
        expected-=(1/(4*np.pi*.27))*np.sum((1/(sensor.distance_2*1e-6))*currents.transpose(),axis=0)*1e-6
        np.testing.assert_array_equal(sensor.read(),expected)
        np.testing.assert_array_equal(sensor.time_ms,[0,.5,1.,1.5,1.5])


class WiringTests(unittest.TestCase):
    def system(self,fail=False):
        events=[]
        class Model(NeuralModel):
            warmup_ms=0.;stop_ms=60.01;sampling_interval_ms=.5;time_ms=0.
            def prepare(self):events.append("prepare")
            def restore(self):events.append("restore")
            def advance(self,t):self.time_ms=t;events.append(("advance",t))
            def close(self):events.append("close")
        class Acquisition(Sensor):
            units="custom signal"
            def bind(self,model):events.append("sensor")
            def read(self):events.append("read");return [2.]
            def clear(self):events.append("clear")
        class Processing(Biomarker):
            input_units=output_units="custom signal";history_ms=0.
            def update(self,samples):
                events.append("process")
                if fail:raise RuntimeError("test measurement failure")
                return samples[0]
        class Feedback(Controller):
            measurement_units="custom signal";command_units="custom command";period_ms=20.
            def __init__(self):super().__init__(0.)
            def update(self,value,t):events.append("control");return self.remember(value,value,3.,t)
        class Stimulation(Actuator):
            command_units="custom command"
            def bind(self,model,times):events.append("actuator")
            def apply(self,u,t):events.append(("apply",u,t))
            def signals(self):return {"custom_waveform":np.array([3.])}
        return ClosedLoop(Model(),Acquisition(),Processing(),Feedback(),Stimulation()),events

    def test_loop_accepts_different_device_types_without_changes(self):
        system,events=self.system()
        result=system.run()
        np.testing.assert_array_equal(result["measurement"],[2.,2.,2.])
        np.testing.assert_array_equal(result["command"],[3.,3.,3.])
        self.assertEqual(events[:4],["prepare","sensor","actuator","restore"])
        self.assertEqual(events.count("read"),3)
        self.assertEqual(events.count("clear"),3)
        self.assertEqual([v for v in events if isinstance(v,tuple) and v[0]=="apply"],
                         [("apply",3.,40.),("apply",3.,60.)])
        self.assertEqual(events[-1],"close")

    def test_model_closes_when_measurement_fails(self):
        system,events=self.system(fail=True)
        with self.assertRaisesRegex(RuntimeError,"measurement failure"):
            system.run()
        self.assertEqual(events[-1],"close")

    def test_unit_mismatch_is_rejected_before_model_preparation(self):
        system,events=self.system()
        system.actuator.command_units="wrong units"
        with self.assertRaisesRegex(ValueError,"units"):
            ClosedLoop(system.model,system.sensor,system.biomarker,system.controller,system.actuator)
        self.assertEqual(events,[])

    def test_opto_fails_before_building_network_without_an_opsin_model(self):
        system,events=self.system()
        with self.assertRaisesRegex(NotImplementedError,"opsin"):
            ClosedLoop(system.model,system.sensor,system.biomarker,system.controller,OptogeneticActuator())
        self.assertEqual(events,[])



class ConfigurationTests(unittest.TestCase):
    def test_matching_implementation_can_reuse_saved_case(self):
        import simulation_runner as runner
        with patch.object(runner,"implementation_hash",return_value="current"):
            runner.validate_reuse("pi",{"source_sha256":"current"})

    def test_changed_components_cannot_reuse_old_results(self):
        import simulation_runner as runner
        with tempfile.TemporaryDirectory() as d, patch.object(runner,"ROOT",Path(d)), patch.object(
                runner,"implementation_hash",return_value="new"):
            with self.assertRaisesRegex(RuntimeError,"another component"):
                runner.validate_reuse("pi",{"source_sha256":"old"})

    def test_validated_legacy_results_are_kept_only_for_the_matching_configuration(self):
        import simulation_runner as runner
        with tempfile.TemporaryDirectory() as d, patch.object(runner,"ROOT",Path(d)), patch.object(
                runner,"implementation_hash",return_value="current"):
            record=Path(d)/"tests/results/component_regression.json"
            record.parent.mkdir(parents=True)
            record.write_text(json.dumps({"engine_sha256":"current","legacy_source_sha256":{"pi":"legacy"}}))
            runner.validate_reuse("pi",{"source_sha256":"legacy"})
            record.write_text(json.dumps({"engine_sha256":"changed","legacy_source_sha256":{"pi":"legacy"}}))
            with self.assertRaises(RuntimeError):
                runner.validate_reuse("pi",{"source_sha256":"legacy"})


if __name__=="__main__":
    unittest.main(verbosity=2)
