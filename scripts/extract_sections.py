import pdfplumber
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
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
    "charging": ["charge", "charging", "battery"],
    "hub": ["hub", "hubs"]
}

def load_toc(toc_file):
    with open(toc_file, encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def extract_sections(pdf_path, toc_entries):
    spec_entries = []
    with pdfplumber.open(pdf_path) as pdf:
        total_sections = len(toc_entries)
        for idx, entry in enumerate(toc_entries):
            start_page = entry["page"] - 1
            end_page = toc_entries[idx + 1]["page"] - 1 if idx + 1 < total_sections else len(pdf.pages) - 1  # <- changed from -2 to -1

            # Sanity check
            if start_page < 0:
                start_page = 0
            if end_page >= len(pdf.pages):
                end_page = len(pdf.pages) - 1
            if end_page < start_page:
                # Instead of skipping, just process the start page
                #print(f"⚠ Page range inverted for {entry['full_path']} — using only start page")
                end_page = start_page

            # Progress output
            print(f"Processing {idx+1}/{total_sections}: {entry['full_path']} (pages {start_page+1}-{end_page+1})")

            content_lines = []
            for p in range(start_page, end_page + 1):
                try:
                    page_text = pdf.pages[p].extract_text()
                except Exception as e:
                    print(f"⚠ Error reading page {p+1}: {e}")
                    page_text = ""
                if page_text:
                    content_lines.append(page_text.lower())

            section_text = "\n".join(content_lines)
            tags = [tag for tag, keywords in TAG_MAP.items() if any(kw in section_text for kw in keywords)]
            clean_title = re.sub(r'\.{2,}', '', entry["title"]).strip()

            spec_entries.append({
                **entry,
                "title": clean_title,
                "full_path": f"{entry['section_id']} {clean_title}",
                "tags": tags
            })
    return spec_entries

if __name__ == "__main__":
    toc_entries = load_toc(TOC_FILE)
    spec_entries = extract_sections(PDF_PATH, toc_entries)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing Sections to: {OUTPUT_FILE.resolve()}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for e in spec_entries:
            f.write(json.dumps(e) + "\n")
    print(f"✅ Sections extracted with tags: {len(spec_entries)}")
