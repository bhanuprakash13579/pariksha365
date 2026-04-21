# Pariksha365 — Subject Books (Study Notes)

One **book per subject** — not a pile of worksheets. Each book is written the way a
well-taught teacher takes you through the subject for the first time: a clear
story arc, one concept leading to the next, frequent recap, memory pegs,
diagrams where they pay off, and exam-facing drills at the end of each chapter.

> **Core promise** — a student who reads **one** of these books cover-to-cover
> (with the usual two re-reads + active recall) can score **80 %+** on that
> subject in SSC / RRB / Banking / State-PSC prelims, and has a solid foundation
> for UPSC GS.

## Books

| File                 | Subject                             | Target pages |
|----------------------|-------------------------------------|--------------|
| `polity.md`          | Indian Polity + Constitution        | ~100 pp      |
| `history.md`         | Indian + World History              | ~140 pp      |
| `geography.md`       | Indian + World Physical + Human Geo | ~100 pp      |
| `economics.md`       | Indian Economy + Basics             | ~90 pp       |
| `physics.md`         | Physics (through modern)            | ~80 pp       |
| `chemistry.md`       | Chemistry (general + organic)       | ~70 pp       |
| `biology.md`         | Biology + Life Sciences             | ~90 pp       |
| `sci_tech.md`        | Sci-Tech, ISRO, DRDO, Computers     | ~70 pp       |
| `general_knowledge.md` | Awards, sports, culture, days     | ~80 pp       |
| `environment.md`     | Environment + Ecology + Climate     | ~60 pp       |

Each book is one long markdown file, organised as:

1. **How to use this book** — 1 page.
2. **Part → Chapter → Section** — narrative order, earlier chapters feed later ones.
3. **Pedagogy elements inside each chapter** —
   - **Hook** (1-line motivation).
   - **Story** (history / why).
   - **Mechanism** (how it works).
   - **Visual** (tree/flow/timeline/map).
   - **Memory pegs** (mnemonics, acronyms, patterns).
   - **Cross-refs** (back to earlier chapters + to the quiz bundles).
   - **Exam hooks** (what to memorise verbatim; probable Q shapes).
4. **Appendices** — timeline, cheatsheet, master mnemonic list.

## Pedagogy design principles

1. **Scaffolding** — every new concept rests on what was built in the previous
   chapter. A reader never meets a term that hasn't been set up.
2. **Dual coding** — every memorisation-heavy fact gets a visual companion
   (diagram, table, or colour-block) + a verbal explanation.
3. **Chunking** — no chapter introduces more than 5–7 new units at once.
4. **Narrative arc per subject** — History is a timeline; Polity is a nested
   institution hierarchy; Geography moves from the planet inward to India's
   regions; Economy flows from micro → macro → Indian.
5. **Spaced repetition anchors** — core facts resurface across chapters so the
   student meets them 3–4 times by book's end.
6. **Active recall prompts** — *"Before reading on, try to name …"* cues
   embedded every few pages.
7. **Memory pegs that delight** — mnemonics that are memorable because they're
   a little ridiculous, not just initial-letter salads.
8. **Exam-facing** — every chapter is paired with the quiz bundle in
   `seeds/static_gk/<subject>/` so reader can close the loop immediately.

## Building PDFs

The books are markdown; build with pandoc:

```bash
cd _build
./build_pdfs.sh                 # build all books
./build_pdfs.sh polity history  # build only those
```

Requires:
- `pandoc` + `texlive-xetex` (or another pandoc PDF engine) — once.
- `@mermaid-js/mermaid-cli` (`npm install -g`) — to render Mermaid diagrams; if
  absent, diagrams render as fenced code blocks in the PDF (still readable).

## Version + status

| Subject             | Stage                                     |
|---------------------|--------------------------------------------|
| Polity              | Parts A + B drafted (foundation + rights)  |
| History             | Part Ancient drafted (IVC through Maurya)  |
| Geography           | Planned                                    |
| Economics           | Planned                                    |
| Physics             | Planned                                    |
| Chemistry           | Planned                                    |
| Biology             | Planned                                    |
| Sci-Tech            | Planned                                    |
| General Knowledge   | Planned                                    |
| Environment         | Planned                                    |

Last updated: 2026-04-21.
