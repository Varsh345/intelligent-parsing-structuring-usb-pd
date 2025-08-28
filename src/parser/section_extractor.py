import pdfplumber
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
import spacy
from spacy.matcher import PhraseMatcher


class USBPDSpecExtractor:
    """
    Extract sections from USB PD PDF, clean titles, assign tags using SpaCy PhraseMatcher,
    and save structured JSONL output.
    """
    def __init__(
        self,
        pdf_path: Path,
        toc_file: Path,
        output_file: Path,
        tag_map: Optional[Dict[str, List[str]]] = None,
        spacy_model: str = "en_core_web_sm",
    ):
        self.pdf_path = pdf_path
        self.toc_file = toc_file
        self.output_file = output_file
        self.tag_map = tag_map or {}

        # Load SpaCy NLP pipeline
        self.nlp = spacy.load(spacy_model)
        self.nlp.max_length = 5_000_000
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self._prepare_matcher()

        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def _prepare_matcher(self):
        """Prepare PhraseMatcher patterns for all tags from tag_map keywords."""
        for tag, keywords in self.tag_map.items():
            patterns = [self.nlp.make_doc(keyword) for keyword in keywords]
            self.matcher.add(tag, patterns)

    def load_toc(self) -> List[Dict]:
        """Load TOC entries from JSONL file."""
        try:
            with self.toc_file.open("r", encoding="utf-8") as f:
                return [json.loads(line) for line in f]
        except Exception as e:
            print(f"Error loading TOC: {e}")
            return []

    @staticmethod
    def clean_title(title: str) -> str:
        title = re.sub(r"\.{2,}", "", title)
        title = re.sub(r"\s+", " ", title)
        return title.strip()

    def assign_tags(self, text: str) -> List[str]:
        """
        Assign tags by matching tag keywords/phrases using SpaCy PhraseMatcher.
        Arguments: text - Text to search for tag keywords.
        Returns: List - List of matched tags.
        """
        doc = self.nlp(text)
        matches = self.matcher(doc)
        matched_tags = {self.nlp.vocab.strings[match_id] for match_id, start, end in matches}
        return sorted(matched_tags)

    def extract_sections(self, toc_entries: List[Dict]) -> List[Dict]:
        sections = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                total_sections = len(toc_entries)

                for idx, entry in enumerate(toc_entries):
                    start_page = max(entry.get("page", 1) - 1, 0)
                    next_page = toc_entries[idx + 1]["page"] - 1 if (idx + 1) < total_sections else total_pages
                    end_page = max(start_page, min(next_page - 1, total_pages - 1))

                    pages_text = (pdf.pages[p].extract_text() or "" for p in range(start_page, end_page + 1))
                    section_text = "\n".join(pages_text).strip()

                    clean_title = self.clean_title(entry.get("title", ""))

                    combined_text = f"{clean_title} {section_text}"
                    tags = self.assign_tags(combined_text)

                    sections.append({
                        **entry,
                        "title": clean_title,
                        "full_path": f"{entry.get('section_id', '')} {clean_title}",
                        "tags": tags
                    })
        except Exception as e:
            print(f"Error extracting sections: {e}")

        return sections

    def save_jsonl(self, sections: List[Dict]):
        try:
            with self.output_file.open("w", encoding="utf-8") as f:
                for section in sections:
                    f.write(json.dumps(section, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Error saving JSONL: {e}")

    def run(self):
        toc_entries = self.load_toc()
        if not toc_entries:
            print("No TOC entries loaded.")
            return
        sections = self.extract_sections(toc_entries)
        if sections:
            self.save_jsonl(sections)
            print(f"Sections extraction complete.")
        else:
            print("No sections extracted.")

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    PDF_PATH = PROJECT_ROOT / "data" / "USB_PD_R3_2 V1_1_2024_10.pdf"
    TOC_FILE = PROJECT_ROOT / "output" / "usb_pd_toc.jsonl"
    OUTPUT_FILE = PROJECT_ROOT / "output" / "usb_pd_spec.jsonl"

    TAG_MAP = {
        "contracts": ["contract", "operational contract", "negotiation"],
        "negotiation": ["negotiation", "negotiate"],
        "epr": ["extended power range", "epr"],
        "spr": ["standard power range", "spr"],
        "pps": ["programmable power supply", "pps"],
        "avs": ["adjustable voltage supply", "avs"],
        "usb4": ["usb4"],
        "charging": ["charge", "charging", "battery", "power", "energy"],
        "hub": ["hub", "hubs", "pdusb", "peripheral", "switch", "device"]
    }

    extractor = USBPDSpecExtractor(PDF_PATH, TOC_FILE, OUTPUT_FILE, TAG_MAP)
    extractor.run()
