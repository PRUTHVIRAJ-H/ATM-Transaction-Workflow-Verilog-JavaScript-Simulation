#!/usr/bin/env python3
"""Simple report generator: parse sim/last_run.txt and produce sim/report.html
Keeps output minimal and easy to demo in interviews.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAST = ROOT / "last_run.txt"
OUT = ROOT / "report.html"

def extract(lines):
    scenarios = []
    tests = []
    waveform = None
    for ln in lines:
        if 'SCENARIO' in ln:
            scenarios.append(ln.strip())
        if '[TEST' in ln:
            tests.append(ln.strip())
        if 'Waveform' in ln and 'vcd' in ln:
            waveform = ln.strip().split()[-1]
    return scenarios, tests, waveform

def make_html(scenarios, tests, waveform, raw):
    css = """
    body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:18px}
    h1{margin-bottom:6px}
    .box{border:1px solid #ddd;padding:12px;border-radius:6px;margin-bottom:12px}
    .mono{font-family:monospace;background:#f8f8f8;padding:8px;border-radius:4px}
    .tests{margin-top:8px}
    """
    html = f"""
    <html><head><meta charset="utf-8"><title>Simulation Report</title>
    <style>{css}</style>
    </head><body>
    <h1>Simulation Report</h1>
    <div class="box">
      <strong>Waveform:</strong> {waveform or 'not found'}<br/>
      <small>Open with GTKWave: <code>gtkwave {waveform or ''}</code></small>
    </div>
    <div class="box">
      <strong>Scenarios</strong>
      <div class="mono">{'<br/>'.join(scenarios) if scenarios else 'No scenarios found'}</div>
    </div>
    <div class="box">
      <strong>Test Results</strong>
      <div class="tests mono">{'<br/>'.join(tests) if tests else 'No test lines found'}</div>
    </div>
    <details class="box"><summary>Full log</summary><pre class="mono">{raw}</pre></details>
    </body></html>
    """
    return html

def main():
    if not LAST.exists():
        print("No sim/last_run.txt found; run sim/run_native.sh first")
        return 1
    txt = LAST.read_text(errors='ignore')
    lines = txt.splitlines()
    scenarios, tests, waveform = extract(lines)
    html = make_html(scenarios, tests, waveform, txt)
    OUT.write_text(html, encoding='utf-8')
    print(f"Report written: {OUT}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
