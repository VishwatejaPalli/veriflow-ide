# OpenHDL-IDE Tool Demonstration Examples

This directory contains comprehensive examples for testing all integrated EDA tools in OpenHDL-IDE.

## Directory Structure

```
examples/
├── demo_alu/              # Digital design examples
│   ├── alu.sv             # SystemVerilog ALU design
│   ├── alu_tb.sv          # Testbench with waveform generation
│   ├── alu_synth.ys       # Yosys synthesis script
│   └── verible_waiver.vlt # Verible lint waiver file
├── demo_spice/            # Analog simulation examples
│   ├── inverter.sp        # CMOS inverter circuit
│   └── rc_circuit.sp      # RC filter circuit
├── demo_timing/           # Timing analysis examples
│   ├── simple_path.sdc    # Timing constraints
│   └── sta_script.tcl     # OpenSTA analysis script
├── demo_layout/           # Layout examples
│   ├── simple_layout.tcl  # Magic layout script
│   └── klayout_drc.lydrc  # KLayout DRC rules
├── demo_netlist/          # LVS examples
│   ├── schematic_netlist.sp
│   ├── layout_netlist.sp
│   └── netgen_setup.tcl
└── README_TOOLS.md        # This file
```

## Tool Usage Examples

### 1. Simulation & Verification

#### **Icarus Verilog - Compile & Simulate**
1. Open: `Tools → Simulation & Verification → Compile with Icarus Verilog...`
2. Add files: `demo_alu/alu.sv`, `demo_alu/alu_tb.sv`
3. Output: `alu_tb.vvp`
4. Language Standard: `SystemVerilog-2012`
5. Click OK to compile
6. View results in Console tab

**Command-line equivalent:**
```bash
cd examples/demo_alu
iverilog -g2012 -o alu_tb.vvp alu.sv alu_tb.sv
vvp alu_tb.vvp
```

#### **View Waveforms**
1. After simulation, go to: `Tools → Waveforms`
2. Select: `demo_alu/alu_tb.vcd`
3. GTKWave will open showing all signals

#### **Verilator Lint**
1. Open: `Tools → Simulation & Verification → Lint with Verilator...`
2. Add file: `demo_alu/alu.sv`
3. Top module: `alu`
4. Enable: `-Wall`
5. Click OK
6. View warnings in Diagnostics tab

**Command-line equivalent:**
```bash
verilator --lint-only -Wall demo_alu/alu.sv
```

#### **Verible Lint**
1. Open: `Tools → Simulation & Verification → Lint with Verible...`
2. Add files: `demo_alu/alu.sv`
3. Waiver file: `demo_alu/verible_waiver.vlt` (optional)
4. Rules: `line-length=120` (optional)
5. View results in Console

**Command-line equivalent:**
```bash
verible-verilog-lint demo_alu/alu.sv
```

#### **Verible Format**
1. Open: `Tools → Simulation & Verification → Format with Verible...`
2. Add file: `demo_alu/alu.sv`
3. Column limit: 100
4. Indentation: 4
5. Check "Modify files in-place" if desired
6. Click OK

**Command-line equivalent:**
```bash
verible-verilog-format --column_limit=100 --indentation_spaces=4 demo_alu/alu.sv
```

---

### 2. Synthesis

#### **Yosys Synthesis**
1. First, make sure you have the ALU design
2. Open: `Tools → Synthesis → Synthesize with Yosys...`
3. Script file: `demo_alu/alu_synth.ys`
4. Optional: Enable verbose output
5. Optional: Set log file to `alu_synth.log`
6. Click OK
7. View results: `demo_alu/alu_synth.v`, `demo_alu/alu_synth.json`

**Command-line equivalent:**
```bash
cd examples/demo_alu
yosys -s alu_synth.ys
```

**Output files:**
- `alu_synth.v` - Gate-level netlist
- `alu_synth.json` - JSON representation
- `alu_schematic.dot` - Graphical representation (view with `dot -Tpng alu_schematic.dot -o alu.png`)

---

### 3. Layout & Physical Verification

#### **Magic Layout Tool**
1. Open: `Tools → Layout & Physical → Open Magic...`
2. Script: `demo_layout/simple_layout.tcl`
3. Enable "No console" for batch mode
4. Click OK
5. Layout will be created and saved as `simple_cell.mag`

**Command-line equivalent:**
```bash
cd examples/demo_layout
magic -noconsole simple_layout.tcl
```

#### **KLayout Viewer**
1. After creating GDS files (requires full flow), use:
2. Open: `Tools → Layout & Physical → KLayout Viewer...`
3. Select your `.gds` file
4. Optional: Specify technology file (`.lyt`)
5. Optional: Specify layer properties (`.lyp`)
6. Click OK

#### **KLayout DRC**
1. Open: `Tools → Layout & Physical → KLayout DRC...`
2. Layout file: Your `.gds` file
3. DRC script: `demo_layout/klayout_drc.lydrc`
4. Report file: `drc_violations.lyrdb`
5. Click OK
6. Check report for violations

**Command-line equivalent:**
```bash
klayout -b -r demo_layout/klayout_drc.lydrc your_layout.gds
```

#### **Netgen LVS**
1. Open: `Tools → Layout & Physical → Netgen LVS...`
2. First circuit: `demo_netlist/schematic_netlist.sp`
3. Second circuit: `demo_netlist/layout_netlist.sp`
4. Setup file: `demo_netlist/netgen_setup.tcl`
5. Output report: `lvs_report.out`
6. Click OK
7. Check report for mismatches

**Command-line equivalent:**
```bash
cd examples/demo_netlist
netgen -batch lvs schematic_netlist.sp layout_netlist.sp netgen_setup.tcl lvs_report.out
```

---

### 4. Timing & Analog

#### **OpenSTA Timing Analysis**
1. First synthesize with Yosys to get netlist
2. Open: `Tools → Timing & Analog → Static Timing (OpenSTA)...`
3. Select script: `demo_timing/sta_script.tcl`
4. Click OK
5. View timing reports in Console

**Note:** You'll need actual `.lib` liberty files for real timing analysis. The example script shows the structure.

**Command-line equivalent:**
```bash
cd examples/demo_timing
sta sta_script.tcl
```

#### **NgSpice Simulation**
1. Open: `Tools → Timing & Analog → NgSpice Simulation...`
2. Netlist: `demo_spice/inverter.sp` or `demo_spice/rc_circuit.sp`
3. Output log: `ngspice_output.log`
4. Click OK
5. Results will be in Console and `inverter_output.raw`

**Command-line equivalent:**
```bash
cd examples/demo_spice
ngspice -b inverter.sp -o inverter.log
```

**View waveforms:**
```bash
ngspice
ngspice> load inverter_output.raw
ngspice> plot v(in) v(out)
```

---

## Quick Test Workflow

### Complete Digital Flow (ALU Example)

```bash
# 1. Compile
Tools → Simulation → Compile with Icarus Verilog
Files: demo_alu/alu.sv, demo_alu/alu_tb.sv
Output: alu_tb.vvp

# 2. Simulate
vvp alu_tb.vvp (or use Tools → Simulate)

# 3. View waveforms
Tools → Waveforms → Select alu_tb.vcd

# 4. Lint check
Tools → Simulation → Lint with Verilator
File: demo_alu/alu.sv

# 5. Format code
Tools → Simulation → Format with Verible
File: demo_alu/alu.sv

# 6. Synthesize
Tools → Synthesis → Synthesize with Yosys
Script: demo_alu/alu_synth.ys
```

### Analog Flow (Inverter Example)

```bash
# 1. Simulate with NgSpice
Tools → Timing & Analog → NgSpice Simulation
Netlist: demo_spice/inverter.sp

# 2. Check results in Console tab

# 3. View plots in output files
```

---

## File Format Reference

### Verilog/SystemVerilog (`.v`, `.sv`)
- Design sources and testbenches
- Supported by: iverilog, Verilator, Verible, Yosys

### SPICE Netlist (`.sp`, `.spice`, `.cir`)
- Analog circuit descriptions
- Supported by: NgSpice, Netgen (LVS)

### Yosys Script (`.ys`)
- Synthesis commands and flow
- Supported by: Yosys

### SDC Constraints (`.sdc`)
- Timing constraints in Synopsys format
- Supported by: OpenSTA

### TCL Scripts (`.tcl`)
- Tool automation scripts
- Supported by: Magic, OpenSTA, Netgen, Yosys

### DRC Rules (`.lydrc`, `.drc`)
- Design rule checking scripts
- Supported by: KLayout

### Layout Files (`.mag`, `.gds`, `.oas`, `.def`)
- Physical layout in various formats
- Supported by: Magic, KLayout

---

## Tips for Best Results

1. **Start Simple**: Begin with the ALU example for digital flow
2. **Check Prerequisites**: Ensure all tools are installed (`which tool_name`)
3. **Use Command Preview**: Always review the command before execution
4. **Check Console Output**: Monitor the Console tab for errors
5. **Incremental Testing**: Test one tool at a time before combining
6. **Real Technology**: For production use, you'll need PDK files (SKY130, etc.)

---

## Common Issues

### "Command not found"
- Install the tool: `sudo apt install tool-name`
- Check PATH: `echo $PATH`

### "File not found"
- Use absolute paths in dialogs
- Check current directory
- Verify file exists: `ls -la filename`

### No output in Console
- Check if tool writes to stderr: Look at both stdout and stderr
- Try verbose mode if available
- Check for log files specified in options

### Synthesis fails
- Verify Verilog syntax with Verilator first
- Check all modules are defined
- Ensure parameter values are valid

---

## Additional Resources

- [Icarus Verilog](http://iverilog.icarus.com/)
- [Verilator](https://www.veripool.org/verilator/)
- [Verible](https://github.com/chipsalliance/verible)
- [Yosys](https://yosyshq.net/yosys/)
- [GTKWave](http://gtkwave.sourceforge.net/)
- [Magic](http://opencircuitdesign.com/magic/)
- [KLayout](https://www.klayout.de/)
- [Netgen](http://opencircuitdesign.com/netgen/)
- [NgSpice](http://ngspice.sourceforge.net/)
- [OpenSTA](https://github.com/The-OpenROAD-Project/OpenSTA)
- [OpenLane](https://github.com/The-OpenROAD-Project/OpenLane)

---

## Contributing Examples

To add new examples:
1. Create a new subdirectory: `examples/demo_yourfeature/`
2. Add source files with clear comments
3. Include test/verification files
4. Add tool configuration files (scripts, constraints)
5. Update this README with usage instructions
6. Test with the IDE dialogs

---

**Happy designing with OpenHDL-IDE! 🚀**
