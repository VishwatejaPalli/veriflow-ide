import shlex

from tools.tool_base import ToolBase


class KLayoutTool(ToolBase):
	"""KLayout layout viewer and editor."""
	
	def __init__(self):
		super().__init__("klayout")
	
	def build_command(self, layout_file=None, tech_file=None, layer_props=None,
	                  script=None, batch=False, extra_args=None):
		"""Build KLayout command.
		
		Args:
			layout_file: Layout file to open (.gds, .oas, .dxf, etc.)
			tech_file: Technology file (.lyt)
			layer_props: Layer properties file (.lyp)
			script: Ruby/Python script to execute
			batch: Run in batch mode (no GUI)
			extra_args: Additional command-line arguments
		"""
		cmd_parts = ["klayout"]
		
		if batch:
			cmd_parts.append("-b")
		
		if tech_file:
			cmd_parts.extend(["-nn", shlex.quote(tech_file)])
		
		if layer_props:
			cmd_parts.extend(["-l", shlex.quote(layer_props)])
		
		if script:
			cmd_parts.extend(["-r", shlex.quote(script)])
		
		if extra_args:
			cmd_parts.extend(extra_args)
		
		if layout_file:
			cmd_parts.append(shlex.quote(layout_file))
		
		return " ".join(cmd_parts)


class KLayoutDRCTool(ToolBase):
	"""KLayout DRC checking."""
	
	def __init__(self):
		super().__init__("klayout")
	
	def build_command(self, layout_file, drc_script, output_file=None, 
	                  report_file=None, extra_args=None):
		"""Build KLayout DRC command.
		
		Args:
			layout_file: Layout file to check
			drc_script: DRC rule script
			output_file: Output layout with markers
			report_file: DRC report file
			extra_args: Additional command-line arguments
		"""
		cmd_parts = ["klayout", "-b"]
		
		cmd_parts.extend(["-r", shlex.quote(drc_script)])
		
		if report_file:
			cmd_parts.extend(["-rd", f"report={shlex.quote(report_file)}"])
		
		if output_file:
			cmd_parts.extend(["-rd", f"target={shlex.quote(output_file)}"])
		
		if extra_args:
			cmd_parts.extend(extra_args)
		
		cmd_parts.append(shlex.quote(layout_file))
		
		return " ".join(cmd_parts)
