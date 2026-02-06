import os
import shutil
import tempfile
import unittest

from tools.iverilog import IverilogTool
from tools.yosys import YosysTool
from tools.vvp import VvpTool
from tools.gtkwave import GtkWaveTool


class ToolCommandTests(unittest.TestCase):
	def setUp(self):
		self.iverilog = IverilogTool()
		self.yosys = YosysTool()
		self.vvp = VvpTool()
		self.gtkwave = GtkWaveTool()

	def test_iverilog_build_command(self):
		cmd = self.iverilog.build_command(["top.v", "tb.v"], "sim.out")
		self.assertEqual(cmd, "iverilog -o sim.out top.v tb.v")

	def test_yosys_build_command(self):
		cmd = self.yosys.build_command("synth.ys")
		self.assertEqual(cmd, "yosys -s synth.ys")

	def test_vvp_build_command(self):
		cmd = self.vvp.build_command("sim.out")
		self.assertEqual(cmd, "vvp sim.out")

	def test_gtkwave_build_command(self):
		cmd = self.gtkwave.build_command("waves.vcd")
		self.assertEqual(cmd, "gtkwave waves.vcd")

	def test_tool_run_executes_shell_command(self):
		stdout, stderr, code = self.iverilog.run("printf 'hello'")
		self.assertEqual(code, 0)
		self.assertIn("hello", stdout)
		self.assertEqual(stderr, "")


class IntegrationFlowTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		missing = [tool for tool in ("iverilog", "vvp") if shutil.which(tool) is None]
		if missing:
			raise unittest.SkipTest(f"Missing required tools: {missing}")
		cls.iverilog = IverilogTool()
		cls.vvp = VvpTool()

	def test_iverilog_to_vvp_flow(self):
		verilog_source = """
module top;
	initial begin
		$display("Integration OK");
		$finish;
	end
endmodule
""".strip()
		with tempfile.TemporaryDirectory() as tmp:
			source_file = os.path.join(tmp, "top.v")
			output_file = os.path.join(tmp, "sim.out")
			with open(source_file, "w", encoding="utf-8") as f:
				f.write(verilog_source)
			compile_cmd = self.iverilog.build_command([source_file], output_file)
			stdout, stderr, code = self.iverilog.run(compile_cmd)
			self.assertEqual(code, 0, msg=f"iverilog stderr: {stderr}")
			run_cmd = self.vvp.build_command(output_file)
			stdout, stderr, code = self.vvp.run(run_cmd)
			self.assertEqual(code, 0, msg=f"vvp stderr: {stderr}")
			self.assertIn("Integration OK", stdout)
