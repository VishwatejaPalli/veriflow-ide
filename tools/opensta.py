import shlex

from tools.tool_base import ToolBase


class OpenSTATool(ToolBase):
	"""OpenSTA static timing analysis tool."""
	
	def __init__(self):
		super().__init__("sta")
	
	def build_command(self, script_file=None, exit_after=True, 
	                  no_init=False, extra_args=None):
		"""Build OpenSTA command.
		
		Args:
			script_file: TCL script to execute
			exit_after: Exit after running script
			no_init: Don't read .sta init file
			extra_args: Additional command-line arguments
		"""
		cmd_parts = ["sta"]
		
		if no_init:
			cmd_parts.append("-no_init")
		
		if exit_after and script_file:
			cmd_parts.append("-exit")
		
		if extra_args:
			cmd_parts.extend(extra_args)
		
		if script_file:
			cmd_parts.append(shlex.quote(script_file))
		
		return " ".join(cmd_parts)
