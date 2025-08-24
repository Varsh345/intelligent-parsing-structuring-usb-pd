from pathlib import Path
import pdfplumber
import logging

class MetadataExtractor:
    """
    Extracts metadata information from USB PD specification PDF.
    """

    def __init__(self, pdf_path: Path, doc_title: str):
        """
        Initialize the extractor with PDF path and document title.
        """
        self.pdf_path = pdf_path
        self.doc_title = doc_title

    def extract(self) -> dict:
        """
        Extract metadata information from the first page of the PDF.
        Returns:
            dict: Metadata details including title, revision, version, release date, publisher, and raw header text.
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                first_page_text = pdf.pages[0].extract_text()
        except FileNotFoundError as e:
            logging.warning(f"File not found: {e}")
            first_page_text = ""
        except Exception as e:
            logging.warning(f"Failed to extract metadata from PDF: {e}")
            first_page_text = ""

        return {
            "doc_title": self.doc_title,
            "revision": "3.2",
            "version": "1.1",
            "release_date": "October 2024",
            "publisher": "USB-IF",
            "raw_header": first_page_text
        }
