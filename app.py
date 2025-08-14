import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent / "scripts"
scripts_to_run = [
    "extract_toc.py",
    "extract_sections.py",
    "extract_metadata.py",
    "validate_sections.py"
]

def run_script(script_name):
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        sys.exit(1)
    result = subprocess.run([sys.executable, str(script_path)])
    if result.returncode != 0:
        sys.exit(result.returncode)
    print(f"{script_name} finished successfully")

if __name__ == "__main__":
    print("Starting USB PD Parsing Pipeline...")
    for script in scripts_to_run:
        run_script(script)
    print("\nOutput saved in the 'output' folder.")
