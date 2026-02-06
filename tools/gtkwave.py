import shlex
import subprocess

from tools.tool_base import ToolBase

class GtkWaveTool(ToolBase):
	def __init__(self):
		super().__init__("gtkwave")

	def build_command(self, vcd_file):
		return f"gtkwave {shlex.quote(vcd_file)}"

	def launch_viewer(self, vcd_file):
		subprocess.Popen(["gtkwave", vcd_file])
