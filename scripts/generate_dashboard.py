from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sim.atm_server import run_verilog_simulation


SCENARIOS = [
    [
        {"kind": "insert_card", "account": 0x1234},
        {"kind": "enter_pin", "pin": 9},
        {"kind": "select_balance"},
    ],
    [
        {"kind": "insert_card", "account": 0x1234},
        {"kind": "enter_pin", "pin": 9},
        {"kind": "withdraw", "amount": 50},
    ],
    [
        {"kind": "insert_card", "account": 0x1234},
        {"kind": "enter_pin", "pin": 1},
    ],
    [
        {"kind": "insert_card", "account": 0x9999},
    ],
    [
        {"kind": "insert_card", "account": 0x1234},
        {"kind": "enter_pin", "pin": 9},
        {"kind": "withdraw", "amount": 200},
    ],
]


STATE_NAMES = {
    0: "HOME",
    1: "CARD_READ",
    2: "PIN_ENTRY",
    3: "AUTH_CHECK",
    4: "MENU",
    5: "BALANCE",
    6: "WITHDRAW",
    7: "DISPENSE",
    8: "TRANSACTION_END",
    9: "EJECT_CARD",
    10: "LOCKED",
    15: "ERROR",
}


reports_dir = ROOT / "reports"
reports_dir.mkdir(exist_ok=True)

all_states = set()
all_transitions = set()
passed = 0
failed = 0

for scenario in SCENARIOS:
    result = run_verilog_simulation(scenario)

    if result["ok"]:
        passed += 1
        all_states.update(result["visited_states"])
        all_transitions.update(result["transitions"])
    else:
        failed += 1


TOTAL_STATES = 12
state_cov = (len(all_states) / TOTAL_STATES) * 100


summary = {
    "tests_passed": passed,
    "tests_failed": failed,
    "states_visited": sorted(list(all_states)),
    "transitions": sorted(list(all_transitions)),
    "state_coverage": round(state_cov, 2),
}

(reports_dir / "summary.json").write_text(
    json.dumps(summary, indent=4)
)


html = f"""
<html>
<head>
<title>ATM Verification Dashboard</title>
<style>
body {{
    font-family: Arial;
    background: #f5f7fb;
    margin: 40px;
}}
.card {{
    background: white;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
}}
.good {{
    color: green;
    font-size: 30px;
    font-weight: bold;
}}
table {{
    border-collapse: collapse;
}}
td, th {{
    border: 1px solid #ddd;
    padding: 8px;
}}
</style>
</head>

<body>

<h1>ATM FSM Verification Dashboard</h1>

<div class="card">
<h2>Test Summary</h2>
<p class="good">{passed} Passed</p>
<p>{failed} Failed</p>
</div>

<div class="card">
<h2>State Coverage</h2>
<p class="good">{state_cov:.2f}%</p>
</div>

<div class="card">
<h2>Visited States</h2>

<table>
<tr>
<th>State ID</th>
<th>Name</th>
</tr>
"""

for s in sorted(all_states):
    html += f"""
<tr>
<td>{s}</td>
<td>{STATE_NAMES.get(s, "UNKNOWN")}</td>
</tr>
"""

html += """
</table>
</div>

<div class="card">
<h2>Transitions</h2>
<ul>
"""

for a, b in sorted(all_transitions):
    html += f"<li>{a} → {b}</li>"

html += """
</ul>
</div>

<div class="card">
<h2>Waveform</h2>
<p>sim/atm_waves.vcd</p>
<p>Open using GTKWave.</p>
</div>

</body>
</html>
"""

(reports_dir / "dashboard.html").write_text(
    html,
    encoding="utf-8"
)

print("Dashboard generated:")
print(reports_dir / "dashboard.html")

