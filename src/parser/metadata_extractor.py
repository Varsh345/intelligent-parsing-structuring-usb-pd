from pathlib import Path
import pdfplumber
import logging
import re

class MetadataExtractor:
    """
    Extracts metadata information from the first page of a USB_PD_specification PDF.
    Attributes:
        pdf_path (Path): Path to the PDF file.
        doc_title (str): Title of the document.
    """

    REQUIRED_FIELDS = ["doc_title", "revision", "version", "release_date", "publisher", "raw_header"]

    def __init__(self, pdf_path: Path, doc_title: str):
        """
        Initialize the extractor with PDF path and document title.
        Arguments:
            pdf_path (Path): The path to the PDF file.
            doc_title (str): The title of the document.
        """
        self.pdf_path = pdf_path
        self.doc_title = doc_title

        # Configure logger
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    def extract(self) -> dict:
        """
        Extract metadata information from the first page of the PDF.
        Returns:
            dict: Metadata details including title, revision, version,
                  release date, publisher, and raw header text.
        """
        first_page_text = ""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                if pdf.pages:
                    first_page_text = pdf.pages[0].extract_text() or ""
                else:
                    logging.warning("PDF has no pages to extract metadata from.")
        except FileNotFoundError as e:
            logging.error(f"File not found: {self.pdf_path} - {e}")
            return {
                "doc_title": self.doc_title,
                "revision": "Unknown",
                "version": "Unknown",
                "release_date": "Unknown",
                "publisher": "USB-IF",
                "raw_header": ""
            }

        except Exception as e:
            logging.error(f"Unexpected error extracting metadata: {e}")
            return {}

        # Extract metadata dynamically using regex
        revision = self._find_pattern(first_page_text, r"Revision\s*([\d.]+)", default="Unknown")
        version = self._find_pattern(first_page_text, r"Version\s*([\d.]+)", default="Unknown")
        release_date = self._find_pattern(first_page_text, r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}", default="Unknown")

        metadata = {
            "doc_title": self.doc_title,
            "revision": revision,
            "version": version,
            "release_date": release_date,
            "publisher": "USB-IF",
            "raw_header": first_page_text.strip()
        }

        # Validate schema
        self._validate_metadata(metadata)

        return metadata

    def _find_pattern(self, text: str, pattern: str, default: str = "Unknown") -> str:
        """Utility to find regex pattern in text, returns default if not found."""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else default

    def _validate_metadata(self, metadata: dict) -> None:
        """Ensure all required fields exist in metadata."""
        missing = [field for field in self.REQUIRED_FIELDS if field not in metadata or not metadata[field]]
        if missing:
            logging.warning(f"Metadata is missing fields: {missing}")
