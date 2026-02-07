# Makefile for OpenHDL-IDE Tool Demonstrations
# Use 'make help' to see available targets

.PHONY: all help clean sim lint synth spice layout timing

# Default target
all: help

help:
	@echo "OpenHDL-IDE Tool Demonstrations"
	@echo "================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make sim       - Run digital simulation (iverilog + vvp)"
	@echo "  make lint      - Run linting (Verilator + Verible)"
	@echo "  make format    - Format code with Verible"
	@echo "  make synth     - Run synthesis (Yosys)"
	@echo "  make spice     - Run SPICE simulation (NgSpice)"
	@echo "  make layout    - Generate layout (Magic)"
	@echo "  make timing    - Run timing analysis (OpenSTA)"
	@echo "  make waveform  - View simulation waveforms"
	@echo "  make all-tests - Run all available tests"
	@echo "  make clean     - Remove generated files"
	@echo ""

# Digital Simulation
sim: demo_alu/alu_tb.vvp
	@echo "Running VVP simulation..."
	cd demo_alu && vvp alu_tb.vvp
	@echo "✓ Simulation complete. VCD file: demo_alu/alu_tb.vcd"

demo_alu/alu_tb.vvp: demo_alu/alu.sv demo_alu/alu_tb.sv
	@echo "Compiling with Icarus Verilog..."
	cd demo_alu && iverilog -g2012 -o alu_tb.vvp alu.sv alu_tb.sv
	@echo "✓ Compilation complete"

# Linting
lint:
	@echo "Running Verilator lint..."
	-verilator --lint-only -Wall demo_alu/alu.sv
	@echo ""
	@echo "Running Verible lint..."
	-cd demo_alu && verible-verilog-lint alu.sv
	@echo "✓ Lint checks complete"

# Code formatting
format:
	@echo "Formatting with Verible..."
	cd demo_alu && verible-verilog-format --inplace --column_limit=100 --indentation_spaces=4 alu.sv
	@echo "✓ Formatting complete"

# Synthesis
synth: demo_alu/alu_synth.v

demo_alu/alu_synth.v: demo_alu/alu.sv demo_alu/alu_synth.ys
	@echo "Running Yosys synthesis..."
	cd demo_alu && yosys -s alu_synth.ys
	@echo "✓ Synthesis complete"
	@echo "Generated files:"
	@echo "  - demo_alu/alu_synth.v"
	@echo "  - demo_alu/alu_synth.json"

# SPICE simulation
spice:
	@echo "Running NgSpice simulation (inverter)..."
	cd demo_spice && ngspice -b inverter.sp -o inverter.log
	@echo "✓ SPICE simulation complete"
	@echo "Log: demo_spice/inverter.log"

# Layout generation
layout:
	@echo "Generating layout with Magic..."
	cd demo_layout && magic -dnull -noconsole simple_layout.tcl
	@echo "✓ Layout generation complete"

# Timing analysis (requires liberty files)
timing:
	@echo "Running OpenSTA timing analysis..."
	@echo "NOTE: Requires actual .lib files for meaningful results"
	-cd demo_timing && sta sta_script.tcl
	@echo "✓ Timing analysis attempted"

# View waveforms
waveform: demo_alu/alu_tb.vcd
	@echo "Opening GTKWave..."
	gtkwave demo_alu/alu_tb.vcd &

demo_alu/alu_tb.vcd: sim

# Run all available tests
all-tests:
	@echo "Running all available tests..."
	@bash run_tests.sh

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -f demo_alu/*.vvp demo_alu/*.vcd demo_alu/*_synth.* demo_alu/*.dot
	rm -f demo_spice/*.log demo_spice/*.raw
	rm -f demo_layout/*.mag demo_layout/*.ext demo_layout/*.spice
	rm -f demo_netlist/*.out
	@echo "✓ Clean complete"

# Quick test - compile and simulate
quick: sim
	@echo ""
	@echo "Quick test complete!"
	@echo "To view waveforms: make waveform"

# Show tool versions
versions:
	@echo "Installed Tool Versions:"
	@echo "========================"
	-@which iverilog >/dev/null 2>&1 && iverilog -V | head -1 || echo "iverilog: not installed"
	-@which verilator >/dev/null 2>&1 && verilator --version | head -1 || echo "verilator: not installed"
	-@which yosys >/dev/null 2>&1 && yosys -V | head -1 || echo "yosys: not installed"
	-@which verible-verilog-lint >/dev/null 2>&1 && verible-verilog-lint --version || echo "verible: not installed"
	-@which ngspice >/dev/null 2>&1 && ngspice -v | head -1 || echo "ngspice: not installed"
	-@which magic >/dev/null 2>&1 && echo "magic: installed" || echo "magic: not installed"
	-@which klayout >/dev/null 2>&1 && klayout -v | head -1 || echo "klayout: not installed"
	-@which gtkwave >/dev/null 2>&1 && echo "gtkwave: installed" || echo "gtkwave: not installed"
