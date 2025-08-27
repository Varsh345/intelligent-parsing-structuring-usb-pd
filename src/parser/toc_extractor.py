from pathlib import Path
import re
import pdfplumber
import json
from typing import List, Optional, Generator
from dataclasses import dataclass, asdict


@dataclass
class TOCEntry:
    """
    Represents a single TOC section.
    """
    doc_title: str
    section_id: str
    title: str
    page: int
    level: int
    parent_id: Optional[str]
    full_path: str


class PDFReader:
    """
    Reads text lines from a PDF efficiently using pdfplumber.
    """

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path

    def extract_lines(self, start_page: int = 1, end_page: Optional[int] = None) -> Generator[str, None, None]:
        """
        Extract lines of text from the PDF pages.

        Args:
            start_page: 1-based start page.
            end_page: 1-based end page.
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                pages = pdf.pages[start_page - 1:end_page]
                for page in pages:
                    text = page.extract_text() or ""
                    for line in text.split("\n"):
                        line = line.strip()
                        if line:
                            yield line
        except FileNotFoundError:
            print(f"Error: PDF file not found at path {self.pdf_path}")
            return
        except Exception as e:
            print(f"Error reading PDF file: {e}")
            return

class TOCParser:
    """
    Parses PDF lines into structured TOC entries.
    """
    TOC_PATTERN = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+?)\s+(\d+)$", re.UNICODE)

    def __init__(self, doc_title: str):
        self.doc_title = doc_title

    @staticmethod
    def clean_line(line: str) -> str:
        """
        Clean PDF line: remove 'PageXX' artifacts and extra spacing.
        Args:- line: Raw PDF line.
        Returns: Cleaned line.
        """
        line = line.replace("…", " ")
        line = re.sub(r'\s*P\s*a\s*g\s*e\s*\d+', '', line, flags=re.IGNORECASE)
        line = re.sub(r'\s+', ' ', line).strip()
        return line

    @staticmethod
    def clean_title(title: str) -> str:
        """
        Fix garbled titles, remove extra dots/spaces.
        Args: Raw title string.
        Returns: Clean title.
        """
        title = re.sub(r'[\s.]+', ' ', title).strip()
        title = re.sub(r'\b(\w)\s(?=\w\b)', r'\1', title) 
        return title

    def parse_lines(self, lines: List[str]) -> List[TOCEntry]:
        """
        Parse cleaned lines into TOCEntry objects.

        Args: List of PDF text lines.

        Returns: Parsed TOC entries.
        """
        entries: List[TOCEntry] = []

        for line in lines:
            normalized = self.clean_line(line)
            match = self.TOC_PATTERN.match(normalized)
            if not match:
                continue

            section_id, title, page_str = match.groups()
            clean_title = self.clean_title(title)
            parts = section_id.split(".")
            parent_id = ".".join(parts[:-1]) if len(parts) > 1 else None

            entries.append(
                TOCEntry(
                    doc_title=self.doc_title,
                    section_id=section_id,
                    title=clean_title,
                    page=int(page_str),
                    level=len(parts),
                    parent_id=parent_id,
                    full_path=f"{section_id} {clean_title}"
                )
            )

        return entries

def save_jsonl(entries: List[TOCEntry], output_file: Path):
    """
    Save TOC entries as JSONL.

    Args:
        entries: TOC entries.
        output_file: Output file path.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")

if __name__ == "__main__":
    # --- Paths ---
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    PDF_PATH = PROJECT_ROOT / "data" / "USB_PD_R3_2 V1_1_2024_10.pdf"
    OUTPUT_FILE = PROJECT_ROOT / "output" / "usb_pd_toc.jsonl"

    #TOC page range
    TOC_START_PAGE = 13
    TOC_END_PAGE = 26

    #Read only TOC pages
    pdf_reader = PDFReader(PDF_PATH)
    toc_lines = list(pdf_reader.extract_lines(start_page=TOC_START_PAGE, end_page=TOC_END_PAGE))

    #Parse TOC entries
    toc_parser = TOCParser("USB Power Delivery Specification Rev 3.2 V1.1 2024-10")
    toc_entries = toc_parser.parse_lines(toc_lines)

    #Save JSONL
    save_jsonl(toc_entries, OUTPUT_FILE)

