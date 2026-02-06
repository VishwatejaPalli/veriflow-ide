# User Guide

## Overview
OpenHDL-IDE focuses on a clean workflow for Verilog/SystemVerilog design:
1. Manage HDL files inside a project.
2. Edit source with syntax assist.
3. Compile and simulate via iverilog/vvp.
4. Synthesize with Yosys.
5. Inspect waveforms in GTKWave.
6. Review diagnostics directly in the IDE.

## Layout
- **Menu bar**: File/Open project, Edit commands, Tools (compile/run hooks), Help.
- **Toolbar**: Quick actions (build/run placeholders—bind them in `gui/main_window.py`).
- **Left pane**: Project/File tree placeholder (to be wired to `gui/file_tree.py`).
- **Right top pane**: QScintilla-based editor (falls back to `QPlainTextEdit` when QScintilla is missing).
- **Right bottom pane**: Console output (`gui/console.py`), colorization to be added.

## Typical Workflow
1. **Create/Open Project**: Use ProjectManager via a quick script or integrate the upcoming dialog:
   ```python
   from project.manager import ProjectManager
   pm = ProjectManager("/path/to/project")
   pm.load()
   pm.add_file("rtl/top.v")
   pm.set_top_module("top")
   ```
2. **Edit HDL**: Launch the IDE (`python main.py`), load files from the tree (future), or use the editor for quick notes.
3. **Compile**: Trigger `IverilogTool` with the project file list. For now, run from a Python shell:
   ```python
   from tools.iverilog import IverilogTool
   cmd = IverilogTool().build_command(["rtl/top.v", "tb/top_tb.v"], "build/out.vvp")
   ```
4. **Simulate**: `VvpTool().run("vvp build/out.vvp")`.
5. **Synthesize**: `YosysTool().run("yosys -s scripts/synth.ys")`.
6. **Waveforms**: After simulation emits a VCD, `GtkWaveTool().launch_viewer("waves/top.vcd")`.
7. **Error Review**: Pipe stdout/stderr into `parser.ErrorParser.parse()` to convert diagnostics into clickable entries.

## Keyboard Shortcuts (planned)
| Action            | Shortcut |
|-------------------|----------|
| Save file         | Ctrl+S   |
| Run simulation    | F5       |
| Launch GTKWave    | F6       |
| Toggle console    | Ctrl+`   |

## Tips
- Keep external tool paths consistent by adding them to PATH or expose them via future settings dialog.
- Use the integration tests (`python -m unittest discover`) after modifying tool wrappers.
- When GTKWave launches from the IDE, it runs as a detached process—close it manually when done.

## Known Limitations
- File tree and dialogs are placeholders.
- Error list is parsed but not yet wired to clickable UI.
- QScintilla wheels for PySide6 are not bundled; install separately.
- Packaging targets Linux/Windows; macOS is untested.
