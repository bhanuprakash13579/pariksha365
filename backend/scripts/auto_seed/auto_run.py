"""
Autonomous question generator — calls `claude --print` as a subprocess per topic.

WHY: When Claude Code generates questions inline, every bundle goes into the
conversation context. After 50–100 topics the context hits 1M tokens and the
session dies. This script moves all generation into fresh child processes so
the parent session stays lean regardless of how many topics are generated.

DEDUP: gate_dedup() fires on every apply() call, checking every new stem
against all pool stems + production-DB signatures. Cache resets between waves.
Run verify_batch_dedup.py before commits for the Jaccard-similarity pass.

SPEED: --workers N runs N topics in parallel (default 4).

Usage (from backend/):
    python3 -m scripts.auto_seed.auto_run                     # 10 topics/wave, 4 workers
    python3 -m scripts.auto_seed.auto_run --topics 20         # 20 per wave
    python3 -m scripts.auto_seed.auto_run --topics 5 --target 20000
    python3 -m scripts.auto_seed.auto_run --dry-run           # validate plumbing only
"""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .apply import apply
from .brief import make_brief
from .state import scan_pool

_BACKEND = Path(__file__).resolve().parents[2]
_STATE_OUT = _BACKEND / "scripts" / "auto_seed" / "state.json"
_APPLY_LOCK = threading.Lock()

MODEL_ALIASES: dict[str, str] = {
    "sonnet": "claude-sonnet-4-6",
    "opus":   "claude-opus-4-8",
    "haiku":  "claude-haiku-4-5-20251001",
}

# ──────────────────────────────────────────────────────────────────────────────
# Generation prompt
# ──────────────────────────────────────────────────────────────────────────────
_PROMPT = """\
You are an experienced paper-setter for Indian competitive examinations
(SSC CGL, CHSL, IBPS PO/Clerk, SBI PO/Clerk, RRB NTPC, State PSC).

Generate exactly 7 MCQ questions for the topic below.
Output ONLY valid JSON — no prose, no markdown fences, no code blocks.

═══════════════════════════════════════════
TOPIC CODE : {topic_code}
SUBJECT    : {subject}
TOPIC      : {topic}
HIGH WEIGHT: {high_weight}
HINT       : {exam_hint}
═══════════════════════════════════════════

ALREADY-ASKED STEMS — generate completely different angles, NEVER paraphrase:
{existing_stems}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIFFICULTY (strict order):
  Q1–Q2 : EASY
  Q3–Q5 : MEDIUM
  Q6–Q7 : HARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MANDATORY QUALITY RULES — violating any one will cause REJECTION:

① NO VALUE-SUBSTITUTION CLONES (most common mistake):
   For QUANT/REASONING topics: each question must test a DIFFERENT application
   or concept angle. Do NOT take an existing problem structure and swap numbers.
   Examples of VARIETY required for percentage questions:
     BAD: Q1 "A is 20% more than B" → Q2 "A is 25% more than B" (same structure!)
     GOOD: Q1 = reverse-percentage, Q2 = population growth, Q3 = mixture ratio,
           Q4 = successive discounts, Q5 = percentage of a percentage, etc.
   For STATIC topics: each question must cover a genuinely different sub-topic
   or angle (not the same fact reworded with different choices).

② OPTION LENGTH PARITY (second most common failure):
   All 4 options MUST be 20–90 characters each.
   After writing all 4 options: correct_option_length / shortest_wrong_option ≤ 1.25
   For vocabulary/synonym/antonym questions: write options as 4–7 word phrases,
     e.g. "exceedingly careful and precise" not just "careful".
   For short factual options (dates, names, numbers): pad with context,
     e.g. "1857 (First War of Independence)" not just "1857".
   Single-word options are FORBIDDEN unless ALL 4 are under 12 chars AND equal.

③ NO ABSOLUTE LANGUAGE IN OPTIONS:
   Never write "all of the above", "none of the above", "always", "never" as options.

④ EXAMINER MINDSET — each question must:
   • Be genuinely plausible in the next exam paper (not trivial, not obscure trivia)
   • Have distractors that represent specific real misunderstandings, not random noise
   • For hard questions: require multi-step reasoning or precise recall
   • Cover PYQ-high-hit angles: GI tags, constitutional articles, folk arts, tribal
     cultures, scientific terminology, niche historical events

⑤ EXPLANATION:
   • ≥ 30 characters
   • Justify why the correct answer is right
   • Explain why the most tempting distractor is wrong

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OUTPUT FORMAT (Schema A — output ONLY this JSON, nothing else):
{{
  "subject": "{subject}",
  "topic": "{topic}",
  "topic_code": "{topic_code}",
  "questions": [
    {{
      "stem": "Question stem ending with ?",
      "options": [
        {{"option_text": "Option A — 20 to 90 chars", "is_correct": false}},
        {{"option_text": "Option B — 20 to 90 chars", "is_correct": true}},
        {{"option_text": "Option C — 20 to 90 chars", "is_correct": false}},
        {{"option_text": "Option D — 20 to 90 chars", "is_correct": false}}
      ],
      "correct_letter": "B",
      "difficulty": "EASY",
      "explanation": "B is correct because... Option A is wrong because..."
    }}
  ]
}}"""

# Retry prompts for self-correction before hitting the gate
_PARITY_RETRY_PROMPT = """\
The previous bundle failed the OPTION LENGTH PARITY check.
Failing questions: {issues}

Rule: correct_option_length / min(wrong_option_lengths) must be ≤ 1.35.
Fix: rewrite SHORT wrong options to match the correct option's length. Do NOT
change stems, correct answers, or explanations. Add context or qualifiers to
short options — e.g. "1857" → "1857 (Sepoy Mutiny year)".
For vocabulary/synonym: expand single-word options to 4–6 word phrases
describing what the word means or how it is used.

Output ONLY the corrected JSON bundle in Schema A format.

Original bundle:
{bundle}"""

_STYLE_RETRY_PROMPT = """\
The previous bundle failed the STYLE check.
Failing options: {issues}

Rule: options must NEVER contain "always", "never", "all of the above",
"none of the above" — these are test-taking shortcuts, not factual statements.
Rewrite the flagged option(s) to express the same idea using specific factual
language. Do NOT change stems, correct answers, or explanations for other questions.

Output ONLY the corrected JSON bundle in Schema A format.

Original bundle:
{bundle}"""

_STEM_RETRY_PROMPT = """\
The previous bundle has questions with stems that are too short (under 25 characters).
Failing questions: {issues}

Rule: every stem must be a complete, meaningful question of at least 25 characters.
Rewrite the flagged question(s) as proper, full-sentence exam questions.
A stem like "What is X?" is too vague — add context, a scenario, or specific constraints.
Do NOT change other questions, options, or explanations.

Output ONLY the corrected JSON bundle in Schema A format.

Original bundle:
{bundle}"""


# ──────────────────────────────────────────────────────────────────────────────
# JSON extraction helper
# ──────────────────────────────────────────────────────────────────────────────

def _extract_json(raw: str) -> str:
    if "```json" in raw:
        s = raw.index("```json") + 7
        e = raw.index("```", s)
        return raw[s:e].strip()
    if "```" in raw:
        s = raw.index("```") + 3
        e = raw.rindex("```")
        return raw[s:e].strip()
    s = raw.find("{")
    e = raw.rfind("}")
    if s >= 0 and e > s:
        return raw[s : e + 1]
    return raw


# ──────────────────────────────────────────────────────────────────────────────
# Core subprocess caller
# ──────────────────────────────────────────────────────────────────────────────

def _call_claude(prompt: str, model_flag: list[str]) -> dict | None:
    """Run `claude --print` and return parsed JSON dict, or None on failure."""
    cmd = ["claude", "--print", "--dangerously-skip-permissions",
           "--output-format", "text", "--effort", "medium"] + model_flag + [prompt]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=300, cwd=str(_BACKEND))
        if result.returncode != 0:
            err = (result.stderr or "").strip()[:300]
            print(f"\n    [claude exit {result.returncode}] {err}", flush=True)
            return None
        raw = result.stdout.strip()
        if not raw:
            print("\n    [empty output]", flush=True)
            return None
        return json.loads(_extract_json(raw))
    except json.JSONDecodeError as e:
        print(f"\n    [JSON error] {e}", flush=True)
        return None
    except subprocess.TimeoutExpired:
        print("\n    [timeout 300s]", flush=True)
        return None
    except Exception as e:
        print(f"\n    [error] {e}", flush=True)
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Per-topic generation (runs in thread pool)
# ──────────────────────────────────────────────────────────────────────────────

def _generate_one(brief: dict, model_flag: list[str], dry_run: bool) -> tuple[str, dict | None]:
    """Generate a 7-question bundle. Returns (topic_code, bundle|None)."""
    tc = brief["topic_code"]
    if dry_run:
        return tc, {"subject": brief["subject"], "topic": brief["topic"],
                    "topic_code": tc, "questions": []}

    stems = brief.get("existing_stems", [])
    stems_text = "\n".join(f"  - {s[:100]}" for s in stems[:15]) or "  (none yet)"
    prompt = _PROMPT.format(
        topic_code=tc,
        subject=brief["subject"],
        topic=brief["topic"],
        high_weight="YES — this is a lion's-share exam topic" if brief.get("high_weight") else "NO",
        exam_hint=brief.get("exam_relevance_hint",
                            "Pick under-asked, examiner-mindset angles on core syllabus topics."),
        existing_stems=stems_text,
    )

    bundle = _call_claude(prompt, model_flag)
    if bundle is None:
        return tc, None

    # No pre-check retry — let gates handle failures; they get retried in next wave.
    # Retries were doubling latency for complex topics (reasoning, polity) without
    # meaningful pass-rate improvement since the gate threshold is already relaxed.

    return tc, bundle


# ──────────────────────────────────────────────────────────────────────────────
# Main loop
# ──────────────────────────────────────────────────────────────────────────────

def run(n_topics: int = 10, target_total: int = 50000,
        workers: int = 4, model: str = "sonnet", dry_run: bool = False) -> None:

    model_id = MODEL_ALIASES.get(model, model)
    model_flag = ["--model", model_id] if model != "sonnet" else []

    if not _STATE_OUT.exists():
        print("state.json missing — run: python3 -m scripts.auto_seed.state")
        sys.exit(1)

    state = json.loads(_STATE_OUT.read_text())
    current = state.get("total_questions", 0)
    print(f"Pool : {current:,} / {target_total:,}  need {max(0, target_total - current):,} more")
    print(f"Setup: {workers} workers | model={model_id}" + (" | DRY RUN" if dry_run else ""))

    from . import gates as _gates_mod
    from .priority import next_picks

    wave = 0
    seen: set[str] = set()
    session_added = 0

    while current < target_total and not (dry_run and wave >= 1):
        wave += 1
        picks = next_picks(state, n=n_topics, exclude=seen)
        if not picks:
            seen.clear()
            state = json.loads(_STATE_OUT.read_text())
            picks = next_picks(state, n=n_topics, exclude=seen)
            if not picks:
                print("No more topics to fill — pool saturated.")
                break

        print(f"\n── Wave {wave}: {len(picks)} topics ──", flush=True)

        # Build briefs upfront
        briefs: dict[str, dict] = {}
        pick_map: dict[str, dict] = {}
        for pick in picks:
            tc = pick["topic_code"]
            seen.add(tc)
            pick_map[tc] = pick
            b = make_brief(topic_code=tc)
            if "error" not in b:
                briefs[tc] = b
            else:
                print(f"  {tc}: {b['error']}", flush=True)

        # Generate in parallel, apply sequentially as results arrive
        wave_added = 0
        results: dict[str, dict | None] = {}

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_generate_one, b, model_flag, dry_run): tc
                for tc, b in briefs.items()
            }
            for fut in as_completed(futures):
                tc, bundle = fut.result()
                results[tc] = bundle
                pick = pick_map.get(tc, {})
                label = f"  {tc:<46} ex={pick.get('existing', '?'):>4}"

                if bundle is None:
                    print(f"{label} → FAIL (generation)", flush=True)
                    continue

                with _APPLY_LOCK:
                    res = apply(bundle, dry_run=dry_run)

                if res.get("ok"):
                    added = len(res.get("added_ids", []))
                    wave_added += added
                    session_added += added
                    current += added
                    print(f"{label} → +{added}  pool={current:,}", flush=True)
                else:
                    fail = ", ".join(
                        k + (f":{v['issues'][0][:50]}" if v.get("issues") else "")
                        for k, v in res.get("gates", {}).items()
                    )
                    print(f"{label} → GATE FAIL [{fail}]", flush=True)

        # Refresh state and reset dedup cache
        if not dry_run:
            snap = scan_pool()
            _STATE_OUT.write_text(json.dumps(snap, indent=2, ensure_ascii=False))
            state = snap
            current = snap["total_questions"]
        _gates_mod._STEM_SIG_CACHE = None

        print(f"Wave {wave} done: +{wave_added}  pool={current:,}  session={session_added:,}",
              flush=True)

    print(f"\nDone: +{session_added:,} this session | pool={current:,}")


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry
# ──────────────────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(
        description="Autonomous generator — subprocess per topic, no context drift"
    )
    ap.add_argument("--topics", type=int, default=10, help="Topics per wave (default 10)")
    ap.add_argument("--target", type=int, default=50000, help="Stop when pool ≥ this")
    ap.add_argument("--workers", type=int, default=4, help="Parallel workers (default 4)")
    ap.add_argument("--model", default="sonnet",
                    choices=list(MODEL_ALIASES.keys()) + list(MODEL_ALIASES.values()),
                    help="Model to use (default: sonnet)")
    ap.add_argument("--dry-run", action="store_true", help="Test plumbing without generating")
    args = ap.parse_args()
    run(n_topics=args.topics, target_total=args.target,
        workers=args.workers, model=args.model, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
