#!/usr/bin/env python3
"""
Convert all plain-text fractions in arithmetic.md to proper LaTeX \dfrac notation.

Rules:
- Convert: 100/120, 1/2, x/y in formulas → $\dfrac{100}{120}$
- SKIP: km/h, m/s, km/hr, per/day type units
- SKIP: year ranges like 2024/25, 2025/26
- SKIP: page refs like p5/6
- SKIP: already inside $...$ or $$...$$ blocks
- SKIP: URL paths (http://, /api/, etc.)
- SKIP: markdown headings
- SKIP: table separator rows (---|---)
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "arithmetic.md"

# Units that should NOT be converted
UNIT_SUFFIXES = re.compile(
    r"/\s*(h|hr|hour|min|minute|sec|second|day|week|month|year|km|m|cm|mm|kg|g|"
    r"litre|L|unit|person|worker|pipe|tap|man|woman|boy|girl|item|article|"
    r"rupee|Rs|₹|%|pc|sq|cu)\b",
    re.IGNORECASE
)

# Year ranges like 2024/25
YEAR_RANGE = re.compile(r"\b(19|20)\d{2}/\d{2,4}\b")

# Page refs like p5/6 or p.30/31
PAGE_REF = re.compile(r"\bp[\.\s]?\d+/\d+\b", re.IGNORECASE)

# Already inside LaTeX
LATEX_BLOCK = re.compile(r"\$\$.*?\$\$|\$[^$]+\$", re.DOTALL)

# The main fraction pattern: integer or simple expression / integer
# Captures: numerator (digits possibly with space), slash, denominator (digits)
FRACTION_PAT = re.compile(
    r"(?<![/$\w])(\d+(?:\s*\.\s*\d+)?)\s*/\s*(\d+(?:\s*\.\s*\d+)?)(?![/$\w%])"
)

# Variable fraction: word/number or number/word
VAR_FRAC_PAT = re.compile(
    r"(?<![/$\w])([A-Za-z_]\w*)\s*/\s*(\d+)(?![/$\w%])"
)


def should_skip_line(line: str) -> bool:
    stripped = line.strip()
    # Table separator
    if re.match(r"^\|?[\s\-\|:]+\|", stripped):
        return False  # still process tables for fractions
    # Headings
    if stripped.startswith("#"):
        return True
    # Code blocks / HTML divs (don't touch)
    if stripped.startswith("```") or stripped.startswith("<") or stripped.startswith(">"):
        return True
    # YAML front-matter
    if stripped == "---" or stripped == "...":
        return True
    return False


def protect_latex(text: str) -> tuple[str, list[str]]:
    """Replace LaTeX blocks with placeholders so we don't double-convert."""
    protected: list[str] = []
    def replacer(m):
        idx = len(protected)
        protected.append(m.group(0))
        return f"\x00LATEX{idx}\x00"
    result = LATEX_BLOCK.sub(replacer, text)
    return result, protected


def restore_latex(text: str, protected: list[str]) -> str:
    for i, orig in enumerate(protected):
        text = text.replace(f"\x00LATEX{i}\x00", orig)
    return text


def convert_fractions(text: str) -> str:
    # Protect existing LaTeX
    text, protected = protect_latex(text)

    # Protect unit fractions (km/h etc)
    unit_holders: list[str] = []
    def protect_unit(m):
        idx = len(unit_holders)
        unit_holders.append(m.group(0))
        return f"\x00UNIT{idx}\x00"
    text = UNIT_SUFFIXES.sub(protect_unit, text)

    # Protect year ranges
    year_holders: list[str] = []
    def protect_year(m):
        idx = len(year_holders)
        year_holders.append(m.group(0))
        return f"\x00YEAR{idx}\x00"
    text = YEAR_RANGE.sub(protect_year, text)

    # Protect page refs
    page_holders: list[str] = []
    def protect_page(m):
        idx = len(page_holders)
        page_holders.append(m.group(0))
        return f"\x00PAGE{idx}\x00"
    text = PAGE_REF.sub(protect_page, text)

    # Convert numeric fractions: 100/120 → $\dfrac{100}{120}$
    def convert_num_frac(m):
        num = m.group(1).strip()
        den = m.group(2).strip()
        # Skip trivial like 1/1
        if num == den:
            return m.group(0)
        return f"$\\dfrac{{{num}}}{{{den}}}$"
    text = FRACTION_PAT.sub(convert_num_frac, text)

    # Restore all protections
    for i, orig in enumerate(page_holders):
        text = text.replace(f"\x00PAGE{i}\x00", orig)
    for i, orig in enumerate(year_holders):
        text = text.replace(f"\x00YEAR{i}\x00", orig)
    for i, orig in enumerate(unit_holders):
        text = text.replace(f"\x00UNIT{i}\x00", orig)
    text = restore_latex(text, protected)
    return text


def process_file(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out_lines: list[str] = []
    in_code_block = False
    in_yaml = False
    changed = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # YAML front-matter
        if i == 0 and stripped == "---":
            in_yaml = True
            out_lines.append(line)
            continue
        if in_yaml:
            out_lines.append(line)
            if stripped == "---" and i > 0:
                in_yaml = False
            continue

        # Code block toggle
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            out_lines.append(line)
            continue
        if in_code_block:
            out_lines.append(line)
            continue

        # Skip headings and HTML
        if should_skip_line(line):
            out_lines.append(line)
            continue

        new_line = convert_fractions(line)
        if new_line != line:
            changed += 1
        out_lines.append(new_line)

    path.write_text("".join(out_lines), encoding="utf-8")
    return changed


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC
    if not target.exists():
        print(f"File not found: {target}")
        sys.exit(1)
    n = process_file(target)
    print(f"Converted {n} lines with fraction changes in {target.name}")
