from pathlib import Path
import numpy as np,json
from neuron import h
ROOT=Path(__file__).resolve().parents[1]
def main():
    sec=h.Section()
    dt=.01
    t=np.round(np.arange(0,60+dt,dt),2)
    pulse=np.zeros_like(t)
    ref=[np.zeros_like(t) for _ in range(3)]
    starts=np.arange(2,60,5)
    for st in starts:
        on=(t>=st)&(t<st+.06-1e-9);pulse[on]=100
        n=1 if st<20 else 3 if st<40 else 0
        for j in range(n):ref[j][on]=100
    tv=h.Vector(t);shared=h.Vector(pulse)
    clamps=[];records=[];refs=[];refvectors=[];refrecords=[]
    for j in range(3):
        c=h.IClamp(sec(.5));c.delay=0;c.dur=1e12 if j<1 else 0;shared.play(c._ref_amp,tv,1)
        v=h.Vector();v.record(c._ref_i,dt);clamps.append(c);records.append(v)
        c=h.IClamp(sec(.5));c.delay=0;c.dur=1e12
        v=h.Vector(ref[j]);v.play(c._ref_amp,tv,1);refvectors.append(v);refs.append(c)
        v=h.Vector();v.record(c._ref_i,dt);refrecords.append(v)
    h.dt=dt;h.finitialize(-65)
    callbacks=[]
    for when,n in [(22-dt,3),(42-dt,0)]:
        def gate(n=n):
            for j,c in enumerate(clamps):c.dur=1e12 if j<n else 0
        callbacks.append(gate);h.CVode().event(when,gate)
    h.continuerun(60)
    error=max(float(np.max(np.abs(np.array(v)-np.array(r)))) for v,r in zip(records,refrecords))
    result={"shared_pulse_gate_max_error_na":error,"tolerance_na":1e-6,"tested_neurons":3,
            "changes":"one to three to zero stimulated cells","duration_ms":60,"dt_ms":dt}
    assert error<1e-6,result
    (ROOT/"tests/results").mkdir(exist_ok=True, parents=True)
    (ROOT/"tests/results/validation_gate.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result))
if __name__=="__main__":main()

