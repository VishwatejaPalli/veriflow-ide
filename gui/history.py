from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem


class RunHistoryWidget(QTreeWidget):
	rerunRequested = Signal(str, str, dict)  # command, description, metadata

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setObjectName("historyTree")
		self.setHeaderLabels(["Started", "Task", "Status"])
		self.setAlternatingRowColors(True)
		self.setRootIsDecorated(False)
		self.itemActivated.connect(self._handle_activated)

	def add_entry(self, description, command, metadata=None):
		timestamp = datetime.now().strftime("%H:%M:%S")
		item = QTreeWidgetItem([timestamp, description, "Running…"])
		item.setData(
			0,
			Qt.UserRole,
			{"command": command, "description": description, "metadata": metadata or {}},
		)
		self.addTopLevelItem(item)
		self.scrollToItem(item)
		return item

	def mark_completed(self, item, exit_code):
		if item is None:
			return
		status = "Success" if exit_code == 0 else f"Failed ({exit_code})"
		item.setText(2, status)

	def _handle_activated(self, item):
		if not item:
			return
		payload = item.data(0, Qt.UserRole)
		if payload:
			self.rerunRequested.emit(
				payload["command"], payload["description"], payload.get("metadata", {})
			)
