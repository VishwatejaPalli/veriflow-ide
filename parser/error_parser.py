import re

class ErrorParser:
	error_pattern = re.compile(r"(?P<file>\S+):(?P<line>\d+):(?P<type>error|warning):(?P<msg>.+)")

	@staticmethod
	def parse(output):
		errors = []
		for line in output.splitlines():
			match = ErrorParser.error_pattern.match(line)
			if match:
				errors.append(match.groupdict())
		return errors
