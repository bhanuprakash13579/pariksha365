# Pariksha365 — Subject Books (Study Notes)

One **book per subject**, exam-target-aware. Each book is the
ultimate single source for that subject — a student who reads one
end-to-end (with the usual two re-reads + active recall on the embedded
prompts) **can attempt every question in the Pariksha365 50k pool for
that subject and target ≥ 90 % in the live exam**.

> **Core promise** — these notes + active-recall + the `/quiz` companion
> bundles + the mock-test surface together form the **one-stop
> preparation kit** for SSC, RRB, Banks, State PSCs and PSU exams.
> No third-party reference book is mandatory.

---

## Book index — which PDF for which exam

The build script (`_build/render_pdf.py`) reads `_build/manifest.json`
and produces one PDF per row. Some subjects share a single source
markdown but ship under exam-specific titles (e.g., `arithmetic.md`
ships as both `arithmetic_ssc_rrb.pdf` and
`quantitative_aptitude_banks.pdf` — same source, different cover, the
candidate is told which appendix to drill).

| PDF | Exams it serves | Reason |
|---|---|---|
| `polity_ssc_rrb_banks_psc.pdf` | SSC, RRB, Banks (GA), State PSC, PSU | Shared — Indian Constitution + Governance is the same |
| `history_ssc_rrb_banks_psc.pdf` | SSC, RRB, Banks (GA), State PSC | Shared — Ancient → Modern + World |
| `geography_ssc_rrb_banks_psc.pdf` | SSC, RRB, Banks (GA), State PSC | Shared — Physical + Indian + World + Human |
| `economics_ssc_rrb_banks_psc.pdf` | SSC, RRB, Banks (GA + Banking), State PSC | Shared — includes Banks-only Part X (Banking Awareness) |
| `physics_ssc_rrb_psc.pdf` | SSC, RRB, State PSC, Banks (GA) | Shared — General Science |
| `chemistry_ssc_rrb_psc.pdf` | SSC, RRB, State PSC, Banks (GA) | Shared — General Science |
| `biology_ssc_rrb_psc.pdf` | SSC, RRB, State PSC, Banks (GA) | Shared — General Science + Health |
| `environment_ssc_rrb_psc.pdf` | SSC, RRB, State PSC | Shared — Biomes, Climate, Acts, NPs |
| `sci_tech_ssc_rrb_banks_psc.pdf` | SSC, RRB, Banks (GA), State PSC | Shared — ISRO/DRDO/Computers |
| `general_knowledge_all_exams.pdf` | All exams | Shared — Awards, Sports, Days, People, Books, Culture; includes the niche favourites chapter (folk dances, festivals, NE tribes, paintings, martial arts, music, GI tags, UNESCO sites) |
| `vocabulary_all_exams.pdf` | All exams | Shared — Roots, Suffixes, Confusables, OWS, Idioms, Foreign phrases |
| `arithmetic_ssc_rrb.pdf` | SSC, RRB | Same source as Banks but emphasizes Geometry + Mensuration + Trig (per the SSC focus appendix) |
| `quantitative_aptitude_banks.pdf` | Banks (PO, Clerk, RRB-Bank, RBI) | Same source but emphasizes DI + Caselet + Approximation + Quadratic comparison |
| `reasoning_ssc_rrb.pdf` | SSC, RRB | Emphasizes series, classification, analogy, blood-relations, direction, non-verbal |
| `reasoning_banks.pdf` | Banks | Emphasizes puzzles (linear, circular, floors, scheduling), input-output, advanced syllogism, coded inequality, data sufficiency |
| `english_ssc_rrb.pdf` | SSC, RRB | Emphasizes vocabulary (synonyms, antonyms, OWS, idioms, spelling), error spotting |
| `english_banks.pdf` | Banks | Emphasizes RC, cloze, para-jumbles, sentence rearrangement, phrasal verbs |

Total: **17 PDFs**. Of these, 11 are shared across exam families (one
build per subject), and 3 subjects (Arithmetic, Reasoning, English) are
built twice each (SSC/RRB version + Banks version) because the syllabus
weight differs.

### What's NOT in these books (intentionally)

- **Current affairs** — handled separately (current-affairs surface is a
  living feed; static-GK books should not stale within months).
- **Topic-by-topic question banks** — those live in `seeds/static_gk/<subj>/`
  and `seeds/quiz/`; these books TEACH the subject so the questions
  become solvable.
- **Exam-specific notifications, cut-offs, vacancies** — these live on
  the exam-detail page in the app, not the static books.

---

## Building PDFs

The build pipeline does **not** require pandoc / xelatex (avoiding
sudo). It uses Python's `markdown` library + Chrome headless +
KaTeX/Mermaid via CDN.

Prereqs (already on most systems):

- `python3` with `markdown` library (`pip3 install --user markdown`).
- `google-chrome` or `chromium` in PATH.
- (Optional, for offline math/diagrams) the CDN scripts can be cached
  locally; for now the build expects internet for KaTeX + Mermaid.

```bash
cd backend/seeds/study_notes/_build
python3 render_pdf.py --list                # show all manifest entries
python3 render_pdf.py polity                # build one
python3 render_pdf.py polity history        # build a subset
python3 render_pdf.py --all                 # build every PDF (~ 4-7 min on a laptop)
```

PDFs are written to `_build/out/`. Each PDF carries a coloured cover
page with the title, subtitle, exam-tag chips, and the "promise"
statement.

### Custom (one-off) build

```bash
python3 render_pdf.py \
  --src ../polity.md --out /tmp/polity.pdf \
  --title "Polity" --subtitle "for revision" --tags "SSC,RRB"
```

---

## Pedagogy design principles (used in every book)

1. **Scaffolding** — every new concept rests on what was built earlier.
2. **Dual coding** — visual + verbal traces stored in parallel.
3. **Chunking** — Miller's 7±2; no section throws more than 5-7 new units.
4. **Story-first, fact-second** — narrative beats lists for memory.
5. **Spaced repetition anchors** — core facts resurface 3-4 times across
   chapters.
6. **Active recall prompts** — "📝 pause + recall" cues every few pages.
7. **Memory pegs** — mnemonics that are memorable because they're a
   little ridiculous, not just initial-letter salads.
8. **Types-first for quant + reasoning + English** — every topic broken
   into a focused set of types, each taught with shortcut FIRST + full
   derivation, then traditional method as fallback, then 2-3 variations,
   then a self-check. No artificial cap on type count — driven by exam
   utility (per `feedback_types_first_and_syllabus`).
9. **Exam-target appendix** — books used across multiple exam families
   (Arithmetic, Reasoning, English, Economics) end with per-exam
   priority chapter maps so the student knows which sections to drill
   harder for SSC vs RRB vs Banks.
10. **Niche favourites coverage** — paper-setter darlings (folk dances,
    festivals, NE tribes, classical music maestros, GI tags, UNESCO sites)
    get a dedicated chapter in `general_knowledge.md`.

---

## Status (2026-04-26)

| Subject | Source MD lines | PDF pages | State |
|---|---|---|---|
| Polity | 1,627 | 38 | Comprehensive |
| Arithmetic (×2 outputs) | 1,400+ | 44 each | Comprehensive + per-exam appendices |
| English (×2 outputs) | 700+ | 46 each | Comprehensive + Banks/SSC focus appendices + 100-word synonym/antonym/OWS/idiom drill tables |
| Reasoning (×2 outputs) | 700+ | 33 each | Worked examples + Banks puzzle drill + SSC non-verbal drill |
| General Knowledge | 1,400+ | 48 | Includes niche favourites (folk dances, festivals, NE tribes, paintings, martial arts, music, GI tags, UNESCO sites) |
| History | 1,108 | 32 | Comprehensive (Ancient → Post-Indep + World) |
| Geography | 1,000 | 24 | Comprehensive |
| Biology | 850 | 30 | Comprehensive |
| Vocabulary | 800 | 33 | Cluster-based (roots, suffixes, themes, foreign phrases) |
| Sci-Tech | 750 | 25 | Comprehensive |
| Economics | 950+ | 22+ | Comprehensive + Banking Awareness Part X (RBI tools, payments, schemes, committees) |
| Environment | 731 | 23 | Comprehensive |
| Physics | 634 | 22 | Comprehensive |
| Chemistry | 595 | 22 | Comprehensive |

Last updated: 2026-04-26.
