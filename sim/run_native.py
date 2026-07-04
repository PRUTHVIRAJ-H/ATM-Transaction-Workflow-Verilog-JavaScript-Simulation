from sim.atm_server import run_verilog_simulation

actions = [
    {"kind": "insert_card", "account": 0x1234},
    {"kind": "enter_pin", "pin": 9},
    {"kind": "select_balance"},
]

result = run_verilog_simulation(actions)

print(result)

