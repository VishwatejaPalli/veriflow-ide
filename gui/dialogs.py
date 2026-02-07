"""Customized dialogs for EDA tool configuration."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
	QCheckBox,
	QComboBox,
	QDialog,
	QDialogButtonBox,
	QFileDialog,
	QFormLayout,
	QGroupBox,
	QHBoxLayout,
	QLabel,
	QLineEdit,
	QListWidget,
	QPushButton,
	QSpinBox,
	QTextEdit,
	QVBoxLayout,
	QWidget,
)


class FileListWidget(QWidget):
	"""Widget for managing a list of files."""
	
	def __init__(self, title="Files", file_filter="All Files (*)", parent=None):
		super().__init__(parent)
		self.file_filter = file_filter
		
		layout = QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		
		# File list
		self.list_widget = QListWidget()
		layout.addWidget(QLabel(title))
		layout.addWidget(self.list_widget)
		
		# Buttons
		btn_layout = QHBoxLayout()
		self.add_btn = QPushButton("Add Files...")
		self.add_btn.clicked.connect(self._add_files)
		self.remove_btn = QPushButton("Remove")
		self.remove_btn.clicked.connect(self._remove_selected)
		self.clear_btn = QPushButton("Clear All")
		self.clear_btn.clicked.connect(self.list_widget.clear)
		
		btn_layout.addWidget(self.add_btn)
		btn_layout.addWidget(self.remove_btn)
		btn_layout.addWidget(self.clear_btn)
		btn_layout.addStretch()
		
		layout.addLayout(btn_layout)
		self.setLayout(layout)
	
	def _add_files(self):
		files, _ = QFileDialog.getOpenFileNames(
			self, "Select Files", "", self.file_filter
		)
		for file in files:
			self.list_widget.addItem(file)
	
	def _remove_selected(self):
		for item in self.list_widget.selectedItems():
			self.list_widget.takeItem(self.list_widget.row(item))
	
	def get_files(self):
		"""Get list of all files."""
		return [self.list_widget.item(i).text() 
		        for i in range(self.list_widget.count())]
	
	def set_files(self, files):
		"""Set the file list."""
		self.list_widget.clear()
		for file in files:
			self.list_widget.addItem(file)


class IverilogDialog(QDialog):
	"""Dialog for configuring Icarus Verilog compilation."""
	
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Icarus Verilog Compiler")
		self.setMinimumWidth(600)
		self.setMinimumHeight(500)
		
		layout = QVBoxLayout()
		
		# Source files
		self.source_widget = FileListWidget(
			"Source Files", 
			"Verilog Files (*.v *.sv *.vh *.svh);;All Files (*)"
		)
		layout.addWidget(self.source_widget)
		
		# Options
		options_group = QGroupBox("Compilation Options")
		options_layout = QFormLayout()
		
		# Output file
		output_layout = QHBoxLayout()
		self.output_edit = QLineEdit("a.out")
		output_btn = QPushButton("Browse...")
		output_btn.clicked.connect(self._browse_output)
		output_layout.addWidget(self.output_edit)
		output_layout.addWidget(output_btn)
		options_layout.addRow("Output File:", output_layout)
		
		# Language standard
		self.std_combo = QComboBox()
		self.std_combo.addItems(["Default", "Verilog-1995", "Verilog-2001", 
		                         "Verilog-2005", "SystemVerilog-2005", 
		                         "SystemVerilog-2009", "SystemVerilog-2012"])
		options_layout.addRow("Language Standard:", self.std_combo)
		
		# Include directories
		self.include_edit = QLineEdit()
		self.include_edit.setPlaceholderText("Comma-separated paths")
		options_layout.addRow("Include Directories:", self.include_edit)
		
		# Defines
		self.define_edit = QLineEdit()
		self.define_edit.setPlaceholderText("e.g., DEBUG, WIDTH=32")
		options_layout.addRow("Defines:", self.define_edit)
		
		# Generate debug info
		self.debug_check = QCheckBox("Generate debug information")
		self.debug_check.setChecked(True)
		options_layout.addRow("", self.debug_check)
		
		# Extra arguments
		self.extra_edit = QLineEdit()
		self.extra_edit.setPlaceholderText("Additional command-line arguments")
		options_layout.addRow("Extra Arguments:", self.extra_edit)
		
		options_group.setLayout(options_layout)
		layout.addWidget(options_group)
		
		# Command preview
		preview_group = QGroupBox("Command Preview")
		preview_layout = QVBoxLayout()
		self.command_preview = QTextEdit()
		self.command_preview.setReadOnly(True)
		self.command_preview.setMaximumHeight(80)
		preview_layout.addWidget(self.command_preview)
		preview_group.setLayout(preview_layout)
		layout.addWidget(preview_group)
		
		# Connect signals to update preview
		self.output_edit.textChanged.connect(self._update_preview)
		self.std_combo.currentTextChanged.connect(self._update_preview)
		self.include_edit.textChanged.connect(self._update_preview)
		self.define_edit.textChanged.connect(self._update_preview)
		self.debug_check.stateChanged.connect(self._update_preview)
		self.extra_edit.textChanged.connect(self._update_preview)
		
		# Buttons
		button_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		)
		button_box.accepted.connect(self.accept)
		button_box.rejected.connect(self.reject)
		layout.addWidget(button_box)
		
		self.setLayout(layout)
		self._update_preview()
	
	def _browse_output(self):
		file, _ = QFileDialog.getSaveFileName(
			self, "Output File", self.output_edit.text(), 
			"VVP Files (*.vvp);;All Files (*)"
		)
		if file:
			self.output_edit.setText(file)
	
	def _update_preview(self):
		"""Update the command preview."""
		from tools.iverilog import IverilogTool
		
		sources = self.source_widget.get_files()
		output = self.output_edit.text()
		
		if not sources:
			self.command_preview.setText("# Add source files to see command")
			return
		
		# Build command with options
		cmd_parts = ["iverilog"]
		
		# Standard
		std_map = {
			"Verilog-1995": "-g1995",
			"Verilog-2001": "-g2001",
			"Verilog-2005": "-g2005",
			"SystemVerilog-2005": "-g2005-sv",
			"SystemVerilog-2009": "-g2009",
			"SystemVerilog-2012": "-g2012",
		}
		std = self.std_combo.currentText()
		if std in std_map:
			cmd_parts.append(std_map[std])
		
		# Include directories
		includes = [i.strip() for i in self.include_edit.text().split(",") if i.strip()]
		for inc in includes:
			cmd_parts.append(f"-I{inc}")
		
		# Defines
		defines = [d.strip() for d in self.define_edit.text().split(",") if d.strip()]
		for define in defines:
			cmd_parts.append(f"-D{define}")
		
		# Debug
		if self.debug_check.isChecked():
			cmd_parts.append("-g2009")
		
		# Extra args
		if self.extra_edit.text().strip():
			cmd_parts.append(self.extra_edit.text().strip())
		
		# Output
		cmd_parts.extend(["-o", output])
		
		# Sources
		cmd_parts.extend(sources)
		
		self.command_preview.setText(" ".join(cmd_parts))
	
	def get_command(self):
		"""Get the configured command."""
		return self.command_preview.toPlainText()
	
	def get_config(self):
		"""Get configuration dictionary."""
		return {
			"sources": self.source_widget.get_files(),
			"output": self.output_edit.text(),
			"standard": self.std_combo.currentText(),
			"includes": self.include_edit.text(),
			"defines": self.define_edit.text(),
			"debug": self.debug_check.isChecked(),
			"extra": self.extra_edit.text(),
		}


class YosysDialog(QDialog):
	"""Dialog for configuring Yosys synthesis."""
	
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Yosys Synthesis")
		self.setMinimumWidth(600)
		self.setMinimumHeight(450)
		
		layout = QVBoxLayout()
		
		# Script file
		script_group = QGroupBox("Synthesis Script")
		script_layout = QVBoxLayout()
		
		file_layout = QHBoxLayout()
		self.script_edit = QLineEdit()
		self.script_edit.setPlaceholderText("Path to Yosys script (.ys)")
		script_btn = QPushButton("Browse...")
		script_btn.clicked.connect(self._browse_script)
		file_layout.addWidget(self.script_edit)
		file_layout.addWidget(script_btn)
		script_layout.addLayout(file_layout)
		
		script_group.setLayout(script_layout)
		layout.addWidget(script_group)
		
		# Options
		options_group = QGroupBox("Options")
		options_layout = QFormLayout()
		
		# Quiet mode
		self.quiet_check = QCheckBox("Quiet mode (suppress info messages)")
		options_layout.addRow("", self.quiet_check)
		
		# Verbose
		self.verbose_check = QCheckBox("Verbose output")
		options_layout.addRow("", self.verbose_check)
		
		# Log file
		log_layout = QHBoxLayout()
		self.log_edit = QLineEdit()
		self.log_edit.setPlaceholderText("Optional log file")
		log_btn = QPushButton("Browse...")
		log_btn.clicked.connect(self._browse_log)
		log_layout.addWidget(self.log_edit)
		log_layout.addWidget(log_btn)
		options_layout.addRow("Log File:", log_layout)
		
		# Extra arguments
		self.extra_edit = QLineEdit()
		self.extra_edit.setPlaceholderText("Additional command-line arguments")
		options_layout.addRow("Extra Arguments:", self.extra_edit)
		
		options_group.setLayout(options_layout)
		layout.addWidget(options_group)
		
		# Command preview
		preview_group = QGroupBox("Command Preview")
		preview_layout = QVBoxLayout()
		self.command_preview = QTextEdit()
		self.command_preview.setReadOnly(True)
		self.command_preview.setMaximumHeight(80)
		preview_layout.addWidget(self.command_preview)
		preview_group.setLayout(preview_layout)
		layout.addWidget(preview_group)
		
		# Connect signals
		self.script_edit.textChanged.connect(self._update_preview)
		self.quiet_check.stateChanged.connect(self._update_preview)
		self.verbose_check.stateChanged.connect(self._update_preview)
		self.log_edit.textChanged.connect(self._update_preview)
		self.extra_edit.textChanged.connect(self._update_preview)
		
		# Buttons
		button_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		)
		button_box.accepted.connect(self.accept)
		button_box.rejected.connect(self.reject)
		layout.addWidget(button_box)
		
		self.setLayout(layout)
		self._update_preview()
	
	def _browse_script(self):
		file, _ = QFileDialog.getOpenFileName(
			self, "Select Yosys Script", "", 
			"Yosys Scripts (*.ys *.tcl);;All Files (*)"
		)
		if file:
			self.script_edit.setText(file)
	
	def _browse_log(self):
		file, _ = QFileDialog.getSaveFileName(
			self, "Log File", "", "Log Files (*.log *.txt);;All Files (*)"
		)
		if file:
			self.log_edit.setText(file)
	
	def _update_preview(self):
		"""Update command preview."""
		cmd_parts = ["yosys"]
		
		if self.quiet_check.isChecked():
			cmd_parts.append("-q")
		
		if self.verbose_check.isChecked():
			cmd_parts.append("-v 3")
		
		if self.log_edit.text().strip():
			cmd_parts.extend(["-l", self.log_edit.text().strip()])
		
		if self.extra_edit.text().strip():
			cmd_parts.append(self.extra_edit.text().strip())
		
		if self.script_edit.text().strip():
			cmd_parts.extend(["-s", self.script_edit.text().strip()])
		else:
			cmd_parts.append("# Specify a script file")
		
		self.command_preview.setText(" ".join(cmd_parts))
	
	def get_command(self):
		"""Get the configured command."""
		return self.command_preview.toPlainText()
	
	
	def get_config(self):
		"""Get configuration dictionary."""
		return {
			"script": self.script_edit.text(),
			"quiet": self.quiet_check.isChecked(),
			"verbose": self.verbose_check.isChecked(),
			"log_file": self.log_edit.text(),
			"extra": self.extra_edit.text(),
		}


class VerilatorDialog(QDialog):
	"""Dialog for configuring Verilator."""
	
	def __init__(self, mode="lint", parent=None):
		super().__init__(parent)
		self.mode = mode
		title = "Verilator Lint" if mode == "lint" else "Verilator Coverage"
		self.setWindowTitle(title)
		self.setMinimumWidth(600)
		self.setMinimumHeight(500)
		
		layout = QVBoxLayout()
		
		# Source files
		self.source_widget = FileListWidget(
			"Source Files",
			"Verilog Files (*.v *.sv *.vh *.svh);;All Files (*)"
		)
		layout.addWidget(self.source_widget)
		
		# Options
		options_group = QGroupBox("Options")
		options_layout = QFormLayout()
		
		# Top module
		self.top_edit = QLineEdit()
		self.top_edit.setPlaceholderText("Top module name")
		options_layout.addRow("Top Module:", self.top_edit)
		
		# Include directories
		self.include_edit = QLineEdit()
		self.include_edit.setPlaceholderText("Comma-separated paths")
		options_layout.addRow("Include Dirs:", self.include_edit)
		
		# Warning options
		self.wall_check = QCheckBox("Enable all warnings (-Wall)")
		options_layout.addRow("", self.wall_check)
		
		if mode == "coverage":
			# Coverage options
			self.coverage_line_check = QCheckBox("Line coverage")
			self.coverage_line_check.setChecked(True)
			self.coverage_toggle_check = QCheckBox("Toggle coverage")
			options_layout.addRow("Coverage:", self.coverage_line_check)
			options_layout.addRow("", self.coverage_toggle_check)
		
		# Extra arguments
		self.extra_edit = QLineEdit()
		self.extra_edit.setPlaceholderText("Additional arguments")
		options_layout.addRow("Extra Args:", self.extra_edit)
		
		options_group.setLayout(options_layout)
		layout.addWidget(options_group)
		
		# Command preview
		preview_group = QGroupBox("Command Preview")
		preview_layout = QVBoxLayout()
		self.command_preview = QTextEdit()
		self.command_preview.setReadOnly(True)
		self.command_preview.setMaximumHeight(80)
		preview_layout.addWidget(self.command_preview)
		preview_group.setLayout(preview_layout)
		layout.addWidget(preview_group)
		
		# Connect signals
		self.top_edit.textChanged.connect(self._update_preview)
		self.include_edit.textChanged.connect(self._update_preview)
		self.wall_check.stateChanged.connect(self._update_preview)
		self.extra_edit.textChanged.connect(self._update_preview)
		
		# Buttons
		button_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		)
		button_box.accepted.connect(self.accept)
		button_box.rejected.connect(self.reject)
		layout.addWidget(button_box)
		
		self.setLayout(layout)
		self._update_preview()
	
	def _update_preview(self):
		"""Update command preview."""
		cmd_parts = ["verilator"]
		
		if self.mode == "lint":
			cmd_parts.append("--lint-only")
		
		if self.wall_check.isChecked():
			cmd_parts.append("-Wall")
		
		if self.mode == "coverage":
			if hasattr(self, 'coverage_line_check') and self.coverage_line_check.isChecked():
				cmd_parts.append("--coverage")
			if hasattr(self, 'coverage_toggle_check') and self.coverage_toggle_check.isChecked():
				cmd_parts.append("--coverage-toggle")
		
		# Include directories
		includes = [i.strip() for i in self.include_edit.text().split(",") if i.strip()]
		for inc in includes:
			cmd_parts.append(f"-I{inc}")
		
		# Top module
		if self.top_edit.text().strip():
			cmd_parts.extend(["--top-module", self.top_edit.text().strip()])
		
		if self.extra_edit.text().strip():
			cmd_parts.append(self.extra_edit.text().strip())
		
		# Sources
		sources = self.source_widget.get_files()
		if sources:
			cmd_parts.extend(sources)
		else:
			cmd_parts.append("# Add source files")
		
		self.command_preview.setText(" ".join(cmd_parts))
	
	def get_command(self):
		"""Get the configured command."""
		return self.command_preview.toPlainText()


class VeribleDialog(QDialog):
	"""Dialog for configuring Verible linter/formatter."""
	
	def __init__(self, mode="lint", parent=None):
		super().__init__(parent)
		self.mode = mode
		title = "Verible Lint" if mode == "lint" else "Verible Format"
		self.setWindowTitle(title)
		self.setMinimumWidth(600)
		self.setMinimumHeight(450)
		
		layout = QVBoxLayout()
		
		# Source files
		self.source_widget = FileListWidget(
			"Source Files",
			"SystemVerilog Files (*.sv *.svh *.v *.vh);;All Files (*)"
		)
		layout.addWidget(self.source_widget)
		
		# Options
		options_group = QGroupBox("Options")
		options_layout = QFormLayout()
		
		if mode == "lint":
			# Lint options
			self.rules_edit = QLineEdit()
			self.rules_edit.setPlaceholderText("e.g., line-length=120")
			options_layout.addRow("Rules:", self.rules_edit)
			
			# Waiver files
			waiver_layout = QHBoxLayout()
			self.waiver_edit = QLineEdit()
			self.waiver_edit.setPlaceholderText("Waiver configuration file")
			waiver_btn = QPushButton("Browse...")
			waiver_btn.clicked.connect(self._browse_waiver)
			waiver_layout.addWidget(self.waiver_edit)
			waiver_layout.addWidget(waiver_btn)
			options_layout.addRow("Waiver File:", waiver_layout)
		
		else:  # format mode
			# Format options
			self.inplace_check = QCheckBox("Modify files in-place")
			options_layout.addRow("", self.inplace_check)
			
			self.column_spin = QSpinBox()
			self.column_spin.setMinimum(40)
			self.column_spin.setMaximum(200)
			self.column_spin.setValue(100)
			options_layout.addRow("Column Limit:", self.column_spin)
			
			self.indent_spin = QSpinBox()
			self.indent_spin.setMinimum(1)
			self.indent_spin.setMaximum(8)
			self.indent_spin.setValue(2)
			options_layout.addRow("Indent Spaces:", self.indent_spin)
		
		# Extra arguments
		self.extra_edit = QLineEdit()
		self.extra_edit.setPlaceholderText("Additional arguments")
		options_layout.addRow("Extra Args:", self.extra_edit)
		
		options_group.setLayout(options_layout)
		layout.addWidget(options_group)
		
		# Command preview
		preview_group = QGroupBox("Command Preview")
		preview_layout = QVBoxLayout()
		self.command_preview = QTextEdit()
		self.command_preview.setReadOnly(True)
		self.command_preview.setMaximumHeight(80)
		preview_layout.addWidget(self.command_preview)
		preview_group.setLayout(preview_layout)
		layout.addWidget(preview_group)
		
		# Connect signals
		self.extra_edit.textChanged.connect(self._update_preview)
		if mode == "lint":
			self.rules_edit.textChanged.connect(self._update_preview)
			self.waiver_edit.textChanged.connect(self._update_preview)
		else:
			self.inplace_check.stateChanged.connect(self._update_preview)
			self.column_spin.valueChanged.connect(self._update_preview)
			self.indent_spin.valueChanged.connect(self._update_preview)
		
		# Buttons
		button_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		)
		button_box.accepted.connect(self.accept)
		button_box.rejected.connect(self.reject)
		layout.addWidget(button_box)
		
		self.setLayout(layout)
		self._update_preview()
	
	def _browse_waiver(self):
		file, _ = QFileDialog.getOpenFileName(
			self, "Select Waiver File", "",
			"Waiver Files (*.vlt *.waiver);;All Files (*)"
		)
		if file:
			self.waiver_edit.setText(file)
	
	def _update_preview(self):
		"""Update command preview."""
		if self.mode == "lint":
			cmd_parts = ["verible-verilog-lint"]
			
			if hasattr(self, 'rules_edit') and self.rules_edit.text().strip():
				rules = [r.strip() for r in self.rules_edit.text().split(",") if r.strip()]
				for rule in rules:
					cmd_parts.append(f"--rules={rule}")
			
			if hasattr(self, 'waiver_edit') and self.waiver_edit.text().strip():
				cmd_parts.append(f"--waiver_files={self.waiver_edit.text().strip()}")
		
		else:  # format
			cmd_parts = ["verible-verilog-format"]
			
			if hasattr(self, 'inplace_check') and self.inplace_check.isChecked():
				cmd_parts.append("--inplace")
			
			if hasattr(self, 'column_spin'):
				cmd_parts.append(f"--column_limit={self.column_spin.value()}")
			
			if hasattr(self, 'indent_spin'):
				cmd_parts.append(f"--indentation_spaces={self.indent_spin.value()}")
		
		if self.extra_edit.text().strip():
			cmd_parts.append(self.extra_edit.text().strip())
		
		sources = self.source_widget.get_files()
		if sources:
			cmd_parts.extend(sources)
		else:
			cmd_parts.append("# Add source files")
		
		self.command_preview.setText(" ".join(cmd_parts))
	
	def get_command(self):
		"""Get the configured command."""
		return self.command_preview.toPlainText()


class MagicDialog(QDialog):
	"""Dialog for configuring Magic VLSI layout tool."""
	
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Magic Layout Tool")
		self.setMinimumWidth(600)
		self.setMinimumHeight(400)
		
		layout = QVBoxLayout()
		
		# File selection
		file_group = QGroupBox("Layout File")
		file_layout = QVBoxLayout()
		
		layout_file_layout = QHBoxLayout()
		self.layout_edit = QLineEdit()
		self.layout_edit.setPlaceholderText("Layout file (.mag, .gds, .def)")
		layout_btn = QPushButton("Browse...")
		layout_btn.clicked.connect(self._browse_layout)
		layout_file_layout.addWidget(self.layout_edit)
		layout_file_layout.addWidget(layout_btn)
		file_layout.addLayout(layout_file_layout)
		
		file_group.setLayout(file_layout)
		layout.addWidget(file_group)
		
		# Options
		options_group = QGroupBox("Options")
		options_layout = QFormLayout()
		
		# Technology file
		tech_layout = QHBoxLayout()
		self.tech_edit = QLineEdit()
		self.tech_edit.setPlaceholderText("Technology file")
		tech_btn = QPushButton("Browse...")
		tech_btn.clicked.connect(self._browse_tech)
		tech_layout.addWidget(self.tech_edit)
		tech_layout.addWidget(tech_btn)
		options_layout.addRow("Tech File:", tech_layout)
		
		# Script
		script_layout = QHBoxLayout()
		self.script_edit = QLineEdit()
		self.script_edit.setPlaceholderText("TCL script to run")
		script_btn = QPushButton("Browse...")
		script_btn.clicked.connect(self._browse_script)
		script_layout.addWidget(self.script_edit)
		script_layout.addWidget(script_btn)
		options_layout.addRow("Script:", script_layout)
		
		# Mode options
		self.noconsole_check = QCheckBox("No console")
		options_layout.addRow("", self.noconsole_check)
		
		self.batch_check = QCheckBox("Batch mode (no GUI)")
		options_layout.addRow("", self.batch_check)
		
		# Extra arguments
		self.extra_edit = QLineEdit()
		options_layout.addRow("Extra Args:", self.extra_edit)
		
		options_group.setLayout(options_layout)
		layout.addWidget(options_group)
		
		# Command preview
		preview_group = QGroupBox("Command Preview")
		preview_layout = QVBoxLayout()
		self.command_preview = QTextEdit()
		self.command_preview.setReadOnly(True)
		self.command_preview.setMaximumHeight(80)
		preview_layout.addWidget(self.command_preview)
		preview_group.setLayout(preview_layout)
		layout.addWidget(preview_group)
		
		# Connect signals
		self.layout_edit.textChanged.connect(self._update_preview)
		self.tech_edit.textChanged.connect(self._update_preview)
		self.script_edit.textChanged.connect(self._update_preview)
		self.noconsole_check.stateChanged.connect(self._update_preview)
		self.batch_check.stateChanged.connect(self._update_preview)
		self.extra_edit.textChanged.connect(self._update_preview)
		
		# Buttons
		button_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		)
		button_box.accepted.connect(self.accept)
		button_box.rejected.connect(self.reject)
		layout.addWidget(button_box)
		
		self.setLayout(layout)
		self._update_preview()
	
	def _browse_layout(self):
		file, _ = QFileDialog.getOpenFileName(
			self, "Select Layout File", "",
			"Layout Files (*.mag *.gds *.def);;All Files (*)"
		)
		if file:
			self.layout_edit.setText(file)
	
	def _browse_tech(self):
		file, _ = QFileDialog.getOpenFileName(
			self, "Select Technology File", "",
			"Technology Files (*.tech);;All Files (*)"
		)
		if file:
			self.tech_edit.setText(file)
	
	def _browse_script(self):
		file, _ = QFileDialog.getOpenFileName(
			self, "Select Script", "",
			"TCL Scripts (*.tcl *.magicrc);;All Files (*)"
		)
		if file:
			self.script_edit.setText(file)
	
	def _update_preview(self):
		"""Update command preview."""
		cmd_parts = ["magic"]
		
		if self.batch_check.isChecked():
			cmd_parts.append("-dnull")
		
		if self.noconsole_check.isChecked():
			cmd_parts.append("-noconsole")
		
		if self.tech_edit.text().strip():
			cmd_parts.extend(["-T", self.tech_edit.text().strip()])
		
		if self.extra_edit.text().strip():
			cmd_parts.append(self.extra_edit.text().strip())
		
		if self.script_edit.text().strip():
			cmd_parts.append(self.script_edit.text().strip())
		
		if self.layout_edit.text().strip():
			cmd_parts.append(self.layout_edit.text().strip())
		
		self.command_preview.setText(" ".join(cmd_parts))
	
	def get_command(self):
		"""Get the configured command."""
		return self.command_preview.toPlainText()


class KLayoutDialog(QDialog):
	"""Dialog for configuring KLayout."""
	
	def __init__(self, mode="view", parent=None):
		super().__init__(parent)
		self.mode = mode
		title = "KLayout Viewer" if mode == "view" else "KLayout DRC"
		self.setWindowTitle(title)
		self.setMinimumWidth(600)
		self.setMinimumHeight(400)
		
		layout = QVBoxLayout()
		
		# File selection
		file_group = QGroupBox("Layout File")
		file_layout = QHBoxLayout()
		self.layout_edit = QLineEdit()
		self.layout_edit.setPlaceholderText("Layout file (.gds, .oas, .dxf)")
		layout_btn = QPushButton("Browse...")
		layout_btn.clicked.connect(self._browse_layout)
		file_layout.addWidget(self.layout_edit)
		file_layout.addWidget(layout_btn)
		file_group.setLayout(file_layout)
		layout.addWidget(file_group)
		
		# Options
		options_group = QGroupBox("Options")
		options_layout = QFormLayout()
		
		if mode == "view":
			# View mode options
			tech_layout = QHBoxLayout()
			self.tech_edit = QLineEdit()
			self.tech_edit.setPlaceholderText("Technology file (.lyt)")
			tech_btn = QPushButton("Browse...")
			tech_btn.clicked.connect(self._browse_tech)
			tech_layout.addWidget(self.tech_edit)
			tech_layout.addWidget(tech_btn)
			options_layout.addRow("Tech File:", tech_layout)
			
			layer_layout = QHBoxLayout()
			self.layer_edit = QLineEdit()
			self.layer_edit.setPlaceholderText("Layer properties (.lyp)")
			layer_btn = QPushButton("Browse...")
			layer_btn.clicked.connect(self._browse_layer)
			layer_layout.addWidget(self.layer_edit)
			layer_layout.addWidget(layer_btn)
			options_layout.addRow("Layer Props:", layer_layout)
		
		else:  # DRC mode
			# DRC script
			script_layout = QHBoxLayout()
			self.script_edit = QLineEdit()
			self.script_edit.setPlaceholderText("DRC rule script")
			script_btn = QPushButton("Browse...")
			script_btn.clicked.connect(self._browse_script)
			script_layout.addWidget(self.script_edit)
			script_layout.addWidget(script_btn)
			options_layout.addRow("DRC Script:", script_layout)
			
			# Report file
			report_layout = QHBoxLayout()
			self.report_edit = QLineEdit()
			self.report_edit.setPlaceholderText("DRC report output")
			report_btn = QPushButton("Browse...")
			report_btn.clicked.connect(self._browse_report)
			report_layout.addWidget(self.report_edit)
			report_layout.addWidget(report_btn)
			options_layout.addRow("Report File:", report_layout)
		
		# Extra arguments
		self.extra_edit = QLineEdit()
		options_layout.addRow("Extra Args:", self.extra_edit)
		
		options_group.setLayout(options_layout)
		layout.addWidget(options_group)
		
		# Command preview
		preview_group = QGroupBox("Command Preview")
		preview_layout = QVBoxLayout()
		self.command_preview = QTextEdit()
		self.command_preview.setReadOnly(True)
		self.command_preview.setMaximumHeight(80)
		preview_layout.addWidget(self.command_preview)
		preview_group.setLayout(preview_layout)
		layout.addWidget(preview_group)
		
		# Connect signals
		self.layout_edit.textChanged.connect(self._update_preview)
		self.extra_edit.textChanged.connect(self._update_preview)
		if mode == "view":
			self.tech_edit.textChanged.connect(self._update_preview)
			self.layer_edit.textChanged.connect(self._update_preview)
		else:
			self.script_edit.textChanged.connect(self._update_preview)
			self.report_edit.textChanged.connect(self._update_preview)
		
		# Buttons
		button_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		)
		button_box.accepted.connect(self.accept)
		button_box.rejected.connect(self.reject)
		layout.addWidget(button_box)
		
		self.setLayout(layout)
		self._update_preview()
	
	def _browse_layout(self):
		file, _ = QFileDialog.getOpenFileName(
			self, "Select Layout", "",
			"Layout Files (*.gds *.oas *.dxf);;All Files (*)"
		)
		if file:
			self.layout_edit.setText(file)
	
	def _browse_tech(self):
		file, _ = QFileDialog.getOpenFileName(
			self, "Select Technology File", "",
			"Technology Files (*.lyt);;All Files (*)"
		)
		if file:
			self.tech_edit.setText(file)
	
	def _browse_layer(self):
		file, _ = QFileDialog.getOpenFileName(
			self, "Select Layer Properties", "",
			"Layer Files (*.lyp);;All Files (*)"
		)
		if file:
			self.layer_edit.setText(file)
	
	def _browse_script(self):
		file, _ = QFileDialog.getOpenFileName(
			self, "Select DRC Script", "",
			"DRC Scripts (*.drc *.lydrc);;All Files (*)"
		)
		if file:
			self.script_edit.setText(file)
	
	def _browse_report(self):
		file, _ = QFileDialog.getSaveFileName(
			self, "Report File", "",
			"Report Files (*.lyrdb *.xml);;All Files (*)"
		)
		if file:
			self.report_edit.setText(file)
	
	def _update_preview(self):
		"""Update command preview."""
		cmd_parts = ["klayout"]
		
		if self.mode == "drc":
			cmd_parts.append("-b")  # Batch mode for DRC
			
			if hasattr(self, 'script_edit') and self.script_edit.text().strip():
				cmd_parts.extend(["-r", self.script_edit.text().strip()])
			
			if hasattr(self, 'report_edit') and self.report_edit.text().strip():
				cmd_parts.extend(["-rd", f"report={self.report_edit.text().strip()}"])
		
		else:  # view mode
			if hasattr(self, 'tech_edit') and self.tech_edit.text().strip():
				cmd_parts.extend(["-nn", self.tech_edit.text().strip()])
			
			if hasattr(self, 'layer_edit') and self.layer_edit.text().strip():
				cmd_parts.extend(["-l", self.layer_edit.text().strip()])
		
		if self.extra_edit.text().strip():
			cmd_parts.append(self.extra_edit.text().strip())
		
		if self.layout_edit.text().strip():
			cmd_parts.append(self.layout_edit.text().strip())
		
		self.command_preview.setText(" ".join(cmd_parts))
	
	def get_command(self):
		"""Get the configured command."""
		return self.command_preview.toPlainText()

