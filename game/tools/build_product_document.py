"""Generate current v0.4 review document from its authored data."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[2]/"work/final-design/build_report.py"),run_name="__main__")
