import shlex

from tools.tool_base import ToolBase

class YosysTool(ToolBase):
	def __init__(self):
		super().__init__("yosys")

	def build_command(self, script):
		return f"yosys -s {shlex.quote(script)}"
