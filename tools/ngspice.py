import shlex

from tools.tool_base import ToolBase


class NgSpiceTool(ToolBase):
	"""NgSpice circuit simulator."""
	
	def __init__(self):
		super().__init__("ngspice")
	
	def build_command(self, netlist_file=None, batch=False, interactive=False,
	                  output_file=None, raw_file=None, extra_args=None):
		"""Build NgSpice command.
		
		Args:
			netlist_file: SPICE netlist file
			batch: Run in batch mode
			interactive: Run in interactive mode (with GUI)
			output_file: Output log file
			raw_file: Raw output data file
			extra_args: Additional command-line arguments
		"""
		cmd_parts = ["ngspice"]
		
		if batch:
			cmd_parts.append("-b")
		
		if output_file:
			cmd_parts.extend(["-o", shlex.quote(output_file)])
		
		if raw_file:
			cmd_parts.extend(["-r", shlex.quote(raw_file)])
		
		if extra_args:
			cmd_parts.extend(extra_args)
		
		if netlist_file:
			cmd_parts.append(shlex.quote(netlist_file))
		
		return " ".join(cmd_parts)
