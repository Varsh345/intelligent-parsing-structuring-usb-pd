import unittest
from pathlib import Path
from src.parser.toc_extractor import TOCExtractor

class TestTOCExtractor(unittest.TestCase):

    def setUp(self):
        # Update this path to match your actual test PDF location
        self.pdf_path = Path("data/USB_PD_R3_2 V1_1_2024_10.pdf")
        self.doc_title = "USB PD Specification Test"
        self.extractor = TOCExtractor(self.pdf_path, self.doc_title)

    def test_extract_returns_entries(self):
        start_page = 13
        end_page = 18
        
        toc_entries = self.extractor.extract(start_page, end_page)

        # Ensuring some TOC entries are returned
        self.assertGreater(len(toc_entries), 0)

        # Checks the first entry structure
        first_entry = toc_entries[0]
        self.assertIn("section_id", first_entry)
        self.assertIn("title", first_entry)
        self.assertIn("page", first_entry)
        self.assertIn("level", first_entry)
        self.assertIn("parent_id", first_entry)
        self.assertIn("full_path", first_entry)
        self.assertEqual(first_entry["doc_title"], self.doc_title)

        # Validate types
        self.assertIsInstance(first_entry["section_id"], str)
        self.assertIsInstance(first_entry["title"], str)
        self.assertIsInstance(first_entry["page"], int)
        self.assertIsInstance(first_entry["level"], int)

if __name__ == "__main__":
    unittest.main()
