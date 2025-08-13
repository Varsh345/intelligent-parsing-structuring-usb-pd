import pdfplumber
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
PDF_PATH = PROJECT_ROOT / "data" / "USB_PD_R3_2 V1_1_2024_10.pdf"
OUTPUT_FILE = PROJECT_ROOT / "output" / "usb_pd_metadata.jsonl"

DOC_TITLE = "USB Power Delivery Specification Rev 3.2 V1.1 2024-10"

def extract_metadata(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page_text = pdf.pages[0].extract_text()
    return {
        "doc_title": DOC_TITLE,
        "revision": "3.2",
        "version": "1.1",
        "release_date": "October 2024",
        "publisher": "USB-IF",
        "raw_header": first_page_text
    }

if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing Metadata to: {OUTPUT_FILE.resolve()}")
    meta = extract_metadata(PDF_PATH)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(meta) + "\n")
    print(f"✅ Metadata extracted: {OUTPUT_FILE}")
