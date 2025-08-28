import unittest
from pathlib import Path
from src.parser.toc_extractor import TOCParser, TOCEntry, PDFReader, save_jsonl


class TestTOCExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = TOCParser(doc_title="Test Document")

    def test_toc_entry_creation(self):
        """Check that a TOCEntry object stores values correctly."""
        entry = TOCEntry(
            doc_title="Test Document",
            section_id="1.0",
            title="Introduction",
            page=1,
            level=1,
            parent_id=None,
            full_path="1.0 Introduction",
        )

        self.assertEqual(entry.section_id, "1.0")
        self.assertEqual(entry.title, "Introduction")
        self.assertEqual(entry.page, 1)
        self.assertEqual(entry.level, 1)
        self.assertIsNone(entry.parent_id)
        self.assertEqual(entry.full_path, "1.0 Introduction")

    def test_save_jsonl(self):
        """Ensure save_jsonl writes entries to a JSONL file correctly."""
        test_file = Path("test_output.jsonl")
        entries = [
            TOCEntry(
                doc_title="Test Document",
                section_id="1.0",
                title="Introduction",
                page=1,
                level=1,
                parent_id=None,
                full_path="1.0 Introduction",
            ),
            TOCEntry(
                doc_title="Test Document",
                section_id="2.0",
                title="Background",
                page=2,
                level=1,
                parent_id=None,
                full_path="2.0 Background",
            ),
        ]

        save_jsonl(entries, test_file)

        # Read file back and check line count
        with open(test_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 2)
        self.assertIn("Introduction", lines[0])
        self.assertIn("Background", lines[1])
        test_file.unlink(missing_ok=True)

if __name__ == "__main__":
    unittest.main()
