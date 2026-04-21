#!/usr/bin/env bash
# Build one PDF per subject book from markdown.
#
# One-time install:
#   sudo apt install pandoc texlive-xetex
#   npm install -g @mermaid-js/mermaid-cli      # optional (for diagrams)
#
# Usage:
#   ./build_pdfs.sh                 # build every subject book
#   ./build_pdfs.sh polity history  # build only those
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTES_DIR="$(dirname "$SCRIPT_DIR")"
OUT_DIR="$SCRIPT_DIR/out"
STYLE="$SCRIPT_DIR/style.css"

mkdir -p "$OUT_DIR"

if [ "$#" -eq 0 ]; then
    SUBJECTS=(polity history geography economics physics chemistry biology sci_tech general_knowledge environment)
else
    SUBJECTS=("$@")
fi

have() { command -v "$1" >/dev/null 2>&1; }
if ! have pandoc; then
    echo "pandoc not installed. Run: sudo apt install pandoc texlive-xetex" >&2
    exit 1
fi

for subj in "${SUBJECTS[@]}"; do
    src="$NOTES_DIR/${subj}.md"
    [ -f "$src" ] || { echo "skip: $subj (no ${subj}.md)"; continue; }
    out="$OUT_DIR/${subj}.pdf"
    tmp="$(mktemp --suffix=.md)"

    if have mmdc; then
        python3 "$SCRIPT_DIR/mermaid_precompile.py" "$src" "$tmp"
    else
        cp "$src" "$tmp"
    fi

    echo ">> $subj"
    pandoc "$tmp" \
        --pdf-engine=xelatex \
        --css="$STYLE" \
        -V geometry:margin=2cm \
        -V mainfont="DejaVu Sans" \
        -V fontsize=11pt \
        -V linkcolor=blue \
        -V documentclass=book \
        --toc --toc-depth=2 \
        -o "$out"
    rm -f "$tmp"
done

echo "PDFs written to $OUT_DIR/"
