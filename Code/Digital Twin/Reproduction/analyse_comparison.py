"""Analyse actual saved signals only; never substitute published numbers for simulation output."""
from pathlib import Path
import csv,json,html,datetime,sys
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"results";OUT.mkdir(exist_ok=True)
def read_json(p,default=None):
    try:return json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError,ValueError):return {} if default is None else default
def comparison(base,pi):
    b=np.asarray(base["beta_mv"]);p=np.asarray(pi["beta_mv"])
    if b.shape!=p.shape:raise ValueError("Paired controller samples do not match")
    if not np.all(np.isfinite(b)) or not np.all(np.isfinite(p)):raise ValueError("Nonfinite beta samples")
    target=float(pi["target_mv"])
    e0=np.maximum((b-target)/target,0).mean()
    ep=np.maximum((p-target)/target,0).mean()
    t=np.asarray(pi["dbs_time_ms"]);x=np.asarray(pi["dbs_ma"])
    m=t>=float(pi["controller_time_s"][0])*1000
    power=float(500*np.mean(x[m]**2))
    power_linear=500*float(np.sum(np.diff(t[m])*(x[m][:-1]**2+x[m][:-1]*x[m][1:]+x[m][1:]**2)/3))/(t[m][-1]-t[m][0])
    ratio=np.divide(p,b,out=np.full_like(p,np.nan),where=b>0)
    suppression=100*float(np.nanmean(1-ratio))
    literal=100*float(np.nanmean(ratio))
    return {"baseline_mean_positive_error":float(e0),"pi_mean_positive_error":float(ep),
       "pi_normalized_error_percent":float(100*ep/e0) if e0>0 else None,
       "pi_error_reduction_percent":float(100*(1-ep/e0)) if e0>0 else None,
       "baseline_mean_beta_mv":float(b.mean()),"pi_mean_beta_mv":float(p.mean()),
       "target_mv":target,"baseline_beta_p20_mv":float(np.percentile(b,20)),
       "target_minus_baseline_p20_mv":target-float(np.percentile(b,20)),
       "pi_commanded_power_uw":power,"pi_linear_play_power_uw":power_linear,
       "ideal_open_loop_reference_uw":24.375,
       "pi_power_percent_of_ideal_open_loop":100*power/24.375,
       "beta_suppression_percent_mean_of_ratios":suppression,
       "efficiency_suppression_percent_per_uw":suppression/power if power>0 else None,
       "efficiency_literal_eq14_percent_per_uw":literal/power if power>0 else None,
       "pi_max_amplitude_rate_ma_s":float(np.max(np.abs(np.diff(pi["amplitude_ma"]))))/.02,
       "paired_samples":len(b),"number_of_trials":1}
def plots(base,pi):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    fig,ax=plt.subplots(3,1,figsize=(11,8),sharex=True,layout="constrained")
    for d,label,col in [(base,"DBS off","#888888"),(pi,"PI amplitude","#1764a0")]:
        if "lfp_time_ms" in d:
            t=d["lfp_time_ms"]/1000-8
        else:t=6+np.arange(len(d["lfp_mv"]))*float(d["sampling_interval_ms"])/1000-8
        ax[0].plot(t[::4],d["lfp_mv"][::4]*1000,color=col,lw=.5,label=label,alpha=.8)
        ax[1].plot(d["controller_time_s"]-8,d["beta_mv"]*1000,color=col,lw=1,label=label)
    ax[0].set_ylabel("Raw STN LFP (uV)");ax[0].legend(loc="upper right")
    ax[1].set_ylabel("Beta ARV (uV)")
    ax[1].axhline(float(pi["target_mv"])*1000,color="#a52626",ls="--",lw=1,label="Target")
    ax[1].legend(loc="upper right")
    ax[2].plot(pi["controller_time_s"]-8,pi["amplitude_ma"],color="#1764a0")
    ax[2].set_ylabel("DBS amplitude (mA)");ax[2].set_xlabel("Time from control start (s)")
    ax[2].set_xlim(0,30);ax[2].set_ylim(-.05,3.05)
    fig.suptitle("One paired simulation: DBS off versus PI amplitude control")
    fig.savefig(OUT/"comparison.svg");fig.savefig(OUT/"comparison.png",dpi=160);plt.close(fig)
def page():
    manifest=read_json(ROOT/"docs/manifest.json")
    statuses={k:read_json(OUT/k/"status.json") for k in ["warmup","baseline","pi"]}
    rows=[]
    for k,s in statuses.items():
        p=read_json(OUT/k/"progress.json")
        tm=p.get("simulation_time_ms")
        rows.append("<tr><td>"+k+"</td><td>"+html.escape(s.get("status","not started"))+"</td><td>"+("" if tm is None else f"{tm/1000:.2f} s")+"</td></tr>")
    result=""
    if (OUT/"baseline/signals.npz").exists() and (OUT/"pi/signals.npz").exists():
        with np.load(OUT/"baseline/signals.npz") as z:b={k:z[k] for k in z.files}
        with np.load(OUT/"pi/signals.npz") as z:p={k:z[k] for k in z.files}
        c=comparison(b,p)
        (OUT/"comparison.json").write_text(json.dumps(c,indent=2),encoding="utf-8")
        with (OUT/"comparison.csv").open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f);w.writerow(["quantity","value"])
            w.writerows(c.items())
        plots(b,p)
        vals="".join("<tr><td>"+html.escape(k.replace("_"," "))+"</td><td>"+html.escape(str(v))+"</td></tr>" for k,v in c.items())
        result="<h2>Measured comparison</h2><p>One paired seed and burst pattern. This does not reproduce the ten-trial averages or all paper figures.</p><img src='comparison.svg' alt='Simulated LFP, beta ARV and stimulation amplitude'><p><a href='comparison.csv'>Metrics CSV</a> | <a href='comparison.json'>Metrics JSON</a> | <a href='comparison.png'>Plot PNG</a></p><table>"+vals+"</table>"
    else:
        result="<p><strong>No full-length comparison result is available yet.</strong> The 100 ms network benchmark and short save/restore checks are validation, not a reproduction of the paper’s outcomes.</p>"
    title="DBS-off versus PI amplitude control"
    doc="""<!doctype html><html lang="en"><meta charset="utf-8"><meta http-equiv="refresh" content="60">
<title>"""+title+"""</title><style>body{font:16px/1.5 system-ui,sans-serif;max-width:1100px;margin:36px auto;padding:0 24px;color:#17212b}h1{font-size:28px}h2{font-size:20px;margin-top:30px}table{border-collapse:collapse;width:100%}th,td{padding:8px 12px;border-bottom:1px solid #ddd;text-align:left}img{width:100%;height:auto}code{background:#eee;padding:2px 5px}iframe{border:0;width:100%;height:200px}li{margin:8px 0}</style>
<h1>"""+title+"""</h1><p>Fleming, Dunn and Lowery (2020), <a href="https://doi.org/10.3389/fnins.2020.00166">doi:10.3389/fnins.2020.00166</a>.</p>
<p>Scope selected: one DBS-off / PI-amplitude pair on this machine. Full parameter sweeps and the other controllers are not launched.</p>
<h2>Live progress</h2><iframe src="progress.html" title="Live progress"></iframe>

"""+result+"""
<h2>Measured performance</h2><p>The active short probe used 6.69 CPU seconds in 6.73 wall seconds: 99.4% of one core, approximately 12.4% of the machine with eight logical processors. Model construction took 1.87 seconds. A cache-reordering probe caused native access violation 0xC0000005, and a four-thread probe was rejected because SynNoise is not thread-safe. The comparison explicitly keeps one thread and cache reordering disabled; its two cases run as independent processes. <a href="../tests/results/performance.json">Detailed measurements</a>.</p><h2>Thread-safe component validation</h2><p>Opt-in SynNoiseTS and xtra_ts variants use private per-cell RNG streams and local stimulation inputs. Currents, voltages, and stimulation traces matched bit-for-bit with 1, 2, and 4 threads on twelve passive cells. This test excludes the full extracellular solver, so it does not establish full-network multithread support. <a href="../tests/threadsafe/validation_summary.json">Validation results</a> | <a href="../tests/threadsafe/README.txt">Integration notes</a>.</p><h2>Protocol and interpretation</h2><ul>
<li>600 conductance-based neurons, supplied network connectivity and positions; 0.01 ms integration step, 0.5 ms recording, 21?29 Hz fourth-order Chebyshev biomarker filter, 20 ms controller calls, seed 3695 and burst pattern 1.</li>
<li>6 s initialization, 2 s biomarker history, and 30 s control evaluation. PI: Kp=0.23, Ti=0.2 s, 130 Hz, 60 us, 0–3 mA. Uses the authors' supplied target 0.10414 uV; the measured baseline 20th percentile is reported for comparison.</li>
<li>The paper specifies Crank–Nicolson, but the released scripts do not set NEURON secondorder. This run retains the code default (secondorder=0). A separately labelled secondorder=2 run is available through the command line; it is not launched.</li>
<li>GPe pulse vectors share their time/amplitude storage. Each IClamp is enabled at the next pulse onset using duration gating. This avoids multi-gigabyte duplicated waveforms without changing the commanded pulse current. The gate/pulse check and save/restore checks are recorded in the validation files.</li>
<li>Reported power includes both the sampled square-wave convention and exact integration of NEURON's linear waveform interpolation. The 24.375 uW open-loop reference is analytical; no third open-loop network simulation is included.</li>
<li>Eq.14 as printed computes remaining beta rather than the stated beta suppression. Both interpretations are exported, so the reported efficiency is not silently redefined.</li>
<li>Original MATLAB analysis scripts, raw result files and the ten published trial seeds were not supplied. The runtime uses NEURON 8.2.7+ and PyNN 0.9.3 with the authors' supplied patches and documented compatibility fixes.</li>
<li>“Healthy” refers to short 100 ms beta bursts within the same PD-oriented network; prolonged bursts are 600–1000 ms. This is not a validated healthy-person versus PD-person comparison.</li></ul>
<h2>Files and commands</h2><p><a href="../docs/manifest.json">Protocol manifest</a> | <a href="../tests/results/network_100ms.log">100 ms network benchmark</a> | <a href="../tests/results/checks.json">Validation checks</a></p>
<p>Run or resume the selected pair from the Reproduction directory: <code>.\\run_comparison.cmd</code>. Generate this report again: <code>.\\analyse_comparison.cmd</code>. To stop only this campaign: <code>.\\stop_comparison.cmd</code>.</p>
</html>"""
    (OUT/"index.html").write_text(doc,encoding="utf-8")
if __name__=="__main__":page()
