"""Operate only processes recorded by this reproduction and using its exact Python."""
from pathlib import Path
import os,ctypes,json,time
ROOT=Path(__file__).resolve().parent
EXE=(ROOT/"runtime/neuron827/bin/python.exe").resolve()
def matching_process(pid):
    if os.name!="nt":return False
    k=ctypes.WinDLL("kernel32",use_last_error=True)
    k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
    k.CloseHandle.argtypes=[ctypes.c_void_p]
    k.QueryFullProcessImageNameW.argtypes=[ctypes.c_void_p,ctypes.c_ulong,ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_ulong)]
    k.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong)]
    handle=k.OpenProcess(0x1000,False,int(pid))
    if not handle:return False
    try:
        size=ctypes.c_ulong(32768);name=ctypes.create_unicode_buffer(size.value);code=ctypes.c_ulong()
        if not k.QueryFullProcessImageNameW(handle,0,name,ctypes.byref(size)):return False
        if not k.GetExitCodeProcess(handle,ctypes.byref(code)) or code.value!=259:return False
        return os.path.normcase(str(Path(name.value).resolve()))==os.path.normcase(str(EXE))
    finally:k.CloseHandle(handle)
def terminate_matching(pid):
    if not matching_process(pid):return False
    k=ctypes.WinDLL("kernel32",use_last_error=True)
    k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
    k.TerminateProcess.argtypes=[ctypes.c_void_p,ctypes.c_uint];k.CloseHandle.argtypes=[ctypes.c_void_p]
    handle=k.OpenProcess(1,False,int(pid))
    if not handle:return False
    try:return bool(k.TerminateProcess(handle,1))
    finally:k.CloseHandle(handle)
def stop():
    r=ROOT/"results"
    # Stop the supervisor first so an unfinished stage cannot start another child.
    p=r/"comparison_status.json"
    if p.exists():
        info=json.loads(p.read_text(encoding="utf-8-sig"))
        if info.get("status")=="running":terminate_matching(info.get("pid",0));info["status"]="stopped";info["completed_unix"]=time.time()
        p.write_text(json.dumps(info,indent=2))
    for stage in ["warmup","baseline","pi"]:
        progress=r/stage/"progress.json"
        state=r/stage/"status.json"
        # A child may have a PID before importing NEURON and writing status.json.
        # Include that startup window so Stop cannot leave an orphan solver.
        info=json.loads(progress.read_text(encoding="utf-8-sig")) if progress.exists() else {}
        active=json.loads(state.read_text(encoding="utf-8-sig")).get("status")=="running" if state.exists() else False
        starting=info.get("phase")=="starting"
        if progress.exists() and (active or starting):
            terminate_matching(info.get("pid",0))
        state=r/stage/"status.json"
        if state.exists():
            info=json.loads(state.read_text(encoding="utf-8-sig"))
            if info.get("status")=="running":
                info["status"]="stopped";state.write_text(json.dumps(info,indent=2))
    (r/"progress.html").write_text("<html><meta charset='utf-8'><p>Stopped. Saved outputs retained; run_comparison.cmd resumes unfinished stages.</p></html>",encoding="utf-8")
    print("Stopped this reproduction only; saved outputs retained.")
if __name__=="__main__":stop()

