#!/usr/bin/env python3
"""
Fix two classes of fraction bugs in arithmetic.md:

1. $\dfrac{X}{1}$ → just X   (whole-number ratios shouldn't be fractions)
2. Comma-mangled fractions like $\dfrac{50}{1}$,250 → $\dfrac{50}{1250}$
   and prefix versions like 72,$\dfrac{000}{12}$,000 → $\dfrac{72000}{12000}$

Also does a second-pass to catch remaining plain num/num fractions
that the first script missed (usually inside prose lines).
"""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "arithmetic.md"

# ── Fix 1: $\dfrac{N}{1}$ → N  (unless N itself is 0 or 1) ──────────────────
DFRAC_OVER_1 = re.compile(r'\$\\dfrac\{(\d+(?:\.\d+)?)\}\{1\}\$')

def fix_over_1(text: str) -> str:
    def replace(m):
        num = m.group(1)
        return num          # plain number, no LaTeX needed
    return DFRAC_OVER_1.sub(replace, text)

# ── Fix 2: suffix comma — $\dfrac{A}{B}$,DIGITS  → $\dfrac{A}{B+DIGITS}$ ───
# e.g. $\dfrac{50}{1}$,250  →  $\dfrac{50}{1250}$
SUFFIX_COMMA = re.compile(
    r'\$\\dfrac\{(\d+)\}\{(\d+)\}\$,([\d,]+)'
)

def fix_suffix_comma(text: str) -> str:
    def replace(m):
        num = m.group(1)
        den = m.group(2)
        suffix = m.group(3).replace(',', '')
        full_den = den + suffix
        if full_den == '1':
            return num
        return f'$\\dfrac{{{num}}}{{{full_den}}}$'
    # Repeat until stable (no nested matches)
    prev = None
    while prev != text:
        prev = text
        text = SUFFIX_COMMA.sub(replace, text)
    return text

# ── Fix 3: prefix comma — DIGITS,$\dfrac{A}{B}$  → $\dfrac{DIGITS+A}{B}$ ──
# e.g. 144,$\dfrac{000}{18}$  →  $\dfrac{144000}{18}$
PREFIX_COMMA = re.compile(
    r'([\d,]+),\$\\dfrac\{(\d+)\}\{(\d+)\}\$'
)

def fix_prefix_comma(text: str) -> str:
    def replace(m):
        prefix = m.group(1).replace(',', '')
        num = m.group(2)
        den = m.group(3)
        full_num = prefix + num
        if den == '1':
            return full_num
        return f'$\\dfrac{{{full_num}}}{{{den}}}$'
    prev = None
    while prev != text:
        prev = text
        text = PREFIX_COMMA.sub(replace, text)
    return text

# ── Fix 4: second-pass plain fractions (lines missed by first script) ────────
# Catches cases like "= 200/5000 ×" that didn't get converted
UNIT_SUFFIXES = re.compile(
    r'/\s*(h|hr|hour|min|minute|sec|second|day|week|month|year|km|m|cm|mm|kg|g|'
    r'litre|L|unit|person|worker|pipe|tap|man|woman|boy|girl|item|article|'
    r'rupee|Rs|₹|%|pc|sq|cu)\b',
    re.IGNORECASE
)
YEAR_RANGE = re.compile(r'\b(19|20)\d{2}/\d{2,4}\b')
ALREADY_LATEX = re.compile(r'\$[^$]+\$|\$\$.*?\$\$', re.DOTALL)
PLAIN_FRAC = re.compile(
    r'(?<![/$\w])(\d+)\s*/\s*(\d+(?:,\d+)*)(?![/$\w%])'
)

def fix_plain_fracs(text: str) -> str:
    """Convert remaining plain a/b fractions that the first script missed."""
    text, protected = _protect(text)
    text = UNIT_SUFFIXES.sub(lambda m: '\x00UNIT' + m.group(0) + '\x00', text)
    text = YEAR_RANGE.sub(lambda m: '\x00YEAR' + m.group(0) + '\x00', text)

    def conv(m):
        num = m.group(1)
        den = m.group(2).replace(',', '')
        if num == den:
            return m.group(0)
        return f'$\\dfrac{{{num}}}{{{den}}}$'

    text = PLAIN_FRAC.sub(conv, text)
    text = text.replace('\x00', '')
    text = _restore(text, protected)
    return text

def _protect(text):
    items = []
    def rep(m):
        idx = len(items)
        items.append(m.group(0))
        return f'\x00LATEX{idx}\x00'
    return ALREADY_LATEX.sub(rep, text), items

def _restore(text, items):
    for i, v in enumerate(items):
        text = text.replace(f'\x00LATEX{i}\x00', v)
    return text


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
            in_yaml = True; out.append(line); continue
        if in_yaml:
            out.append(line)
            if s == '---' and i > 0: in_yaml = False
            continue

        # Code blocks
        if s.startswith('```'):
            in_code = not in_code; out.append(line); continue
        if in_code or s.startswith('<') or s.startswith('#'):
            out.append(line); continue

        new = line
        new = fix_over_1(new)
        new = fix_suffix_comma(new)
        new = fix_prefix_comma(new)
        # Only run plain-frac pass on prose lines (not SVG attribute lines)
        if not any(tok in new for tok in ('stroke=', 'fill=', 'width=', 'height=',
                                           'viewBox', 'cx=', 'cy=', 'x1=', 'y1=')):
            new = fix_plain_fracs(new)
        if new != line:
            changed += 1
        out.append(new)

    path.write_text(''.join(out), encoding='utf-8')
    print(f'Fixed {changed} lines in {path.name}')


if __name__ == '__main__':
    import sys
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC
    process(target)
