import unittest
import sys
from pathlib import Path
import logging
from src.parser.metadata_extractor import MetadataExtractor

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

class TestMetadataExtractor(unittest.TestCase):
    """Simple unit tests for MetadataExtractor class."""

    def setUp(self):
        test_data_dir = Path(__file__).resolve().parent.parent / "data"
        self.existing_pdf_path = test_data_dir / "USB_PD_R3_2 V1_1_2024_10.pdf"
        self.nonexistent_pdf_path = test_data_dir / "non_existent.pdf"
        self.doc_title = "USB PD Spec Test"

    def test_extract_with_missing_file(self):
        """If PDF does not exist, defaults should be returned."""
        # Temporarily suppress error logging
        logging.disable(logging.ERROR)

        extractor = MetadataExtractor(self.nonexistent_pdf_path, self.doc_title)
        metadata = extractor.extract()

        # Re-enable logging
        logging.disable(logging.NOTSET)

        self.assertEqual(metadata["doc_title"], self.doc_title)
        self.assertEqual(metadata["raw_header"], "")
        self.assertEqual(metadata["publisher"], "USB-IF")
        self.assertEqual(metadata["revision"], "Unknown")

    def test_find_pattern(self):
        """_find_pattern should return correct match or default."""

        # Skip this test if the actual PDF is missing
        if not self.existing_pdf_path.is_file():
            self.skipTest(f"Required PDF not found: {self.existing_pdf_path}")

        text = "Revision: 1.2\nVersion: 3.4\nRelease Date: 2024-10-01"
        extractor = MetadataExtractor(self.existing_pdf_path, self.doc_title)

        self.assertEqual(extractor._find_pattern(text, r"Revision\s*:?\s*([\d.]+)"), "1.2")
        self.assertEqual(extractor._find_pattern(text, r"Version\s*:?\s*([\d.]+)"), "3.4")
        self.assertEqual(extractor._find_pattern(text, r"Release\s*Date\s*:?\s*([\d\-]+)"), "2024-10-01")
        self.assertEqual(extractor._find_pattern(text, r"Nonexistent\s*:?\s*(\w+)"), "Unknown")


if __name__ == "__main__":
    unittest.main(verbosity=2)
