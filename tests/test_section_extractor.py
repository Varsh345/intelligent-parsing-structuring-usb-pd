import unittest
from pathlib import Path
from src.parser.section_extractor import USBPDSpecExtractor  # adjust import if needed


class TestUSBPDSpecExtractor(unittest.TestCase):
    """Simple tests for USBPDSpecExtractor."""

    def setUp(self):
        self.extractor = USBPDSpecExtractor(
            pdf_path=Path("dummy.pdf"),
            toc_file=Path("dummy_toc.jsonl"),
            output_file=Path("dummy_out.jsonl"),
            tag_map={
                "contracts": ["contract", "negotiation"],
                "charging": ["charge", "battery"]
            }
        )

    def test_clean_title(self):
        """clean_title should strip dots and extra spaces."""
        dirty_title = "Section 1 .....   Introduction   "
        result = self.extractor.clean_title(dirty_title)
        self.assertEqual(result, "Section 1 Introduction")

    def test_assign_tags(self):
        """assign_tags should map words in text to categories."""
        text = "This contract explains how battery charging works."
        tags = self.extractor.assign_tags(text)
        self.assertIn("contracts", tags)
        self.assertIn("charging", tags)


if __name__ == "__main__":
    unittest.main(verbosity=2)
