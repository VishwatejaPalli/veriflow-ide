import shutil
import json
from pathlib import Path

from PySide6.QtCore import QDir, Qt, Signal, QSize, QSettings
from PySide6.QtGui import (
	QAction, QColor, QFont, QIcon, QKeySequence, QPainter, QPixmap,
	QLinearGradient, QPainterPath
)
from PySide6.QtWidgets import (
	QApplication,
	QCheckBox,
	QColorDialog,
	QComboBox,
	QDialog,
	QDialogButtonBox,
	QFileDialog,
	QFileIconProvider,
	QFileSystemModel,
	QFormLayout,
	QGroupBox,
	QHBoxLayout,
	QInputDialog,
	QLabel,
	QMenu,
	QMessageBox,
	QListView,
	QPushButton,
	QScrollArea,
	QStyle,
	QStyleFactory,
	QStyledItemDelegate,
	QTreeView,
	QVBoxLayout,
	QWidget,
)


class FileTreeSettings:
	"""Persistent settings for file tree customization."""

	def __init__(self):
		self.settings = QSettings("OpenHDL IDE", "FileTree")
		
	def get_icon_style(self):
		return self.settings.value("icon_style", "badge")
	
	def set_icon_style(self, style):
		self.settings.setValue("icon_style", style)
	
	def get_icon_shape(self):
		return self.settings.value("icon_shape", "rounded_rect")
	
	def set_icon_shape(self, shape):
		self.settings.setValue("icon_shape", shape)
	
	def get_hdl_color(self):
		return self.settings.value("hdl_color", "#1e3a8a")
	
	def set_hdl_color(self, color):
		self.settings.setValue("hdl_color", color)
	
	def get_hdl_text_color(self):
		return self.settings.value("hdl_text_color", "#f1f5f9")
	
	def set_hdl_text_color(self, color):
		self.settings.setValue("hdl_text_color", color)
	
	def get_script_color(self):
		return self.settings.value("script_color", "#065f46")
	
	def set_script_color(self, color):
		self.settings.setValue("script_color", color)
	
	def get_script_text_color(self):
		return self.settings.value("script_text_color", "#f1f7f5")
	
	def set_script_text_color(self, color):
		self.settings.setValue("script_text_color", color)
	
	def get_folder_color(self):
		return self.settings.value("folder_color", "#d97706")
	
	def set_folder_color(self, color):
		self.settings.setValue("folder_color", color)
	
	def get_folder_text_color(self):
		return self.settings.value("folder_text_color", "#ffffff")
	
	def set_folder_text_color(self, color):
		self.settings.setValue("folder_text_color", color)


class CustomizationDialog(QDialog):
	"""Modern customization panel with graphical previews."""

	PRESETS = {
		"Modern Blue": {
			"style": "badge",
			"shape": "rounded_rect",
			"hdl_bg": "#1e3a8a",
			"hdl_text": "#f1f5f9",
			"script_bg": "#065f46",
			"script_text": "#f1f7f5",
			"folder_bg": "#d97706",
			"folder_text": "#ffffff"
		},
		"Vibrant": {
			"style": "gradient",
			"shape": "circle",
			"hdl_bg": "#8b5cf6",
			"hdl_text": "#faf5ff",
			"script_bg": "#ec4899",
			"script_text": "#fdf2f8",
			"folder_bg": "#f59e0b",
			"folder_text": "#fffbeb"
		},
		"Minimal": {
			"style": "flat",
			"shape": "square",
			"hdl_bg": "#374151",
			"hdl_text": "#f9fafb",
			"script_bg": "#6b7280",
			"script_text": "#f9fafb",
			"folder_bg": "#9ca3af",
			"folder_text": "#ffffff"
		}
	}

	def __init__(self, settings, parent=None):
		super().__init__(parent)
		self.settings = settings
		self.current_preset = None
		self.custom_settings = {
			"style": str(settings.get_icon_style()),
			"shape": str(settings.get_icon_shape()),
			"hdl_bg": str(settings.get_hdl_color()),
			"hdl_text": str(settings.get_hdl_text_color()),
			"script_bg": str(settings.get_script_color()),
			"script_text": str(settings.get_script_text_color()),
			"folder_bg": str(settings.get_folder_color()),
			"folder_text": str(settings.get_folder_text_color())
		}
		self.setWindowTitle("Icon Theme Settings")
		self.setMinimumSize(850, 650)
		self.setStyleSheet("""
			QDialog {
				background-color: #f8f9fa;
			}
			QGroupBox {
				font-weight: bold;
				border: 2px solid #dee2e6;
				border-radius: 8px;
				margin-top: 12px;
				padding: 15px;
				background-color: white;
			}
			QGroupBox::title {
				subcontrol-origin: margin;
				left: 20px;
				padding: 0 8px;
				color: #212529;
			}
			QPushButton {
				background-color: #0d6efd;
				color: white;
				border: none;
				border-radius: 6px;
				padding: 8px 16px;
				font-weight: bold;
				font-size: 13px;
			}
			QPushButton:hover {
				background-color: #0b5ed7;
			}
			QPushButton:pressed {
				background-color: #0a58ca;
			}
			QPushButton:checked {
				background-color: #198754;
			}
			QLabel#presetLabel {
				padding: 8px;
				border: 2px solid transparent;
				border-radius: 6px;
				background-color: #f8f9fa;
			}
			QLabel#presetLabel:hover {
				border-color: #0d6efd;
				background-color: white;
			}
		""")
		self._build_ui()

	def _build_ui(self):
		layout = QVBoxLayout()
		layout.setSpacing(15)
		
		# Title
		title = QLabel("Choose Your Icon Theme")
		title.setStyleSheet("font-size: 20px; font-weight: bold; color: #212529; padding: 10px;")
		layout.addWidget(title)
		
		# Preset Themes Section
		preset_group = QGroupBox("Preset Themes")
		preset_layout = QHBoxLayout()
		preset_layout.setSpacing(20)
		
		self.preset_widgets = {}
		for preset_name, preset_values in self.PRESETS.items():
			preset_widget = self._create_preset_widget(preset_name, preset_values)
			preset_layout.addWidget(preset_widget)
			self.preset_widgets[preset_name] = preset_widget
		
		preset_group.setLayout(preset_layout)
		layout.addWidget(preset_group)
		
		# Custom Settings Section
		custom_group = QGroupBox("Custom Settings")
		custom_layout = QVBoxLayout()
		
		# Style and Shape
		style_shape_layout = QHBoxLayout()
		
		style_layout = QFormLayout()
		self.style_combo = QComboBox()
		self.style_combo.addItems(["badge", "flat", "gradient"])
		self.style_combo.setCurrentText(self.custom_settings["style"])
		self.style_combo.currentTextChanged.connect(self._on_custom_change)
		style_layout.addRow("Icon Style:", self.style_combo)
		
		self.shape_combo = QComboBox()
		self.shape_combo.addItems(["rounded_rect", "circle", "square"])
		self.shape_combo.setCurrentText(self.custom_settings["shape"])
		self.shape_combo.currentTextChanged.connect(self._on_custom_change)
		style_layout.addRow("Icon Shape:", self.shape_combo)
		
		style_shape_layout.addLayout(style_layout)
		
		# Preview
		preview_container = QVBoxLayout()
		preview_label = QLabel("Preview:")
		preview_label.setStyleSheet("font-weight: bold; font-size: 13px;")
		preview_container.addWidget(preview_label)
		
		self.preview_widget = QLabel()
		self.preview_widget.setMinimumSize(200, 80)
		self.preview_widget.setStyleSheet("background-color: white; border: 1px solid #dee2e6; border-radius: 4px;")
		self.preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
		preview_container.addWidget(self.preview_widget)
		
		style_shape_layout.addLayout(preview_container)
		custom_layout.addLayout(style_shape_layout)
		
		# Color Customization Grid
		colors_layout = QHBoxLayout()
		
		# HDL Colors
		hdl_box = self._create_color_box("HDL Files", "hdl_bg", "hdl_text")
		colors_layout.addWidget(hdl_box)
		
		# Script Colors
		script_box = self._create_color_box("Script Files", "script_bg", "script_text")
		colors_layout.addWidget(script_box)
		
		# Folder Colors (only background color)
		folder_box = self._create_folder_color_box("Folders", "folder_bg")
		colors_layout.addWidget(folder_box)
		
		custom_layout.addLayout(colors_layout)
		custom_group.setLayout(custom_layout)
		layout.addWidget(custom_group)
		
		layout.addStretch()
		
		# Dialog buttons
		button_layout = QHBoxLayout()
		button_layout.addStretch()
		
		apply_btn = QPushButton("Apply")
		apply_btn.setMinimumWidth(100)
		apply_btn.clicked.connect(self._save_settings)
		
		cancel_btn = QPushButton("Cancel")
		cancel_btn.setMinimumWidth(100)
		cancel_btn.setStyleSheet("background-color: #6c757d;")
		cancel_btn.clicked.connect(self.reject)
		
		button_layout.addWidget(cancel_btn)
		button_layout.addWidget(apply_btn)
		layout.addLayout(button_layout)
		
		self.setLayout(layout)
		self._update_preview()

	def _create_preset_widget(self, name, values):
		"""Create a clickable preset theme widget with preview."""
		container = QWidget()
		container.setMinimumWidth(250)
		container.setCursor(Qt.CursorShape.PointingHandCursor)
		layout = QVBoxLayout()
		
		# Preset name
		name_label = QLabel(name)
		name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #212529;")
		name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
		layout.addWidget(name_label)
		
		# Preview icons
		preview_container = QLabel()
		preview_container.setObjectName("presetLabel")
		preview_container.setMinimumHeight(100)
		preview_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
		
		# Generate preview icons
		preview_pixmap = self._generate_preset_preview(values)
		preview_container.setPixmap(preview_pixmap)
		preview_container.mousePressEvent = lambda e: self._apply_preset(name, values)
		
		layout.addWidget(preview_container)
		
		# Apply button
		apply_btn = QPushButton(f"Use {name}")
		apply_btn.setStyleSheet("background-color: #198754; font-size: 12px; padding: 6px;")
		apply_btn.clicked.connect(lambda: self._apply_preset(name, values))
		layout.addWidget(apply_btn)
		
		container.setLayout(layout)
		return container

	def _generate_preset_preview(self, values):
		"""Generate preview pixmap showing 3 sample icons."""
		width = 220
		height = 80
		pixmap = QPixmap(width, height)
		pixmap.fill(Qt.GlobalColor.white)
		
		painter = QPainter(pixmap)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		
		# Draw three sample icons
		icons = [
			("HD", values["hdl_bg"], values["hdl_text"], False),
			("SH", values["script_bg"], values["script_text"], False),
			("folder", values["folder_bg"], values["folder_text"], True)
		]
		
		icon_size = 48
		spacing = (width - 3 * icon_size) // 4
		y_pos = (height - icon_size) // 2
		
		for i, (label, bg_color, text_color, is_folder) in enumerate(icons):
			x_pos = spacing + i * (icon_size + spacing)
			
			painter.setPen(Qt.PenStyle.NoPen)
			
			# Draw background shape only for non-folder icons
			if not is_folder:
				if values["style"] == "gradient":
					gradient = QLinearGradient(x_pos, y_pos, x_pos, y_pos + icon_size)
					gradient.setColorAt(0, QColor(bg_color))
					gradient.setColorAt(1, QColor(text_color))
					painter.setBrush(gradient)
				else:
					painter.setBrush(QColor(bg_color))
				
				# Draw shape
				if values["shape"] == "circle":
					painter.drawEllipse(x_pos, y_pos, icon_size, icon_size)
				elif values["shape"] == "square":
					painter.drawRect(x_pos, y_pos, icon_size, icon_size)
				else:  # rounded_rect
					painter.drawRoundedRect(x_pos, y_pos, icon_size, icon_size, 8, 8)
			
			# Draw content
			if is_folder:
				# Draw traditional folder icon
				painter.setBrush(QColor(bg_color))
				
				# Scale folder to preview size
				scale = icon_size / 24
				base_x = x_pos + (icon_size - int(18 * scale)) // 2
				base_y = y_pos + (icon_size - int(13 * scale)) // 2
				
				# Folder tab
				tab_path = QPainterPath()
				tab_path.moveTo(base_x, base_y + int(2 * scale))
				tab_path.lineTo(base_x, base_y)
				tab_path.lineTo(base_x + int(6 * scale), base_y)
				tab_path.lineTo(base_x + int(7 * scale), base_y + int(2 * scale))
				tab_path.closeSubpath()
				painter.drawPath(tab_path)
				
				# Folder body
				body_path = QPainterPath()
				body_path.moveTo(base_x, base_y + int(2 * scale))
				body_path.lineTo(base_x, base_y + int(11 * scale))
				body_path.lineTo(base_x + int(18 * scale), base_y + int(11 * scale))
				body_path.lineTo(base_x + int(18 * scale), base_y + int(2 * scale))
				body_path.closeSubpath()
				painter.drawPath(body_path)
				
				# Shadow for depth
				painter.setOpacity(0.3)
				painter.setBrush(Qt.GlobalColor.black)
				painter.drawRect(base_x + int(1 * scale), base_y + int(10 * scale), 
							   int(17 * scale), int(1 * scale))
				painter.setOpacity(1.0)
			else:
				# Draw text label
				painter.setPen(QColor(text_color))
				font = QFont("Fira Code", 16, int(QFont.Weight.Bold))
				painter.setFont(font)
				painter.drawText(x_pos, y_pos, icon_size, icon_size, 
								Qt.AlignmentFlag.AlignCenter, label)
		
		painter.end()
		return pixmap

	def _create_color_box(self, title, bg_key, text_key):
		"""Create color customization box."""
		box = QGroupBox(title)
		box.setStyleSheet("QGroupBox { padding-top: 20px; }")
		layout = QVBoxLayout()
		
		# Background color
		bg_layout = QHBoxLayout()
		bg_label = QLabel("Background:")
		bg_label.setMinimumWidth(90)
		self.color_buttons = getattr(self, 'color_buttons', {})
		bg_btn = QPushButton()
		bg_btn.setFixedSize(60, 30)
		bg_btn.setStyleSheet(f"background-color: {self.custom_settings[bg_key]}; border: 1px solid #ccc;")
		bg_btn.clicked.connect(lambda: self._pick_color(bg_key, bg_btn))
		self.color_buttons[bg_key] = bg_btn
		bg_layout.addWidget(bg_label)
		bg_layout.addWidget(bg_btn)
		bg_layout.addStretch()
		layout.addLayout(bg_layout)
		
		# Text color
		text_layout = QHBoxLayout()
		text_label = QLabel("Text:")
		text_label.setMinimumWidth(90)
		text_btn = QPushButton()
		text_btn.setFixedSize(60, 30)
		text_btn.setStyleSheet(f"background-color: {self.custom_settings[text_key]}; border: 1px solid #ccc;")
		text_btn.clicked.connect(lambda: self._pick_color(text_key, text_btn))
		self.color_buttons[text_key] = text_btn
		text_layout.addWidget(text_label)
		text_layout.addWidget(text_btn)
		text_layout.addStretch()
		layout.addLayout(text_layout)
		
		box.setLayout(layout)
		return box

	def _create_folder_color_box(self, title, bg_key):
		"""Create color customization box for folders (color only)."""
		box = QGroupBox(title)
		box.setStyleSheet("QGroupBox { padding-top: 20px; }")
		layout = QVBoxLayout()
		
		# Folder color
		bg_layout = QHBoxLayout()
		bg_label = QLabel("Folder Color:")
		bg_label.setMinimumWidth(90)
		self.color_buttons = getattr(self, 'color_buttons', {})
		bg_btn = QPushButton()
		bg_btn.setFixedSize(60, 30)
		bg_btn.setStyleSheet(f"background-color: {self.custom_settings[bg_key]}; border: 1px solid #ccc;")
		bg_btn.clicked.connect(lambda: self._pick_color(bg_key, bg_btn))
		self.color_buttons[bg_key] = bg_btn
		bg_layout.addWidget(bg_label)
		bg_layout.addWidget(bg_btn)
		bg_layout.addStretch()
		layout.addLayout(bg_layout)
		
		# Add spacer to match height of other boxes
		layout.addSpacing(38)
		
		box.setLayout(layout)
		return box

	def _apply_preset(self, name, values):
		"""Apply a preset theme."""
		self.current_preset = name
		self.custom_settings = values.copy()
		
		# Update UI
		self.style_combo.setCurrentText(values["style"])
		self.shape_combo.setCurrentText(values["shape"])
		
		for key, button in self.color_buttons.items():
			button.setStyleSheet(f"background-color: {values[key]}; border: 1px solid #ccc;")
		
		self._update_preview()

	def _pick_color(self, key, button):
		"""Pick a color."""
		color = QColorDialog.getColor(
			QColor(self.custom_settings[key]),
			self,
			"Choose Color"
		)
		if color.isValid():
			self.custom_settings[key] = color.name()
			button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
			self._update_preview()

	def _on_custom_change(self):
		"""Handle custom setting changes."""
		self.custom_settings["style"] = self.style_combo.currentText()
		self.custom_settings["shape"] = self.shape_combo.currentText()
		self._update_preview()

	def _update_preview(self):
		"""Update the preview widget."""
		preview_pixmap = self._generate_preset_preview(self.custom_settings)
		self.preview_widget.setPixmap(preview_pixmap)

	def _save_settings(self):
		"""Save all customization settings."""
		self.settings.set_icon_style(self.custom_settings["style"])
		self.settings.set_icon_shape(self.custom_settings["shape"])
		self.settings.set_hdl_color(self.custom_settings["hdl_bg"])
		self.settings.set_hdl_text_color(self.custom_settings["hdl_text"])
		self.settings.set_script_color(self.custom_settings["script_bg"])
		self.settings.set_script_text_color(self.custom_settings["script_text"])
		self.settings.set_folder_color(self.custom_settings["folder_bg"])
		self.settings.set_folder_text_color(self.custom_settings["folder_text"])
		
		self.accept()


class ProjectIconProvider(QFileIconProvider):
	"""Custom icons for HDL projects with customizable styles."""

	HDL_EXTENSIONS = {".v", ".sv", ".vh", ".svh", ".vhd", ".vhdl"}
	SCRIPT_EXTENSIONS = {".tcl", ".sh", ".py"}

	def __init__(self, settings=None):
		super().__init__()
		self.settings = settings or FileTreeSettings()
		app = QApplication.instance()
		style = app.style() if isinstance(app, QApplication) else None
		if style is None and hasattr(QStyleFactory, "create"):
			style = QStyleFactory.create("Fusion")
		self._folder_icon = style.standardIcon(QStyle.StandardPixmap.SP_DirIcon) if style else QIcon()
		self._file_icon = style.standardIcon(QStyle.StandardPixmap.SP_FileIcon) if style else QIcon()
		self._build_icons()

	def _build_icons(self):
		"""Build icons based on current settings."""
		icon_style: str = str(self.settings.get_icon_style())
		icon_shape: str = str(self.settings.get_icon_shape())
		
		if icon_style == "badge":
			self._hdl_icon = self._build_badge_icon("HD", self.settings.get_hdl_color(), self.settings.get_hdl_text_color(), icon_shape)
			self._script_icon = self._build_badge_icon("SH", self.settings.get_script_color(), self.settings.get_script_text_color(), icon_shape)
			self._folder_icon_custom = self._build_simple_folder_icon(self.settings.get_folder_color())
		elif icon_style == "flat":
			self._hdl_icon = self._build_flat_icon("HD", self.settings.get_hdl_color(), icon_shape)
			self._script_icon = self._build_flat_icon("SH", self.settings.get_script_color(), icon_shape)
			self._folder_icon_custom = self._build_simple_folder_icon(self.settings.get_folder_color())
		else:  # gradient
			self._hdl_icon = self._build_gradient_icon("HD", self.settings.get_hdl_color(), self.settings.get_hdl_text_color(), icon_shape)
			self._script_icon = self._build_gradient_icon("SH", self.settings.get_script_color(), self.settings.get_script_text_color(), icon_shape)
			self._folder_icon_custom = self._build_simple_folder_icon(self.settings.get_folder_color())

	def icon(self, info):
		if isinstance(info, QFileIconProvider.IconType):
			return self._folder_icon_custom if info == QFileIconProvider.IconType.Folder else self._file_icon
		path = Path(info.filePath()) if info else None
		if not path:
			return self._file_icon
		if info.isDir():
			return self._folder_icon_custom
		suffix = path.suffix.lower()
		if suffix in self.HDL_EXTENSIONS:
			return self._hdl_icon
		if suffix in self.SCRIPT_EXTENSIONS:
			return self._script_icon
		return self._file_icon

	def _build_badge_icon(self, label, background, text_color, shape="rounded_rect"):
		"""Build badge-style icon."""
		size = 24
		pixmap = QPixmap(size, size)
		pixmap.fill(Qt.GlobalColor.transparent)
		painter = QPainter(pixmap)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setPen(Qt.PenStyle.NoPen)
		painter.setBrush(QColor(background))
		
		if shape == "circle":
			painter.drawEllipse(2, 2, size - 4, size - 4)
		elif shape == "square":
			painter.drawRect(2, 2, size - 4, size - 4)
		else:  # rounded_rect
			painter.drawRoundedRect(2, 2, size - 4, size - 4, 6, 6)
		
		painter.setPen(QColor(text_color))
		font = QFont("Fira Code", 8, int(QFont.Weight.Bold))
		painter.setFont(font)
		painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, label)
		painter.end()
		return QIcon(pixmap)

	def _build_flat_icon(self, label, background, shape="rounded_rect"):
		"""Build flat-style icon (no shadow, clean)."""
		size = 24
		pixmap = QPixmap(size, size)
		pixmap.fill(Qt.GlobalColor.transparent)
		painter = QPainter(pixmap)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setPen(Qt.PenStyle.NoPen)
		painter.setBrush(QColor(background))
		
		if shape == "circle":
			painter.drawEllipse(3, 3, size - 6, size - 6)
		elif shape == "square":
			painter.drawRect(3, 3, size - 6, size - 6)
		else:  # rounded_rect
			painter.drawRoundedRect(3, 3, size - 6, size - 6, 4, 4)
		
		painter.setPen(Qt.GlobalColor.white)
		font = QFont("Fira Code", 7, int(QFont.Weight.Bold))
		painter.setFont(font)
		painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, label)
		painter.end()
		return QIcon(pixmap)

	def _build_gradient_icon(self, label, start_color, end_color, shape="rounded_rect"):
		"""Build gradient-style icon."""
		size = 24
		pixmap = QPixmap(size, size)
		pixmap.fill(Qt.GlobalColor.transparent)
		painter = QPainter(pixmap)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		
		gradient = QLinearGradient(2, 2, 2, size - 2)
		gradient.setColorAt(0, QColor(start_color))
		gradient.setColorAt(1, QColor(end_color))
		painter.setPen(Qt.PenStyle.NoPen)
		painter.setBrush(gradient)
		
		if shape == "circle":
			painter.drawEllipse(2, 2, size - 4, size - 4)
		elif shape == "square":
			painter.drawRect(2, 2, size - 4, size - 4)
		else:  # rounded_rect
			painter.drawRoundedRect(2, 2, size - 4, size - 4, 6, 6)
		
		painter.setPen(QColor(end_color))
		font = QFont("Fira Code", 8, int(QFont.Weight.Bold))
		painter.setFont(font)
		painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, label)
		painter.end()
		return QIcon(pixmap)

	def _build_simple_folder_icon(self, folder_color):
		"""Build a simple colored folder icon with consistent shape."""
		size = 24
		pixmap = QPixmap(size, size)
		pixmap.fill(Qt.GlobalColor.transparent)
		painter = QPainter(pixmap)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		
		# Draw traditional folder shape
		painter.setPen(Qt.PenStyle.NoPen)
		painter.setBrush(QColor(folder_color))
		
		# Folder tab (top left)
		tab_path = QPainterPath()
		tab_path.moveTo(3, 8)
		tab_path.lineTo(3, 6)
		tab_path.lineTo(9, 6)
		tab_path.lineTo(10, 8)
		tab_path.closeSubpath()
		painter.drawPath(tab_path)
		
		# Folder body (main part)
		body_path = QPainterPath()
		body_path.moveTo(3, 8)
		body_path.lineTo(3, 19)
		body_path.lineTo(21, 19)
		body_path.lineTo(21, 8)
		body_path.closeSubpath()
		painter.drawPath(body_path)
		
		# Add slight shadow for depth
		painter.setOpacity(0.3)
		painter.setBrush(Qt.GlobalColor.black)
		painter.drawRect(4, 18, 17, 1)
		
		painter.end()
		return QIcon(pixmap)


class CenterAlignedDelegate(QStyledItemDelegate):
	"""Delegate for center-aligning cell content."""

	def paint(self, painter, option, index):
		# Copy the option and set alignment to center
		opt = option
		opt.displayAlignment = Qt.AlignmentFlag.AlignCenter
		super().paint(painter, opt, index)


class FileTreeWidget(QWidget):
	"""Simple project browser that emits file selections."""

	fileActivated = Signal(str)
	settingsChanged = Signal()

	def __init__(self, root_path=None, parent=None):
		super().__init__(parent)
		self._root_path = Path(root_path or Path.cwd()).resolve()
		self.settings = FileTreeSettings()
		self._build_ui()

	def _build_ui(self):
		layout = QVBoxLayout()

		controls = QHBoxLayout()
		self.path_label = QLabel(str(self._root_path))
		self.path_label.setObjectName("fileTreePathLabel")
		change_button = QPushButton("Change…")
		change_button.clicked.connect(self._select_root)
		customize_button = QPushButton("⚙ Customize")
		customize_button.setMaximumWidth(120)
		customize_button.clicked.connect(self._show_customization)
		controls.addWidget(self.path_label)
		controls.addStretch()
		controls.addWidget(customize_button)
		controls.addWidget(change_button)
		layout.addLayout(controls)

		self.model = QFileSystemModel(self)
		self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Files)
		self.model.setRootPath(str(self._root_path))
		self._icon_provider = ProjectIconProvider(self.settings)
		self.model.setIconProvider(self._icon_provider)

		# Create tree view with columns (details view)
		self.tree = QTreeView(self)
		self.tree.setModel(self.model)
		self.tree.setRootIndex(self.model.index(str(self._root_path)))
		self.tree.setObjectName("projectTree")
		self.tree.setAlternatingRowColors(True)
		self.tree.setUniformRowHeights(True)
		self.tree.setAnimated(False)
		self.tree.setExpandsOnDoubleClick(True)
		self.tree.setIconSize(QSize(24, 24))
		self.tree.doubleClicked.connect(self._handle_activated)
		self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.tree.customContextMenuRequested.connect(self._show_context_menu)
		# Show columns for details view
		self.tree.setColumnHidden(1, False)  # Size
		self.tree.setColumnHidden(2, False)  # Type
		self.tree.setColumnHidden(3, False)  # Date Modified
		
		# Center-align the size column
		self.tree.setItemDelegateForColumn(1, CenterAlignedDelegate(self.tree))
		
		layout.addWidget(self.tree)

		self._register_shortcuts()

		self.setLayout(layout)

	def _handle_activated(self, index):
		if self.model.isDir(index):
			return
		self.fileActivated.emit(self.model.filePath(index))

	def _show_context_menu(self, position):
		index = self.tree.indexAt(position)
		menu = QMenu(self)
		change_action = menu.addAction("Change Folder…")
		self._apply_shortcut_hint(change_action, self._change_folder_action.shortcut())
		menu.addSeparator()
		new_file_action = menu.addAction("New File…")
		self._apply_shortcut_hint(new_file_action, self._new_file_action.shortcut())
		new_folder_action = menu.addAction("New Folder…")
		self._apply_shortcut_hint(new_folder_action, self._new_folder_action.shortcut())
		ren_action = menu.addAction("Rename…")
		self._apply_shortcut_hint(ren_action, QKeySequence("F2"))
		delete_action = menu.addAction("Delete")
		self._apply_shortcut_hint(delete_action, QKeySequence(QKeySequence.StandardKey.Delete))
		menu.addSeparator()
		refresh_action = menu.addAction("Refresh")
		self._apply_shortcut_hint(refresh_action, QKeySequence(QKeySequence.StandardKey.Refresh))
		
		selected = menu.exec(self.tree.viewport().mapToGlobal(position))
		if selected is None:
			return
		if selected == change_action:
			self._select_root()
		elif selected == new_file_action:
			self._create_file(index)
		elif selected == new_folder_action:
			self._create_folder(index)
		elif selected == ren_action:
			self._rename_path(index)
		elif selected == delete_action:
			self._delete_path(index)
		elif selected == refresh_action:
			self._refresh_model()

	def _directory_for_index(self, index):
		if not index or not index.isValid():
			return self._root_path
		path = Path(self.model.filePath(index))
		if self.model.isDir(index):
			return path
		return path.parent

	def _create_file(self, index):
		directory = self._directory_for_index(index)
		name, accepted = QInputDialog.getText(self, "New File", "File name:")
		if not accepted or not name.strip():
			return
		target = directory / name.strip()
		if target.exists():
			QMessageBox.warning(self, "Exists", f"{target} already exists")
			return
		try:
			target.touch()
		except OSError as exc:
			QMessageBox.critical(self, "Create Failed", str(exc))
			return
		self._refresh_model()

	def _create_folder(self, index):
		directory = self._directory_for_index(index)
		name, accepted = QInputDialog.getText(self, "New Folder", "Folder name:")
		if not accepted or not name.strip():
			return
		target = directory / name.strip()
		if target.exists():
			QMessageBox.warning(self, "Exists", f"{target} already exists")
			return
		try:
			target.mkdir(parents=False, exist_ok=False)
		except OSError as exc:
			QMessageBox.critical(self, "Create Failed", str(exc))
			return
		self._refresh_model()

	def _rename_path(self, index):
		if not index or not index.isValid():
			return
		old_path = Path(self.model.filePath(index))
		name, accepted = QInputDialog.getText(self, "Rename", "New name:", text=old_path.name)
		if not accepted or not name.strip() or name.strip() == old_path.name:
			return
		new_path = old_path.parent / name.strip()
		if new_path.exists():
			QMessageBox.warning(self, "Exists", f"{new_path} already exists")
			return
		try:
			old_path.rename(new_path)
		except OSError as exc:
			QMessageBox.critical(self, "Rename Failed", str(exc))
			return
		self._refresh_model()

	def _delete_path(self, index):
		if not index or not index.isValid():
			return
		target = Path(self.model.filePath(index))
		response = QMessageBox.question(
			self,
			"Delete",
			f"Delete {target}?",
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
			QMessageBox.StandardButton.No,
		)
		if response != QMessageBox.StandardButton.Yes:
			return
		try:
			if target.is_dir():
				shutil.rmtree(target)
			else:
				target.unlink()
		except OSError as exc:
			QMessageBox.critical(self, "Delete Failed", str(exc))
			return
		self._refresh_model()

	def _refresh_model(self):
		# QFileSystemModel doesn't expose refresh; reset the root path to reindex
		self.model.setRootPath(str(self._root_path))

	def _show_customization(self):
		"""Open customization dialog."""
		dialog = CustomizationDialog(self.settings, self)
		if dialog.exec() == QDialog.DialogCode.Accepted:
			self._refresh_icons()

	def _refresh_icons(self):
		"""Rebuild icons after settings change."""
		self._icon_provider._build_icons()
		self.model.setIconProvider(self._icon_provider)
		self._refresh_model()
		self.settingsChanged.emit()

	def _register_shortcuts(self):
		self._change_folder_action = QAction("Change Folder…", self)
		self._change_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
		self._change_folder_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
		self._change_folder_action.triggered.connect(self._select_root)
		self.addAction(self._change_folder_action)

		self._new_file_action = QAction("New File…", self)
		self._new_file_action.setShortcut(QKeySequence("Ctrl+Alt+N"))
		self._new_file_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
		self._new_file_action.triggered.connect(lambda: self._create_file(self.tree.currentIndex()))
		self.addAction(self._new_file_action)

		self._new_folder_action = QAction("New Folder…", self)
		self._new_folder_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
		self._new_folder_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
		self._new_folder_action.triggered.connect(lambda: self._create_folder(self.tree.currentIndex()))
		self.addAction(self._new_folder_action)

		self._refresh_action = QAction("Refresh", self)
		self._refresh_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Refresh))
		self._refresh_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
		self._refresh_action.triggered.connect(self._refresh_model)
		self.addAction(self._refresh_action)

	def _apply_shortcut_hint(self, action, sequence):
		if not action or not sequence:
			return
		text = sequence.toString()
		if not text:
			return
		action.setShortcut(sequence)
		if hasattr(action, "setShortcutVisibleInContextMenu"):
			action.setShortcutVisibleInContextMenu(True)

	def _select_root(self):
		dlg = QFileDialog(self, "Select Project Folder", str(self._root_path))
		dlg.setFileMode(QFileDialog.FileMode.Directory)
		dlg.setOption(QFileDialog.Option.ShowDirsOnly, True)
		dlg.setViewMode(QFileDialog.ViewMode.Detail)
		dlg.setOption(QFileDialog.Option.DontUseNativeDialog, True)
		# Increase icon sizes in the internal views of the dialog
		list_view = dlg.findChild(QListView)
		if list_view:
			list_view.setIconSize(QSize(40, 40))
			tree_view = dlg.findChild(QTreeView)
			if tree_view:
				tree_view.setIconSize(QSize(40, 40))
		if dlg.exec():
			selected = dlg.selectedFiles()
			if selected:
				self.set_root_path(Path(selected[0]))

	def set_root_path(self, root_path):
		self._root_path = Path(root_path).resolve()
		self.path_label.setText(str(self._root_path))
		self.model.setRootPath(str(self._root_path))
		root_index = self.model.index(str(self._root_path))
		self.tree.setRootIndex(root_index)

	def root_path(self):
		return self._root_path
