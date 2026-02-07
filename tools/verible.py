import shlex

from tools.tool_base import ToolBase


class VeribleLintTool(ToolBase):
	"""Verible SystemVerilog linter."""
	
	def __init__(self):
		super().__init__("verible-verilog-lint")
	
	def build_command(self, sources, rules=None, waiver_files=None, extra_args=None):
		"""Build verible-verilog-lint command.
		
		Args:
			sources: List of source files to lint
			rules: List of rule configurations (e.g., "line-length=120")
			waiver_files: List of waiver configuration files
			extra_args: Additional command-line arguments
		"""
		cmd_parts = ["verible-verilog-lint"]
		
		if rules:
			for rule in rules:
				cmd_parts.append(f"--rules={shlex.quote(rule)}")
		
		if waiver_files:
			for waiver in waiver_files:
				cmd_parts.append(f"--waiver_files={shlex.quote(waiver)}")
		
		if extra_args:
			cmd_parts.extend(extra_args)
		
		for source in sources:
			cmd_parts.append(shlex.quote(source))
		
		return " ".join(cmd_parts)


class VeribleFormatTool(ToolBase):
	"""Verible SystemVerilog formatter."""
	
	def __init__(self):
		super().__init__("verible-verilog-format")
	
	def build_command(self, sources, inplace=False, column_limit=100, 
	                  indentation_spaces=2, extra_args=None):
		"""Build verible-verilog-format command.
		
		Args:
			sources: List of source files to format
			inplace: Whether to modify files in-place
			column_limit: Maximum column width
			indentation_spaces: Number of spaces per indent level
			extra_args: Additional command-line arguments
		"""
		cmd_parts = ["verible-verilog-format"]
		
		if inplace:
			cmd_parts.append("--inplace")
		
		cmd_parts.append(f"--column_limit={column_limit}")
		cmd_parts.append(f"--indentation_spaces={indentation_spaces}")
		
		if extra_args:
			cmd_parts.extend(extra_args)
		
		for source in sources:
			cmd_parts.append(shlex.quote(source))
		
		return " ".join(cmd_parts)
