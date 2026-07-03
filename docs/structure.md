Repository layout (clean, interview-friendly)

- src/: Verilog RTL sources (e.g., `src/atm_fsm.v`)
- tb/: Verilog testbenches (e.g., `tb/atm_tb.v`)
- sim/: Simulation helpers and outputs (e.g., `sim/run_native.sh`, `sim/atm_waves.vcd`)
- docs/: Short docs and running instructions (this file)
- Makefile: top-level convenience targets (`make native`, `make test`, `make cleanlocal`)

Quick run (local):

1. Install Icarus Verilog: `sudo apt-get install iverilog`
2. Run `make native` or `./sim/run_native.sh`
3. Open waveform: `gtkwave sim/atm_waves.vcd`

Keep things small and explainable in interviews: point to `src/atm_fsm.v` (RTL) and `tb/atm_tb.v` (scenarios and self-checks).
