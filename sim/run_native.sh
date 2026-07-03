#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Running native Icarus Verilog simulation..."
iverilog -o sim_native src/atm_fsm.v tb/atm_tb.v
vvp sim_native
echo "Waveform saved to sim/atm_waves.vcd"
