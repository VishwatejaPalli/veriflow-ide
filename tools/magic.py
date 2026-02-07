import shlex

from tools.tool_base import ToolBase


class MagicTool(ToolBase):
	"""Magic VLSI layout tool."""
	
	def __init__(self):
		super().__init__("magic")
	
	def build_command(self, layout_file=None, tech_file=None, script=None, 
	                  noconsole=False, dnull=False, extra_args=None):
		"""Build Magic command.
		
		Args:
			layout_file: Layout file to open (.mag, .gds, .def)
			tech_file: Technology file
			script: TCL script to run
			noconsole: Run without console
			dnull: Use null display (batch mode)
			extra_args: Additional command-line arguments
		"""
		cmd_parts = ["magic"]
		
		if dnull:
			cmd_parts.append("-dnull")
		
		if noconsole:
			cmd_parts.append("-noconsole")
		
		if tech_file:
			cmd_parts.extend(["-T", shlex.quote(tech_file)])
		
		if script:
			cmd_parts.append(shlex.quote(script))
		
		if extra_args:
			cmd_parts.extend(extra_args)
		
		if layout_file:
			cmd_parts.append(shlex.quote(layout_file))
		
		return " ".join(cmd_parts)


class NetgenTool(ToolBase):
	"""Netgen LVS tool."""
	
	def __init__(self):
		super().__init__("netgen")
	
	def build_command(self, circuit1, circuit2, setup_file, 
	                  output_file=None, batch=True, extra_args=None):
		"""Build Netgen LVS command.
		
		Args:
			circuit1: First circuit netlist
			circuit2: Second circuit netlist  
			setup_file: Netgen setup file
			output_file: Output comparison file
			batch: Run in batch mode
			extra_args: Additional command-line arguments
		"""
		cmd_parts = ["netgen"]
		
		if batch:
			cmd_parts.append("-batch")
		
		cmd_parts.append("lvs")
		cmd_parts.append(shlex.quote(circuit1))
		cmd_parts.append(shlex.quote(circuit2))
		cmd_parts.append(shlex.quote(setup_file))
		
		if output_file:
			cmd_parts.append(shlex.quote(output_file))
		
		if extra_args:
			cmd_parts.extend(extra_args)
		
		return " ".join(cmd_parts)
