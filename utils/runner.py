import subprocess

from PySide6.QtCore import QObject, Signal


class CommandRunner(QObject):
	output = Signal(str)
	finished = Signal(int)

	def __init__(self, command: str):
		super().__init__()
		self.command = command

	def run(self):
		try:
			process = subprocess.Popen(
				self.command,
				shell=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True,
			)  # noqa: S602 (command built via trusted UI)
			for line in process.stdout or []:
				self.output.emit(line.rstrip())
			process.wait()
			self.finished.emit(process.returncode)
		except Exception as exc:  # pragma: no cover - safety path
			self.output.emit(f"Command failed: {exc}")
			self.finished.emit(-1)
