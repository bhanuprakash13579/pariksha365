"""Quality gates for autonomously-generated batches.

A gate returns (ok: bool, issues: list[str]). The driver only accepts a
batch when every gate passes. Soft warnings are returned as ok=True with
non-empty issues — driver logs them but proceeds.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

from .canonical import CANONICAL_SUBJECT, to_schema_a

_BACKEND = Path(__file__).resolve().parents[2]
_POOL = _BACKEND / "seeds" / "static_gk"

# --- Gate 1: schema/structure --- ------------------------------------------

REQUIRED_BUNDLE_FIELDS = ("subject", "topic", "topic_code", "questions")
REQUIRED_Q_FIELDS = ("stem", "options", "correct_letter", "difficulty", "explanation")


def gate_schema(bundle: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    for f in REQUIRED_BUNDLE_FIELDS:
        if not bundle.get(f):
            issues.append(f"bundle missing {f}")
    if bundle.get("subject") not in CANONICAL_SUBJECT.values():
        issues.append(f"non-canonical subject: {bundle.get('subject')!r}")
    qs = bundle.get("questions") or []
    if len(qs) != 7:
        issues.append(f"expected 7 questions, got {len(qs)}")
    for i, q in enumerate(qs, 1):
        for f in REQUIRED_Q_FIELDS:
            if not q.get(f):
                issues.append(f"Q{i}: missing {f}")
        opts = q.get("options") or []
        if len(opts) != 4:
            issues.append(f"Q{i}: expected 4 options, got {len(opts)}")
        correct_count = sum(1 for o in opts if isinstance(o, dict) and o.get("is_correct"))
        if correct_count != 1:
            issues.append(f"Q{i}: must have exactly 1 correct option (got {correct_count})")
        if q.get("correct_letter") not in ("A", "B", "C", "D"):
            issues.append(f"Q{i}: correct_letter must be A/B/C/D, got {q.get('correct_letter')!r}")
        if len((q.get("stem") or "").strip()) < 25:
            issues.append(f"Q{i}: stem too short ({len((q.get('stem') or '').strip())} chars)")
        if len((q.get("explanation") or "").strip()) < 30:
            issues.append(f"Q{i}: explanation too short — must justify the answer")
    return (not issues, issues)


# --- Gate 2: difficulty distribution --- -----------------------------------

# Allow either 2/3/2 (canonical per-file shape) or 2/4/1 (closer to pool 30/50/20).
_ALLOWED_DIFF_SHAPES = {(2, 3, 2), (2, 4, 1), (3, 3, 1)}


def gate_difficulty(bundle: dict) -> tuple[bool, list[str]]:
    qs = bundle.get("questions") or []
    counts = {"EASY": 0, "MEDIUM": 0, "HARD": 0}
    for q in qs:
        d = (q.get("difficulty") or "").upper()
        if d in counts:
            counts[d] += 1
    shape = (counts["EASY"], counts["MEDIUM"], counts["HARD"])
    if shape not in _ALLOWED_DIFF_SHAPES:
        return (False, [f"difficulty shape {shape} not in {_ALLOWED_DIFF_SHAPES}"])
    return (True, [])


# --- Gate 3: option-length parity --- --------------------------------------

_LETTERS = ("A", "B", "C", "D", "E")
_PARITY_RATIO_LIMIT = 1.40


def gate_parity(bundle: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    for i, q in enumerate(bundle.get("questions") or [], 1):
        opts = q.get("options") or []
        lens = [len((o.get("option_text") or "")) for o in opts if isinstance(o, dict)]
        if not lens or min(lens) == 0:
            issues.append(f"Q{i}: empty option text")
            continue
        try:
            ci = _LETTERS.index(q.get("correct_letter") or "")
        except ValueError:
            ci = -1
        if ci < 0 or ci >= len(lens):
            issues.append(f"Q{i}: correct_letter unresolvable for parity check")
            continue
        clen = lens[ci]
        wmin = min(l for j, l in enumerate(lens) if j != ci)
        if wmin == 0:
            issues.append(f"Q{i}: empty wrong-option text")
            continue
        ratio = clen / wmin
        if ratio >= _PARITY_RATIO_LIMIT:
            issues.append(f"Q{i}: parity ratio {ratio:.2f} ≥ {_PARITY_RATIO_LIMIT} "
                          f"(correct={clen}, min_wrong={wmin})")
    return (not issues, issues)


# --- Gate 4: style (tier tags, absolute language, namesake) --- ------------

_TIER_TAG = re.compile(r"\[(Clerk|CGL|CHSL|Tier\s*\d|Prelims|Mains)[^\]]*\]", re.I)
_ABS_LANG = re.compile(r"\b(always|never|all of the above|none of the above)\b", re.I)


def gate_style(bundle: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    for i, q in enumerate(bundle.get("questions") or [], 1):
        stem = q.get("stem") or ""
        if _TIER_TAG.search(stem):
            issues.append(f"Q{i}: stem contains visible tier/section tag")
        for j, o in enumerate(q.get("options") or []):
            text = (o.get("option_text") or "") if isinstance(o, dict) else ""
            if _ABS_LANG.search(text):
                issues.append(f"Q{i}.{_LETTERS[j]}: option uses absolute/cop-out language")
    return (not issues, issues)


# --- Gate 5: dedup vs pool (uses normalised stem signatures) --- -----------

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)


def _norm_stem(raw: str, max_len: int = 160) -> str:
    s = (raw or "").lower()
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s[:max_len]


_STEM_SIG_CACHE: set[str] | None = None


def _load_pool_stem_sigs() -> set[str]:
    global _STEM_SIG_CACHE
    if _STEM_SIG_CACHE is not None:
        return _STEM_SIG_CACHE
    sigs: set[str] = set()
    for f in _POOL.rglob("*.json"):
        if f.name.startswith("_"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        questions = d if isinstance(d, list) else (d.get("questions") or [])
        for q in questions:
            if not isinstance(q, dict):
                continue
            stem = q.get("stem") or q.get("text") or ""
            if stem:
                sigs.add(_norm_stem(stem))
    # Also include production-DB signatures if available
    dedup_path = _BACKEND / "seeds" / "_dedup" / "existing_quiz_signatures.json"
    if dedup_path.exists():
        try:
            doc = json.loads(dedup_path.read_text())
            for s in doc.get("stem_signatures") or []:
                sigs.add(s)
        except Exception:
            pass
    _STEM_SIG_CACHE = sigs
    return sigs


def gate_dedup(bundle: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    pool = _load_pool_stem_sigs()
    seen_in_batch: set[str] = set()
    for i, q in enumerate(bundle.get("questions") or [], 1):
        sig = _norm_stem(q.get("stem") or "")
        if not sig:
            continue
        if sig in pool:
            issues.append(f"Q{i}: dup stem already in pool: {sig[:60]!r}")
        elif sig in seen_in_batch:
            issues.append(f"Q{i}: dup stem within this batch")
        seen_in_batch.add(sig)
    return (not issues, issues)


# --- Composite gate runner --- ---------------------------------------------

GATES: list[tuple[str, Callable]] = [
    ("schema", gate_schema),
    ("difficulty", gate_difficulty),
    ("parity", gate_parity),
    ("style", gate_style),
    ("dedup", gate_dedup),
]


def run_all_gates(bundle: dict) -> dict:
    bundle_a = {
        "subject": bundle.get("subject"),
        "topic": bundle.get("topic"),
        "topic_code": bundle.get("topic_code"),
        "questions": [to_schema_a(q) for q in bundle.get("questions") or []],
    }
    bundle_a["subject"] = (CANONICAL_SUBJECT.get(bundle_a["subject"] or "")
                           or bundle_a["subject"])
    report: dict = {"ok": True, "results": {}}
    for name, fn in GATES:
        ok, issues = fn(bundle_a)
        report["results"][name] = {"ok": ok, "issues": issues}
        if not ok:
            report["ok"] = False
    report["normalised_bundle"] = bundle_a
    return report


def main() -> int:
    import argparse, sys
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="Bundle JSON to validate")
    args = ap.parse_args()
    bundle = json.loads(Path(args.file).read_text())
    rep = run_all_gates(bundle)
    print(f"OVERALL: {'PASS' if rep['ok'] else 'FAIL'}")
    for name, res in rep["results"].items():
        sym = "✓" if res["ok"] else "✗"
        print(f"  {sym} {name}: {len(res['issues'])} issue(s)")
        for iss in res["issues"][:5]:
            print(f"      - {iss}")
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
