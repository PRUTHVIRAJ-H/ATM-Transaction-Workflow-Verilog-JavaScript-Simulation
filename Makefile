# Default settings
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Your Verilog file
VERILOG_SOURCES += $(PWD)/src/atm_fsm.v

# Use the Python file we just created (without the .py extension)
MODULE = test_atm_fuzzer

# The name of the top-level module inside your Verilog code
TOPLEVEL = atm_fsm

# This flag tells Icarus Verilog to generate the GTKWave .vcd file automatically!
# Do not pass simulator-specific flags via EXTRA_ARGS (avoids vvp receiving -g2012)

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: native
native:
	iverilog -o sim_native src/atm_fsm.v tb/atm_tb.v
	vvp sim_native

.PHONY: test
test: native
	@echo "Native simulation completed (test)."

.PHONY: all
all: test

.PHONY: cleanlocal
cleanlocal:
	rm -f sim_native atm_waves.vcd
	rm -rf sim_build

