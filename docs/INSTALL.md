# Installation Guide

## 1. Prerequisites
- **Python**: 3.10 or newer (3.12 tested)
- **System packages**: build-essential (Linux) or Visual Studio Build Tools (Windows) to satisfy PySide6 dependencies.
- **EDA tools** (install via your package manager or source builds):
  - [Icarus Verilog](http://iverilog.icarus.com/)
  - [Yosys](https://yosyshq.net/yosys/)
  - [GTKWave](http://gtkwave.sourceforge.net/)
  - `vvp` is installed alongside Icarus Verilog.
- **Git** for cloning the repo.

## 2. Clone the Repository
```
git clone https://github.com/<your-org>/openhdl-ide.git
cd openhdl-ide
```

## 3. Configure Python Environment
```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
```

## 4. Install Python Dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Verify Toolchain
```
iverilog -v
vvp -V
yosys -V
gtkwave --version
```
Address missing tools before running the IDE.

## 6. Launch the IDE
```
python main.py
```
If QScintilla bindings are not found, the editor falls back to a plain text widget—install matching PySide6 QScintilla wheels for full syntax features.

## 7. Troubleshooting
- **Qt platform errors**: ensure `QT_PLUGIN_PATH` is unset or points to the PySide6 installation.
- **Missing libxcb (Linux)**: install `libxcb-xinerama0` and related Qt runtime packages.
- **PyInstaller build fails**: delete `build/` and `dist/`, ensure the virtualenv is active, rerun `pyinstaller openhdl-ide.spec`.
- **Tool not in PATH**: update your shell rc file or use the in-app settings (future feature) to point to binaries.
