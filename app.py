import json
from pathlib import Path
from src.parser.metadata_extractor import MetadataExtractor
from src.parser.toc_extractor import TOCExtractor
from src.parser.section_extractor import SectionExtractor, TagAssigner
from src.validator.section_validator import SectionValidator

def main():
    PROJECT_ROOT = Path(__file__).parent.resolve()

    PDF_PATH = PROJECT_ROOT / "data" / "USB_PD_R3_2 V1_1_2024_10.pdf"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    OUTPUT_DIR.mkdir(exist_ok=True)

    tag_map = {
        "power_delivery": ["power delivery", "pd"],
        "protocol": ["protocol", "message", "communication"],
        "physical_layer": ["physical layer", "phy"],
        "source_sink": ["source", "sink"],
    }

    DOC_TITLE = "USB Power Delivery Specification Rev 3.2 V1.1 2024-10"

    # Step 1: Extract Metadata
    meta_extractor = MetadataExtractor(PDF_PATH, DOC_TITLE)
    metadata = meta_extractor.extract()
    with open(OUTPUT_DIR / "usb_pd_metadata.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(metadata) + "\n")

    # Step 2: Extract TOC 
    toc_extractor = TOCExtractor(PDF_PATH, start_page=13, end_page=18, doc_title=DOC_TITLE)
    toc_entries = toc_extractor.extract()
    with open(OUTPUT_DIR / "usb_pd_toc.json", "w", encoding="utf-8") as f:
        json.dump(toc_entries, f, indent=2, ensure_ascii=False)

    # Step 3: Extract Spec Sections based on TOC entries
    tagger = TagAssigner(tag_map)
    section_extractor = SectionExtractor(PDF_PATH, tagger, DOC_TITLE)    
    spec_sections = section_extractor.extract_sections(toc_entries)
    with open(OUTPUT_DIR / "usb_pd_spec.jsonl", "w", encoding="utf-8") as f:
        for section in spec_sections:
            f.write(json.dumps(section) + "\n")

    print("Metadata, TOC, and Section extraction completed.")

    # Step 4: Validate and generate XLSX report
    toc_file = OUTPUT_DIR / "usb_pd_toc.json"
    spec_file = OUTPUT_DIR / "usb_pd_spec.jsonl"
    validation_report = OUTPUT_DIR / "validation_report.xlsx"
    validator = SectionValidator(toc_file, spec_file, validation_report)
    validator.run()
    print(f"Validation report generated: {validation_report}")

if __name__ == "__main__":
    main()