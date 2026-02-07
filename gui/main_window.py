import json
import shlex
import subprocess
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QThread, QUrl, QEvent, QObject, QTimer, QSize
from PySide6.QtGui import QAction, QActionGroup, QColor, QDesktopServices, QFont, QKeySequence
from PySide6.QtWidgets import (
	QApplication,
	QColorDialog,
	QFileDialog,
	QFontDialog,
	QDialog,
	QInputDialog,
	QLabel,
	QListView,
	QMainWindow,
	QMenuBar,
	QMessageBox,
	QSplitter,
	QTabWidget,
	QToolBar,
	QVBoxLayout,
	QWidget,
	QTreeView,
)

from gui.console import ConsoleWidget
from gui.coverage import CoverageWidget
from gui.diagnostics import DiagnosticsWidget
from gui.dialogs import (
	IverilogDialog,
	YosysDialog,
	VerilatorDialog,
	VeribleDialog,
	MagicDialog,
	KLayoutDialog,
)
from gui.editor import EditorTabs
from gui.file_tree import FileTreeWidget
from gui.history import RunHistoryWidget
from parser.error_parser import ErrorParser
from tools.gtkwave import GtkWaveTool
from tools.iverilog import IverilogTool
from tools.klayout import KLayoutDRCTool, KLayoutTool
from tools.magic import MagicTool, NetgenTool
from tools.ngspice import NgSpiceTool
from tools.openlane import OpenLaneTool, OpenROADTool
from tools.opensta import OpenSTATool
from tools.verible import VeribleFormatTool, VeribleLintTool
from tools.verilator import VerilatorCoverageTool, VerilatorLintTool
from tools.vvp import VvpTool
from tools.yosys import YosysTool
from utils.runner import CommandRunner

THEME_PALETTES = {
	"light": {
		"window": "#f9fbff",
		"menu": "#eef3fb",
		"panel": "#ffffff",
		"text": "#1e293b",
		"subtext": "#475569",
		"border": "#d0d9ea",
		"splitter": "#c7d2e8",
		"status": "#e7ecf6",
		"accent": "#2563eb",
		"error": "#dc2626",
		"warning": "#d97706",
		"success": "#16a34a",
	},
	"dark": {
		"window": "#0b1220",
		"menu": "#121a2f",
		"panel": "#161f36",
		"text": "#f1f5f9",
		"subtext": "#94a3b8",
		"border": "#2b3553",
		"splitter": "#334067",
		"status": "#121a2f",
		"accent": "#3b82f6",
		"error": "#ef4444",
		"warning": "#f59e0b",
		"success": "#22c55e",
	},
}

ACCENT_PALETTES = {
	"blue": {"accent": "#2563eb", "hover": "#1d4ed8", "selection": "#cbdcfb"},
	"emerald": {"accent": "#10b981", "hover": "#059669", "selection": "#bbf7d0"},
	"amber": {"accent": "#f59e0b", "hover": "#d97706", "selection": "#fde68a"},
	"violet": {"accent": "#7c3aed", "hover": "#6d28d9", "selection": "#ddd6fe"},
	"rose": {"accent": "#e11d48", "hover": "#be123c", "selection": "#fecdd3"},
}

APP_VERSION = "1"

UI_SCALE_PRESETS = {
	"small": {"label": "Compact", "font": 10, "scale": 0.9},
	"medium": {"label": "Standard", "font": 11, "scale": 1.0},
	"large": {"label": "Comfort", "font": 12, "scale": 1.15},
}


def _shade(color_hex, factor):
    color = QColor(color_hex)
    if factor >= 0:
        color = color.lighter(100 + factor)
    else:
        color = color.darker(100 - factor)
    return color.name()


class WatermarkOverlay(QObject):
	def __init__(self, target, text):
		super().__init__(target)
		self._target = target
		self._scale = 1.0
		self._color_hex = "#ffffff"
		self._label = QLabel(text.upper(), target)
		self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
		self._label.setStyleSheet(self._style(self._color_hex))
		self._label.setObjectName("watermarkLabel")
		self._target.installEventFilter(self)
		self._update_position()
		self._label.raise_()

	def set_color(self, color_hex):
		self._color_hex = color_hex
		self._label.setStyleSheet(self._style(color_hex))

	def set_scale(self, scale):
		self._scale = max(0.75, min(1.5, scale or 1.0))
		self._label.setStyleSheet(self._style(self._color_hex))
		self._update_position()

	def eventFilter(self, obj, event):
		if obj is self._target and event.type() in {QEvent.Type.Resize, QEvent.Type.Show}:
			self._update_position()
		return super().eventFilter(obj, event)

	def _update_position(self):
		margin = max(6, int(10 * self._scale))
		self._label.adjustSize()
		self._label.move(margin, margin)

	def _style(self, color_hex):
		color = QColor(color_hex)
		alpha = 60
		font_size = max(9, int(11 * self._scale))
		letter = max(2, int(4 * self._scale))
		return (
			"color: rgba({r}, {g}, {b}, {a}); font-size: {size}px; font-weight: 600; "
			"letter-spacing: {letter}px; text-transform: uppercase; background: transparent;"
		).format(r=color.red(), g=color.green(), b=color.blue(), a=alpha, size=font_size, letter=letter)


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle(f"OpenHDL-IDE v{APP_VERSION}")
		self.resize(1100, 720)
		self._active_runs = []
		self._run_contexts = {}
		self._theme = "light"
		self._accent = "blue"
		self._ui_scale_mode = "medium"
		self._ui_scale_group = None
		self._auto_theme_enabled = False
		self._auto_theme_day = "light"
		self._auto_theme_night = "dark"
		self._auto_theme_day_start = 7
		self._auto_theme_night_start = 19
		self._auto_theme_action = None
		self._auto_day_group = None
		self._auto_night_group = None
		self._editor_font = QFont("Fira Code", 11)
		self._custom_window_color = None
		self._settings_path = Path.home() / ".openhdl_ide_settings.json"
		self._theme_timer = None
		self.iverilog = IverilogTool()
		self.vvp = VvpTool()
		self.yosys = YosysTool()
		self.gtkwave = GtkWaveTool()
		self.verilator_lint = VerilatorLintTool()
		self.verilator_coverage = VerilatorCoverageTool()
		# New tools
		self.verible_lint = VeribleLintTool()
		self.verible_format = VeribleFormatTool()
		self.magic = MagicTool()
		self.netgen = NetgenTool()
		self.klayout = KLayoutTool()
		self.klayout_drc = KLayoutDRCTool()
		self.ngspice = NgSpiceTool()
		self.opensta = OpenSTATool()
		self.openlane = OpenLaneTool()
		self.openroad = OpenROADTool()
		self._watermarks = []
		self._version_label = None
		self._load_user_settings()
		self._setup_ui()
		self._initialize_auto_theme()

	def _setup_ui(self):
		menu_bar = QMenuBar(self)
		self.setMenuBar(menu_bar)
		self._build_menus(menu_bar)

		toolbar = QToolBar("Main Toolbar", self)
		self.addToolBar(toolbar)

		self._add_action(toolbar, "Compile", self.compile_design)
		self._add_action(toolbar, "Simulate", self.run_simulation)
		self._add_action(toolbar, "Synthesize", self.run_synthesis)
		self._add_action(toolbar, "Waveforms", self.launch_waveform_viewer)
		self._add_action(toolbar, "View Schematic", self.open_schematic_file)
		self._add_action(toolbar, "Clear Console", self.clear_console)

		for action in toolbar.actions():
			self.tools_menu.addAction(action)
		self.tools_menu.addSeparator()
		
		# Simulation & Verification submenu
		sim_menu = self.tools_menu.addMenu("Simulation && Verification")
		self._add_menu_action(sim_menu, "Compile with Icarus Verilog...", self.run_iverilog_dialog)
		self._add_menu_action(sim_menu, "Lint with Verilator...", self.run_verilator_lint_dialog)
		self._add_menu_action(sim_menu, "Coverage Report (Verilator)", self.run_verilator_coverage)
		self._add_menu_action(sim_menu, "Lint with Verible...", self.run_verible_lint_dialog)
		self._add_menu_action(sim_menu, "Format with Verible...", self.run_verible_format_dialog)
		
		# Synthesis submenu
		synth_menu = self.tools_menu.addMenu("Synthesis")
		self._add_menu_action(synth_menu, "Synthesize with Yosys...", self.run_yosys_dialog)
		self._add_menu_action(synth_menu, "OpenLane Flow...", self.run_openlane_dialog)
		self._add_menu_action(synth_menu, "OpenROAD...", self.run_openroad_dialog)
		
		# Layout & Physical Verification submenu
		layout_menu = self.tools_menu.addMenu("Layout && Physical")
		self._add_menu_action(layout_menu, "Open Magic...", self.run_magic_dialog)
		self._add_menu_action(layout_menu, "KLayout Viewer...", self.run_klayout_dialog)
		self._add_menu_action(layout_menu, "KLayout DRC...", self.run_klayout_drc_dialog)
		self._add_menu_action(layout_menu, "Netgen LVS...", self.run_netgen_dialog)
		
		# Timing & SPICE submenu
		timing_menu = self.tools_menu.addMenu("Timing && Analog")
		self._add_menu_action(timing_menu, "Static Timing (OpenSTA)...", self.run_opensta_dialog)
		self._add_menu_action(timing_menu, "NgSpice Simulation...", self.run_ngspice_dialog)

		main_splitter = QSplitter(Qt.Orientation.Horizontal)
		self.file_tree = FileTreeWidget(Path.cwd())
		self.file_tree.fileActivated.connect(self._handle_tree_file_activated)

		right_splitter = QSplitter(Qt.Orientation.Vertical)
		self.editor_tabs = EditorTabs()
		self.editor_tabs.set_global_font(self._editor_font)
		self.editor_tabs.currentFileChanged.connect(self._handle_current_file_changed)
		self.console_panel = ConsoleWidget()
		self.diagnostics_panel = DiagnosticsWidget()
		self.diagnostics_panel.diagnosticActivated.connect(self._handle_diagnostic_selected)
		self.coverage_panel = CoverageWidget()
		self.history_panel = RunHistoryWidget()
		self.history_panel.rerunRequested.connect(self._handle_history_rerun)
		self.output_tabs = QTabWidget()
		self.output_tabs.setDocumentMode(True)
		self.output_tabs.setTabPosition(QTabWidget.TabPosition.South)
		self.output_tabs.addTab(self.console_panel, "Console")
		self.output_tabs.addTab(self.diagnostics_panel, "Diagnostics")
		self.output_tabs.addTab(self.coverage_panel, "Coverage")
		self.output_tabs.addTab(self.history_panel, "History")

		right_splitter.addWidget(self.editor_tabs)
		right_splitter.addWidget(self.output_tabs)
		right_splitter.setSizes([500, 200])

		main_splitter.addWidget(self.file_tree)
		main_splitter.addWidget(right_splitter)
		main_splitter.setSizes([250, 850])

		central_widget = QWidget()
		layout = QVBoxLayout()
		layout.addWidget(main_splitter)
		central_widget.setLayout(layout)
		self.setCentralWidget(central_widget)
		self._version_label = QLabel(f"Version {APP_VERSION}")
		self.statusBar().addPermanentWidget(self._version_label)
		self.statusBar().showMessage("Ready")
		self._update_window_title()
		self._init_watermarks()
		self._apply_theme()

	def _build_menus(self, menu_bar):
		file_menu = menu_bar.addMenu("File")
		self._add_menu_action(file_menu, "New File", self.new_file, QKeySequence.StandardKey.New)
		self._add_menu_action(file_menu, "Open…", self.open_file, QKeySequence.StandardKey.Open)
		self._add_menu_action(file_menu, "Save", self.save_file, QKeySequence.StandardKey.Save)
		self._add_menu_action(file_menu, "Save As…", self.save_file_as, QKeySequence.StandardKey.SaveAs)
		file_menu.addSeparator()
		self._add_menu_action(file_menu, "Exit", self.close, QKeySequence.StandardKey.Quit)

		edit_menu = menu_bar.addMenu("Edit")
		self._add_menu_action(edit_menu, "Undo", self._editor_undo, QKeySequence.StandardKey.Undo)
		self._add_menu_action(edit_menu, "Redo", self._editor_redo, QKeySequence.StandardKey.Redo)
		edit_menu.addSeparator()
		self._add_menu_action(edit_menu, "Cut", self._editor_cut, QKeySequence.StandardKey.Cut)
		self._add_menu_action(edit_menu, "Copy", self._editor_copy, QKeySequence.StandardKey.Copy)
		self._add_menu_action(edit_menu, "Paste", self._editor_paste, QKeySequence.StandardKey.Paste)
		edit_menu.addSeparator()
		self._add_menu_action(edit_menu, "Select All", self._editor_select_all, QKeySequence.StandardKey.SelectAll)

		settings_menu = menu_bar.addMenu("Settings")
		self._build_settings_menu(settings_menu)

		self.tools_menu = menu_bar.addMenu("Tools")
		help_menu = menu_bar.addMenu("Help")
		self._add_menu_action(help_menu, "About", self.show_about)

	def _build_settings_menu(self, settings_menu):
		theme_menu = settings_menu.addMenu("Theme Mode")
		self._theme_group = QActionGroup(self)
		self._theme_group.setExclusive(True)
		for theme_name in THEME_PALETTES.keys():
			action = theme_menu.addAction(theme_name.title())
			action.setCheckable(True)
			action.setChecked(theme_name == self._theme)
			action.setData(theme_name)
			action.triggered.connect(
				lambda checked, name=theme_name: self._set_theme(name) if checked else None
			)
			self._theme_group.addAction(action)

		accent_menu = settings_menu.addMenu("Accent Color")
		self._accent_group = QActionGroup(self)
		self._accent_group.setExclusive(True)
		for accent_name in ACCENT_PALETTES.keys():
			action = accent_menu.addAction(accent_name.title())
			action.setCheckable(True)
			action.setChecked(accent_name == self._accent)
			action.triggered.connect(
				lambda checked, name=accent_name: self._set_accent(name) if checked else None
			)
			self._accent_group.addAction(action)

		ui_scale_menu = settings_menu.addMenu("Interface Size")
		self._ui_scale_group = QActionGroup(self)
		self._ui_scale_group.setExclusive(True)
		for scale_key, preset in UI_SCALE_PRESETS.items():
			action = ui_scale_menu.addAction(preset["label"])
			action.setCheckable(True)
			action.setChecked(scale_key == self._ui_scale_mode)
			action.setData(scale_key)
			action.triggered.connect(
				lambda checked, name=scale_key: self._set_ui_scale_mode(name) if checked else None
			)
			self._ui_scale_group.addAction(action)

		auto_menu = settings_menu.addMenu("Auto Theme")
		self._auto_theme_action = auto_menu.addAction("Enable Day/Night Automation")
		self._auto_theme_action.setCheckable(True)
		self._auto_theme_action.setChecked(self._auto_theme_enabled)
		self._auto_theme_action.toggled.connect(self._toggle_auto_theme)

		self._auto_day_group = QActionGroup(self)
		self._auto_day_group.setExclusive(True)
		day_menu = auto_menu.addMenu("Day Theme")
		for theme_name in THEME_PALETTES.keys():
			action = day_menu.addAction(theme_name.title())
			action.setCheckable(True)
			action.setChecked(theme_name == self._auto_theme_day)
			action.setData(theme_name)
			action.triggered.connect(
				lambda checked, name=theme_name: self._set_auto_day_theme(name) if checked else None
			)
			self._auto_day_group.addAction(action)

		self._auto_night_group = QActionGroup(self)
		self._auto_night_group.setExclusive(True)
		night_menu = auto_menu.addMenu("Night Theme")
		for theme_name in THEME_PALETTES.keys():
			action = night_menu.addAction(theme_name.title())
			action.setCheckable(True)
			action.setChecked(theme_name == self._auto_theme_night)
			action.setData(theme_name)
			action.triggered.connect(
				lambda checked, name=theme_name: self._set_auto_night_theme(name) if checked else None
			)
			self._auto_night_group.addAction(action)

		auto_menu.addSeparator()
		self._add_menu_action(auto_menu, "Set Day Start Hour…", self._choose_day_start)
		self._add_menu_action(auto_menu, "Set Night Start Hour…", self._choose_night_start)

		self._update_theme_action_checks()
		self._update_action_group_selection(self._auto_day_group, self._auto_theme_day)
		self._update_action_group_selection(self._auto_night_group, self._auto_theme_night)
		self._update_action_group_selection(self._ui_scale_group, self._ui_scale_mode)

		settings_menu.addSeparator()
		self._add_menu_action(settings_menu, "Change Editor Font…", self._choose_editor_font)
		self._add_menu_action(settings_menu, "Set Window Color…", self._choose_window_color)
		self._add_menu_action(settings_menu, "Reset Window Color", self._reset_window_color)

	def _add_action(self, container, text, handler):
		action = QAction(text, self)
		action.triggered.connect(handler)
		container.addAction(action)
		return action

	def _add_menu_action(self, menu, text, handler, shortcut=None):
		action = menu.addAction(text)
		action.triggered.connect(handler)
		if shortcut:
			action.setShortcut(shortcut)
		return action

	def _make_file_dialog(
		self,
		title,
		file_mode,
		name_filter=None,
		accept_mode=QFileDialog.AcceptMode.AcceptOpen,
		start_dir=None,
		show_dirs_only=False,
	):
		dlg = QFileDialog(self, title, str(start_dir) if start_dir else "")
		dlg.setFileMode(file_mode)
		dlg.setAcceptMode(accept_mode)
		if name_filter:
			dlg.setNameFilter(name_filter)
		if show_dirs_only:
			dlg.setOption(QFileDialog.Option.ShowDirsOnly, True)
		dlg.setViewMode(QFileDialog.ViewMode.Detail)
		dlg.setOption(QFileDialog.Option.DontUseNativeDialog, True)
		# Larger icons for better visibility in the dialog
		icon_size = QSize(40, 40)
		list_view = dlg.findChild(QListView)
		if list_view:
			list_view.setIconSize(icon_size)
			tree_view = dlg.findChild(QTreeView)
			if tree_view:
				tree_view.setIconSize(icon_size)
		return dlg

	def _get_open_files(self, title, name_filter=None):
		dlg = self._make_file_dialog(title, QFileDialog.FileMode.ExistingFiles, name_filter)
		return dlg.selectedFiles() if dlg.exec() else []

	def _get_open_file(self, title, name_filter=None):
		dlg = self._make_file_dialog(title, QFileDialog.FileMode.ExistingFile, name_filter)
		if not dlg.exec():
			return ""
		selected = dlg.selectedFiles()
		return selected[0] if selected else ""

	def _get_save_file(self, title, name_filter=None):
		dlg = self._make_file_dialog(
			title,
			QFileDialog.FileMode.AnyFile,
			name_filter,
			accept_mode=QFileDialog.AcceptMode.AcceptSave,
		)
		if not dlg.exec():
			return ""
		selected = dlg.selectedFiles()
		return selected[0] if selected else ""

	def _get_directory(self, title):
		dlg = self._make_file_dialog(
			title,
			QFileDialog.FileMode.Directory,
			show_dirs_only=True,
		)
		if not dlg.exec():
			return ""
		selected = dlg.selectedFiles()
		return selected[0] if selected else ""

	def compile_design(self):
		sources = self._get_open_files(
			"Select Verilog/SystemVerilog Sources",
			"HDL Files (*.v *.sv *.vh);;All Files (*.*)",
		)
		if not sources:
			return
		output = self._get_save_file(
			"Select Output Executable",
			"Simulation Binary (*.out *.vvp);;All Files (*.*)",
		)
		if not output:
			return
		command = self.iverilog.build_command(sources, output)
		self._execute_command(command, "Compilation")

	def run_simulation(self):
		compiled = self._get_open_file(
			"Select Compiled Simulation Output",
			"Simulation Files (*.out *.vvp);;All Files (*.*)",
		)
		if not compiled:
			return
		command = self.vvp.build_command(compiled)
		self._execute_command(command, "Simulation")

	def run_synthesis(self):
		script = self._get_open_file(
			"Select Yosys Script",
			"Yosys Scripts (*.ys *.tcl);;All Files (*.*)",
		)
		if not script:
			return
		command = self.yosys.build_command(script)
		self._execute_command(command, "Synthesis")

	def run_verilator_lint(self):
		sources = self._get_open_files(
			"Select Sources for Verilator Lint",
			"HDL/C++ Files (*.v *.sv *.vh *.svh *.cpp *.cc *.c *.h *.hpp);;All Files (*.*)",
		)
		if not sources:
			return
		top_module, accepted = QInputDialog.getText(
			self,
			"Top Module (Optional)",
			"Enter top module name (leave blank for auto-detect):",
		)
		if not accepted:
			return
		top_module = top_module.strip() or None
		extra_flags, accepted = QInputDialog.getText(
			self,
			"Extra Verilator Flags",
			"Additional flags (optional):",
		)
		if not accepted:
			return
		flag_list = shlex.split(extra_flags) if extra_flags.strip() else None
		command = self.verilator_lint.build_command(
			sources,
			top_module=top_module,
			extra_args=flag_list,
		)
		self._execute_command(command, "Verilator Lint")

	def run_verilator_coverage(self):
		data_file = self._get_open_file(
			"Select Verilator Coverage Data",
			"Coverage Files (*.dat *.info *.coverage);;All Files (*.*)",
		)
		if not data_file:
			return
		annotate_dir = self._get_directory("Select Annotation Output Directory (optional)")
		info_file = self._get_save_file(
			"Save Coverage Summary (optional)",
			"Coverage Info (*.info *.txt);;All Files (*.*)",
		)
		command = self.verilator_coverage.build_command(
			data_file,
			annotate_dir=annotate_dir or None,
			info_output=info_file or None,
		)
		metadata = {"type": "coverage", "info_file": info_file or None}
		self._execute_command(command, "Verilator Coverage", metadata=metadata)

	def launch_waveform_viewer(self):
		vcd_file = self._get_open_file(
			"Select VCD File",
			"Waveform Files (*.vcd);;All Files (*.*)",
		)
		if not vcd_file:
			return
		self.console_panel.append_text(f"Launching GTKWave: {vcd_file}")
		try:
			self.gtkwave.launch_viewer(vcd_file)
			self.statusBar().showMessage("GTKWave launched", 5000)
		except Exception as exc:  # pragma: no cover - GUI feedback path
			QMessageBox.critical(self, "GTKWave Error", str(exc))

	def clear_console(self):
		self.console_panel.console.clear()

	def _set_theme(self, theme_name):
		if theme_name not in THEME_PALETTES or theme_name == self._theme:
			return
		if self._auto_theme_enabled:
			self._disable_auto_theme()
		self._theme = theme_name
		self._update_theme_action_checks()
		self._apply_theme()

	def _set_accent(self, accent_name):
		if accent_name not in ACCENT_PALETTES or accent_name == self._accent:
			return
		self._accent = accent_name
		self._apply_theme()

	def _set_ui_scale_mode(self, scale_key):
		if scale_key not in UI_SCALE_PRESETS or scale_key == self._ui_scale_mode:
			return
		self._ui_scale_mode = scale_key
		self._update_action_group_selection(self._ui_scale_group, scale_key)
		self._apply_theme()

	def _get_ui_metrics(self):
		preset = UI_SCALE_PRESETS.get(self._ui_scale_mode, UI_SCALE_PRESETS["medium"])
		scale = preset.get("scale", 1.0)

		def px(value):
			return f"{max(1, int(round(value * scale)))}px"

		def fx(value):
			return max(1, int(round(value * scale)))

		return {"preset": preset, "scale": scale, "font": preset.get("font", 11), "px": px, "fx": fx}

	def _apply_global_font(self, point_size):
		app = QApplication.instance()
		try:
			qt_app = app if isinstance(app, QApplication) else None
			if not qt_app:
				return
			font = qt_app.font()
			font.setPointSize(point_size)
			qt_app.setFont(font)
		except Exception:
			pass

	def _update_watermark_scale(self, scale):
		if not self._watermarks:
			return
		for overlay in self._watermarks:
			overlay.set_scale(scale)

	def _choose_editor_font(self):
		dialog = QFontDialog(self)
		dialog.setCurrentFont(self._editor_font)
		dialog.setOption(QFontDialog.FontDialogOption.DontUseNativeDialog, True)
		if dialog.exec() != QDialog.DialogCode.Accepted:
			return
		font = dialog.selectedFont()
		self._editor_font = font
		self.editor_tabs.set_global_font(font)
		self.statusBar().showMessage(f"Editor font set to {font.family()} {font.pointSize()}pt", 5000)

	def _choose_window_color(self):
		palette = THEME_PALETTES.get(self._theme, THEME_PALETTES["light"])
		initial_hex = self._custom_window_color or palette["window"]
		initial_color = QColor(initial_hex)
		color = QColorDialog.getColor(initial_color, self, "Select Window Color")
		if not color.isValid():
			return
		self._custom_window_color = color.name()
		self._apply_theme()
		self.statusBar().showMessage(f"Window color set to {self._custom_window_color}", 5000)

	def _reset_window_color(self):
		if self._custom_window_color is None:
			return
		self._custom_window_color = None
		self._apply_theme()
		self.statusBar().showMessage("Window color reset to theme default", 5000)

	def _init_watermarks(self):
		for overlay in self._watermarks:
			self._remove_watermark(overlay)
		self._watermarks = []
		file_view = getattr(self.file_tree, "tree", None)
		file_target = file_view.viewport() if file_view else self.file_tree
		editor_target = self.editor_tabs
		output_target = self.output_tabs
		console_widget = getattr(self.console_panel, "console", None)
		console_target = console_widget.viewport() if console_widget else self.console_panel
		targets = [
			(file_target, "Files"),
			(editor_target, "Editor"),
			(output_target, "Output"),
			(console_target, "Console"),
		]
		for widget, label in targets:
			if widget is None:
				continue
			self._watermarks.append(WatermarkOverlay(widget, label))
		self._sync_watermarks()

	def _remove_watermark(self, overlay):
		if not overlay:
			return
		label = getattr(overlay, "_label", None)
		if label:
			label.deleteLater()

	def _sync_watermarks(self, color_hex=None):
		if not self._watermarks:
			return
		if color_hex is None:
			palette = THEME_PALETTES.get(self._theme, THEME_PALETTES["light"])
			color_hex = palette.get("subtext", palette["text"])
		for overlay in self._watermarks:
			overlay.set_color(color_hex)

	def _apply_theme(self):
		palette = THEME_PALETTES.get(self._theme, THEME_PALETTES["light"])
		accent = ACCENT_PALETTES.get(self._accent)
		window_color = self._custom_window_color or palette["window"]
		panel = palette["panel"]
		text = palette["text"]
		subtext = palette.get("subtext", text)
		border = palette["border"]
		status_bg = palette["status"]
		base_accent = palette.get("accent", border)
		if not accent:
			accent = {
				"accent": base_accent,
				"hover": _shade(base_accent, -15),
				"selection": _shade(base_accent, 35),
			}
		selection = accent["selection"]
		accent_color = accent["accent"]
		hover = accent["hover"]
		toolbar_gradient = (
			f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {_shade(accent_color, 25)}, "
			f"stop:1 {accent_color})"
		)
		tab_hover = _shade(accent_color, 35)
		tab_selected = _shade(accent_color, 10)
		metrics = self._get_ui_metrics()
		px = metrics["px"]
		scale = metrics["scale"]
		font_size = metrics["font"]
		muted_panel = _shade(panel, -8)
		console_bg = _shade(panel, -4)
		console_border = _shade(border, -15)
		button_text = "#f8fafc"
		semantic_error = palette.get("error", "#e11d48")
		semantic_warning = palette.get("warning", "#f59e0b")
		semantic_success = palette.get("success", "#10b981")
		letter_space = f"{max(1, int(round(1 * scale)))}px"
		toolbar_letter = f"{max(0.5, round(0.5 * scale, 2))}px"
		scrollbar_radius = px(5)
		style = f"""
		QWidget {{
			font-size: {font_size}px;
		}}
		QMainWindow {{
			background-color: {window_color};
			color: {text};
		}}
		QMenuBar {{
			background-color: {palette['menu']};
			border: none;
			color: {text};
		}}
		QMenuBar::item {{
			padding: {px(6)} {px(12)};
			background: transparent;
		}}
		QMenuBar::item:selected {{
			background: {hover};
			color: {text};
		}}
		QMenu {{
			background-color: {palette['menu']};
			color: {text};
			border: 1px solid {border};
			border-radius: 6px;
			padding: {px(6)};
		}}
		QMenu::separator {{
			height: 1px;
			background: {border};
			margin: {px(4)} {px(12)};
		}}
		QMenu::item:selected {{
			background: {hover};
			color: {text};
		}}
		QToolBar {{
			background: {toolbar_gradient};
			border: none;
			padding: {px(4)} {px(8)};
			border-bottom: 1px solid {_shade(accent_color, -25)};
		}}
		QToolButton {{
			color: {subtext};
			background: transparent;
			padding: {px(4)} {px(10)};
			border-radius: {px(4)};
		}}
		QToolButton:hover {{
			background: {_shade(panel, 12)};
			color: {text};
		}}
		QToolBar QToolButton {{
			color: {button_text};
			font-weight: 600;
			letter-spacing: {toolbar_letter};
		}}
		QToolBar QToolButton:hover {{
			background: rgba(255, 255, 255, 0.18);
		}}
		QToolButton#consoleClearButton {{
			border: 1px solid {border};
			background: {panel};
			color: {subtext};
			padding: {px(4)} {px(12)};
			border-radius: {px(4)};
		}}
		QToolButton#consoleClearButton:hover {{
			border-color: {accent_color};
			color: {text};
			background: {_shade(panel, 6)};
		}}
		QSplitter::handle {{
			background: {palette['splitter']};
			margin: 0 {px(4)};
			border-radius: {px(2)};
		}}
		QSplitter::handle:horizontal {{
			width: {px(6)};
		}}
		QSplitter::handle:vertical {{
			height: {px(6)};
		}}
		QTabWidget::pane {{
			border: 1px solid {border};
			border-radius: {px(8)};
			background: {muted_panel};
			padding: {px(6)};
		}}
		QTabBar::tab {{
			background: transparent;
			color: {text};
			padding: {px(6)} {px(14)};
			margin: {px(2)};
			border-radius: {px(6)};
		}}
		QTabBar::tab:hover {{
			background: {tab_hover};
		}}
		QTabBar::tab:selected {{
			background: {tab_selected};
			color: {text};
		}}
		QTreeView, QTreeWidget {{
			background: {panel};
			color: {text};
			selection-background-color: {selection};
			selection-color: {text};
			border: 1px solid {border};
			alternate-background-color: {_shade(panel, -4)};
		}}
		QTreeView::item:hover, QTreeWidget::item:hover {{
			background: {hover};
		}}
		QPlainTextEdit, QTextEdit, QsciScintilla {{
			background: {panel};
			color: {text};
			selection-background-color: {selection};
			border: 1px solid {border};
			border-radius: {px(6)};
			padding: {px(6)};
		}}
		QTextEdit#consoleText {{
			background: {console_bg};
			border: 1px solid {console_border};
			border-radius: {px(8)};
			padding: {px(8)};
			color: {subtext};
		}}
		QPlainTextEdit#coveragePane {{
			background: {console_bg};
			color: {subtext};
		}}
		QLineEdit, QSpinBox, QComboBox, QDateEdit {{
			background: {panel};
			color: {text};
			border: 1px solid {border};
			border-radius: {px(5)};
			padding: {px(4)} {px(8)};
		}}
		QPushButton {{
			background: {accent_color};
			color: {button_text};
			border: none;
			padding: {px(6)} {px(14)};
			border-radius: {px(6)};
			font-weight: 600;
		}}
		QPushButton:hover {{
			background: {hover};
		}}
		QScrollBar:vertical {{
			background: {muted_panel};
			width: {px(10)};
			margin: {px(4)};
			border-radius: {scrollbar_radius};
		}}
		QScrollBar::handle:vertical {{
			background: {accent_color};
			border-radius: {scrollbar_radius};
		}}
		QScrollBar:horizontal {{
			background: {muted_panel};
			height: {px(10)};
			margin: {px(4)};
			border-radius: {scrollbar_radius};
		}}
		QScrollBar::handle:horizontal {{
			background: {accent_color};
			border-radius: {scrollbar_radius};
		}}
		QLabel#fileTreePathLabel {{
			color: {subtext};
			font-weight: 600;
			text-transform: uppercase;
			letter-spacing: {letter_space};
		}}
		QStatusBar {{
			background: {status_bg};
			color: {text};
			border-top: 1px solid {border};
		}}
		QStatusBar QLabel {{
			color: {subtext};
		}}
		*[state="error"], QLabel[role="error"] {{
			color: {semantic_error};
		}}
		*[state="warning"], QLabel[role="warning"] {{
			color: {semantic_warning};
		}}
		*[state="success"], QLabel[role="success"] {{
			color: {semantic_success};
		}}
		"""
		self.setStyleSheet(style)
		self._apply_global_font(font_size)
		self._update_watermark_scale(scale)
		self._sync_watermarks(subtext)
		console_widget = getattr(self.console_panel, "console", None)
		if console_widget:
			console_font = console_widget.font()
			console_font.setPointSize(max(9, int(round(font_size + 1))))
			console_widget.setFont(console_font)

	def _initialize_auto_theme(self):
		self._ensure_theme_timer()
		if self._auto_theme_enabled and self._auto_theme_action:
			self._auto_theme_action.blockSignals(True)
			self._auto_theme_action.setChecked(True)
			self._auto_theme_action.blockSignals(False)
		if self._auto_theme_enabled:
			if self._theme_timer is not None:
				self._theme_timer.start()
			self._apply_auto_theme(force=True)

	def _ensure_theme_timer(self):
		if self._theme_timer is None:
			self._theme_timer = QTimer(self)
			self._theme_timer.setInterval(5 * 60 * 1000)
			self._theme_timer.timeout.connect(self._apply_auto_theme)

	def _set_auto_theme_enabled(self, enabled):
		self._ensure_theme_timer()
		self._auto_theme_enabled = enabled
		if enabled:
			if self._theme_timer is not None:
				self._theme_timer.start()
			self._apply_auto_theme(force=True)
		elif self._theme_timer:
			self._theme_timer.stop()

	def _disable_auto_theme(self):
		if self._auto_theme_action:
			self._auto_theme_action.blockSignals(True)
			self._auto_theme_action.setChecked(False)
			self._auto_theme_action.blockSignals(False)
		self._set_auto_theme_enabled(False)

	def _toggle_auto_theme(self, enabled):
		self._set_auto_theme_enabled(bool(enabled))

	def _apply_auto_theme(self, force=False):
		if not self._auto_theme_enabled:
			return
		target_theme = self._auto_theme_day if self._is_daytime() else self._auto_theme_night
		if target_theme not in THEME_PALETTES:
			target_theme = "light"
		if force or target_theme != self._theme:
			self._theme = target_theme
			self._update_theme_action_checks()
			self._apply_theme()

	def _is_daytime(self):
		hour = datetime.now().hour
		day_start = self._auto_theme_day_start % 24
		night_start = self._auto_theme_night_start % 24
		if day_start == night_start:
			return True
		if day_start < night_start:
			return day_start <= hour < night_start
		return hour >= day_start or hour < night_start

	def _update_theme_action_checks(self):
		if not getattr(self, "_theme_group", None):
			return
		for action in self._theme_group.actions():
			theme_name = action.data()
			action.setChecked(theme_name == self._theme)

	def _update_action_group_selection(self, group, target):
		if not group:
			return
		for action in group.actions():
			action.setChecked(action.data() == target)

	def _set_auto_day_theme(self, theme_name):
		if theme_name not in THEME_PALETTES:
			return
		self._auto_theme_day = theme_name
		self._update_action_group_selection(self._auto_day_group, theme_name)
		if self._auto_theme_enabled and self._is_daytime():
			self._apply_auto_theme(force=True)

	def _set_auto_night_theme(self, theme_name):
		if theme_name not in THEME_PALETTES:
			return
		self._auto_theme_night = theme_name
		self._update_action_group_selection(self._auto_night_group, theme_name)
		if self._auto_theme_enabled and not self._is_daytime():
			self._apply_auto_theme(force=True)

	def _choose_day_start(self):
		hour, accepted = QInputDialog.getInt(
			self,
			"Daytime Start",
			"Enter hour (0-23) when the day theme should activate:",
			self._auto_theme_day_start,
			0,
			23,
		)
		if not accepted:
			return
		self._auto_theme_day_start = hour
		if self._auto_theme_enabled:
			self._apply_auto_theme(force=True)

	def _choose_night_start(self):
		hour, accepted = QInputDialog.getInt(
			self,
			"Night Start",
			"Enter hour (0-23) when the night theme should activate:",
			self._auto_theme_night_start,
			0,
			23,
		)
		if not accepted:
			return
		self._auto_theme_night_start = hour
		if self._auto_theme_enabled:
			self._apply_auto_theme(force=True)

	def new_file(self):
		self.editor_tabs.new_document()
		self._update_window_title()
		self.statusBar().showMessage("New file", 4000)

	def open_file(self, path=None):
		if not path:
			path = self._get_open_file(
				"Open Source File",
				"HDL Files (*.v *.sv *.vh);;All Files (*.*)",
			)
		if not path:
			return
		self._open_file_path(path)

	def save_file(self):
		editor = self.editor_tabs.current_editor()
		if not editor:
			return
		if not editor.file_path:
			self.save_file_as()
			return
		self._write_editor_contents(editor, editor.file_path)

	def save_file_as(self):
		editor = self.editor_tabs.current_editor()
		if not editor:
			return
		path = self._get_save_file(
			"Save Source File",
			"HDL Files (*.v *.sv *.vh);;All Files (*.*)",
		)
		if not path:
			return
		self._write_editor_contents(editor, path)

	def _write_editor_contents(self, editor, path):
		try:
			with open(path, "w", encoding="utf-8") as file_obj:
				file_obj.write(editor.get_text())
		except OSError as exc:
			QMessageBox.critical(self, "Save Failed", str(exc))
			return
		self.editor_tabs.set_editor_path(editor, path)
		editor.mark_clean()
		self.console_panel.append_text(f"Saved file: {path}")
		self._update_window_title()
		self.statusBar().showMessage(f"Saved {Path(path).name}", 4000)

	def _update_window_title(self):
		current_path = self.editor_tabs.current_file_path()
		if current_path:
			self.setWindowTitle(f"OpenHDL-IDE v{APP_VERSION} - {Path(current_path).name}")
		else:
			self.setWindowTitle(f"OpenHDL-IDE v{APP_VERSION}")

	def _editor_undo(self):
		editor = self.editor_tabs.current_editor()
		if editor:
			try:
				editor.undo()
			except AttributeError:
				w = editor.widget()
				fn = getattr(w, "undo", None)
				if callable(fn):
					fn()

	def _editor_redo(self):
		editor = self.editor_tabs.current_editor()
		if editor:
			try:
				editor.redo()
			except AttributeError:
				w = editor.widget()
				fn = getattr(w, "redo", None)
				if callable(fn):
					fn()

	def _editor_cut(self):
		editor = self.editor_tabs.current_editor()
		if editor:
			try:
				editor.cut()
			except AttributeError:
				w = editor.widget()
				fn = getattr(w, "cut", None)
				if callable(fn):
					fn()

	def _editor_copy(self):
		editor = self.editor_tabs.current_editor()
		if editor:
			try:
				editor.copy()
			except AttributeError:
				w = editor.widget()
				fn = getattr(w, "copy", None)
				if callable(fn):
					fn()

	def _editor_paste(self):
		editor = self.editor_tabs.current_editor()
		if editor:
			try:
				editor.paste()
			except AttributeError:
				w = editor.widget()
				fn = getattr(w, "paste", None)
				if callable(fn):
					fn()

	def _editor_select_all(self):
		editor = self.editor_tabs.current_editor()
		if editor:
			try:
				editor.select_all()
			except AttributeError:
				w = editor.widget()
				fn = getattr(w, "selectAll", None)
				if callable(fn):
					fn()

	def show_about(self):
		QMessageBox.information(
			self,
			"About OpenHDL-IDE",
			(
				f"OpenHDL-IDE v{APP_VERSION}\n\n"
				"Integrated environment for iverilog, Yosys, and GTKWave."
			),
		)

	def _open_file_path(self, path):
		try:
			with open(path, "r", encoding="utf-8") as file_obj:
				contents = file_obj.read()
		except OSError as exc:
			QMessageBox.critical(self, "Open Failed", str(exc))
			return
		self.editor_tabs.open_document(path, contents)
		self.console_panel.append_text(f"Opened file: {path}")
		self._update_window_title()
		self.statusBar().showMessage(f"Loaded {Path(path).name}", 4000)

	def _handle_tree_file_activated(self, path):
		self._open_file_path(path)

	def _handle_current_file_changed(self, _path):
		self._update_window_title()

	def _handle_diagnostic_selected(self, diagnostic):
		if not diagnostic:
			return
		file_path = diagnostic.get("file")
		line = diagnostic.get("line")
		if not file_path:
			return
		resolved = Path(file_path)
		if not resolved.is_absolute():
			resolved = Path.cwd() / resolved
		if not resolved.exists():
			QMessageBox.warning(self, "File Not Found", f"Cannot open {resolved}")
			return
		self._open_file_path(str(resolved))
		if line:
			try:
				line_number = int(line)
			except ValueError:
				return
			editor = self.editor_tabs.current_editor()
			if editor:
				editor.goto_line(line_number)

	def _handle_history_rerun(self, command, description, metadata):
		if not command:
			return
		self._execute_command(command, f"{description} (rerun)", metadata=metadata)

	def open_schematic_file(self):
		schematic_file = self._get_open_file(
			"Select Schematic File",
			"Schematics (*.svg *.png *.pdf *.dot);;All Files (*.*)",
		)
		if not schematic_file:
			return
		self.console_panel.append_text(f"Opening schematic: {schematic_file}")
		opened = QDesktopServices.openUrl(QUrl.fromLocalFile(schematic_file))
		if not opened:
			self.console_panel.append_text("Trying xdg-open fallback...")
			try:
				subprocess.Popen(["xdg-open", schematic_file])
				self.statusBar().showMessage("Schematic opened via xdg-open", 5000)
			except Exception:
				self.console_panel.append_text("Unable to auto-open schematic; open the file manually.")
				self.statusBar().showMessage("Unable to auto-open schematic", 5000)
		else:
			self.statusBar().showMessage("Schematic opened", 5000)

	def _execute_command(self, command, description, metadata=None):
		self.console_panel.append_text(f"$ {command}")
		thread = QThread()
		runner = CommandRunner(command)
		runner.moveToThread(thread)
		context = {
			"thread": thread,
			"runner": runner,
			"buffer": [],
			"description": description,
			"command": command,
			"metadata": metadata or {},
		}
		self._run_contexts[runner] = context
		context["history_item"] = self.history_panel.add_entry(description, command, metadata)

		thread.started.connect(runner.run)
		runner.finished.connect(self._handle_runner_finished, Qt.ConnectionType.QueuedConnection)
		runner.output.connect(self._handle_runner_output, Qt.ConnectionType.QueuedConnection)
		thread.start()
		self._active_runs.append(context)
		self.statusBar().showMessage(f"{description} running…")

	def _handle_runner_output(self, text):
		runner = self.sender()
		context = self._run_contexts.get(runner)
		if not context:
			return
		context["buffer"].append(text)
		self.console_panel.append_text(text)

	def _handle_runner_finished(self, exit_code):
		runner = self.sender()
		context = self._run_contexts.pop(runner, None)
		if not context:
			return
		thread = context["thread"]
		description = context["description"]
		metadata = context.get("metadata", {})
		command = context.get("command", "")
		history_item = context.get("history_item")
		buffer = context["buffer"]

		thread.quit()
		thread.wait()
		runner.deleteLater()
		thread.deleteLater()
		self._active_runs = [run for run in self._active_runs if run["runner"] is not runner]

		joined_output = "\n".join(buffer)
		errors = ErrorParser.parse(joined_output)
		self.diagnostics_panel.update_entries(errors)
		if errors:
			self.output_tabs.setCurrentWidget(self.diagnostics_panel)
			first = errors[0]
			self.console_panel.append_text(
				f"Diagnostics: {first['file']}:{first['line']} {first['type']} {first['msg'].strip()}"
			)

		self.history_panel.mark_completed(history_item, exit_code)

		if exit_code == 0:
			self.console_panel.append_text(f"✔ {description} completed successfully")
			self.statusBar().showMessage(f"{description} completed", 5000)
			if metadata.get("type") == "coverage":
				info_path = metadata.get("info_file")
				if info_path:
					try:
						with open(info_path, "r", encoding="utf-8") as info_stream:
							contents = info_stream.read()
					except OSError as exc:
						self.coverage_panel.show_message(str(exc))
					else:
						self.coverage_panel.show_summary(info_path, contents)
						self.output_tabs.setCurrentWidget(self.coverage_panel)
				else:
					self.coverage_panel.show_message(
						"No coverage info file provided. Re-run and choose 'Save Coverage Summary'."
					)
		else:
			self.statusBar().showMessage(f"{description} failed (code {exit_code})", 8000)
			QMessageBox.warning(
				self,
				"Command Failed",
				f"{description} exited with code {exit_code}. Check console for details.",
			)
	
	def run_iverilog_dialog(self):
		"""Open Icarus Verilog configuration dialog."""
		dialog = IverilogDialog(self)
		if dialog.exec() == QDialog.DialogCode.Accepted:
			command = dialog.get_command()
			self._execute_command(command, "Icarus Verilog Compilation")
	
	def run_yosys_dialog(self):
		"""Open Yosys configuration dialog."""
		dialog = YosysDialog(self)
		if dialog.exec() == QDialog.DialogCode.Accepted:
			command = dialog.get_command()
			self._execute_command(command, "Yosys Synthesis")
	
	def run_verilator_lint_dialog(self):
		"""Open Verilator lint configuration dialog."""
		dialog = VerilatorDialog("lint", self)
		if dialog.exec() == QDialog.DialogCode.Accepted:
			command = dialog.get_command()
			self._execute_command(command, "Verilator Lint")
	
	def run_verible_lint_dialog(self):
		"""Open Verible lint configuration dialog."""
		dialog = VeribleDialog("lint", self)
		if dialog.exec() == QDialog.DialogCode.Accepted:
			command = dialog.get_command()
			self._execute_command(command, "Veribe Lint")
	
	def run_verible_format_dialog(self):
		"""Open Verible format configuration dialog."""
		dialog = VeribleDialog("format", self)
		if dialog.exec() == QDialog.DialogCode.Accepted:
			command = dialog.get_command()
			self._execute_command(command, "Verible Format")
	
	def run_magic_dialog(self):
		"""Open Magic layout tool configuration dialog."""
		dialog = MagicDialog(self)
		if dialog.exec() == QDialog.DialogCode.Accepted:
			command = dialog.get_command()
			self._execute_command(command, "Magic Layout Tool")
	
	def run_klayout_dialog(self):
		"""Open KLayout viewer configuration dialog."""
		dialog = KLayoutDialog("view", self)
		if dialog.exec() == QDialog.DialogCode.Accepted:
			command = dialog.get_command()
			self._execute_command(command, "KLayout Viewer")
	
	def run_klayout_drc_dialog(self):
		"""Open KLayout DRC configuration dialog."""
		dialog = KLayoutDialog("drc", self)
		if dialog.exec() == QDialog.DialogCode.Accepted:
			command = dialog.get_command()
			self._execute_command(command, "KLayout DRC")
	
	def run_netgen_dialog(self):
		"""Open Netgen LVS tool (placeholder - need dialog)."""
		circuit1 = self._get_open_file(
			"Select First Circuit Netlist",
			"Netlist Files (*.spice *.sp *.cir);;All Files (*)",
		)
		if not circuit1:
			return
		
		circuit2 = self._get_open_file(
			"Select Second Circuit Netlist",
			"Netlist Files (*.spice *.sp *.cir);;All Files (*)",
		)
		if not circuit2:
			return
		
		setup = self._get_open_file(
			"Select Netgen Setup File",
			"Setup Files (*.tcl *.setup);;All Files (*)",
		)
		if not setup:
			return
		
		output = self._get_save_file(
			"Save Comparison Report",
			"Report Files (*.out *.txt);;All Files (*)",
		)
		
		command = self.netgen.build_command(
			circuit1, circuit2, setup, 
			output_file=output or None
		)
		self._execute_command(command, "Netgen LVS")
	
	def run_opensta_dialog(self):
		"""Open OpenSTA timing analysis (placeholder)."""
		script = self._get_open_file(
			"Select OpenSTA Script",
			"TCL Scripts (*.tcl);;All Files (*)",
		)
		if not script:
			return
		
		command = self.opensta.build_command(script)
		self._execute_command(command, "OpenSTA Timing Analysis")
	
	def run_ngspice_dialog(self):
		"""Open NgSpice simulation (placeholder)."""
		netlist = self._get_open_file(
			"Select SPICE Netlist",
			"SPICE Files (*.sp *.cir *.spice);;All Files (*)",
		)
		if not netlist:
			return
		
		output = self._get_save_file(
			"Save Output Log",
			"Log Files (*.log *.txt);;All Files (*)",
		)
		
		command = self.ngspice.build_command(
			netlist, 
			batch=True, 
			output_file=output or None
		)
		self._execute_command(command, "NgSpice Simulation")
	
	def run_openlane_dialog(self):
		"""Open OpenLane flow (placeholder)."""
		design_name, ok = QInputDialog.getText(
			self, "OpenLane Flow", "Enter design name:"
		)
		if not ok or not design_name.strip():
			return
		
		design_dir = self._get_directory("Select Design Directory")
		if not design_dir:
			return
		
		command = self.openlane.build_command(
			design_dir, design_name.strip()
		)
		self._execute_command(command, "OpenLane Flow")
	
	def run_openroad_dialog(self):
		"""Open OpenROAD (placeholder)."""
		script = self._get_open_file(
			"Select OpenROAD Script",
			"TCL Scripts (*.tcl);;All Files (*)",
		)
		if not script:
			return
		
		log = self._get_save_file(
			"Save Log File (optional)",
			"Log Files (*.log);;All Files (*)",
		)
		
		command = self.openroad.build_command(
			script, 
			log_file=log or None
		)
		self._execute_command(command, "OpenROAD")

	def closeEvent(self, event):
		self._save_user_settings()
		for run in self._active_runs:
			thread = run["thread"]
			thread.requestInterruption()
			thread.quit()
			thread.wait(2000)
		self._active_runs.clear()
		super().closeEvent(event)

	def _load_user_settings(self):
		if not self._settings_path.exists():
			return
		try:
			with open(self._settings_path, "r", encoding="utf-8") as settings_file:
				data = json.load(settings_file)
		except (OSError, json.JSONDecodeError):
			return
		theme = data.get("theme")
		if theme in THEME_PALETTES:
			self._theme = theme
		accent = data.get("accent")
		if accent in ACCENT_PALETTES:
			self._accent = accent
		scale_mode = data.get("ui_scale")
		if scale_mode in UI_SCALE_PRESETS:
			self._ui_scale_mode = scale_mode
		auto_data = data.get("auto_theme")
		if isinstance(auto_data, dict):
			enabled = auto_data.get("enabled")
			if isinstance(enabled, bool):
				self._auto_theme_enabled = enabled
			day_theme = auto_data.get("day_theme")
			if day_theme in THEME_PALETTES:
				self._auto_theme_day = day_theme
			night_theme = auto_data.get("night_theme")
			if night_theme in THEME_PALETTES:
				self._auto_theme_night = night_theme
			day_start = auto_data.get("day_start")
			if isinstance(day_start, int):
				self._auto_theme_day_start = max(0, min(23, day_start))
			night_start = auto_data.get("night_start")
			if isinstance(night_start, int):
				self._auto_theme_night_start = max(0, min(23, night_start))
		color = data.get("custom_window_color")
		if color:
			self._custom_window_color = color
		font_data = data.get("editor_font")
		if font_data:
			family = font_data.get("family") or self._editor_font.family()
			size = font_data.get("size") or self._editor_font.pointSize()
			self._editor_font = QFont(family, int(size))

	def _save_user_settings(self):
		data = {
			"theme": self._theme,
			"accent": self._accent,
			"custom_window_color": self._custom_window_color,
			"ui_scale": self._ui_scale_mode,
			"auto_theme": {
				"enabled": self._auto_theme_enabled,
				"day_theme": self._auto_theme_day,
				"night_theme": self._auto_theme_night,
				"day_start": self._auto_theme_day_start,
				"night_start": self._auto_theme_night_start,
			},
			"editor_font": {
				"family": self._editor_font.family(),
				"size": self._editor_font.pointSize(),
			},
		}
		try:
			with open(self._settings_path, "w", encoding="utf-8") as settings_file:
				json.dump(data, settings_file, indent=2)
		except OSError:
			pass
