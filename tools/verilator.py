import shlex
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
	project_root = Path(__file__).resolve().parents[1]
	if str(project_root) not in sys.path:
		sys.path.insert(0, str(project_root))

from tools.tool_base import ToolBase


class VerilatorLintTool(ToolBase):
	def __init__(self):
		super().__init__("verilator")

	def build_command(self, sources, top_module=None, extra_args=None):
		args = ["verilator", "--lint-only"]
		extra_args = extra_args or []
		if not any(flag in ("--timing", "--no-timing") for flag in extra_args):
			args.append("--timing")
		if top_module:
			args += ["--top-module", top_module]
		if extra_args:
			args.extend(extra_args)
		args.extend(sources)
		return " ".join(shlex.quote(arg) for arg in args)

class VerilatorCoverageTool(ToolBase):
	def __init__(self):
		super().__init__("verilator_coverage")

	def build_command(self, data_file, annotate_dir=None, info_output=None):
		if not data_file:
			raise ValueError("Coverage data file is required")
		args = ["verilator_coverage"]
		if annotate_dir:
			args += ["--annotate", annotate_dir]
		if info_output:
			args += ["--write-info", info_output]
		args.append(data_file)
		return " ".join(shlex.quote(arg) for arg in args)
