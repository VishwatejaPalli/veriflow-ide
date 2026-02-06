import subprocess
from abc import ABC, abstractmethod

class ToolBase(ABC):
	def __init__(self, name):
		self.name = name

	@abstractmethod
	def build_command(self, *args, **kwargs):
		pass

	def run(self, command):
		try:
			result = subprocess.run(command, shell=True, capture_output=True, text=True)
			return result.stdout, result.stderr, result.returncode
		except Exception as e:
			return "", str(e), -1
