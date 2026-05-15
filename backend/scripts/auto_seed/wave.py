"""Wave driver — pick N priority topics and emit per-topic briefs.

Usage flow per session:
  1. python3 -m scripts.auto_seed.wave plan -n 5
       → prints 5 briefs + creates wave manifest at /tmp/auto_seed_wave.json
  2. Claude session generates 5 bundles, writing each to its staging path
       (paths returned in step 1)
  3. python3 -m scripts.auto_seed.wave apply
       → ingests all staged files via apply(), reports per-file pass/fail
  4. python3 -m scripts.auto_seed.state  (refresh)
       → snapshot for next wave's priority calculation

This is the loop that makes autonomous operation possible — every step
is a deterministic CLI invocation; only the bundle-writing in step 2
requires Claude (or any LLM) creative output.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .apply import apply
from .brief import make_brief
from .state import scan_pool

_BACKEND = Path(__file__).resolve().parents[2]
_WAVE = Path("/tmp/auto_seed_wave.json")
_STATE_OUT = _BACKEND / "scripts" / "auto_seed" / "state.json"


def plan(n: int = 5) -> dict:
    state = json.loads(_STATE_OUT.read_text())
    # Refresh existing-count info from latest scan
    chosen: list[dict] = []
    seen: set[str] = set()
    # priority.next_picks accepts an exclude set — call it iteratively to
    # avoid clustering all N on the same subject if we ever extend
    from .priority import next_picks
    while len(chosen) < n:
        picks = next_picks(state, n=1, exclude=seen)
        if not picks:
            break
        tc = picks[0]["topic_code"]
        seen.add(tc)
        brief = make_brief(topic_code=tc)
        if "error" in brief:
            continue
        chosen.append(brief)

    manifest = {
        "planned_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "briefs": chosen,
    }
    _WAVE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return manifest


def apply_wave() -> dict:
    if not _WAVE.exists():
        return {"ok": False, "error": "no wave manifest at /tmp/auto_seed_wave.json"}
    manifest = json.loads(_WAVE.read_text())
    results = []
    accepted = rejected = 0
    for brief in manifest.get("briefs", []):
        staging = Path(brief["staging_path"])
        if not staging.exists():
            results.append({"topic_code": brief["topic_code"], "status": "missing"})
            continue
        try:
            bundle = json.loads(staging.read_text())
        except Exception as e:
            results.append({"topic_code": brief["topic_code"], "status": "parse_error", "error": str(e)})
            rejected += 1
            continue
        res = apply(bundle, generator_tag=f"autoseed-wave-{manifest['planned_at'][:10]}")
        if res.get("ok"):
            accepted += 1
            results.append({"topic_code": brief["topic_code"], "status": "applied",
                            "added": len(res["added_ids"]), "total_after": res["total_after"]})
        else:
            rejected += 1
            results.append({"topic_code": brief["topic_code"], "status": "rejected",
                            "reason": res.get("reason"), "gates": res.get("gates", {})})
    # Refresh state
    snap = scan_pool()
    _STATE_OUT.write_text(json.dumps(snap, indent=2, ensure_ascii=False))
    return {
        "ok": True,
        "accepted_bundles": accepted,
        "rejected_bundles": rejected,
        "results": results,
        "pool_total_questions_now": snap["total_questions"],
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_plan = sub.add_parser("plan")
    p_plan.add_argument("-n", type=int, default=5)
    sub.add_parser("apply")
    args = ap.parse_args()

    if args.cmd == "plan":
        m = plan(n=args.n)
        print(f"WAVE PLANNED — {len(m['briefs'])} bundle(s) to generate")
        print(f"Manifest: {_WAVE}")
        print()
        for b in m["briefs"]:
            print(f"  → {b['topic_code']:<40} {b['subject']:<22} existing={b['existing_count']}")
            print(f"      staging_path: {b['staging_path']}")
        return 0
    elif args.cmd == "apply":
        r = apply_wave()
        print(json.dumps(r, indent=2, ensure_ascii=False)[:3000])
        return 0 if r.get("ok") else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
