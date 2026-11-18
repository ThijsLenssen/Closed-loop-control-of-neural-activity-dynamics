"use strict";
const $ = id => document.getElementById(id);
let sessionToken = "", latest = null, lastSeries = {baseline: [], pi: []};
let busy = false, polling = false, connected = false, logText = "", logChosen = false;
const colors = {baseline: "#91a29b", pi: "#1c7567", target: "#b78858"};
const duration = seconds => {
  if (!Number.isFinite(seconds)) return "—";
  seconds = Math.max(0, Math.round(seconds));
  if (seconds < 60) return seconds + " s";
  if (seconds < 3600) return Math.floor(seconds / 60) + " min " + seconds % 60 + " s";
  return Math.floor(seconds / 3600) + " h " + Math.floor(seconds % 3600 / 60) + " min";
};
const num = (value, places=1) => Number.isFinite(value) ? value.toFixed(places) : "—";
const title = value => (value || "").replace(/^\w/, c => c.toUpperCase());
async function api(path, options) {
  const response = await fetch(path, {cache: "no-store", ...options});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "The dashboard could not complete the request.");
  return data;
}
function connection(ok) {
  connected = ok;
  $("connection-dot").className = ok ? "online" : "";
  $("connection-text").textContent = ok ? "Connected to local runner" : "Connection lost";
  updateButtons();
}
function updateButtons() {
  const running = latest && latest.running;
  $("start-button").disabled = !connected || !latest || running || busy || latest.status === "completed";
  $("stop-button").disabled = !connected || !running || busy;
  $("analyse-button").disabled = !connected || busy || latest?.analysis_running;
  $("start-label").textContent = running ? "Comparison running" :
    latest?.status === "completed" ? "Comparison complete" :
    ["stopped", "failed", "interrupted"].includes(latest?.status) ? "Resume comparison" : "Start comparison";
}
function render(snapshot) {
  latest = snapshot;
  const running = snapshot.running;
  const current = snapshot.stages.find(s => s.alive);
  $("state-pill").textContent = running ? "Running · " + (current?.name || "Starting") : title(snapshot.status);
  $("state-pill").className = "pill " + snapshot.status;
  $("updated-label").textContent = "Updated " + new Date(snapshot.now * 1000).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit", second: "2-digit"});
  $("overall-percent").replaceChildren(document.createTextNode(num(snapshot.percent)), Object.assign(document.createElement("small"), {textContent: "%"}));
  $("overall-bar").style.width = snapshot.percent + "%";
  $("elapsed").textContent = duration(snapshot.elapsed_s);
  $("eta").textContent = snapshot.eta_s ? "~ " + duration(snapshot.eta_s) : "—";
  $("campaign-heading").textContent = snapshot.status === "completed" ? "Comparison complete" :
    running ? (current?.kind === "warmup" ? "Preparing the network" : current ? "Simulating the paired trials" : "Starting the comparison") :
    snapshot.status === "idle" ? "Ready to run" :
    snapshot.status === "stopped" ? "Simulation stopped" :
    snapshot.status === "interrupted" ? "Runner is no longer active" : "Simulation needs attention";
  const fragment = document.createDocumentFragment();
  snapshot.stages.forEach((stage, i) => {
    const card = document.createElement("div");
    card.className = "stage " + stage.status;
    const top = document.createElement("div"); top.className = "stage-top";
    const marker = document.createElement("span"); marker.className = "stage-marker";
    marker.textContent = stage.status === "completed" ? "✓" : String(i + 1);
    top.append(marker, document.createTextNode(stage.name));
    const track = document.createElement("div"); track.className = "stage-track";
    track.setAttribute("role", "progressbar"); track.setAttribute("aria-label", stage.name);
    track.setAttribute("aria-valuenow", stage.percent.toFixed(1)); track.setAttribute("aria-valuemin", "0"); track.setAttribute("aria-valuemax", "100");
    const fill = document.createElement("i"); fill.style.width = stage.percent + "%"; track.append(fill);
    const state = document.createElement("div"); state.className = "stage-state";
    state.textContent = stage.alive ? "Running" : title(stage.status);
    const time = document.createElement("div"); time.className = "stage-time";
    time.textContent = num(stage.integrated_s, 2) + " / " + stage.duration_s.toFixed(0) + " s";
    card.append(top, track, state, time); fragment.append(card);
  });
  $("stages").replaceChildren(fragment);
  $("work-note").textContent = running ? current?.kind === "warmup" ?
    "Warmup is shared by both trials. The DBS-off and PI cases follow automatically." :
    "Trials run in separate processes. Progress updates at solver checkpoints." :
    snapshot.status === "completed" ? "Both full-length trials finished. Comparison results are available below." :
    "Completed stages are retained. Resume restarts unfinished stages from their beginning.";
  $("target-value").textContent = num(snapshot.settings.target * 1000, 5) + " µV";
  $("target-legend").textContent = $("target-value").textContent;
  $("seed-value").textContent = snapshot.settings.seed + " / 1";
  $("solver-value").textContent = "dt 0.01 ms · order " + snapshot.settings.secondorder;
  const processes = snapshot.processes;
  const cpu = processes.reduce((sum, p) => sum + (p.cpu_one_core_percent || 0), 0);
  const sampled = processes.some(p => p.cpu_one_core_percent !== null);
  const ram = processes.reduce((sum, p) => sum + (p.memory_mb || 0), 0);
  $("cpu-value").textContent = !processes.length ? "0%" : sampled ? num(cpu, 0) + "%" : "…";
  $("cpu-bar").style.width = Math.min(cpu / 2, 100) + "%";
  $("machine-cpu").textContent = sampled ? num(cpu / snapshot.logical_cpus) + "% of " + snapshot.logical_cpus + " logical CPUs · 200% = two cores" :
    processes.length ? "Sampling process activity…" : "No active solver processes";
  $("memory-value").textContent = num(ram, 0) + " MB";
  $("process-count").textContent = processes.length;
  const errors = [snapshot.error, ...snapshot.stages.map(s => s.error)].filter(Boolean);
  $("error-banner").textContent = errors.join(" · ");
  $("error-banner").hidden = !errors.length;
  if (!logChosen && current) $("log-stage").value = current.kind;
  renderResults(snapshot);
  updateButtons();
}
function renderResults(snapshot) {
  const data = snapshot.comparison;
  const has = Object.keys(data).length > 0;
  $("metric-beta").textContent = has ? num(data.beta_suppression_percent_mean_of_ratios) + "%" : "—";
  $("metric-error").textContent = has ? num(data.pi_error_reduction_percent) + "%" : "—";
  $("metric-power").textContent = has ? num(data.pi_linear_play_power_uw, 2) + " µW" : "—";
  $("results-note").textContent = has ? "Measured from this paired simulation. One seed and burst pattern; these are not the paper’s multi-trial averages." : "Comparison metrics and the LFP plot appear when both trials finish.";
  const exports = [
    ["index.html", "Open simulation report ↗"],
    ["comparison.png", "Plot PNG ↓"], ["comparison.svg", "Plot SVG ↓"],
    ["comparison.csv", "Metrics CSV ↓"], ["comparison.json", "Metrics JSON ↓"]
  ];
  const fragment = document.createDocumentFragment();
  for (const [file, label] of exports) {
    if (!snapshot.artifacts[file]) continue;
    const a = document.createElement("a");
    a.href = snapshot.artifacts[file]; a.textContent = label;
    if (file !== "index.html") a.download = file;
    else { a.target = "_blank"; a.rel = "noopener"; }
    fragment.append(a);
  }
  for (const stage of snapshot.stages.filter(s => s.status === "completed" && s.kind !== "warmup")) {
    const a = document.createElement("a"); a.href = "/results/" + stage.kind + "/signals.npz";
    a.textContent = stage.name + " signals ↓"; a.download = stage.kind + "_signals.npz"; fragment.append(a);
  }
  $("downloads").replaceChildren(fragment);
  const image = snapshot.artifacts["comparison.png"];
  if (image && !($("comparison-image").getAttribute("src"))) $("comparison-image").src = image;
  $("comparison-image").hidden = !image;
}
function drawChart(id, field, fixedMaximum=null, target=null) {
  const canvas = $(id), parent = canvas.parentElement;
  const width = parent.clientWidth, height = parent.clientHeight;
  if (width < 1) return;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
  const c = canvas.getContext("2d"); c.scale(dpr, dpr);
  const pad = {left: 44, right: 10, top: 10, bottom: 25};
  const w = width - pad.left - pad.right, h = height - pad.top - pad.bottom;
  const all = [...lastSeries.baseline, ...lastSeries.pi];
  const values = all.map(d => d[field]).filter(Number.isFinite);
  let ymax = fixedMaximum || Math.max(target ? target * 1.8 : .2, ...values) * 1.12;
  if (!Number.isFinite(ymax) || ymax <= 0) ymax = 1;
  const x = t => pad.left + Math.max(0, Math.min(30, t)) / 30 * w;
  const y = v => pad.top + h - v / ymax * h;
  c.lineWidth = 1; c.font = "9px Segoe UI, sans-serif"; c.fillStyle = "#98a49c"; c.strokeStyle = "#eaf0eb";
  for (let i = 0; i <= 3; i++) {
    const v = i * ymax / 3, yy = y(v);
    c.beginPath(); c.moveTo(pad.left, yy); c.lineTo(width - pad.right, yy); c.stroke();
    c.textAlign = "right"; c.fillText(fixedMaximum ? num(v, 0) : num(v, ymax < 1 ? 2 : 1), pad.left - 10, yy + 3);
  }
  c.textAlign = "center";
  for (let t = 0; t <= 30; t += 5) {
    c.fillText(t, x(t), height - 7);
  }
  c.save(); c.beginPath(); c.rect(pad.left - 1, pad.top - 1, w + 2, h + 2); c.clip();
  if (target !== null) {
    c.strokeStyle = colors.target; c.lineWidth = 1; c.setLineDash([4, 4]);
    c.beginPath(); c.moveTo(x(0), y(target)); c.lineTo(x(30), y(target)); c.stroke(); c.setLineDash([]);
  }
  for (const kind of ["baseline", "pi"]) {
    const points = lastSeries[kind].filter(p => p.time_s >= -.05 && p.time_s <= 30.05);
    if (!points.length) continue;
    c.strokeStyle = colors[kind]; c.lineWidth = kind === "pi" ? 1.65 : 1.25;
    c.beginPath();
    points.forEach((p, i) => { if (i) c.lineTo(x(p.time_s), y(p[field])); else c.moveTo(x(p.time_s), y(p[field])); });
    c.stroke();
    const last = points.at(-1);
    c.fillStyle = colors[kind]; c.beginPath(); c.arc(x(last.time_s), y(last[field]), 2.7, 0, Math.PI * 2); c.fill();
  }
  c.restore();
}

function renderCharts() {
  const count = lastSeries.baseline.length + lastSeries.pi.length;
  $("signal-status").textContent = count ? count.toLocaleString() + " samples" : "Awaiting samples";
  $("beta-empty").hidden = count > 0; $("amplitude-empty").hidden = count > 0;
  const last = lastSeries.pi.at(-1) || lastSeries.baseline.at(-1);
  $("beta-latest").textContent = last ? num(last.beta_uv, 4) + " µV" : "";
  $("amplitude-latest").textContent = last ? num(last.amplitude_ma, 3) + " mA" : "";
  drawChart("beta-chart", "beta_uv", null, (latest?.settings.target || 1.0414e-4) * 1000);
  drawChart("amplitude-chart", "amplitude_ma", 3);
}

async function refreshLog() {
  const stage = $("log-stage").value;
  const result = await api("/api/log?stage=" + encodeURIComponent(stage));
  if (stage !== $("log-stage").value) return;
  const pre = $("log-output");
  const atBottom = pre.scrollTop + pre.clientHeight >= pre.scrollHeight - 35;
  const changed = logText !== result.text;
  logText = result.text;
  pre.textContent = logText || "No output yet for this process.";
  if (changed && atBottom) pre.scrollTop = pre.scrollHeight;
  $("log-path").textContent = ["analysis", "supervisor"].includes(stage) ? "results/" + stage + ".log" : "results/" + stage + "/run.log";
}

async function refresh() {
  if (polling) return;
  polling = true;
  try {
    const [status, series] = await Promise.all([api("/api/status"), api("/api/series")]);
    connection(true); render(status); lastSeries = series; renderCharts();
    await refreshLog();
  } catch (error) {
    connection(false);
    $("updated-label").textContent = "Last data retained. Reconnecting…";
    if (!latest) { $("campaign-heading").textContent = "Waiting for the local dashboard server"; }
  } finally { polling = false; }
}

async function act(action) {
  if (busy) return;
  busy = true; updateButtons();
  $("toast").hidden = true;
  try {
    // Refresh the per-server token so restarting the dashboard needs no page reload.
    sessionToken = (await api("/api/session")).token;
    const result = await api("/api/" + action, {
      method: "POST", headers: {"Content-Type": "application/json", "X-Dashboard-Token": sessionToken}, body: "{}"
    });
    $("toast").classList.add("success"); $("toast").textContent = result.message; $("toast").hidden = false;
    await refresh();
  } catch (error) {
    $("toast").classList.remove("success"); $("toast").textContent = error.message; $("toast").hidden = false;
  } finally { busy = false; updateButtons(); }
}

$("start-button").addEventListener("click", () => act("start"));
$("stop-button").addEventListener("click", () => act("stop"));
$("analyse-button").addEventListener("click", () => act("analyse"));
$("log-stage").addEventListener("change", () => { logChosen = true; refreshLog().catch(() => connection(false)); });
$("copy-log").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(logText);
    $("copy-log").textContent = "Copied";
    setTimeout(() => { $("copy-log").textContent = "Copy log"; }, 1500);
  } catch { $("copy-log").textContent = "Select and copy from the log"; }
});

new ResizeObserver(() => renderCharts()).observe($("beta-chart").parentElement);
document.addEventListener("visibilitychange", () => { if (!document.hidden) refresh(); });
renderCharts(); refresh(); setInterval(() => { if (!document.hidden) refresh(); }, 3000);
