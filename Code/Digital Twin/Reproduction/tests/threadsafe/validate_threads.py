"""Validate local stimulation and private RNGs across actual NEURON threads."""
from pathlib import Path
import os,sys,json,argparse,time,ctypes
if os.name=="nt":
    ctypes.windll.kernel32.SetErrorMode(3)  # Native failures become exit codes, not desktop popups.
import numpy as np
from neuron import h
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from threadsafe_support import bind_noise,require_supported_full_network_threads
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--threads",type=int,required=True);a=ap.parse_args()
    if not hasattr(h,"SynNoiseTS"):h.nrn_load_dll(str(ROOT/"nrnmech.dll"))
    h.CVode().cache_efficient(0)
    h.dt=.01;h.steps_per_ms=100
    pc=h.ParallelContext();pc.nthread(a.threads);pc.set_maxstep(10)
    sections=[];noises=[];rngs=[];records=[];volts=[];stim_records=[]
    t=h.Vector([0,10,30,60,80,100]);wave=h.Vector([0,-1e-7,1e-7,0,-1e-7,0])
    for gid in range(12):
        s=h.Section(name="test_"+str(gid));s.L=20;s.diam=20;s.nseg=1
        s.insert("pas");s.insert("xtra_ts")
        n=h.SynNoiseTS(s(.5));setattr(n,"del",0);n.dur=100;n.f0=0;n.f1=0;n.std=.2;n.bias=0
        rngs.append(bind_noise(n,gid,3695))
        for seg in s:
            seg.xtra_ts.rx=.01
            h.setpointer(seg._ref_i_pas,"im",seg.xtra_ts)
            h.setpointer(seg._ref_e_pas,"ex",seg.xtra_ts)
            wave.play(n,seg.xtra_ts._ref_stimulus,t,1)
        rec=h.Vector();rec.record(n,n._ref_i)
        vr=h.Vector();vr.record(n,s(.5)._ref_v)
        er=h.Vector();er.record(n,s(.5)._ref_e_pas)
        sections.append(s);noises.append(n);records.append(rec);volts.append(vr);stim_records.append(er)
    h.dt=.01;h.finitialize(-65)
    start=time.perf_counter();cpu=time.process_time();pc.psolve(100)
    wall=time.perf_counter()-start;cpu=time.process_time()-cpu
    currents=np.array([np.array(v) for v in records]);voltage=np.array([np.array(v) for v in volts]);stimulus=np.array([np.array(v) for v in stim_records])
    # The original normrand(0,std) treats std as variance, not standard deviation.
    print("THREAD_TIMES",[pc.t(k) for k in range(a.threads)],"RNG_SEQ",[r.seq() for r in rngs],flush=True)
    empirical=currents[:,10:-10]
    mean=float(empirical.mean());variance=float(empirical.var())
    cross=float(np.max(np.abs(np.corrcoef(empirical)-np.eye(len(empirical)))))
    np.savez_compressed(ROOT/f"diagnostic_{a.threads}.npz",currents=currents,voltage=voltage,stimulus=stimulus)
    print("STATS",a.threads,mean,variance,cross,flush=True)
    assert abs(mean)<.02,(mean,variance)
    assert abs(variance-.2)<.02,(mean,variance)
    assert cross<.08,cross
    assert np.isfinite(voltage).all()
    guard=False
    try:require_supported_full_network_threads(4)
    except RuntimeError:guard=True
    assert guard
    result={"threads":int(pc.nthread()),"cells":12,"duration_ms":100,"dt_ms":.01,
       "mean_noise_na":mean,"noise_variance_na2":variance,"expected_variance_na2":.2,
       "max_pairwise_noise_correlation":cross,"wall_s":wall,"cpu_s":cpu,
       "full_extracellular_guard":guard,"cache_efficient":int(h.CVode().cache_efficient())}
    np.savez_compressed(ROOT/f"thread_check_{a.threads}.npz",currents=currents,voltage=voltage,stimulus=stimulus)
    (ROOT/f"thread_check_{a.threads}.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result),flush=True)
if __name__=="__main__":main()

