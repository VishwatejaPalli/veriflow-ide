from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem

class DiagnosticsWidget(QTreeWidget):
	diagnosticActivated = Signal(dict)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setObjectName("diagnosticsTree")
		self.setHeaderLabels(["File", "Line", "Type", "Message"])
		self.setAlternatingRowColors(True)
		self.setRootIsDecorated(False)
		self._diagnostics = []
		self.itemActivated.connect(self._handle_item_activated)

	def update_entries(self, diagnostics):
		self.clear()
		self._diagnostics = diagnostics or []
		for diag in self._diagnostics:
			item = QTreeWidgetItem(
				[
					diag.get("file", "<unknown>"),
					str(diag.get("line", "")),
					diag.get("type", ""),
					diag.get("msg", "").strip(),
				]
			)
			item.setData(0, Qt.UserRole, diag)
			self.addTopLevelItem(item)
		if self.topLevelItemCount() > 0:
			self.resizeColumnToContents(0)
			self.resizeColumnToContents(1)

	def _handle_item_activated(self, item):
		if not item:
			return
		diag = item.data(0, Qt.UserRole)
		if diag:
			self.diagnosticActivated.emit(diag)