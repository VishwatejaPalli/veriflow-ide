import unittest

from parser.error_parser import ErrorParser


class ErrorParserTests(unittest.TestCase):
    def test_parse_errors_and_warnings(self):
        sample_output = """
rtl/top.v:10:error:Undefined signal
rtl/top.v:22:warning:Unused wire
""".strip()
        errors = ErrorParser.parse(sample_output)
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]["file"], "rtl/top.v")
        self.assertEqual(errors[0]["line"], "10")
        self.assertEqual(errors[0]["type"], "error")
        self.assertIn("Undefined", errors[0]["msg"])
        self.assertEqual(errors[1]["type"], "warning")

    def test_parse_ignores_irrelevant_lines(self):
        sample_output = "Compilation started...\nDone"
        errors = ErrorParser.parse(sample_output)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
