import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional
import pdfplumber
import spacy
from spacy.matcher import PhraseMatcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TOCExtractor:
    """Handles loading and cleaning of TOC entries from JSONL."""

    def __init__(self, toc_file: Path):
        self.toc_file = toc_file

    def load(self) -> list[dict]:
        """Load TOC entries from JSON file."""
        try:
            with self.toc_file.open("r", encoding="utf-8") as f:
                entries = json.load(f)
            logging.info("Loaded %d TOC entries.", len(entries))
            return entries
        except Exception as e:
            logging.error("Error loading TOC: %s", e)
            return []

    @staticmethod
    def clean_title(title: str) -> str:
        """Normalize section titles by removing extra dots/spaces."""
        title = re.sub(r"\.{2,}", "", title)
        title = re.sub(r"\s+", " ", title)
        return title.strip()


class TagAssigner:
    """Assigns semantic tags to text using SpaCy PhraseMatcher."""

    def __init__(self, tag_map: Dict[str, List[str]], model: str = "en_core_web_sm"):
        self.nlp = spacy.load(model)
        self.nlp.max_length = 5_000_000
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self._cache = {}
        self._prepare(tag_map)

    def _prepare(self, tag_map: Dict[str, List[str]]):
        """Prepare matcher patterns for all tags."""
        for tag, keywords in tag_map.items():
            patterns = [self.nlp.make_doc(k) for k in keywords]
            self.matcher.add(tag, patterns)

    def assign(self, text: str) -> List[str]:
        """Return tags for given text."""
        if text in self._cache:
            return self._cache[text]
        doc = self.nlp(text)
        matches = self.matcher(doc)
        tags = sorted({self.nlp.vocab.strings[mid] for mid, _, _ in matches})
        self._cache[text] = tags
        return tags


class SectionExtractor:
    """Extracts document sections from PDF using TOC and heuristics."""

    def __init__(self, pdf_path: Path, tagger: TagAssigner, doc_title: str):
        self.pdf_path = pdf_path
        self.tagger = tagger
        self.doc_title = doc_title

    def extract_sections(self, toc_entries: List[Dict]) -> List[Dict]:
        """Extract all TOC-based sections."""
        sections = []
        with pdfplumber.open(self.pdf_path) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
            total_pages = len(pages)

            for idx, entry in enumerate(toc_entries):
                start = max(entry.get("page", 1) - 1, 0)
                if idx + 1 < len(toc_entries):
                    next_start = toc_entries[idx + 1].get("page", total_pages + 1)
                    end = max(start, min(next_start - 2, total_pages - 1))
                else:
                    end = total_pages - 1

                section_text = " ".join(pages[start : end + 1])
                tags = self.tagger.assign(section_text)
                sections.append(
                    {
                        "doc_title": self.doc_title,
                        "section_id": entry.get("section_id", ""),
                        "title": TOCExtractor.clean_title(entry.get("title", "")),
                        "page": start + 1,
                        "level": entry.get("level", 1),
                        "parent_id": entry.get("parent_id"),
                        "full_path": entry.get("full_path", ""),
                        "tags": tags
                    }
                )

        return sections   

class Exporter:
    """Handles saving extracted data into JSONL format."""

    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def save(self, sections: List[Dict]) -> None:
        """Save section data to JSONL."""
        try:
            with self.output_file.open("w", encoding="utf-8") as f:
                for sec in sections:
                    f.write(json.dumps(sec, ensure_ascii=False) + "\n")
            logging.info("Saved %d sections to %s", len(sections), self.output_file)
        except Exception as e:
            logging.error("Error saving JSONL: %s", e)


class ExtractionPipeline:
    """Coordinates the full extraction process."""

    def __init__(
        self,
        pdf_path: Path,
        toc_file: Path,
        output_file: Path,
        doc_title: str,
        tag_map: Dict[str, List[str]],
    ):
        self.toc_extractor = TOCExtractor(toc_file)
        self.tagger = TagAssigner(tag_map)
        self.section_extractor = SectionExtractor(pdf_path, self.tagger, doc_title)
        self.exporter = Exporter(output_file)

    def run(self) -> None:
        """Execute full pipeline."""
        toc_entries = self.toc_extractor.load()
        if not toc_entries:
            logging.warning("No TOC entries found.")
            return
        sections = self.section_extractor.extract_sections(toc_entries)
        if sections:
            self.exporter.save(sections)
            print("Sections extraction completed.")
        else:
            logging.warning("No sections extracted.")


if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    PDF_PATH = PROJECT_ROOT / "data" / "USB_PD_R3_2 V1_1_2024_10.pdf"
    TOC_FILE = PROJECT_ROOT / "output" / "usb_pd_toc.json"
    OUTPUT_FILE = PROJECT_ROOT / "output" / "usb_pd_spec.jsonl"
    DOC_TITLE = "USB Power Delivery Specification Rev X"

    TAG_MAP = {
        "contracts": ["contract", "operational contract", "negotiation"],
        "negotiation": ["negotiation", "negotiate"],
        "epr": ["extended power range", "epr"],
        "spr": ["standard power range", "spr"],
        "pps": ["programmable power supply", "pps"],
        "avs": ["adjustable voltage supply", "avs"],
        "usb4": ["usb4"],
        "charging": ["charge", "charging", "battery", "power", "energy"],
        "hub": ["hub", "hubs", "pdusb", "peripheral", "switch", "device"],
    }

    pipeline = ExtractionPipeline(
        PDF_PATH, TOC_FILE, OUTPUT_FILE, DOC_TITLE, TAG_MAP
    )
    pipeline.run()
