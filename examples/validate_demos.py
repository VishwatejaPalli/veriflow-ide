#!/usr/bin/env python3
"""
Demo File Generator and Validator for OpenHDL-IDE
This script validates all demo files and can regenerate them if needed.
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath):
    """Check if a file exists and return status."""
    path = Path(filepath)
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    return exists, size

def validate_demos():
    """Validate all demo files."""
    print("OpenHDL-IDE Demo Files Validator")
    print("=" * 50)
    print()
    
    demo_files = {
        "Digital Simulation": [
            "demo_alu/alu.sv",
            "demo_alu/alu_tb.sv",
        ],
        "Synthesis": [
            "demo_alu/alu_synth.ys",
        ],
        "Linting": [
            "demo_alu/verible_waiver.vlt",
        ],
        "Analog Simulation": [
            "demo_spice/inverter.sp",
            "demo_spice/rc_circuit.sp",
        ],
        "Timing Analysis": [
            "demo_timing/simple_path.sdc",
            "demo_timing/sta_script.tcl",
        ],
        "Layout": [
            "demo_layout/simple_layout.tcl",
            "demo_layout/klayout_drc.lydrc",
        ],
        "LVS": [
            "demo_netlist/schematic_netlist.sp",
            "demo_netlist/layout_netlist.sp",
            "demo_netlist/netgen_setup.tcl",
        ],
    }
    
    script_dir = Path(__file__).parent
    all_valid = True
    
    for category, files in demo_files.items():
        print(f"{category}:")
        for file in files:
            filepath = script_dir / file
            exists, size = check_file_exists(filepath)
            status = "✓" if exists else "✗"
            size_str = f"({size} bytes)" if exists else "(missing)"
            print(f"  [{status}] {file:40s} {size_str}")
            if not exists:
                all_valid = False
        print()
    
    if all_valid:
        print("✓ All demo files are present!")
    else:
        print("✗ Some demo files are missing!")
        print("\nYou can regenerate them from the OpenHDL-IDE repository")
        print("or by re-running the file creation process.")
    
    return all_valid

def list_tool_commands():
    """List example commands for each tool."""
    print("\nQuick Command Reference")
    print("=" * 50)
    
    commands = {
        "Icarus Verilog": "iverilog -g2012 -o design.vvp design.sv testbench.sv",
        "VVP Simulator": "vvp design.vvp",
        "GTKWave": "gtkwave waveform.vcd",
        "Verilator Lint": "verilator --lint-only -Wall design.sv",
        "Verible Lint": "verible-verilog-lint design.sv",
        "Verible Format": "verible-verilog-format --inplace design.sv",
        "Yosys": "yosys -s synth_script.ys",
        "Magic": "magic -noconsole layout_script.tcl",
        "KLayout": "klayout layout.gds",
        "KLayout DRC": "klayout -b -r drc_rules.lydrc layout.gds",
        "Netgen LVS": "netgen -batch lvs schem.sp layout.sp setup.tcl",
        "NgSpice": "ngspice -b netlist.sp",
        "OpenSTA": "sta timing_script.tcl",
    }
    
    for tool, cmd in commands.items():
        print(f"\n{tool}:")
        print(f"  {cmd}")
    print()

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--commands":
        list_tool_commands()
        return
    
    valid = validate_demos()
    
    print("\nUsage:")
    print("  python validate_demos.py             - Validate all demo files")
    print("  python validate_demos.py --commands  - Show command reference")
    print()
    
    return 0 if valid else 1

if __name__ == "__main__":
    sys.exit(main())
