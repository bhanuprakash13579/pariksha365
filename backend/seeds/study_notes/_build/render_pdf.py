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
<script src="{mermaid_js_uri}"></script>
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
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'neutral',
      flowchart: {{ htmlLabels: true, nodeSpacing: 28, rankSpacing: 38, curve: 'basis' }},
      fontSize: 13
    }});
  }}
  // Wait for Mermaid SVG rendering then signal Chrome ready.
  function _waitReady() {{
    var pending = document.querySelectorAll('.mermaid:not([data-processed])').length;
    if (pending === 0) {{
      document.title = document.title + ' [READY]';
    }} else {{
      setTimeout(_waitReady, 200);
    }}
  }}
  setTimeout(_waitReady, 2000);
</script>
</body>
</html>
"""

CSS = textwrap.dedent("""
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  @page { size: A4; margin: 18mm 16mm 22mm 16mm; }

  html, body {
    font-family: "Inter", "DejaVu Sans", "Noto Sans", system-ui, sans-serif;
    line-height: 1.62;
    color: #1a202c;
    font-size: 10.5pt;
  }

  body { margin: 0; }

  /* ── Cover page ── */
  .cover {
    page-break-after: always;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #6c1d5f 0%, #1e3a8a 100%);
    color: #fff !important;
  }
  .cover, .cover *,
  .cover h1, .cover h2, .cover h3, .cover h4,
  .cover .cover-title, .cover .cover-subtitle,
  .cover .brand, .cover .meta, .cover .promise,
  .cover .exam-tags, .cover .exam-tags .tag {
    color: #ffffff !important;
    border-color: rgba(255,255,255,0.5) !important;
  }
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

  /* ── PART divider pages ── */
  .part-divider {
    page-break-before: always;
    page-break-after: always;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(150deg, #1e3a5f 0%, #0f2540 100%);
    color: #fff;
    text-align: center;
  }
  .part-divider-inner { max-width: 75%; }
  .part-label {
    font-size: 10pt;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    opacity: 0.7;
    margin-bottom: 16pt;
  }
  .part-title {
    font-size: 30pt;
    font-weight: 700;
    line-height: 1.2;
    margin: 0 0 16pt 0;
    color: #fff;
    border: none;
  }
  .part-subtitle {
    font-size: 13pt;
    font-weight: 400;
    opacity: 0.85;
    font-style: italic;
    color: #e0e7ff;
  }

  .content { padding: 0; }

  /* ── Headings ── */
  h1 {
    color: #6c1d5f;
    border-bottom: 2.5px solid #6c1d5f;
    padding-bottom: 5pt;
    margin-top: 8pt;
    page-break-after: avoid;
    font-size: 19pt;
    font-weight: 700;
    letter-spacing: -0.01em;
  }
  h2 {
    color: #0f4c75;
    margin-top: 14pt;
    margin-bottom: 3pt;
    font-size: 13.5pt;
    font-weight: 600;
    page-break-after: avoid;
    border-left: 3.5pt solid #0f4c75;
    padding-left: 7pt;
  }
  h3 {
    color: #1d4ed8;
    font-size: 11.5pt;
    font-weight: 600;
    margin-top: 9pt;
    margin-bottom: 2pt;
    page-break-after: avoid;
  }
  h4 {
    color: #374151;
    font-size: 10.5pt;
    font-weight: 600;
    margin-top: 6pt;
    margin-bottom: 2pt;
    page-break-after: avoid;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-size: 9pt;
  }
  p { margin: 0 0 7pt 0; orphans: 2; widows: 2; }
  li { margin-bottom: 7pt; line-height: 1.68; orphans: 2; widows: 2; }
  ol, ul { padding-left: 22pt; margin: 5pt 0 10pt 0; }
  ol > li { margin-bottom: 9pt; }
  /* Nested lists — slightly tighter */
  li > ul, li > ol { margin-top: 4pt; margin-bottom: 2pt; }
  li > ul > li, li > ol > li { margin-bottom: 4pt; }
  h1 + *, h2 + *, h3 + *, h4 + * { page-break-before: avoid; }

  /* ── Plain blockquote (narrative / italic aside) ── */
  blockquote {
    background: #fff7ed;
    border-left: 3px solid #f97316;
    padding: 6pt 12pt;
    margin: 10pt 0;
    font-style: italic;
    color: #7c2d12;
  }

  pre, code {
    font-family: "JetBrains Mono", "DejaVu Sans Mono", "Menlo", monospace;
    font-size: 9.2pt;
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

  /* ── Step-by-step computation box ── */
  .steps {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-left: 4pt solid #0369a1;
    border-radius: 4pt;
    padding: 8pt 14pt;
    margin: 7pt 0;
    font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
    font-size: 9.5pt;
    line-height: 1.80;
    page-break-inside: avoid;
  }
  .steps p { margin: 0 0 8pt 0; }
  .steps ol, .steps ul { margin: 4pt 0 8pt 0; }
  .steps li { margin-bottom: 6pt; }
  .steps strong { color: #0369a1; }
  .steps code { background: none; padding: 0; font-size: 9.5pt; }
  /* Inline annotation inside step blocks — subtle grey italic */
  .steps em { color: #6b7280; font-style: italic; font-size: 8.5pt; }

  /* ── Method A / Method B sub-boxes (inside .worked) ── */
  .method-a, .method-b {
    padding: 6pt 10pt;
    margin: 6pt 0 4pt 0;
    border-radius: 0 3pt 3pt 0;
    page-break-inside: avoid;
  }
  .method-a { border-left: 3.5pt solid #16a34a; background: #f0fdf4; }
  .method-b { border-left: 3.5pt solid #ea580c; background: #fff7ed; }
  .method-a::before {
    content: "\\25B6  METHOD A \\2014  Standard (safe every time)";
    display: block; font-size: 7.8pt; font-weight: 700;
    letter-spacing: 0.05em; color: #15803d; margin-bottom: 3pt;
  }
  .method-b::before {
    content: "\\26A1  METHOD B \\2014  Exam Shortcut";
    display: block; font-size: 7.8pt; font-weight: 700;
    letter-spacing: 0.05em; color: #c2410c; margin-bottom: 3pt;
  }

  /* ── Tables ── */
  table {
    border-collapse: collapse;
    margin: 8pt 0;
    width: 100%;
    font-size: 9.5pt;
    page-break-inside: auto;
    font-variant-numeric: tabular-nums;
  }
  table tr { page-break-inside: avoid; page-break-after: auto; }
  table thead { display: table-header-group; }
  table th, table td {
    border: 1px solid #94a3b8;
    padding: 4.5pt 8pt;
    text-align: left;
    vertical-align: top;
  }
  table th {
    background: #dbeafe;
    font-weight: 600;
    color: #1e3a8a;
    letter-spacing: 0.02em;
    font-size: 9pt;
  }
  /* Alternating row tint */
  table tbody tr:nth-child(even) td { background: #f8fafc; }

  hr { border: 0; border-top: 1px dashed #94a3b8; margin: 14pt 0; }

  /* ── Callout boxes — EPFO-style with labeled color header bars ── */
  /* Shared rules for all labeled callout boxes */
  .intuition, .definition, .formula, .worked, .examtip,
  .keypoint, .mnemonic, .pitfall, .pyq {
    border-radius: 4pt;
    margin: 12pt 0;
    overflow: hidden;
    page-break-inside: avoid;
  }
  /* Shared ::before label bar */
  .intuition::before, .definition::before, .formula::before,
  .worked::before, .examtip::before, .keypoint::before,
  .mnemonic::before, .pitfall::before, .pyq::before {
    display: block;
    padding: 4pt 12pt;
    font-weight: 700;
    font-size: 8pt;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #ffffff;
  }

  /* Quick Recall (teal) */
  .intuition {
    background: #e6f7f5;
    border: 1px solid #0d9488;
    padding: 8pt 12pt;
    color: #134e4a;
  }
  .intuition::before {
    content: "\\2714  Quick Recall";
    background: #0d9488;
    margin: -8pt -12pt 8pt -12pt;
  }
  .intuition strong { color: #0f766e; }

  /* Definition (indigo) */
  .definition {
    background: #eef2ff;
    border: 1px solid #4f46e5;
    padding: 8pt 12pt;
    color: #1e1b4b;
  }
  .definition::before {
    content: "\\25B6  Definition";
    background: #4f46e5;
    margin: -8pt -12pt 8pt -12pt;
  }
  .definition strong { color: #3730a3; }

  /* Formula / Key Points (purple) */
  .formula {
    background: #faf5ff;
    border: 1px solid #7c3aed;
    padding: 8pt 12pt;
    color: #3b0764;
  }
  .formula::before {
    content: "\\25C6  Formula / Key Points";
    background: #7c3aed;
    margin: -8pt -12pt 8pt -12pt;
  }
  .formula strong { color: #6d28d9; }

  /* Worked Example (forest green) */
  .worked {
    background: #f0fdf4;
    border: 1px solid #16a34a;
    padding: 8pt 12pt;
    color: #14532d;
  }
  .worked::before {
    content: "\\270E  Worked Example";
    background: #16a34a;
    margin: -8pt -12pt 8pt -12pt;
  }
  .worked strong { color: #15803d; }

  /* Exam Alert (amber) */
  .examtip {
    background: #fffbeb;
    border: 1px solid #b45309;
    padding: 8pt 12pt;
    color: #78350f;
  }
  .examtip::before {
    content: "\\26A0  Exam Alert";
    background: #b45309;
    margin: -8pt -12pt 8pt -12pt;
  }
  .examtip strong { color: #92400e; }

  /* Key Fact (sky blue) */
  .keypoint {
    background: #f0f9ff;
    border: 1px solid #0284c7;
    padding: 8pt 12pt;
    color: #0c4a6e;
  }
  .keypoint::before {
    content: "\\2714  Key Fact";
    background: #0284c7;
    margin: -8pt -12pt 8pt -12pt;
  }
  .keypoint strong { color: #0369a1; }

  /* Mnemonic (medium green) */
  .mnemonic, blockquote.mnemonic {
    background: #f0fdf4;
    border: 1px solid #16a34a;
    padding: 8pt 12pt;
    margin: 12pt 0;
    color: #14532d;
    font-style: normal;
    overflow: hidden;
    border-radius: 4pt;
  }
  .mnemonic::before, blockquote.mnemonic::before {
    content: "\\25CE  Mnemonic";
    display: block;
    background: #16a34a;
    color: #fff;
    padding: 4pt 12pt;
    margin: -8pt -12pt 8pt -12pt;
    font-weight: 700;
    font-size: 8pt;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  /* Common Trap (red) */
  .pitfall, blockquote.pitfall {
    background: #fef2f2;
    border: 1px solid #dc2626;
    padding: 8pt 12pt;
    margin: 12pt 0;
    color: #7f1d1d;
    font-style: normal;
    overflow: hidden;
    border-radius: 4pt;
  }
  .pitfall::before, blockquote.pitfall::before {
    content: "\\2715  Common Trap";
    display: block;
    background: #dc2626;
    color: #fff;
    padding: 4pt 12pt;
    margin: -8pt -12pt 8pt -12pt;
    font-weight: 700;
    font-size: 8pt;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .pitfall strong, blockquote.pitfall strong { color: #b91c1c; }

  /* PYQ / Exam Question (blue) */
  .pyq {
    background: #eff6ff;
    border: 1px solid #3b82f6;
    padding: 6pt 10pt;
    color: #1e3a8a;
    font-size: 10pt;
  }
  .pyq::before {
    content: "\\25C7  Exam-Style Question";
    background: #3b82f6;
    margin: -6pt -10pt 6pt -10pt;
  }

  img, svg { max-width: 100%; height: auto; }
  .mermaid { text-align: center; margin: 12pt 0; }

  /* ── Chapter Summary tree wrapper ── */
  .chapter-summary {
    border: 1.5pt solid #7c3aed;
    border-radius: 5pt;
    overflow: hidden;
    margin: 14pt 0 6pt 0;
    page-break-inside: avoid;
  }
  .chapter-summary::before {
    content: "\\25CE  Chapter Summary \\2014  Everything in One View";
    display: block;
    background: #7c3aed;
    color: #ffffff;
    padding: 4pt 12pt;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .chapter-summary .mermaid {
    padding: 6pt 4pt;
    background: #faf5ff;
    margin: 0;
  }

  /* ── Page break controls ── */
  h1 { page-break-before: always; }
  h1:first-of-type { page-break-before: avoid; }
  pre, .mermaid { page-break-inside: avoid; }
  blockquote { page-break-inside: avoid; }
  table { page-break-inside: auto; }
  table tr { page-break-inside: avoid; page-break-after: auto; }
  table thead { display: table-header-group; }
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


def _protect_math(text: str) -> tuple[str, dict]:
    """Stash $...$ and $$...$$ spans so markdown can't mangle underscores/asterisks inside them."""
    placeholders: dict[str, str] = {}
    counter = [0]

    def _store(m: re.Match) -> str:
        key = f"XMATHPH{counter[0]}X"
        counter[0] += 1
        placeholders[key] = m.group(0)
        return key

    # Escape currency dollar signs ($123, $4.5B, $700 billion, etc.) BEFORE LaTeX detection
    # so they are never mistaken for LaTeX delimiters.
    text = re.sub(r"\$(?=[\d~])", "&#36;", text)

    # Display math first ($$...$$, possibly multi-line), then inline ($...$)
    text = re.sub(r"\$\$.*?\$\$", _store, text, flags=re.DOTALL)
    text = re.sub(r"\$[^\$\n]+?\$", _store, text)
    return text, placeholders


def _restore_math(html_text: str, placeholders: dict) -> str:
    for key, value in placeholders.items():
        html_text = html_text.replace(key, value)
    return html_text


_MD_DIV_CLASSES = (
    "steps", "method-a", "method-b", "worked", "examtip", "keypoint",
    "mnemonic", "pitfall", "pyq", "intuition", "definition", "formula",
    "chapter-summary", "part-divider",
)

def _inject_markdown_attr(text: str) -> str:
    """Add markdown="block" to our custom callout divs so Python-Markdown
    processes **bold** / *italic* / tables inside them correctly."""
    pattern = re.compile(
        r'(<div\s+class="('
        + "|".join(re.escape(c) for c in _MD_DIV_CLASSES)
        + r')")',
    )
    return pattern.sub(r'\1 markdown="block"', text)


def _render_html(md_text: str) -> str:
    md_text = _strip_pandoc_directives(md_text)
    md_text = _inject_markdown_attr(md_text)
    # Protect math spans before markdown processes emphasis/italic markers
    md_text, placeholders = _protect_math(md_text)
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
            "md_in_html",
        ],
        extension_configs={"toc": {"permalink": False, "toc_depth": "2-3"}},
    )
    body = md.convert(md_text)
    body = _restore_math(body, placeholders)
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

    # Dynamic per-book page footer (title + page number + verification year)
    footer_title = title.replace('"', '\\"').replace("\\", "\\\\")
    footer_css = (
        f"@page {{\n"
        f"  @bottom-center {{\n"
        f"    content: \"{footer_title}  ·  Page \" counter(page) \"  ·  Verified 2026\";\n"
        f"    font-size: 7.5pt;\n"
        f"    color: #6b7280;\n"
        f"    font-family: 'DejaVu Sans', sans-serif;\n"
        f"    border-top: 0.5pt solid #e5e7eb;\n"
        f"    padding-top: 3pt;\n"
        f"  }}\n"
        f"}}\n"
        f"@page:first {{\n"
        f"  @bottom-center {{ content: \"\"; }}\n"
        f"}}\n"
    )

    # Use local Mermaid.js (CDN may be unavailable in headless environment)
    local_mermaid = SCRIPT_DIR / "lib" / "mermaid.min.js"
    mermaid_uri = local_mermaid.as_uri() if local_mermaid.exists() else "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"

    full_html = HTML_TEMPLATE.format(
        title_html=html.escape(title),
        subtitle_html=html.escape(subtitle),
        exam_tags_html=tag_html,
        version_html=html.escape(version),
        css=CSS + footer_css,
        body_html=body_html,
        mermaid_js_uri=mermaid_uri,
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
            "--virtual-time-budget=30000",
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
