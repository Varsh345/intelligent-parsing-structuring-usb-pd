import pdfplumber
import re
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
PDF_PATH = PROJECT_ROOT / "data" / "USB_PD_R3_2 V1_1_2024_10.pdf"
OUTPUT_FILE = PROJECT_ROOT / "output" / "usb_pd_toc.jsonl"

DOC_TITLE = "USB Power Delivery Specification Rev 3.2 V1.1 2024-10"
TOC_START_PAGE = 13
TOC_END_PAGE = 18

def extract_toc_text(pdf_path, start_page, end_page):
    toc_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_index in range(start_page - 1, end_page):
            text = pdf.pages[page_index].extract_text()
            if text:
                for line in text.split("\n"):
                    if not line.strip():
                        continue
                    toc_lines.append(line.strip())
    return toc_lines

def parse_toc_lines(lines, doc_title):
    toc_entries = []
    section_re = re.compile(r'^(\d+(?:\.\d+)*)(?:\s+)(.+?)\s+(\d+)$')
    for line in lines:
        m = section_re.match(line.strip().replace("…", " "))
        if m:
            sec_id = m.group(1)
            clean_title = re.sub(r'\.{2,}', '', m.group(2)).strip()
            page = int(m.group(3))
            level = sec_id.count(".") + 1
            parent_id = ".".join(sec_id.split(".")[:-1]) if "." in sec_id else None
            toc_entries.append({
                "doc_title": doc_title,
                "section_id": sec_id,
                "title": clean_title,
                "page": page,
                "level": level,
                "parent_id": parent_id,
                "full_path": f"{sec_id} {clean_title}"
            })
    return toc_entries

if __name__ == "__main__":
    toc_lines = extract_toc_text(PDF_PATH, TOC_START_PAGE, TOC_END_PAGE)
    toc_entries = parse_toc_lines(toc_lines, DOC_TITLE)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing TOC to: {OUTPUT_FILE.resolve()}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for e in toc_entries:
            f.write(json.dumps(e) + "\n")
    print(f"TOC extracted: {len(toc_entries)} sections")
