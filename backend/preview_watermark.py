"""Run from the backend/ directory to preview the watermark on a real PDF.

  cd backend
  python preview_watermark.py

Output: ~/Desktop/watermark_preview.pdf
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from app.services.pdf_watermark_service import watermark_pdf

src = Path(__file__).parent / "seeds/study_notes/_build/out/polity_ssc_rrb_banks_psc.pdf"
if not src.exists():
    # fallback to whatever is first in the folder
    pdfs = sorted((Path(__file__).parent / "seeds/study_notes/_build/out").glob("*.pdf"))
    if not pdfs:
        print("No PDFs found in _build/out/"); sys.exit(1)
    src = pdfs[0]

print(f"Source: {src.name}  ({src.stat().st_size // 1024} KB)")

pdf_bytes = src.read_bytes()
wm_bytes = watermark_pdf(
    pdf_bytes=pdf_bytes,
    user_name="Ravi Kumar Venkatanarasimharajuvaripeta",
    user_email="ravi.kumar.venkatanarasimha.rajuvaripeta@gmail.com",
    user_phone="9876543210",
)

out = Path.home() / "Desktop" / "watermark_preview.pdf"
out.write_bytes(wm_bytes)
print(f"Preview saved → {out}  ({len(wm_bytes) // 1024} KB)")
print("Open it to check how the watermark looks.")
