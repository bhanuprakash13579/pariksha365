---
title: "Reasoning — The Pariksha365 Types-First Book"
subtitle: "focused type set per topic (no arbitrary cap) • pattern-recognition first • accurate diagrams only"
author: "Pariksha365 Study Notes"
date: "2026"
---

# 📘 How To Use This Book

Reasoning is not a single topic — it is a **cluster of pattern families**. Once you can see the pattern in 5 seconds, the rest is bookkeeping.

Same type-first discipline as `arithmetic.md`. For every topic:

- **Opener** — why it appears, what you must memorise cold, universal attack plan.
- **Types** — a focused set. Many topics settle around 8-15 types; complex topics (Puzzles, Input-Output, Non-verbal) may need 20-25. **There is no upper cap** — a type is included if it unlocks a distinct pattern that will earn marks; never padded just for a round number.
- **For each type** — recognition cue → core insight → shortcut-first solution (with derivation) → 2-3 variations → self-check.

### Diagram accuracy — a hard rule

Reasoning questions whose answer depends on a visual (mirror-image, water-image, dice, paper-fold, cube-counting, embedded figures, mirror-Line-of-symmetry, figure-completion) can only be taught with **precise, to-scale illustrations** — not rough ASCII or hand-wave sketches. Wrong visuals confuse worse than no visuals.

- This text book teaches the **method** for each visual type (how a mirror flips about a vertical line, how dice opposite-face rule works, how a folded paper unfolds, how to rotate a 3-D cube in your head).
- **Figures live in `_build/figures/reasoning/`** as exact SVG. The pandoc build embeds them. No figure is shipped until a human has verified the mirror / rotation / unfold is physically correct.
- If a specific question cannot be diagrammed faithfully at ship-time, it is deferred — never replaced with a crude approximation.

---

\newpage

# 🔤 PART 1 — SERIES (NUMBER, LETTER, ALPHANUMERIC)

## 1.0 Opener

**Why:** 2-4 questions every prelims. Cheapest marks if you drill the patterns.

**Mental-math arsenal:**
- Squares 1-30, cubes 1-15 (for number series).
- Alphabet positions (A=1, N=14, Z=26) and reverse positions (A=26, Z=1).
- Prime list up to 50.

**Attack plan:** compute first differences. If constant → AP. Not constant → second differences, or ratio, or known sequence (squares/cubes/primes/Fibonacci).

## Types

1. **Arithmetic progression** — constant difference.
2. **Geometric progression** — constant ratio.
3. **Square / cube series** — n², n²+1, n²−1, n², (n+1)²…
4. **Fibonacci-style** — each term = sum of two previous.
5. **Alternate series** — odd positions form one pattern, even positions another.
6. **Mixed operations** — ×2 +1, ×2 +1 … (recurring recipe).
7. **Prime / composite based**.
8. **Letter series** — differences in alphabet positions; forward/backward/alternating.
9. **Alphanumeric** — letter + number pairs, each tracked separately.
10. **Missing term at position k** — recognise pattern, extrapolate.

For each type the shortcut is: **compute the Δ row and see if it's a known row.**

---

\newpage

# 🔗 PART 2 — CODING-DECODING

## 2.0 Opener

**Memorised:**
- A=1…Z=26 (and Z=1…A=26 reverse).
- Common offsets: +1 (B→A), +2, ×reverse.

## Types

1. **Letter shift coding** — every letter shifted by k positions (CAT → DBU with k=+1).
2. **Reverse letter coding** — letter replaced by (27 − position) letter (A↔Z, B↔Y).
3. **Position-dependent coding** — even positions shifted differently from odd.
4. **Word coding by blocks** — split word, shift blocks.
5. **Substitution coding** — whole-word replacement (sun = tree, moon = flower…), questions require cross-sentence inference.
6. **Mathematical coding** — digits + symbols used as letters.
7. **Chinese-coding / symbol-coding** (new pattern) — given a mapping table, decode.
8. **Letter-digit hybrid codes** — each letter has position + offset rule.

Shortcut: **always write the alphabet row + index row on your rough sheet first**, then slide the shift.

---

\newpage

# 🧭 PART 3 — DIRECTION SENSE

## 3.0 Opener

**Memorised:** the 8 directions on a compass rose; the **rotation of a direction under "left"/"right" turn** (90° CCW / 90° CW). Pythagorean triples (for shortest-distance questions).

**Attack plan:** draw a clear cross (N up, E right); mark each move to scale; use Pythagoras for diagonal distance.

## Types

1. **Sequential movement** — plot each leg, sum vectors.
2. **Final displacement** — Pythagoras on N-S vs E-W net movements.
3. **Left/Right turns at each step** — maintain current heading; apply rotation.
4. **Starting direction unknown** — deduce from constraints later in the problem.
5. **Shadow direction / time of day** — morning shadows point W, evening E.
6. **Two persons meeting** — relative-position geometry.
7. **Rotation + reflection combo** — someone turns 135° clockwise; track new heading.

Shortcut: **always finish one person's path fully before starting the next; don't merge.**

---

\newpage

# 👪 PART 4 — BLOOD RELATIONS

## 4.0 Opener

**Memorised:** the family tree notation — square for male, circle for female, horizontal line for spouse, vertical line down for child. (In notes we use `M` / `F` and `→` / `↓`.)

## Types

1. **Self-referential** — "Pointing to a photo: 'his father is my father's son' " → speaker is father of the photo-subject.
2. **Generation gap** — count levels between A and B.
3. **Cousin / in-law chain** — mother's brother's wife's son etc.
4. **Coded family relations** — P+Q means P is father of Q, etc. Decode with a key.
5. **Family tree puzzle** (grid-style) — several facts, build the full tree.
6. **"How is A related to B"** asked when tree is already built — just traverse.

Shortcut: build the tree once; answer every sub-question off it.

---

\newpage

# 💺 PART 5 — SEATING ARRANGEMENT

## 5.0 Opener

**Types of arrangements:**
- Linear (n people in a row, some facing north, some south).
- Circular (facing centre / facing outward / both).
- Rectangular / square (4 on corners + middle).
- Parallel rows (two rows facing each other).
- Double-line (e.g., people + their gifts).

**Attack plan (universal):** take the **most-constrained** clue first; build a skeleton; plug in permissive clues last.

## Types

1. **Pure linear, all facing same way**.
2. **Linear with mixed facing** — pay attention to left/right inversion.
3. **Circular, facing centre** — left/right of X is unambiguous.
4. **Circular, facing outward** — left/right flips.
5. **Mixed facing in circle** — track each person's orientation.
6. **Rectangular with 8 persons** — diagonals + sides rules.
7. **Two parallel rows** — "opposite", "immediate left of opposite" etc.
8. **Arrangement + attribute** (profession/color/age) — 2-variable puzzle.
9. **Arrangement + attribute + 2nd attribute** — 3-variable puzzle; backbone of banking mains.
10. **Month / day / floor puzzles**.
11. **Order + ranking** — (from top / from bottom, total count).

For multi-variable puzzles: make **one table per variable aligned to the seat skeleton**.

---

\newpage

# 🧩 PART 6 — PUZZLES (FLOOR / BOX / SCHEDULING)

## 6.0 Opener

Same discipline as seating. The puzzle is a **constraint-satisfaction problem**; you are a human SAT solver.

## Types

1. **Floor-based**: n persons, n floors; clues like "A lives immediately above B".
2. **Box stacking** — "box P is above Q but below R".
3. **Day-based scheduling** (Mon-Sun) — who works which day + extra constraint.
4. **Month-date combo** — 7 people, 7 months, 2 possible dates each.
5. **Colour / city / sport** — 3-dimensional attribute binding.
6. **Comparison puzzles** — A > B > C ranking across multiple metrics.
7. **Mixed floor + facing + attribute** — banking-mains boss level.
8. **Uncertain puzzles** — when the answer needs "cannot be determined".

Attack plan: Pick the clue that **fixes the most positions at once**. Use the table format: rows = positions, columns = attributes. Fill the unambiguous cells first.

---

\newpage

# 🔢 PART 7 — MATHEMATICAL INEQUALITIES

## 7.0 Opener

**Memorised:** how inequality chains combine.
- A > B ≥ C → A > C. (Strict wins.)
- A ≥ B = C → A ≥ C.
- A > B, B > C, C = D → A > D.

## Types

1. **Direct inequality** — "if P > Q ≥ R < S, is P > S?" Note: R < S doesn't fix P vs S.
2. **Coded inequality** — @, #, &, $ stand for >, ≥, <, ≤, =. Decode, then apply rules.
3. **Statement + conclusions** (I & II, "only I", "both", "either") — logical conjunction.
4. **Double-decker conclusions** — inequality chains of length 5-6.

Shortcut: replace all coded symbols with actual inequality signs FIRST. Then scan for the two terms you need; confirm an unbroken chain.

---

\newpage

# ⛓️ PART 8 — SYLLOGISM

## 8.0 Opener

**Memorised:** 4 standard statements.
- **A**: All S are P.
- **E**: No S is P.
- **I**: Some S are P.
- **O**: Some S are not P.

And a fundamental fact: **"Some S are P" also means "Some P are S"** (conversion rule for I). "No S is P" converts to "No P is S" (conversion of E).

## Types

1. **Two statements, two conclusions** — ‘follows / does not follow’.
2. **Three statements, two conclusions**.
3. **Possibility conclusions** — "at least some" vs "all S are P is a possibility".
4. **Negative universal + particular** — mixing A/E/I/O.
5. **Chained syllogism** — A→B→C type conclusions.

**Attack plan — the Venn-diagram method** (universal shortcut):
1. For each statement, draw the unambiguous Venn region (Overlap for I, disjoint for E, subset for A, complement for O).
2. For each conclusion, check if ALL consistent Venn diagrams support it.
3. If even one valid Venn contradicts the conclusion, it "does not follow".

This is the one method that NEVER fails, unlike mnemonic trick-rules that break on uncommon cases.

---

\newpage

# 📥 PART 9 — INPUT-OUTPUT (Banking Mains)

## 9.0 Opener

A sequence of rearrangements (swap, shift, insertion, arithmetic op on numbers) is applied repeatedly; the candidate must find the rule and predict final / intermediate steps.

## Types

1. **Word/number pure shifting** (e.g., words sorted alphabetically left-to-right).
2. **Arithmetic on numbers** (each number increased by index, squared, etc.).
3. **Odd-even splitting**.
4. **Combined word-number** (alphabetise AND square).
5. **New-age input-output** (complex rules — Bank PO mains speciality).

Shortcut: compare input and step 1 only first; detect the rule; verify on step 2 → step 3. Solve fast.

---

\newpage

# 🧠 PART 10 — DATA SUFFICIENCY

## 10.0 Opener

Given a question + 2 (or 3) statements; determine which subset of statements suffices.

Answer format (standard SBI/IBPS):
- (a) Statement I alone suffices.
- (b) Statement II alone suffices.
- (c) Each alone suffices.
- (d) Both together needed.
- (e) Neither alone nor together sufficient.

## Types

1. **Quantitative DS** — solve with I only? with II only? with both?
2. **Reasoning DS** — similar but with ranking/seating/family tree statements.
3. **Syllogism / directional DS**.

Attack: deliberately IGNORE one statement while checking the other. Never merge too early.

---

\newpage

# 🎲 PART 11 — NON-VERBAL REASONING (VISUAL)

> **Diagram accuracy is mandatory here.** The types below are taught by method; shipped questions each have a to-scale SVG rendering verified before publication.

## 11.1 Mirror Image (vertical line of reflection)

**Rule:** horizontally flip across a vertical mirror. Letters like A, H, I, M, O, T, U, V, W, X, Y read the same in mirror; B, C, D, E, K visibly flip; N, S, Z reverse along diagonals. Digits 0, 8 same; 1, 2, 3, 5, 6, 7, 9 change.

**Shortcut:** imagine writing the string, then read it in reverse order with each character's mirror-image shape.

## 11.2 Water Image (horizontal line of reflection)

**Rule:** vertical flip. Letters like B, C, D, E, H, I, K, O, X are visually symmetric under appropriate axes; most are not.

## 11.3 Paper Folding & Paper Cutting

**Rule:** a paper is folded k times along shown lines; then a cut of given shape is made; you must show how the unfolded paper looks.

**Method:** fold mentally in reverse. For each fold, reflect the cut about the fold-line. Do this k times.

## 11.4 Cubes & Dice

**Core fact (opposite-face rule):** on a standard die, opposite faces sum to 7. So 1↔6, 2↔5, 3↔4.

**Types:**
- **Unfolded cube (net)** — identify which faces are opposite in the final assembled cube.
- **Painted cube problem** — cube painted on outside, cut into n³ small cubes; count small cubes with 3 / 2 / 1 / 0 painted faces.
  - Corners (always 8): 3 faces painted.
  - Edges (non-corner): 12·(n−2) cubes with 2 painted.
  - Face centres: 6·(n−2)² cubes with 1 painted.
  - Interior: (n−2)³ cubes with 0 painted.
- **Dice rotation** — given two/three views, figure out which face lands where.

## 11.5 Embedded Figures

Find a given simple figure inside a complex one. Method: outline the target figure's defining lines; trace each possible position in the complex figure.

## 11.6 Figure Series

Series of figures following a rule (rotation by 45°, addition of one line per step, shading pattern). Method: isolate the **rule per element** (rotation, count, shade), then apply.

## 11.7 Analogy of Figures

A : B :: C : ?  — find the transformation A→B and apply to C.

## 11.8 Classification of Figures

Identify the odd-one-out; usually by shape, count of angles, symmetry, or shading.

---

\newpage

# 🧮 PART 12 — VERBAL REASONING (Statement-based)

## Types

1. **Statement + Conclusion** — does the conclusion strictly follow?
2. **Statement + Assumption** — is the assumption necessary for the statement?
3. **Statement + Argument** — is the argument STRONG / WEAK?
4. **Statement + Course of action** — is the action appropriate?
5. **Cause and effect**.

These resemble CAT's verbal logical reasoning. Drill on past papers.

---

\newpage

# 🔡 PART 13 — RANKING / ORDER

## Types

1. **Single row ranking** — "A is 7th from left, 12th from right — total?" → 7 + 12 − 1 = 18.
2. **Before / after in queue**.
3. **Moved forward / backward** — "A moves 3 places up, now at 5th from top; earlier position?".
4. **Heights / weights ranking**.

---

\newpage

# APPENDIX — Attack-plan matrix

| Cue in stem | Part | Critical first move |
|---|---|---|
| "sitting in a row" | 5 | draw n-cell skeleton |
| "lives on floor" | 6 | draw n-floor skeleton (bottom = 1) |
| "pointing at photo" | 4 | identify speaker's relation first |
| "walks 5 m north, 3 m east" | 3 | draw on N-E cross |
| "all, some, no" | 8 | Venn diagrams |
| "mirror/water image" | 11 | check axis of reflection |
| "input-output steps" | 9 | diff step 1 vs input |
| "> , ≥ , < , ≤" | 7 | chain scan, no skipping |
| "Statement I / II, which" | 10 | test each alone first |
| "cube cut into 125 smaller" | 11.4 | n=5, apply corner/edge/face counts |

---

# APPENDIX B — Figure Asset Policy

No reasoning figure is shipped unless it is:
1. Authored as SVG with exact coordinates / angles.
2. Physically verified — a mirror is an actual horizontal reflection, not a lazy sketch.
3. Reviewed once against the answer — if the figure does not uniquely admit the "correct" option, it is rejected.

Crude ASCII-art diagrams are banned from this book and from shipped questions. If a figure asset is not ready, the corresponding question is held back in a **visual-queue** (`_build/figures/reasoning/_todo.md`) until the asset is authored.

---

*Companion: `arithmetic.md` for quant, `english.md` for verbal. Quiz pairings live under `REAS_*`.*
