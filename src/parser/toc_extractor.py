from pathlib import Path
import re
import pdfplumber


class TOCExtractor:
    """
    Extracts and parses the Table of Contents (TOC) from a USB PD specification PDF.

    Attributes:
        pdf_path (Path): Path to the PDF file.
        doc_title (str): Document title for the TOC entries.
    """

    TOC_PATTERN = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+?)\s+(\d+)$")

    def __init__(self, pdf_path: Path, doc_title: str):
        self.pdf_path = pdf_path
        self.doc_title = doc_title

    def extract(self, start_page: int, end_page: int):
        """
        Extracts TOC entries as a list of dictionaries, each representing a TOC record.

        Args:
            start_page (int): 1-based first page number of the TOC in the PDF.
            end_page (int): 1-based last page number of the TOC.

        Returns:
            List[dict]: List of TOC entry dicts with keys:
                        'doc_title', 'section_id', 'title', 'page', 
                        'level', 'parent_id', 'full_path'.
        """
        toc_lines = self._extract_text_lines(start_page, end_page)
        toc_entries = self._parse_toc_lines(toc_lines)
        return toc_entries

    def _extract_text_lines(self, start_page: int, end_page: int):
        """Extract non-empty text lines from specified PDF pages."""
        lines = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(start_page - 1, end_page):
                page_text = pdf.pages[page_num].extract_text() or ""
                page_lines = [line.strip() for line in page_text.split("\n") if line.strip()]
                lines.extend(page_lines)
        return lines

    def _parse_toc_lines(self, lines):
        """Parse TOC lines using regex pattern and return structured entries."""
        entries = []
        for line in lines:
            #Replace dots with space for consistent parsing
            normalized_line = line.replace("…", " ")
            match = self.TOC_PATTERN.match(normalized_line)
            if match:
                section_id, title, page_str = match.groups()
                #Clean up trailing dots in title
                clean_title = re.sub(r"\.{2,}", "", title).strip()
                entry = {
                    "doc_title": self.doc_title,
                    "section_id": section_id,
                    "title": clean_title,
                    "page": int(page_str),
                    "level": section_id.count(".") + 1,
                    "parent_id": (
                        ".".join(section_id.split(".")[:-1]) if "." in section_id else None
                    ),
                    "full_path": f"{section_id} {clean_title}",
                }
                entries.append(entry)
        return entries
