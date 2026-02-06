# OpenHDL-IDE

OpenHDL-IDE is a cross-platform HDL development environment that brings editing, simulation, synthesis, waveform viewing, and project management into a single PySide6 desktop application. It targets open-source toolchains (iverilog/vvp, Yosys, GTKWave) while remaining lightweight and hackable for hardware teams.

## Feature Highlights
- QScintilla-powered Verilog/SystemVerilog editor with fallbacks when QScintilla bindings are unavailable
- Tool wrappers for iverilog, vvp, Yosys, and GTKWave with unified command execution
- Optional Verilator lint + coverage helpers (verilator_coverage annotate/write-info flows)
- Multi-pane output dock with Console, Diagnostics, Coverage, and History tabs plus one-click reruns
- File tree context menu for fast new-file/new-folder, rename, and delete operations
- Docked console for logs plus regex-based error parsing to jump from diagnostics back to code (WIP UI hookup)
- JSON project manifest with top-module tracking and file lists
- Integration tests that compile and run a minimal design through iverilog → vvp to keep the flow healthy

## Requirements
- Python 3.10+
- PySide6 and QScintilla Python bindings (installed via `pip install -r requirements.txt`)
- CLI tools in `$PATH`: `iverilog`, `vvp`, `yosys`, `gtkwave` (optional: `verilator`, `verilator_coverage` for lint/coverage helpers)
- Linux or Windows desktop (macOS should work but is untested)

## Getting Started
1. **Clone & enter**
	```bash
	git clone https://github.com/<your-org>/openhdl-ide.git
	cd openhdl-ide
	```
2. **Create virtualenv (optional but recommended)**
	```bash
	python -m venv .venv
	source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
	```
3. **Install Python deps**
	```bash
	pip install -r requirements.txt
	```
4. **Run the IDE**
	```bash
	python main.py
	```

## Testing
Run the full suite (unit + integration) via:
```bash
python -m unittest discover
```
Integration tests automatically skip if the required external tools are missing.

## Examples
- `examples/simple_counter/`: runnable Verilog design + testbench + Yosys scripts
- `examples/systemverilog_demo.sv`: standalone SystemVerilog module showcasing packages, interfaces, and `always_ff/always_comb`

## Project Layout
```
openhdl-ide/
├── core/          # App bootstrap, config, logging
├── gui/           # Main window, editor, console, dialogs, future widgets
├── tools/         # Wrappers for iverilog, yosys, vvp, GTKWave
├── project/       # JSON project manager helpers
├── parser/        # Error/log parsers
├── utils/         # Execution helpers, threading utilities (future work)
├── resources/     # Icons and other assets
└── tests/         # Unit & integration tests
```

## Documentation
- [docs/INSTALL.md](docs/INSTALL.md): OS/tooling prerequisites & troubleshooting
- [docs/USER_GUIDE.md](docs/USER_GUIDE.md): IDE walkthrough, workflows, shortcuts
- [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md): Architecture notes, coding standards, roadmap

## Packaging
Use PyInstaller to build a standalone binary once dependencies are installed:
```bash
pyinstaller openhdl-ide.spec
```
See [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for customization tips and platform notes.

## Roadmap
- Hook GUI to tool runners and error parser for clickable diagnostics
- Implement file tree/project dialogs and logging pane persistence
- Add waveform launch actions plus run/simulate toolbar buttons
- Expand automated tests (GUI smoke tests, parser edge cases)
- Polish cross-platform installer experience

Contributions via issues/PRs are welcome!
