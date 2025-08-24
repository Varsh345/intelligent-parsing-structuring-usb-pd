import unittest
from pathlib import Path
from src.parser.metadata_extractor import MetadataExtractor

class TestMetadataExtractor(unittest.TestCase):

    def setUp(self):
        self.pdf_path = Path("data/USB_PD_R3_2 V1_1_2024_10.pdf")
        self.doc_title = "USB PD Spec Test"

    def test_extract_returns_expected_keys(self):
        extractor = MetadataExtractor(self.pdf_path, self.doc_title)
        metadata = extractor.extract()
        expected_keys = {
            "doc_title", "revision", "version", "release_date", "publisher", "raw_header"
        }
        self.assertTrue(expected_keys.issubset(metadata.keys()))
        self.assertEqual(metadata["doc_title"], self.doc_title)

    def test_extract_handles_missing_file(self):
        fake_path = Path("data/non_existent.pdf")
        extractor = MetadataExtractor(fake_path, self.doc_title)
        metadata = extractor.extract()
        self.assertEqual(metadata["raw_header"], "")

if __name__ == "__main__":
    unittest.main()
