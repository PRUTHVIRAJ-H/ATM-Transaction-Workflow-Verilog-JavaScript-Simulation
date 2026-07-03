# Design Notes — ATM FSM

Overview
- The FSM models a simple ATM flow: card insertion, PIN entry, auth check,
  menu selection (balance or withdraw), dispense, and transaction end.

Security Features
- 3-strike PIN lockout (`MAX_PIN_ATTEMPTS`)
- Per-transaction withdrawal limit (`MAX_WITHDRAW_AMOUNT`)

Testing
- `atm_tb.v` provides deterministic scenarios validating withdraws,
  insufficient funds, and lockouts.
- `test_atm_fuzzer.py` is a cocotb test that performs state-aware fuzzing.

Notes for cocotb
- Cocotb requires a Python package installation (`cocotb`) and a simulator
  with matching VPI/VPI bindings (Icarus/iverilog). On some systems, an extra
  helper package may be needed to provide the Python bindings; if you hit
  ModuleNotFoundError for `pygpi` or similar, ensure cocotb is installed from
  pip and that the simulator is available on PATH.
