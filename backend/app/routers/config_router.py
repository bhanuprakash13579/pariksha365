"""Public, env-driven configuration the frontend needs at runtime.

Currently surfaces the "Notes Bundle" offer parameters (price, UPI handle,
contact email, on/off flag) so the marketing copy and the payment instructions
can be tweaked from Railway without redeploying the SPA. The endpoint is
intentionally unauthenticated — every value here is already shown publicly on
the /notes page anyway.
"""
import json
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

# Resolve once at import time. The study-notes corpus and its prebuilt PDFs
# live under backend/seeds/study_notes — this router file is at
# backend/app/routers/config_router.py, so two parents up gets us to backend/.
_BACKEND = Path(__file__).resolve().parent.parent.parent
_NOTES_OUT = _BACKEND / "seeds" / "study_notes" / "_build" / "out"
_MANIFEST = _BACKEND / "seeds" / "study_notes" / "_build" / "manifest.json"

# Default sample shown on the storefront. Polity is the universally-relevant
# common book (every exam family asks Constitution / Governance), it's the
# most polished file in the corpus, and at ~1.5 MB it shows substantial
# content without being unwieldy. Override with NOTES_SAMPLE_FILE if a future
# sample swap is needed.
_DEFAULT_SAMPLE_FILE = "polity_ssc_rrb_banks_psc.pdf"


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _load_materials() -> list[dict]:
    """Pull the list of books from the existing study-notes manifest so the
    storefront stays in lockstep with what's actually in the bundle. Returns
    [] if the manifest is missing — callers tolerate the empty list.
    """
    if not _MANIFEST.exists():
        return []
    try:
        doc = json.loads(_MANIFEST.read_text())
    except Exception:
        return []
    out: list[dict] = []
    for book in doc.get("books", []):
        out.append({
            "id": book.get("id"),
            "title": book.get("title"),
            "subtitle": book.get("subtitle"),
            "exams": book.get("exams") or [],
        })
    return out


@router.get("/notes")
async def get_notes_offer_config() -> dict:
    """Surface the Notes-bundle offer params for the storefront page and the
    dashboard brochure card. All values are env-driven so the price / UPI /
    contact email can be rotated without a redeploy.

    Env vars (all optional — fall back to safe defaults so the page never
    breaks if Railway loses a variable):

    * ``NOTES_ENABLED``      — "true"/"false". Hides the entire offer when off.
    * ``NOTES_PRICE_INR``    — integer rupees (default 100).
    * ``NOTES_UPI_ID``       — UPI handle to receive payment (default the
                                 founder's personal handle so first-time deploys
                                 don't ship an empty page; override in prod).
    * ``NOTES_CONTACT_EMAIL``— email for buyers to send their UPI ref + delivery
                                 address (default contact@gsicorp.in).
    * ``NOTES_PAYEE_NAME``   — name displayed on the UPI deep-link
                                 (cosmetic — appears in the buyer's UPI app).
    * ``NOTES_BUNDLE_TITLE`` — headline for the page / card.
    * ``NOTES_PAGE_COUNT``   — informational; how many pages the bundle is
                                 advertised at.
    * ``NOTES_SUBJECT_COUNT``— informational; how many subjects covered.
    """
    materials = _load_materials()
    sample_file = os.getenv("NOTES_SAMPLE_FILE", _DEFAULT_SAMPLE_FILE).strip()

    # Find the manifest entry that matches the chosen sample file so the
    # storefront can label the sample button accurately ("Free sample —
    # Polity & Constitution") instead of a generic "Sample".
    sample_meta = None
    for book in materials:
        if (book.get("title") or "").lower().startswith("polity"):
            sample_meta = book
            break
    # Sample is an optional-by-design feature: only advertise it if the file
    # is actually present on disk. Avoids broken-download UX in environments
    # where the corpus hasn't been built yet.
    sample_available = (_NOTES_OUT / sample_file).exists()

    from app.core.config import settings
    return {
        "enabled": _bool_env("NOTES_ENABLED", True),
        "price_inr": int(os.getenv("NOTES_PRICE_INR", "100")),
        "upi_id": os.getenv("NOTES_UPI_ID", "bhanuprakashnaidu13579@okicici").strip(),
        "payee_name": os.getenv("NOTES_PAYEE_NAME", "Pariksha365 Notes").strip(),
        "contact_email": os.getenv("NOTES_CONTACT_EMAIL", "contact@gsicorp.in").strip(),
        "bundle_title": os.getenv(
            "NOTES_BUNDLE_TITLE", "Pariksha365 Master Notes Bundle"
        ).strip(),
        "page_count": int(os.getenv("NOTES_PAGE_COUNT", "1500")),
        "subject_count": int(os.getenv("NOTES_SUBJECT_COUNT", str(len(materials) or 15))),
        "materials": materials,
        "sample_available": sample_available,
        "sample_title": (sample_meta or {}).get("title") or "Polity & Constitution — Common Book",
        "sample_pdf_url": "/config/notes/sample" if sample_available else None,
        # True once CASHFREE_APP_ID is set in Railway env vars
        "cashfree_enabled": bool(settings.CASHFREE_APP_ID),
    }


@router.get("/notes/sample")
async def download_notes_sample():
    """Serve the public sample PDF. The file lives under
    ``backend/seeds/study_notes/_build/out/`` and is whichever name
    ``NOTES_SAMPLE_FILE`` resolves to (default: Polity).

    The sample MUST stay in the static-GK / awareness category — never quant,
    reasoning, English, or vocabulary, since those are the lion's-share
    scoring subjects and giving them away free undercuts the paid bundle.
    """
    sample_file = os.getenv("NOTES_SAMPLE_FILE", _DEFAULT_SAMPLE_FILE).strip()
    path = _NOTES_OUT / sample_file
    if not path.exists():
        raise HTTPException(status_code=404, detail="Sample not available")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename="Pariksha365-Notes-Sample-Polity.pdf",
    )
