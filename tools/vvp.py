import shlex

from tools.tool_base import ToolBase

class VvpTool(ToolBase):
	def __init__(self):
		super().__init__("vvp")

	def build_command(self, output):
		return f"vvp {shlex.quote(output)}"
