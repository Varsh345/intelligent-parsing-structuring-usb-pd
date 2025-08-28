import unittest
import json
from pathlib import Path
import tempfile
from src.validator.section_validator import SectionValidator


class TestSectionValidator(unittest.TestCase):
    def setUp(self):
        """Create a temporary folder and files for each test."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.toc_file = Path(self.tmpdir.name) / "toc.jsonl"
        self.spec_file = Path(self.tmpdir.name) / "spec.jsonl"
        self.output_file = Path(self.tmpdir.name) / "report.xlsx"

    def tearDown(self):
        """Remove temporary files."""
        self.tmpdir.cleanup()

    def test_validate_fails_with_empty_files(self):
        """If files are empty, validate() should return False."""
        self.toc_file.write_text("")   # empty file
        self.spec_file.write_text("")  # empty file
        validator = SectionValidator(self.toc_file, self.spec_file, self.output_file)
        self.assertFalse(validator.validate())

    def test_validate_passes_with_data(self):
        """If files have valid JSONL, validate() should return True."""
        self.toc_file.write_text(json.dumps({"section_id": "1.0", "title": "Intro"}) + "\n")
        self.spec_file.write_text(json.dumps({"section_id": "1.0", "title": "Intro"}) + "\n")
        validator = SectionValidator(self.toc_file, self.spec_file, self.output_file)
        self.assertTrue(validator.validate())


if __name__ == "__main__":
    unittest.main()
