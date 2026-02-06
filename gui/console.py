from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QHBoxLayout, QTextEdit, QToolButton, QVBoxLayout, QWidget, QStyle

class ConsoleWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		layout = QVBoxLayout()
		controls = QHBoxLayout()
		controls.addStretch()
		self.clear_button = QToolButton(self)
		self.clear_button.setObjectName("consoleClearButton")
		self.clear_button.setText("Clear")
		self.clear_button.setToolTip("Clear console output")
		style = self.style() or QApplication.style()
		if style:
			self.clear_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
		self.clear_button.clicked.connect(self.clear)
		controls.addWidget(self.clear_button)
		layout.addLayout(controls)

		self.console = QTextEdit()
		self.console.setReadOnly(True)
		self.console.setObjectName("consoleText")
		self.console.setFont(QFont("Fira Code", 11))
		layout.addWidget(self.console)
		self.setLayout(layout)

	def append_text(self, text):
		self.console.append(text)

	def clear(self):
		self.console.clear()
