# Developer Guide

## Architecture
```
GUI (PySide6 widgets)
  └── Controllers/Managers
        └── Tool wrappers + Runner utilities
              └── External CLI tools (iverilog, vvp, yosys, gtkwave)
```
- `core/app.py` bootstraps Qt and loads `gui/main_window.py`.
- `gui/` contains presentational widgets; keep business logic out of them when possible.
- `tools/` hosts thin wrappers that turn arguments into shell commands and run them via `ToolBase`.
- `project/` stores metadata in JSON for reproducible builds.
- `parser/` transforms console logs into structured data for UI consumption.

## Coding Guidelines
- Prefer dependency injection: pass tool instances/controllers instead of importing singletons.
- Keep GUI responsive—run long operations in threads (future `utils/threads.py`).
- Log meaningful events once `core/logger.py` is implemented; plan for log levels.
- Default to ASCII unless files already rely on Unicode.
- Add concise comments only when intent is non-obvious.

## Tests
- Location: `tests/`
- Run command: `python -m unittest discover`
- `test_tools.py`: command builders + iverilog→vvp integration flow
- `test_project.py`: verifies project metadata persistence
- `test_parser.py`: validates error regex
- Extend with mocks/fakes for GUI interactions as features mature.

## Packaging with PyInstaller
1. Activate the virtualenv and install deps.
2. Run `pyinstaller openhdl-ide.spec`.
3. Output directories:
   - `dist/openhdl-ide/` contains the distributable bundle
   - `build/` holds intermediate artifacts (safe to delete)
4. Ship supporting files (icons, README, docs) alongside the executable or embed via `datas` in the spec file.

## Release Checklist
- `python -m unittest discover`
- `python -m compileall .`
- Manual smoke test: create project, run compile/simulate, open waveform
- Update README + docs with any new features
- Build PyInstaller artifact on each target platform
- Tag release and attach binaries

## Roadmap for Contributors
1. Wire GUI actions to tool execution and log console.
2. Implement file tree + dialogs for new/open project and file import.
3. Add error list dockable widget with jump-to-line support.
4. Persist workspace settings (recent projects, tool paths).
5. Integrate synthesis reports and resource visualization.
6. Explore basic waveform preview inside the IDE.
