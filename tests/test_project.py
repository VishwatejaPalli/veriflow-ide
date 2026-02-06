import json
import os
import tempfile
import unittest

from project.manager import ProjectManager


class ProjectManagerTests(unittest.TestCase):
    def test_add_file_and_persist(self):
        with tempfile.TemporaryDirectory() as tmp:
            pm = ProjectManager(tmp)
            pm.load()
            pm.add_file("rtl/top.v")
            pm.set_top_module("top")

            self.assertIn("rtl/top.v", pm.data["files"])
            self.assertEqual(pm.data["top_module"], "top")

            reloaded = ProjectManager(tmp)
            reloaded.load()
            self.assertIn("rtl/top.v", reloaded.data["files"])
            self.assertEqual(reloaded.data["top_module"], "top")

    def test_load_missing_file_initializes_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            pm = ProjectManager(tmp)
            pm.load()
            self.assertEqual(pm.data, {})


if __name__ == "__main__":
    unittest.main()
