"""Pre-compile fenced mermaid blocks in a markdown file to SVG + rewrite the
block to an image reference. Used by build_pdfs.sh so that pandoc (which does
not natively render mermaid) gets real diagrams in the output PDF.

Requires the ``mmdc`` CLI from ``@mermaid-js/mermaid-cli`` on PATH.

Usage:
    python3 mermaid_precompile.py <input.md> <output.md>
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

_FENCE_RE = re.compile(
    r"^```mermaid\s*$(?P<body>.*?)^```\s*$",
    re.MULTILINE | re.DOTALL,
)


def _hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]


def main(inp: str, outp: str) -> int:
    src = Path(inp).read_text(encoding="utf-8")
    out_dir = Path(outp).parent / "_mermaid_svg"
    out_dir.mkdir(parents=True, exist_ok=True)

    if shutil.which("mmdc") is None:
        # No mermaid CLI: pass through unchanged. pandoc will emit the block as
        # code verbatim; PDF will still build, just without rendered diagrams.
        Path(outp).write_text(src, encoding="utf-8")
        return 0

    def replace(match: re.Match) -> str:
        body = match.group("body").strip()
        sha = _hash(body)
        svg_in = out_dir / f"{sha}.mmd"
        svg_out = out_dir / f"{sha}.svg"
        if not svg_out.exists():
            svg_in.write_text(body, encoding="utf-8")
            try:
                subprocess.run(
                    ["mmdc", "-i", str(svg_in), "-o", str(svg_out), "-b", "transparent"],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                # On failure, keep original block so content isn't lost
                return match.group(0)
        return f"![diagram]({svg_out.as_posix()})\n"

    new_src = _FENCE_RE.sub(replace, src)
    Path(outp).write_text(new_src, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
