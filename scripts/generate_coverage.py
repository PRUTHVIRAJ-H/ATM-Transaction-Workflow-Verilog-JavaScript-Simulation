from pathlib import Path
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


all_states = set()
all_transitions = set()

for scenario in SCENARIOS:
    result = run_verilog_simulation(scenario)

    all_states.update(
        result["visited_states"]
    )

    all_transitions.update(
        result["transitions"]
    )


report = []

report.append("Visited States")
report.append("================")
report.append("")

for s in sorted(all_states):
    report.append(
        f"{s} : {STATE_NAMES.get(s, 'UNKNOWN')}"
    )

report.append("")
report.append("Transitions")
report.append("================")
report.append("")

for a, b in sorted(all_transitions):
    report.append(f"{a} -> {b}")

text = "\n".join(report)

outfile = Path("coverage.txt")
outfile.write_text(text)

print(text)
print()
print("Coverage written to coverage.txt")

