#!/usr/bin/env python3
"""Simple report generator: parse sim/last_run.txt and produce sim/report.html.
Keeps output clean and interview-friendly.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAST = ROOT / "last_run.txt"
OUT = ROOT / "report.html"


def extract(lines):
    scenarios = []
    tests = []
    waveform = None
    for ln in lines:
        if "SCENARIO" in ln:
            scenarios.append(ln.strip())
        if "[TEST" in ln:
            tests.append(ln.strip())
        if "dumpfile" in ln and ".vcd" in ln:
            parts = ln.split("dumpfile", 1)[1].split("opened", 1)[0].strip()
            waveform = parts
    if waveform is None:
        waveform = "sim/atm_waves.vcd"
    return scenarios, tests, waveform


def badge_html(test_line):
    if "PASS" in test_line:
        return '<span class="badge pass">PASS</span>'
    if "FAIL" in test_line:
        return '<span class="badge fail">FAIL</span>'
    return '<span class="badge">INFO</span>'


def make_html(scenarios, tests, waveform, raw):
    css = """
    body{font-family:Inter,Segoe UI,Roboto,Arial,sans-serif;margin:24px;background:#f5f7fb;color:#1f2937}
    .container{max-width:900px;margin:0 auto;background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;box-shadow:0 8px 24px rgba(0,0,0,.05)}
    h1{margin:0 0 8px;font-size:1.6rem}
    .subtitle{color:#6b7280;margin-bottom:18px}
    .card{border:1px solid #e5e7eb;border-radius:10px;padding:14px 16px;margin-bottom:14px;background:#fafafa}
    .label{font-weight:700;margin-bottom:8px;color:#111827}
    .mono{font-family:ui-monospace,Consolas,monospace;background:#fff;border:1px solid #e5e7eb;padding:10px;border-radius:8px;white-space:pre-wrap}
    .list{display:grid;gap:8px}
    .row{display:flex;align-items:center;gap:10px;padding:8px 10px;background:#fff;border:1px solid #e5e7eb;border-radius:8px}
    .badge{display:inline-block;padding:3px 8px;border-radius:999px;font-size:.8rem;font-weight:700;background:#e5e7eb;color:#374151}
    .badge.pass{background:#dcfce7;color:#166534}
    .badge.fail{background:#fee2e2;color:#991b1b}
    code{background:#f3f4f6;padding:2px 4px;border-radius:4px}
    details summary{cursor:pointer;font-weight:600}
    input[type=file]{margin-top:8px}
    .bar{width:120px;height:8px;background:linear-gradient(90deg,#4f46e5,#0ea5e9);border-radius:999px}
    .tiny{font-size:.8rem;color:#6b7280}
    """
    scenario_rows = "".join(f'<div class="row">{sc}</div>' for sc in scenarios) if scenarios else '<div class="row">No scenarios found</div>'
    test_rows = "".join(f'<div class="row">{badge_html(t)} <span>{t}</span></div>' for t in tests) if tests else '<div class="row">No test lines found</div>'
    html = f"""
    <html><head><meta charset="utf-8"><title>ATM FSM Simulation Report</title>
    <style>{css}</style></head>
    <body>
    <div class="container">
      <h1>ATM FSM Simulation Report</h1>
      <div class="subtitle">A clean browser view of the simulation run for interviews and demos.</div>
      <div class="card">
        <div class="label">Waveform</div>
        <div class="mono">{waveform or 'not found'}</div>
        <input id="vcd-file" type="file" accept=".vcd" />
        <div id="status" style="margin-top:8px;color:#4b5563;">Upload a .vcd file to preview it here.</div>
        <div id="waveform" style="margin-top:10px"></div>
      </div>
      <div class="card">
        <div class="label">Scenarios</div>
        <div class="list">{scenario_rows}</div>
      </div>
      <div class="card">
        <div class="label">Test Results</div>
        <div class="list">{test_rows}</div>
      </div>
      <details class="card"><summary>Full log</summary><pre class="mono" style="margin-top:10px">{raw}</pre></details>
    </div>
    <script src="waveform.js"></script>
    </body></html>
    """
    return html


def main():
    if not LAST.exists():
        print("No sim/last_run.txt found; run sim/run_native.sh first")
        return 1
    txt = LAST.read_text(errors="ignore")
    lines = txt.splitlines()
    scenarios, tests, waveform = extract(lines)
    html = make_html(scenarios, tests, waveform, txt)
    OUT.write_text(html, encoding="utf-8")
    print(f"Report written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
