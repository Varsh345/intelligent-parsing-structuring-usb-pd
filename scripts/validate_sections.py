import json
import openpyxl
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
TOC_FILE = PROJECT_ROOT / "output" / "usb_pd_toc.jsonl"
SPEC_FILE = PROJECT_ROOT / "output" / "usb_pd_spec.jsonl"
OUTPUT_FILE = PROJECT_ROOT / "output" / "validation_report.xlsx"

def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def write_validation_report(toc_entries, spec_entries, out_file):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Validation"

    toc_ids = [t["section_id"] for t in toc_entries]
    spec_ids = [s["section_id"] for s in spec_entries]
    missing = sorted(set(toc_ids) - set(spec_ids))

    ws.append(["Check", "TOC Count", "Parsed Count", "Missing Count"])
    ws.append(["Section Count", len(toc_ids), len(spec_ids), len(missing)])

    ws.append([])
    ws.append(["Missing TOC Sections in Parsed"])
    for sec in missing:
        match_title = next((t["title"] for t in toc_entries if t["section_id"] == sec), "")
        ws.append([sec, match_title])

    wb.save(out_file)

if __name__ == "__main__":
    toc_entries = load_jsonl(TOC_FILE)
    spec_entries = load_jsonl(SPEC_FILE)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    write_validation_report(toc_entries, spec_entries, OUTPUT_FILE)
    print(f"Validation report saved: {OUTPUT_FILE}")
