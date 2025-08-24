from pathlib import Path
import json

from src.parser.metadata_extractor import MetadataExtractor
from src.parser.toc_extractor import TOCExtractor

def main():
    PROJECT_ROOT = Path(__file__).parent.resolve()
    PDF_PATH = PROJECT_ROOT / "data" / "USB_PD_R3_2 V1_1_2024_10.pdf"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    OUTPUT_DIR.mkdir(exist_ok=True)

    DOC_TITLE = "USB Power Delivery Specification Rev 3.2 V1.1 2024-10"

    # Step 1: Extract Metadata
    meta_extractor = MetadataExtractor(PDF_PATH, DOC_TITLE)
    metadata = meta_extractor.extract()
    with open(OUTPUT_DIR / "usb_pd_metadata.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(metadata) + "\n")

    # Step 2: Extract TOC
    toc_extractor = TOCExtractor(PDF_PATH, DOC_TITLE)
    toc_entries = toc_extractor.extract(start_page=13, end_page=18)  # adjust TOC pages
    with open(OUTPUT_DIR / "usb_pd_toc.jsonl", "w", encoding="utf-8") as f:
        for entry in toc_entries:
            f.write(json.dumps(entry) + "\n")

    print("Metadata and TOC extraction completed.")

if __name__ == "__main__":
    main()
