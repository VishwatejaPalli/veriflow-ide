import shlex
from pathlib import Path

from tools.tool_base import ToolBase


class OpenLaneTool(ToolBase):
	"""OpenLane ASIC flow tool."""
	
	def __init__(self):
		super().__init__("flow.tcl")
	
	def build_command(self, design_dir, design_name, config_file=None, tag=None, 
	                  interactive=False, extra_args=None):
		"""Build OpenLane flow command.
		
		Args:
			design_dir: Directory containing the design
			design_name: Name of the design
			config_file: Optional custom config.json file
			tag: Run tag for organizing outputs
			interactive: Whether to run in interactive mode
			extra_args: Additional command-line arguments
		"""
		cmd_parts = ["flow.tcl"]
		
		cmd_parts.append(f"-design {shlex.quote(design_name)}")
		
		if config_file:
			cmd_parts.append(f"-config_file {shlex.quote(config_file)}")
		
		if tag:
			cmd_parts.append(f"-tag {shlex.quote(tag)}")
		
		if interactive:
			cmd_parts.append("-interactive")
		
		if extra_args:
			cmd_parts.extend(extra_args)
		
		return " ".join(cmd_parts)


class OpenROADTool(ToolBase):
	"""OpenROAD place and route tool."""
	
	def __init__(self):
		super().__init__("openroad")
	
	def build_command(self, script_file=None, interactive=False, 
	                  log_file=None, extra_args=None):
		"""Build OpenROAD command.
		
		Args:
			script_file: TCL script to execute
			interactive: Whether to run in interactive mode
			log_file: Path to log file
			extra_args: Additional command-line arguments
		"""
		cmd_parts = ["openroad"]
		
		if log_file:
			cmd_parts.append(f"-log {shlex.quote(log_file)}")
		
		if extra_args:
			cmd_parts.extend(extra_args)
		
		if script_file and not interactive:
			cmd_parts.append(shlex.quote(script_file))
		elif not interactive:
			cmd_parts.append("-exit")
		
		return " ".join(cmd_parts)
