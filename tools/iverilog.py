import shlex
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:  # script run directly
	project_root = Path(__file__).resolve().parents[1]
	if str(project_root) not in sys.path:
		sys.path.insert(0, str(project_root))

from tools.tool_base import ToolBase

class IverilogTool(ToolBase):
	def __init__(self):
		super().__init__("iverilog")

	def build_command(self, sources, output):
		quoted_sources = " ".join(shlex.quote(path) for path in sources)
		return f"iverilog -o {shlex.quote(output)} {quoted_sources}"
