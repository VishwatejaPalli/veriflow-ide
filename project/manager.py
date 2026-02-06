import json
import os

class ProjectManager:
	def __init__(self, project_path):
		self.project_path = project_path
		self.project_file = os.path.join(project_path, "project.json")
		self.data = {}

	def load(self):
		if os.path.exists(self.project_file):
			with open(self.project_file, "r") as f:
				self.data = json.load(f)
		else:
			self.data = {}

	def save(self):
		with open(self.project_file, "w") as f:
			json.dump(self.data, f, indent=4)

	def set_top_module(self, module_name):
		self.data["top_module"] = module_name
		self.save()

	def add_file(self, file_path):
		if "files" not in self.data:
			self.data["files"] = []
		if file_path not in self.data["files"]:
			self.data["files"].append(file_path)
		self.save()
