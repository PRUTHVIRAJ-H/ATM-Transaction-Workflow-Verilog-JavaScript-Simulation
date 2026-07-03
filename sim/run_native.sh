#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Running native Icarus Verilog simulation..."
mkdir -p sim
iverilog -o sim_native src/atm_fsm.v tb/atm_tb.v
# run and save full console output for report
vvp sim_native 2>&1 | tee sim/last_run.txt
echo "Waveform saved to sim/atm_waves.vcd"
# generate simple HTML report
if command -v python3 >/dev/null 2>&1; then
	python3 sim/generate_report.py || true
fi
echo "Report: sim/report.html"
