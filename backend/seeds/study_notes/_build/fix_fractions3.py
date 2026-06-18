#!/usr/bin/env python3
"""
Third-pass fraction fixer for arithmetic.md.
Converts plain num/den fractions to $\dfrac{num}{den}$ LaTeX.

Protection strategy: split each line on existing $...$ boundaries.
Only plain-text segments (between LaTeX blocks) are processed.
No null-byte markers needed — no artifacts possible.

Skips:
  - Heading lines (start with #)
  - Code blocks (between ```)
  - SVG attribute lines
  - Year ranges like 2024/25 or 2024/2025
  - Lines with only whitespace
"""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "arithmetic.md"

# Matches plain a/b with optional commas in digits (e.g. 1,000/500)
# Lookbehind: not preceded by /$\w or . (the . prevents matching partial decimals like 0.25/1.25)
# Lookahead: not followed by /$\w%. (the . prevents matching 600/1.20 where 1.20 is decimal)
PLAIN_FRAC = re.compile(
    r'(?<![/$\w.])(\d[\d,]*)(\s*/\s*)(\d[\d,]*)(?![/$\w%.])'
)

# Matches existing LaTeX inline math (both $...$ and $$...$$)
# We split lines on this to protect already-converted fracs
LATEX_BLOCK = re.compile(r'\$\$[^$]+\$\$|\$[^$\n]+\$')

# Year ranges like 2024/25, 2023/24, 1999/2000
YEAR_RANGE = re.compile(
    r'^((?:19|20)\d{2})\s*/\s*(\d{2}|\d{4})$'
)

SVG_TOKENS = ('stroke=', 'fill=', 'width=', 'height=', 'viewBox',
              'cx=', 'cy=', 'x1=', 'y1=', 'x2=', 'y2=', 'rx=', 'ry=')


def try_convert(num_raw: str, den_raw: str, original: str) -> str:
    num = num_raw.replace(',', '')
    den = den_raw.replace(',', '')

    # Skip trivial 1/1 only if it literally looks like a ratio label (not a real frac)
    # Actually 1/1 = 100%, fine to keep as-is or convert; keep as-is to avoid cluttering table
    if num == den and num == '1':
        return original

    # Skip year ranges
    combined = num_raw.strip() + '/' + den_raw.strip()
    if YEAR_RANGE.match(combined):
        return original

    # Skip denomiator of 0
    if den == '0':
        return original

    return f'$\\dfrac{{{num}}}{{{den}}}$'


def fix_plain_in_text(text: str) -> str:
    """Fix plain fractions in a plain-text segment (no existing LaTeX inside)."""
    def replace(m):
        return try_convert(m.group(1), m.group(3), m.group(0))
    return PLAIN_FRAC.sub(replace, text)


def fix_line(line: str) -> str:
    """Split on existing LaTeX blocks, fix plain segments, rejoin."""
    parts = LATEX_BLOCK.split(line)
    latex_parts = LATEX_BLOCK.findall(line)

    result = []
    for i, plain in enumerate(parts):
        result.append(fix_plain_in_text(plain))
        if i < len(latex_parts):
            result.append(latex_parts[i])  # keep LaTeX unchanged
    return ''.join(result)


def process(path: Path) -> None:
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
    out = []
    in_code = False
    in_yaml = False
    changed = 0

    for i, line in enumerate(lines):
        s = line.strip()

        # YAML front matter
        if i == 0 and s == '---':
            in_yaml = True
            out.append(line)
            continue
        if in_yaml:
            out.append(line)
            if s == '---' and i > 0:
                in_yaml = False
            continue

        # Code blocks — pass through verbatim
        if s.startswith('```'):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue

        # Headings — skip (fraction labels like "1/2" in headings should stay)
        if s.startswith('#'):
            out.append(line)
            continue

        # SVG attribute lines — skip
        if any(tok in line for tok in SVG_TOKENS):
            out.append(line)
            continue

        new = fix_line(line)
        if new != line:
            changed += 1
        out.append(new)

    path.write_text(''.join(out), encoding='utf-8')
    print(f'Fixed {changed} lines in {path.name}')


if __name__ == '__main__':
    import sys
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC
    process(target)
