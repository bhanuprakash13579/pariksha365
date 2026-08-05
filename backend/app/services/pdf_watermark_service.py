"""Bake a personalized deterrence watermark into a PDF in memory.

Industry approach (Scribd / Springer / ACM style):
  • One large, very-light diagonal stamp centred on each page — visible enough
    to deter sharing, transparent enough to read content underneath.
  • A small footer line with the buyer's identity — survives cropping/printing.

Both are burned into the content stream (garbage=4 + clean=True) so there
is no separate removable layer in the output file.
"""
from __future__ import annotations

import io
from datetime import datetime

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default(size=size)


def _make_watermark_png(
    w_pt: float, h_pt: float,
    name_line: str, email_line: str, site_line: str, footer_line: str,
) -> bytes:
    """
    Full-page transparent PNG with:
      • One large diagonal stamp centred on the page  (very light)
      • One small footer line at the bottom            (readable, always visible)
    """
    scale = 1.5
    W, H = int(w_pt * scale), int(h_pt * scale)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # ── Centred diagonal stamp ───────────────────────────────────────────────
    stamp_font_sz = int(20 * scale)
    stamp_font    = _load_font(stamp_font_sz)
    # 110/255 ≈ 43% opacity — clearly visible but content readable through it
    stamp_gray    = (80, 80, 80, 110)

    # Measure actual text widths so the strip is never too narrow
    _probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    strip_w = max(
        int(_probe.textlength(name_line,  font=stamp_font)),
        int(_probe.textlength(email_line, font=stamp_font)),
        int(_probe.textlength(site_line,  font=stamp_font)),
    ) + 20   # small right-side padding

    strip_h = stamp_font_sz * 5
    strip   = Image.new("RGBA", (strip_w, strip_h), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(strip)
    draw.text((0, 0),                       name_line,  fill=stamp_gray, font=stamp_font)
    draw.text((0, stamp_font_sz + 6),       email_line, fill=stamp_gray, font=stamp_font)
    draw.text((0, (stamp_font_sz + 6) * 2), site_line,  fill=stamp_gray, font=stamp_font)

    rotated = strip.rotate(35, expand=True,
                           resample=Image.BICUBIC,
                           fillcolor=(0, 0, 0, 0))

    # Centre on page; if rotated image is wider than page the edges bleed off
    # naturally — that is fine, the key info in the middle stays fully visible
    cx = (W - rotated.width)  // 2
    cy = (H - rotated.height) // 2
    canvas.paste(rotated, (cx, cy), rotated)

    # ── Small footer line ────────────────────────────────────────────────────
    footer_font_sz = int(7.5 * scale)
    footer_font    = _load_font(footer_font_sz)
    footer_gray    = (80, 80, 80, 180)        # more opaque — always readable
    footer_text    = footer_line

    footer_strip = Image.new("RGBA", (W, footer_font_sz + 8), (0, 0, 0, 0))
    ImageDraw.Draw(footer_strip).text(
        (int(W * 0.04), 4), footer_text, fill=footer_gray, font=footer_font
    )
    canvas.paste(footer_strip, (0, H - footer_strip.height - int(6 * scale)), footer_strip)

    buf = io.BytesIO()
    canvas.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def watermark_pdf(
    pdf_bytes: bytes,
    user_name: str,
    user_email: str,
    user_phone: str | None = None,
) -> bytes:
    """Return a copy of the PDF with a deterrence watermark burned into every page."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    phone_part = f" | Ph: {user_phone}" if user_phone else ""
    date_str   = datetime.now().strftime("%d %b %Y")
    name_line  = f"Sold to: {user_name}"
    email_line = f"{user_email}{phone_part}"
    site_line  = f"Pariksha365.com  |  {date_str}  |  Sharing is illegal"
    # footer keeps the full identity on one line
    footer_line = f"Sold to: {user_name} | {user_email}{phone_part}  |  Pariksha365.com | {date_str}"

    # Cache the watermark PNG per unique page size — every page of a book is normally the
    # same size, so this renders the (expensive) image once instead of once per page. This
    # is what keeps large books (80+ pages) from timing out the request into a 502.
    wm_cache: dict[tuple[int, int], bytes] = {}
    for page in doc:
        key = (round(page.rect.width), round(page.rect.height))
        wm_png = wm_cache.get(key)
        if wm_png is None:
            wm_png = _make_watermark_png(
                page.rect.width, page.rect.height,
                name_line, email_line, site_line, footer_line,
            )
            wm_cache[key] = wm_png
        page.insert_image(page.rect, stream=wm_png, overlay=True)

    buf = io.BytesIO()
    # deflate keeps it compact; drop the expensive garbage=4/clean full-doc rewrite.
    doc.save(buf, deflate=True, garbage=1)
    doc.close()
    return buf.getvalue()
