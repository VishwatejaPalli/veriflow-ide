# OpenHDL-IDE Tools Guide

This guide documents all the EDA (Electronic Design Automation) tools integrated into OpenHDL-IDE with their GUI dialogs and configuration options.

## Table of Contents
- [Simulation & Verification](#simulation--verification)
- [Synthesis](#synthesis)
- [Layout & Physical Verification](#layout--physical-verification)
- [Timing & Analog](#timing--analog)

---

## Simulation & Verification

### Icarus Verilog (iverilog)
**Purpose**: Verilog/SystemVerilog compiler

**Dialog Features**:
- File list widget for adding multiple source files
- Output file selection with browse button
- Language standard selection (Verilog-1995 through SystemVerilog-2012)
- Include directories (comma-separated)
- Preprocessor defines
- Debug information toggle
- Extra command-line arguments
- Live command preview

**Menu**: Tools → Simulation & Verification → Compile with Icarus Verilog...

**Example Use Cases**:
- Compile Verilog designs for simulation
- Generate VVP executable for VVP simulator

---

### Verilator Lint
**Purpose**: High-performance Verilog/SystemVerilog linter

**Dialog Features**:
- Source file selector
- Top module name configuration
- Include directory paths
- Warning level control (-Wall option)
- Extra arguments field
- Command preview

**Menu**: Tools → Simulation & Verification → Lint with Verilator...

**Example Use Cases**:
- Check code for lint warnings
- Verify SystemVerilog syntax
- Catch design issues early

---

### Verilator Coverage
**Purpose**: Code coverage analysis

**Menu**: Tools → Simulation & Verification → Coverage Report (Verilator)

**Note**: Uses file selection dialogs for coverage data files

---

### Verible Lint
**Purpose**: SystemVerilog style linter from Google

**Dialog Features**:
- Source file list management
- Custom lint rules configuration
- Waiver file support (for suppressing specific warnings)
- Extra arguments
- Command preview

**Menu**: Tools → Simulation & Verification → Lint with Verible...

**Example Use Cases**:
- Enforce coding style guidelines
- Check SystemVerilog best practices
- Integrate with CI/CD pipelines

**Documentation**: https://github.com/chipsalliance/verible

---

### Verible Format
**Purpose**: SystemVerilog code formatter

**Dialog Features**:
- Source file selection
- In-place modification toggle
- Column limit configuration (40-200)
- Indentation spaces (1-8)
- Extra arguments
- Command preview

**Menu**: Tools → Simulation & Verification → Format with Verible...

**Example Use Cases**:
- Auto-format code to standard style
- Clean up inconsistent indentation
- Prepare code for version control

---

## Synthesis

### Yosys
**Purpose**: Open-source RTL synthesis tool

**Dialog Features**:
- Synthesis script file browser
- Quiet mode toggle
- Verbose output option
- Log file specification
- Extra arguments
- Command preview

**Menu**: Tools → Synthesis → Synthesize with Yosys...

**Example Use Cases**:
- Synthesize Verilog to gate-level netlist
- Technology mapping
- Generate graphical representations (show command)

**Documentation**: https://yosyshq.net/yosys/

---

### OpenLane
**Purpose**: Complete RTL-to-GDSII flow

**Menu**: Tools → Synthesis → OpenLane Flow...

**Note**: Uses input dialogs for design name and directory selection

**Example Use Cases**:
- Run full ASIC design flow
- Generate GDSII layout from RTL
- Target SkyWater 130nm PDK

**Documentation**: https://github.com/The-OpenROAD-Project/OpenLane

---

### OpenROAD
**Purpose**: Place and route tool

**Menu**: Tools → Synthesis → OpenROAD...

**Note**: Uses file selection for TCL scripts

**Example Use Cases**:
- Physical design implementation
- Floorplanning and placement
- Clock tree synthesis
- Detailed routing

**Documentation**: https://github.com/The-OpenROAD-Project

---

## Layout & Physical Verification

### Magic
**Purpose**: VLSI layout editor and DRC/LVS tool

**Dialog Features**:
- Layout file browser (.mag, .gds, .def)
- Technology file selection
- TCL script execution
- No console mode
- Batch mode (no GUI)
- Extra arguments
- Command preview

**Menu**: Tools → Layout & Physical → Open Magic...

**Example Use Cases**:
- View and edit layouts
- Run DRC (Design Rule Check)
- Extract SPICE netlists
- GDS import/export

**Documentation**: http://opencircuitdesign.com/magic/

---

### KLayout Viewer
**Purpose**: High-performance layout viewer

**Dialog Features**:
- Layout file browser (.gds, .oas, .dxf)
- Technology file (.lyt)
- Layer properties file (.lyp)
- Extra arguments
- Command preview

**Menu**: Tools → Layout & Physical → KLayout Viewer...

**Example Use Cases**:
- View GDS/OASIS layouts
- Inspect design hierarchy
- Measure features
- Cross-section viewing

**Documentation**: https://www.klayout.de/

---

### KLayout DRC
**Purpose**: Design Rule Checking with KLayout

**Dialog Features**:
- Layout file selection
- DRC rule script browser
- Report file output specification
- Batch mode execution
- Command preview

**Menu**: Tools → Layout & Physical → KLayout DRC...

**Example Use Cases**:
- Verify design against technology rules
- Generate DRC violation reports
- Automated physical verification

---

### Netgen LVS
**Purpose**: Layout vs. Schematic verification

**Menu**: Tools → Layout & Physical → Netgen LVS...

**Note**: Uses sequential file dialogs for two circuits and setup file

**Example Use Cases**:
- Verify layout matches schematic
- Compare pre/post-layout netlists
- Ensure correct device extraction

**Documentation**: http://opencircuitdesign.com/netgen/

---

## Timing & Analog

### OpenSTA
**Purpose**: Static Timing Analysis

**Menu**: Tools → Timing & Analog → Static Timing (OpenSTA)...

**Note**: Uses file selection for TCL scripts

**Example Use Cases**:
- Verify timing constraints
- Analyze setup/hold violations
- Generate timing reports
- Corner analysis

**Documentation**: https://github.com/The-OpenROAD-Project/OpenSTA

---

### NgSpice
**Purpose**: Open-source SPICE simulator

**Menu**: Tools → Timing & Analog → NgSpice Simulation...

**Note**: Uses file selection for SPICE netlists

**Example Use Cases**:
- Analog circuit simulation
- Transistor-level verification
- Power analysis
- Transient/AC/DC analysis

**Documentation**: http://ngspice.sourceforge.net/

---

## Tool Installation

### Linux (Ubuntu/Debian)
```bash
# Simulation & Verification
sudo apt install iverilog verilator gtkwave

# Verible (from GitHub releases)
wget https://github.com/chipsalliance/verible/releases/download/latest/verible-latest-linux-static-x86_64.tar.gz
tar -xzf verible-latest-linux-static-x86_64.tar.gz
sudo cp verible-*/bin/* /usr/local/bin/

# Synthesis
sudo apt install yosys

# Layout & Physical
sudo apt install magic klayout netgen

# Analog
sudo apt install ngspice
```

### macOS (Homebrew)
```bash
brew install icarus-verilog verilator
brew install yosys
brew install magic netgen ngspice
brew install --cask klayout
```

### Windows
Most tools have prebuilt Windows binaries or can be built using MSYS2/MinGW.

---

## Command Preview Feature

All dialogs include a **Command Preview** section that shows the exact command-line string that will be executed. This allows you to:

1. **Learn**: See how command-line options are structured
2. **Debug**: Verify parameters before execution
3. **Reproduce**: Copy commands for use in scripts or makefiles
4. **Customize**: Understand what to add in "Extra Arguments" fields

---

## File Selection Widgets

Many dialogs feature a **FileListWidget** for managing multiple input files:

- **Add Files...**: Browse and select multiple files
- **Remove**: Delete selected items from list
- **Clear All**: Empty the entire list
- Drag and drop support (planned)

---

## Best Practices

### 1. Start Simple
Begin with basic options before adding complex arguments.

### 2. Use Command Preview
Always check the command preview before execution to catch typos or mistakes.

### 3. Save Configurations
For repeated operations, consider:
- Saving commands to a script
- Using project makefiles
- Creating build automation

### 4. Check Tool Availability
Use `which <tool>` or `<tool> --version` to verify tools are installed and in your PATH.

### 5. Read Tool Documentation
Each tool has extensive documentation. Links are provided in this guide.

---

## Integration with IDE

### Console Output
All tool executions display output in the **Console** tab at the bottom panel.

### Diagnostics
Error parsing extracts file/line information from tool output and displays it in the **Diagnostics** tab for quick navigation.

### History
The **History** tab tracks all executed commands with timestamps and status. Click any entry to re-run.

### Coverage
Verilator coverage results display in the dedicated **Coverage** tab.

---

## Future Enhancements

- [ ] Save/Load dialog configurations
- [ ] Project-specific tool settings
- [ ] Preset configurations (e.g., "Quick Lint", "Full Synthesis")
- [ ] Tool chain automation (compile → simulate → verify)
- [ ] Additional tool integrations (Surelog, Slang, etc.)
- [ ] Waveform viewer integration improvements
- [ ] Real-time output streaming with syntax highlighting

---

## Contributing

To add a new tool:

1. Create tool wrapper in `tools/<toolname>.py` extending `ToolBase`
2. Create dialog in `gui/dialogs.py` with configuration widgets
3. Add imports and initialization in `gui/main_window.py`
4. Add menu action and handler method
5. Update this documentation
6. Add tests in `tests/test_tools.py`

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed architecture information.

---

## Troubleshooting

### Tool Not Found
**Error**: `command not found` or similar

**Solution**: 
- Install the tool using your package manager
- Add tool directory to PATH
- Verify with `which <tool>` or `where <tool>` (Windows)

### Permission Denied
**Error**: Permission issues when running tools

**Solution**:
- Check file permissions
- Ensure tool executables have execute bit set: `chmod +x /path/to/tool`

### Path Issues
**Error**: Tool can't find input files

**Solution**:
- Use absolute paths in file selections
- Check current working directory
- Verify file existence before running

### Output Not Showing
**Error**: Command runs but no output in console

**Solution**:
- Check if tool sends output to stderr instead of stdout
- Look for log files specified in tool options
- Try verbose mode if available

---

For more help, see:
- [USER_GUIDE.md](USER_GUIDE.md) - General IDE usage
- [INSTALL.md](INSTALL.md) - Installation and setup
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Architecture and development
