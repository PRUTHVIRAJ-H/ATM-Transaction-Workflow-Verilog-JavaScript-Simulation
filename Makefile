# Native Icarus Verilog simulation Makefile

.PHONY: native test all serve backend deps cleanlocal start

native:
	iverilog -o sim_native src/atm_fsm.v tb/atm_tb.v
	vvp sim_native

test: native
	@echo "Native simulation completed (test)."

all: test

deps:
	pip install -q flask flask-cors

backend: deps
	python3 app.py

serve:
	python3 -m http.server 8000

start:
	python3 start.py

cleanlocal:
	rm -f sim_native sim/atm_waves.vcd sim/last_run.txt
	rm -rf sim_build

