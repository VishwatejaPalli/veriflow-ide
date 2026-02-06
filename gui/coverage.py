from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit


class CoverageWidget(QPlainTextEdit):
	"""Simple viewer for verilator_coverage summaries."""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setReadOnly(True)
		self.setObjectName("coveragePane")
		font = QFont("Fira Code", 11)
		font.setStyleHint(QFont.Monospace)
		self.setFont(font)
		self.setPlaceholderText(
			"Run verilator_coverage with an info file to see summary output here."
		)

	def show_summary(self, info_path, contents):
		path = Path(info_path)
		header = f"Summary from {path}\n{'=' * (12 + len(path.name))}\n\n"
		self.setPlainText(header + contents)

	def show_message(self, message):
		self.setPlainText(message)
