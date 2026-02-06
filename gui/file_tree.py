import shutil
from pathlib import Path

from PySide6.QtCore import QDir, Qt, Signal, QSize
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence, QPainter, QPixmap
from PySide6.QtWidgets import (
	QApplication,
	QFileDialog,
	QFileIconProvider,
	QFileSystemModel,
	QHBoxLayout,
	QInputDialog,
	QLabel,
	QMenu,
	QMessageBox,
	QListView,
	QPushButton,
	QStyle,
	QStyleFactory,
	QTreeView,
	QVBoxLayout,
	QWidget,
)


class ProjectIconProvider(QFileIconProvider):
	"""Custom icons for HDL projects."""

	HDL_EXTENSIONS = {".v", ".sv", ".vh", ".svh", ".vhd", ".vhdl"}
	SCRIPT_EXTENSIONS = {".tcl", ".sh", ".py"}

	def __init__(self):
		super().__init__()
		app = QApplication.instance()
		style = app.style() if isinstance(app, QApplication) else None
		if style is None and hasattr(QStyleFactory, "create"):
			style = QStyleFactory.create("Fusion")
		self._folder_icon = style.standardIcon(QStyle.StandardPixmap.SP_DirIcon) if style else QIcon()
		self._file_icon = style.standardIcon(QStyle.StandardPixmap.SP_FileIcon) if style else QIcon()
		self._hdl_icon = self._build_badge_icon("HD", "#1e3a8a", "#f1f5f9")
		self._script_icon = self._build_badge_icon("SH", "#065f46", "#f1f7f5")

	def icon(self, info):
		if isinstance(info, QFileIconProvider.IconType):
			return self._folder_icon if info == QFileIconProvider.IconType.Folder else self._file_icon
		path = Path(info.filePath()) if info else None
		if not path:
			return self._file_icon
		suffix = path.suffix.lower()
		if suffix in self.HDL_EXTENSIONS:
			return self._hdl_icon
		if suffix in self.SCRIPT_EXTENSIONS:
			return self._script_icon
		return self._folder_icon if info.isDir() else self._file_icon

	def _build_badge_icon(self, label, background, text_color):
		size = 24
		pixmap = QPixmap(size, size)
		pixmap.fill(Qt.GlobalColor.transparent)
		painter = QPainter(pixmap)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setPen(Qt.PenStyle.NoPen)
		painter.setBrush(QColor(background))
		painter.drawRoundedRect(2, 2, size - 4, size - 4, 6, 6)
		painter.setPen(QColor(text_color))
		font = QFont("Fira Code", 9, int(QFont.Weight.Bold))
		painter.setFont(font)
		painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, label)
		painter.end()
		return QIcon(pixmap)


class FileTreeWidget(QWidget):
	"""Simple project browser that emits file selections."""

	fileActivated = Signal(str)

	def __init__(self, root_path=None, parent=None):
		super().__init__(parent)
		self._root_path = Path(root_path or Path.cwd()).resolve()
		self._build_ui()

	def _build_ui(self):
		layout = QVBoxLayout()

		controls = QHBoxLayout()
		self.path_label = QLabel(str(self._root_path))
		self.path_label.setObjectName("fileTreePathLabel")
		change_button = QPushButton("Change…")
		change_button.clicked.connect(self._select_root)
		controls.addWidget(self.path_label)
		controls.addStretch()
		controls.addWidget(change_button)
		layout.addLayout(controls)

		self.model = QFileSystemModel(self)
		self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Files)
		self.model.setRootPath(str(self._root_path))
		self._icon_provider = ProjectIconProvider()
		self.model.setIconProvider(self._icon_provider)

		self.tree = QTreeView(self)
		self.tree.setModel(self.model)
		self.tree.setRootIndex(self.model.index(str(self._root_path)))
		self.tree.setHeaderHidden(True)
		self.tree.setObjectName("projectTree")
		self.tree.setAlternatingRowColors(True)
		# Performance: uniform row heights and no expand/collapse animations
		self.tree.setUniformRowHeights(True)
		self.tree.setAnimated(False)
		self.tree.setExpandsOnDoubleClick(True)
		self.tree.setIconSize(QSize(28, 28))
		self.tree.doubleClicked.connect(self._handle_activated)
		self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.tree.customContextMenuRequested.connect(self._show_context_menu)
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
		self.tree.setRootIndex(self.model.index(str(self._root_path)))

	def root_path(self):
		return self._root_path
