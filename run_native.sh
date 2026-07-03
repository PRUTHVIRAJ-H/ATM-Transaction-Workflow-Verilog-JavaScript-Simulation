#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "Running native Verilog simulation (iverilog + vvp)..."
iverilog -o sim_native atm_fsm.v atm_tb.v
vvp sim_native
echo "Simulation done. Wavefile: atm_waves.vcd"
echo "To view: gtkwave atm_waves.vcd"