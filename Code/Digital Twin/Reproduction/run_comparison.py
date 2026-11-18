"""Run only the user-selected DBS-off versus PI-amplitude pair; resume completed stages."""
from pathlib import Path
import argparse,json,subprocess,sys,time,threading,traceback,html,os
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from process_control import matching_process
from simulation_runner import validate_reuse
PYTHON=ROOT/"runtime"/"neuron827"/"bin"/"python.exe"
ACTIVE={}
def another_comparison_running(state):
    # The dashboard writes this child's PID before the child enters main().
    pid = state.get("pid", 0)
    return (state.get("status") == "running" and pid != os.getpid()
            and matching_process(pid))

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    t=path.with_suffix(".tmp");t.write_text(json.dumps(obj,indent=2),encoding="utf-8");t.replace(path)
def status(kind):
    p=ROOT/"results"/kind/"status.json"
    try:return json.loads(p.read_text())
    except (OSError,ValueError):return {}
def run(kind,args):
    old=status(kind)
    if old.get("status")=="completed":
        validate_reuse(kind, old)
        if old.get("secondorder") != args.secondorder or old.get("seed") != args.seed:
            raise RuntimeError("Existing results use another seed/solver setting; keep runs in separate copies.")
        if kind == "pi" and old.get("target_mv") != args.target:
            raise RuntimeError("Existing PI result uses another target; keep runs in separate copies.")
        if kind=="warmup" and not (ROOT/"model"/"steady_state.bin").exists():pass
        else:return
    out=ROOT/"results"/kind;out.mkdir(parents=True,exist_ok=True)
    cmd=[str(PYTHON),"-u",str(ROOT/"run_case.py"),kind,"--seed",str(args.seed),"--secondorder",str(args.secondorder)]
    if kind=="pi":cmd+=["--target",str(args.target)]
    progress={"kind":kind,"phase":"starting","started_unix":time.time()}
    write(out/"progress.json",progress)
    with (out/"run.log").open("w",encoding="utf-8") as log:
        p=subprocess.Popen(cmd,cwd=ROOT/"model",stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="replace",bufsize=1)
        ACTIVE[kind]=p
        progress["pid"]=p.pid;write(out/"progress.json",progress)
        for line in p.stdout:
            log.write(line);log.flush()
            if "WARMUP_MS " in line:
                progress.update(phase="integrating",simulation_time_ms=float(line.split("WARMUP_MS ")[1].split()[0]))
            elif "RESTORED_MS " in line:
                progress.update(phase="collecting 2-second biomarker history",simulation_time_ms=float(line.split("RESTORED_MS ")[1].split()[0]))
            elif "Controller Called at t:" in line:
                progress.update(phase="integrating",simulation_time_ms=float(line.split("t:")[1].split()[0]))
            else:continue
            progress["updated_unix"]=time.time()
            write(out/"progress.json",progress)
        rc=p.wait()
    if rc or status(kind).get("status")!="completed":
        failed=status(kind);failed.update(status="failed",exit_code=rc,error="Child process failed; see run.log")
        write(out/"status.json",failed)
        raise RuntimeError(kind+" failed; see "+str(out/"run.log"))
    progress.update(phase="completed",completed_unix=time.time());write(out/"progress.json",progress)
def dashboard():
    body=[]
    for kind in ['warmup','baseline','pi']:
        st=status(kind);p=ROOT/'results'/kind/'progress.json'
        try:pr=json.loads(p.read_text())
        except (OSError,ValueError):pr={}
        t=pr.get('simulation_time_ms')
        phase=st.get('status','not started')
        if phase=='running':phase=pr.get('phase',phase)
        clock='' if t is None else f'{t/1000:.2f} simulated seconds'
        body.append('<tr><td>'+kind+'</td><td>'+html.escape(phase)+'</td><td>'+clock+'</td></tr>')
    doc='<html><meta charset="utf-8"><meta http-equiv="refresh" content="30"><style>body{font:15px system-ui}td{padding:7px 18px;border-bottom:1px solid #ddd}table{border-collapse:collapse}</style><table>'+''.join(body)+'</table><p>Updated '+time.strftime('%Y-%m-%d %H:%M:%S')+'</p></html>'
    (ROOT/'results'/'progress.html').write_text(doc,encoding='utf-8')
def heartbeat(done):
    while not done.is_set():
        dashboard()
        done.wait(30)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--seed",type=int,default=3695)
    ap.add_argument("--secondorder",type=int,choices=[0,2],default=0)
    ap.add_argument("--target",type=float,default=1.0414e-4,help="Authors' supplied controller target, mV")
    args=ap.parse_args()
    existing=ROOT/"results"/"comparison_status.json"
    if existing.exists():
        previous=json.loads(existing.read_text(encoding="utf-8-sig"))
        if another_comparison_running(previous):
            print("Comparison already running; open results/index.html")
            return
    for kind in ("warmup", "baseline", "pi"):
        old = status(kind)
        if old.get("status") == "completed":
            validate_reuse(kind, old)
            if old.get("seed") != args.seed or old.get("secondorder") != args.secondorder:
                raise RuntimeError("Completed stages use another seed/solver setting; use a separate folder.")
            if kind == "pi" and old.get("target_mv") != args.target:
                raise RuntimeError("Completed PI stage uses another target; use a separate folder.")
        progress_path = ROOT/"results"/kind/"progress.json"
        try: progress = json.loads(progress_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError): progress = {}
        if old.get("status") == "running" and matching_process(progress.get("pid", 0)):
            print("A simulation stage is already running; open the dashboard.")
            return
    done=threading.Event()
    monitor=threading.Thread(target=heartbeat,args=(done,),daemon=True)
    monitor.start()
    runstate={"status":"running","started_unix":time.time(),"pid":__import__("os").getpid(),"scope":"DBS off versus PI amplitude; no sweeps","arguments":vars(args)}
    write(ROOT/"results"/"comparison_status.json",runstate)
    subprocess.run([str(PYTHON),str(ROOT/"analyse_comparison.py")],cwd=ROOT,check=True)
    try:
        run("warmup",args)
        failures=[]
        def task(kind):
            try:run(kind,args)
            except Exception as e:
                failures.append((kind,str(e),traceback.format_exc()))
                for child in list(ACTIVE.values()):
                    if child.poll() is None:child.terminate()
        threads=[threading.Thread(target=task,args=(kind,)) for kind in ["baseline","pi"]]
        for t in threads:t.start()
        for t in threads:t.join()
        if failures:raise RuntimeError(str(failures))
        runstate.update(status="completed",completed_unix=time.time())
    except Exception as e:
        runstate.update(status="failed",error=str(e),completed_unix=time.time())
        raise
    finally:
        write(ROOT/"results"/"comparison_status.json",runstate)
        subprocess.run([str(PYTHON),str(ROOT/"analyse_comparison.py")],cwd=ROOT,check=False)
if __name__=="__main__":main()

