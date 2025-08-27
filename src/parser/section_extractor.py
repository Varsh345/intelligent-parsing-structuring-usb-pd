import pdfplumber
import json
import re
from pathlib import Path
from typing import List, Dict, Optional


class USBPDSpecExtractor:
    """
    Extracts sections from a USB PD specification PDF based on TOC entries,
    cleans titles, assigns tags, and saves structured JSONL output.
    """

    def __init__(self, pdf_path: Path, toc_file: Path, output_file: Path, tag_map: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the extractor.

        Args:
            pdf_path (Path): Path to USB PD PDF.
            toc_file (Path): Path to TOC JSONL.
            output_file (Path): Path for saving extracted sections JSONL.
            tag_map (Optional[Dict[str, List[str]]]): Mapping of semantic tags to keywords.
        """
        self.pdf_path = pdf_path
        self.toc_file = toc_file
        self.output_file = output_file
        self.tag_map = tag_map or {}

        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_toc(toc_file: Path) -> List[Dict]:
        """Load TOC entries from JSONL file."""
        with toc_file.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]

    @staticmethod
    def clean_title(title: str) -> str:
        """Clean section title by removing extra dots and whitespace."""
        title = re.sub(r'\.{2,}', '', title)
        title = re.sub(r'\s+', ' ', title)
        return title.strip()

    def extract_sections(self, toc_entries: List[Dict]) -> List[Dict]:
        """
        Extract sections from PDF using TOC, clean titles, and assign tags.

        Args:
            toc_entries (List[Dict]): TOC entries loaded from JSONL.

        Returns:
            List[Dict]: List of sections with cleaned titles, full_path, and tags.
        """
        sections: List[Dict] = []

        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            total_sections = len(toc_entries)

            for idx, entry in enumerate(toc_entries):
                start_page = max(entry["page"] - 1, 0)
                end_page = toc_entries[idx + 1]["page"] - 2 if idx + 1 < total_sections else total_pages - 1
                end_page = max(start_page, min(end_page, total_pages - 1))

                # Extract all page text efficiently
                section_text = "\n".join(
                    pdf.pages[p].extract_text() or "" for p in range(start_page, end_page + 1)
                ).lower()

                # Assign tags based on presence of keywords
                tags = [tag for tag, keywords in self.tag_map.items() if any(kw in section_text for kw in keywords)]

                clean_title = self.clean_title(entry["title"])
                sections.append({
                    **entry,
                    "title": clean_title,
                    "full_path": f"{entry['section_id']} {clean_title}",
                    "tags": tags
                })

        return sections

    def save_jsonl(self, sections: List[Dict]):
        """Save extracted sections to JSONL file."""
        with self.output_file.open("w", encoding="utf-8") as f:
            for section in sections:
                f.write(json.dumps(section, ensure_ascii=False) + "\n")

    def run(self):
        """Main method to execute extraction and save JSONL."""
        toc_entries = self.load_toc(self.toc_file)
        sections = self.extract_sections(toc_entries)
        self.save_jsonl(sections)
        print(f"Sections extracted and saved: {len(sections)}")


if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    PDF_PATH = PROJECT_ROOT / "data" / "USB_PD_R3_2 V1_1_2024_10.pdf"
    TOC_FILE = PROJECT_ROOT / "output" / "usb_pd_toc.jsonl"
    OUTPUT_FILE = PROJECT_ROOT / "output" / "usb_pd_spect.jsonl"

    TAG_MAP = {
        "contracts": ["contract", "operational contract", "negotiation"],
        "negotiation": ["negotiation", "negotiate"],
        "epr": ["extended power range", "epr"],
        "spr": ["standard power range", "spr"],
        "pps": ["programmable power supply", "pps"],
        "avs": ["adjustable voltage supply", "avs"],
        "usb4": ["usb4"],
        "charging": ["charge", "charging", "battery"],
        "hub": ["hub", "hubs"]
    }

    extractor = USBPDSpecExtractor(PDF_PATH, TOC_FILE, OUTPUT_FILE, TAG_MAP)
    extractor.run()
