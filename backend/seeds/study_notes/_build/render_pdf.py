#!/usr/bin/env python3
"""Render study-notes markdown to PDF via Chrome headless.

No sudo / pandoc needed. Pipeline:
  markdown (Python `markdown`) -> HTML wrapper (KaTeX + Mermaid via CDN)
                               -> google-chrome --headless --print-to-pdf

Usage:
  python3 render_pdf.py polity                  # build polity book per manifest
  python3 render_pdf.py polity history          # build subset
  python3 render_pdf.py --all                   # build every entry in manifest
  python3 render_pdf.py --src ../polity.md \\   # one-shot, no manifest
                        --out /tmp/x.pdf \\
                        --title "Polity" --subtitle "SSC + RRB"
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import markdown

SCRIPT_DIR = Path(__file__).resolve().parent
NOTES_DIR = SCRIPT_DIR.parent
OUT_DIR = SCRIPT_DIR / "out"
MANIFEST_PATH = SCRIPT_DIR / "manifest.json"

CHROME_BIN = (
    shutil.which("google-chrome")
    or shutil.which("google-chrome-stable")
    or shutil.which("chromium-browser")
    or shutil.which("chromium")
)


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title_html}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<style>
{css}
</style>
</head>
<body>

<section class="cover">
  <div class="cover-inner">
    <div class="brand">Pariksha365 — Study Notes</div>
    <h1 class="cover-title">{title_html}</h1>
    <h2 class="cover-subtitle">{subtitle_html}</h2>
    <div class="exam-tags">{exam_tags_html}</div>
    <div class="meta">v {version_html}</div>
    <div class="promise">
      <strong>The promise.</strong> Read this book end-to-end (with the usual
      two re-reads + active recall on the embedded prompts) and you will be
      able to attempt every quiz question in the Pariksha365 pool for this
      subject with a strong fundamental grasp.
    </div>
  </div>
</section>

<main class="content">
{body_html}
</main>

<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
<script>
  if (typeof renderMathInElement === 'function') {{
    renderMathInElement(document.body, {{
      delimiters: [
        {{left: '$$', right: '$$', display: true}},
        {{left: '$',  right: '$',  display: false}}
      ],
      throwOnError: false
    }});
  }}
  if (typeof mermaid !== 'undefined') {{
    mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
  }}
  // Signal Chrome that rendering is done.
  setTimeout(() => {{ document.title = document.title + ' [READY]'; }}, 1500);
</script>
</body>
</html>
"""

CSS = textwrap.dedent("""
  @page { size: A4; margin: 18mm 16mm 18mm 16mm; }

  html, body {
    font-family: "DejaVu Sans", "Noto Sans", system-ui, sans-serif;
    line-height: 1.5;
    color: #1f2937;
    font-size: 10.5pt;
  }

  body { margin: 0; }

  .cover {
    page-break-after: always;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #6c1d5f 0%, #1e3a8a 100%);
    color: #fff !important;
  }
  /* Force ALL text on cover page to be white (overrides global h1/h2 colors) */
  .cover, .cover *,
  .cover h1, .cover h2, .cover h3, .cover h4,
  .cover .cover-title, .cover .cover-subtitle,
  .cover .brand, .cover .meta, .cover .promise,
  .cover .exam-tags, .cover .exam-tags .tag {
    color: #ffffff !important;
    border-color: rgba(255,255,255,0.5) !important;
  }
  /* Remove the dark border-bottom that h1 inherits from global rule */
  .cover h1, .cover .cover-title {
    border-bottom: none !important;
    padding-bottom: 0 !important;
  }
  .cover-inner { text-align: center; max-width: 80%; }
  .brand { letter-spacing: 0.25em; font-size: 11pt; text-transform: uppercase; opacity: 0.9; }
  .cover-title { font-size: 38pt; margin: 24pt 0 8pt 0; line-height: 1.15; }
  .cover-subtitle { font-size: 16pt; font-weight: 400; opacity: 0.95; margin: 0 0 24pt 0; }
  .exam-tags { font-size: 11pt; margin: 12pt 0 0 0; }
  .exam-tags .tag {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.5);
    border-radius: 999px;
    padding: 3pt 10pt;
    margin: 3pt;
  }
  .meta { margin-top: 18pt; font-size: 10pt; opacity: 0.85; }
  .promise {
    margin-top: 36pt;
    background: rgba(0,0,0,0.25);
    padding: 12pt 18pt;
    border-radius: 8pt;
    font-size: 11pt;
    line-height: 1.5;
    text-align: left;
  }

  .content { padding: 0; }

  h1 {
    color: #6c1d5f;
    border-bottom: 2px solid #6c1d5f;
    padding-bottom: 4pt;
    margin-top: 8pt;
    page-break-before: auto;
    page-break-after: avoid;
    font-size: 18pt;
  }
  h2 { color: #0f4c75; margin-top: 10pt; margin-bottom: 4pt; font-size: 14pt; page-break-after: avoid; }
  h3 { color: #1d4ed8; font-size: 12pt; margin-top: 8pt; margin-bottom: 3pt; page-break-after: avoid; }
  h4 { color: #2563eb; font-size: 11pt; margin-top: 6pt; margin-bottom: 2pt; page-break-after: avoid; }
  p, li { orphans: 2; widows: 2; }
  /* Keep heading + at least first paragraph together */
  h1 + *, h2 + *, h3 + *, h4 + * { page-break-before: avoid; }

  blockquote {
    background: #fff7ed;
    border-left: 3px solid #f97316;
    padding: 6pt 12pt;
    margin: 10pt 0;
    font-style: italic;
    color: #7c2d12;
  }

  pre, code {
    font-family: "DejaVu Sans Mono", "Menlo", monospace;
    font-size: 9.5pt;
  }
  code { background: #f1f5f9; padding: 1pt 4pt; border-radius: 3pt; }
  pre {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4pt;
    padding: 8pt 10pt;
    overflow-x: auto;
  }
  pre code { background: none; padding: 0; }

  table {
    border-collapse: collapse;
    margin: 6pt 0;
    width: 100%;
    font-size: 9.5pt;
    /* Allow long tables to break across pages */
    page-break-inside: auto;
  }
  /* Keep individual rows together (don't split a row across pages) */
  table tr {
    page-break-inside: avoid;
    page-break-after: auto;
  }
  /* Repeat header row on each page when table breaks */
  table thead {
    display: table-header-group;
  }
  table th, table td {
    border: 1px solid #94a3b8;
    padding: 4pt 7pt;
    text-align: left;
    vertical-align: top;
  }
  table th { background: #e2e8f0; }

  hr { border: 0; border-top: 1px dashed #94a3b8; margin: 14pt 0; }

  /* ── Callout boxes ── */

  /* Intuition / plain-English explanation (teal) */
  .intuition {
    background: #e6f7f5;
    border-left: 4px solid #0d9488;
    padding: 10pt 14pt;
    margin: 12pt 0;
    color: #134e4a;
    border-radius: 0 4pt 4pt 0;
  }
  .intuition strong { color: #0f766e; }

  /* Formal definition (indigo) */
  .definition {
    background: #eef2ff;
    border-left: 4px solid #4f46e5;
    padding: 10pt 14pt;
    margin: 10pt 0;
    color: #1e1b4b;
    border-radius: 0 4pt 4pt 0;
  }
  .definition strong { color: #3730a3; }

  /* Key formula / theorem (purple) */
  .formula {
    background: #faf5ff;
    border-left: 4px solid #7c3aed;
    padding: 10pt 14pt;
    margin: 10pt 0;
    color: #3b0764;
    border-radius: 0 4pt 4pt 0;
  }
  .formula strong { color: #6d28d9; }

  /* Worked example (green) */
  .worked {
    background: #f0fdf4;
    border-left: 4px solid #16a34a;
    padding: 10pt 14pt;
    margin: 10pt 0;
    color: #14532d;
    border-radius: 0 4pt 4pt 0;
  }
  .worked strong { color: #15803d; }

  /* Exam tip (amber) */
  .examtip {
    background: #fffbeb;
    border-left: 4px solid #d97706;
    padding: 10pt 14pt;
    margin: 10pt 0;
    color: #78350f;
    border-radius: 0 4pt 4pt 0;
  }
  .examtip strong { color: #b45309; }

  /* Key insight / remember (sky blue) */
  .keypoint {
    background: #f0f9ff;
    border-left: 4px solid #0284c7;
    padding: 10pt 14pt;
    margin: 10pt 0;
    color: #0c4a6e;
    border-radius: 0 4pt 4pt 0;
  }
  .keypoint strong { color: #0369a1; }

  /* Mnemonic / memory aid (green — kept) */
  .mnemonic, blockquote.mnemonic {
    background: #f0fdf4;
    border-left: 3px solid #22c55e;
    padding: 8pt 12pt;
    margin: 10pt 0;
    color: #14532d;
    font-style: normal;
  }

  /* Common pitfall / trap (red — kept) */
  .pitfall, blockquote.pitfall {
    background: #fef2f2;
    border-left: 4px solid #ef4444;
    padding: 10pt 14pt;
    margin: 10pt 0;
    color: #7f1d1d;
    font-style: normal;
    border-radius: 0 4pt 4pt 0;
  }
  .pitfall strong { color: #b91c1c; }

  /* PYQ / exam-style question (blue — kept) */
  .pyq {
    background: #eff6ff;
    border-left: 3px solid #3b82f6;
    padding: 6pt 10pt;
    margin: 10pt 0;
    font-size: 10pt;
    color: #1e3a8a;
  }

  img, svg { max-width: 100%; height: auto; }
  .mermaid { text-align: center; margin: 12pt 0; }

  /* page break controls */
  h1 { page-break-before: always; }
  h1:first-of-type { page-break-before: avoid; }
  /* Tables — allow break inside long tables; only avoid for short tables (controlled inline) */
  pre, blockquote, .mermaid { page-break-inside: avoid; }
  table { page-break-inside: auto; }
  table tr { page-break-inside: avoid; page-break-after: auto; }
  table thead { display: table-header-group; }
  /* Prevent orphan headings */
  h1 + h2, h2 + h3, h3 + h4 { page-break-before: avoid; margin-top: 8pt; }
""")


def _strip_pandoc_directives(text: str) -> str:
    # \newpage from pandoc -> CSS page break
    text = re.sub(r"\\newpage", '\n<div style="page-break-after: always;"></div>\n', text)
    # YAML front-matter
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :].lstrip("\n")
    return text


def _convert_mermaid_blocks(html_text: str) -> str:
    # ```mermaid blocks survived as <pre><code class="language-mermaid">...
    pattern = re.compile(
        r'<pre[^>]*><code[^>]*class="language-mermaid"[^>]*>(.*?)</code></pre>',
        re.DOTALL,
    )

    def _repl(m: re.Match) -> str:
        body = html.unescape(m.group(1))
        return f'<div class="mermaid">\n{body}\n</div>'

    return pattern.sub(_repl, html_text)


def _render_html(md_text: str) -> str:
    md_text = _strip_pandoc_directives(md_text)
    md = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "toc",
            "attr_list",
            "def_list",
            "sane_lists",
            "abbr",
            "footnotes",
        ],
        extension_configs={"toc": {"permalink": False, "toc_depth": "2-3"}},
    )
    body = md.convert(md_text)
    body = _convert_mermaid_blocks(body)
    return body


def render_pdf(
    src: Path,
    out: Path,
    title: str,
    subtitle: str = "",
    exam_tags: list[str] | None = None,
    version: str = "2026-04",
) -> None:
    if CHROME_BIN is None:
        raise RuntimeError("google-chrome / chromium not found in PATH.")

    md_text = src.read_text(encoding="utf-8")
    body_html = _render_html(md_text)

    exam_tags = exam_tags or []
    tag_html = "".join(
        f'<span class="tag">{html.escape(t)}</span>' for t in exam_tags
    )

    full_html = HTML_TEMPLATE.format(
        title_html=html.escape(title),
        subtitle_html=html.escape(subtitle),
        exam_tags_html=tag_html,
        version_html=html.escape(version),
        css=CSS,
        body_html=body_html,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="p365_pdf_") as tmpd:
        tmp_html = Path(tmpd) / f"{src.stem}.html"
        tmp_html.write_text(full_html, encoding="utf-8")

        cmd = [
            CHROME_BIN,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--virtual-time-budget=20000",
            f"--print-to-pdf={out}",
            tmp_html.as_uri(),
        ]
        print(f"  chrome -> {out.name}")
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=180
        )
        if not out.exists():
            sys.stderr.write(result.stdout)
            sys.stderr.write(result.stderr)
            raise RuntimeError(f"chrome failed to produce {out}")


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _exam_tags_for(book: dict, manifest: dict) -> list[str]:
    fams = manifest["exam_families"]
    out: list[str] = []
    for fam in book.get("exams", []):
        out.append(fam.upper().replace("_", " "))
    return out


def build_book(book: dict, manifest: dict) -> Path:
    src = NOTES_DIR / book["src"]
    out = OUT_DIR / book["out"]
    title = book.get("title") or src.stem.replace("_", " ").title()
    subtitle = book.get("subtitle", "")
    tags = _exam_tags_for(book, manifest)
    print(f">> {book['id']}  ({src.name} -> {out.name})")
    render_pdf(src, out, title=title, subtitle=subtitle, exam_tags=tags)
    return out


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("ids", nargs="*", help="manifest book ids to build")
    p.add_argument("--all", action="store_true", help="build every manifest entry")
    p.add_argument("--list", action="store_true", help="list manifest book ids")
    p.add_argument("--src", help="one-shot mode: source markdown path")
    p.add_argument("--out", help="one-shot mode: output PDF path")
    p.add_argument("--title", default="Pariksha365 Notes")
    p.add_argument("--subtitle", default="")
    p.add_argument("--tags", default="", help="comma-separated exam tag list")
    args = p.parse_args(argv)

    if args.src:
        if not args.out:
            p.error("--out is required with --src")
        render_pdf(
            Path(args.src),
            Path(args.out),
            title=args.title,
            subtitle=args.subtitle,
            exam_tags=[t.strip() for t in args.tags.split(",") if t.strip()],
        )
        return 0

    manifest = _load_manifest()
    if args.list:
        for b in manifest["books"]:
            print(f"  {b['id']:30s} -> {b['out']}")
        return 0

    if args.all:
        targets = manifest["books"]
    else:
        ids = set(args.ids)
        targets = [b for b in manifest["books"] if b["id"] in ids]
        missing = ids - {b["id"] for b in manifest["books"]}
        if missing:
            sys.stderr.write(f"unknown book ids: {sorted(missing)}\n")
            return 2
        if not targets:
            p.error("pass at least one book id, --all, or --list")

    for b in targets:
        try:
            build_book(b, manifest)
        except Exception as exc:
            sys.stderr.write(f"!! {b['id']} failed: {exc}\n")

    print(f"\nPDFs written to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
