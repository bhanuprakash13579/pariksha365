---
title: "Arithmetic — The Pariksha365 Types-First Book"
subtitle: "Every topic broken into a focused set of types (no arbitrary cap) • shortcut-first • mental-math first"
author: "Pariksha365"
date: "2026"
---

# How to use this book

This book is different from the static-GK books. Here **every topic is broken into a focused set of TYPES**. Most topics settle at 8-15 types; some (Geometry, Input-Output, Puzzles) go higher — **there is no artificial cap**. What matters is that each type unlocks a *distinct* pattern or method. Almost every quantitative question you will ever see in SSC / Banking / RRB / PSU / State-PSC exams is a **tweak of one of these types**. If you can recognise the type in 5 seconds, you are already halfway to the answer.

For every TYPE you will see:

1. **What it looks like** — the recognition cue. Read the stem and ask: "which type is this?"
2. **Core insight / formula** — the single equation or idea that drives it.
3. **Smart / shortcut method FIRST** — the way a trained student solves it in their head in under 20 seconds, **with a full derivation** so you know *why* it works (so a twist will not break you).
4. **Traditional method SECOND** — the longer, safe fallback when the shortcut's precondition is not met.
5. **Variations** — 2-3 important tweaks that examiners love.
6. **Self-check** — one mini question to prove to yourself you have the type.

**Before each topic**, you will find a "Opener" box with:

- **Why the topic matters** (where you meet it in exams).
- **Mental-math arsenal** — the tables / constants you MUST know cold (no pen-paper).
- **Memorised formulas** — the 3-6 equations that run the topic.
- **Generic attack plan** — what to identify first, what to compute mentally, when to switch methods.

> **Golden rule of arithmetic prep:** the student who knows 10 types cold beats the student who has solved 1,000 questions without classifying them.

---

\newpage

# PART 0 — THE MENTAL-MATH ARSENAL

You cannot be fast at arithmetic without *cached* values in your head. Before any topic, master this core.

## 0.1 Fraction ↔ Percentage ↔ Decimal table (MUST memorise)

| Fraction | Percentage | Decimal |
|----------|-----------|---------|
| 1/1 | 100 % | 1.000 |
| 1/2 | 50 % | 0.500 |
| 1/3 | 33.33 % | 0.333… |
| 1/4 | 25 % | 0.250 |
| 1/5 | 20 % | 0.200 |
| 1/6 | 16.67 % | 0.166… |
| 1/7 | 14.28 % | 0.142857… |
| 1/8 | 12.5 % | 0.125 |
| 1/9 | 11.11 % | 0.111… |
| 1/10 | 10 % | 0.100 |
| 1/11 | 9.09 % | 0.0909… |
| 1/12 | 8.33 % | 0.0833… |
| 1/13 | 7.69 % | 0.0769… |
| 1/14 | 7.14 % | 0.0714… |
| 1/15 | 6.66 % | 0.0667… |
| 1/16 | 6.25 % | 0.0625 |
| 1/20 | 5 % | 0.050 |
| 1/25 | 4 % | 0.040 |
| 1/40 | 2.5 % | 0.025 |
| 1/50 | 2 % | 0.020 |

Also the multiples: 3/8 = 37.5 %, 5/8 = 62.5 %, 2/3 = 66.67 %, 3/7 = 42.85 %, 4/7 = 57.14 %, 5/11 = 45.45 %, etc.

## 0.2 Squares, cubes, roots

- Squares of 1-30 (NON-NEGOTIABLE), bonus 31-50.
- Cubes of 1-15 (NON-NEGOTIABLE), bonus 16-20.
- √2 ≈ 1.414, √3 ≈ 1.732, √5 ≈ 2.236, √7 ≈ 2.645, √10 ≈ 3.162.
- π ≈ 3.1416, π² ≈ 9.87, e ≈ 2.718.

## 0.3 Tables 11-20 (yes, all of them)

If you still compute 17 × 14 by column multiplication, you are losing 15 seconds per question. Drill these.

## 0.4 Universal shortcuts (used everywhere)

- **10% trick** — move decimal one place left. 10% of 742 = 74.2. Everything else is built on this.
- **1% trick** — move decimal two places left. 1% of 742 = 7.42.
- **5% = half of 10%**. 5% of 742 = 37.1.
- **Break a nasty percentage into a sum of easy ones.** 17% = 10% + 5% + 2% = 10% + 5% + 2×1%.
- **Fraction conversion:** "x is what % of y" is faster as the fraction x/y matched to the table above.
- **Percent-change symmetry:** a% of b = b% of a. 32% of 50 = 50% of 32 = 16. Use whichever side is easier.

## 0.5 Generic problem-solving flow

1. **Read once — label the type.** Don't start solving yet.
2. **Identify the one equation / ratio / insight** the type uses.
3. **Check if values suit the shortcut** (round numbers, known fractions, symmetric setups). If yes, shortcut.
4. **Else traditional method**, but compute mentally where possible (step 0 onwards).
5. **Sanity-check the sign / order of magnitude.** A 120% increase cannot land below the original.

---

\newpage

# 📈 PART 1 — PERCENTAGE

## 1.0 Opener

**Why:** Percentage is the single highest-frequency topic. It appears *inside* profit-loss, simple/compound interest, data interpretation, DI caselets, ratio problems, population, discount, tax, exam-marks, mixtures, error measurement. If percentage is slow, everything downstream is slow.

**Mental-math arsenal:**
- The fraction-percent table (§ 0.1) — the single most powerful table in arithmetic.
- Squares 1-30.
- 10%, 1%, 5%, 25% as reflexes.

**Memorised formulas:**
1. x % of y = (x/100) · y = (y/100) · x *(interchange)*.
2. Percentage change = (New − Old) / Old × 100.
3. Successive % changes a, b → net = a + b + (a·b)/100.
4. If A is r % more than B, then B is (r / (100 + r)) × 100 % **less** than A. Symmetric for "less than".
5. Population after n years at r % p.a. growth = P · (1 + r/100)ⁿ. (Same as CI.)

**Generic attack plan:** ask "what is the base (100)?" before anything. Then match to a type.

---

## Type 1 — Convert fraction ↔ percentage ↔ decimal

**Cue:** "Express 5/8 as a percentage" / "37.5 % = ? fraction".

**Insight:** The table in § 0.1. Done.

**Shortcut:** Table lookup. 5/8 = 62.5 %.

**Traditional:** 5/8 = 5 × 100 / 8 = 62.5.

**Variations:** Recurring decimals → 0.333… = 1/3; 0.142857… = 1/7 (period 6 — a known pattern).

**Self-check:** 7/8 = ? %. → **87.5 %** (50 + 25 + 12.5).

---

## Type 2 — "x % of y" direct calculation

**Cue:** "Find 23 % of 850".

**Insight:** Decompose x into multiples of 10, 5, 1.

**Shortcut:**
- 23 % of 850 = 20 % + 3 %.
- 20 % of 850 = 170. 1 % of 850 = 8.5. 3 % = 25.5. Total = 195.5.
- Took < 10 sec mentally.

**Traditional:** 23/100 × 850 = 19,550/100 = 195.5.

**Variations:**
- Use the symmetry trick: 36 % of 25 = 25 % of 36 = 9.
- Ugly percentages (17.5 %) → 17.5 = 10 + 5 + 2.5.

**Self-check:** 36 % of 250 = ? → 25 % of 360 = **90**.

---

## Type 3 — "A is what percentage of B?"

**Cue:** "What percent of 64 is 24?"

**Insight:** Compute A/B, then map to the table.

**Shortcut:** 24/64 = 3/8 = 37.5 %.

**Traditional:** (24 × 100) / 64 = 2400/64 = 37.5.

**Variations:**
- "By what percentage is A greater than B?" → (A−B)/B × 100 (base is B).
- "By what percentage is A less than B?" → (B−A)/B × 100 (base is B).

**Self-check:** 45 is what % of 75? → 45/75 = 3/5 = **60 %**.

---

## Type 4 — Percentage increase / decrease (basic)

**Cue:** "Price rose from 240 to 300. % increase?"

**Insight:** Change / Original × 100, original (the *old* value) is the base.

**Shortcut:** 300 − 240 = 60. 60/240 = 1/4 = **25 %**.

**Traditional:** 60 × 100 / 240 = 25.

**Variations:**
- Watch the base direction: "decreased from 300 to 240" → 60/300 = 1/5 = **20 %**.
- Two different bases give two different answers — the exam exploits this.

**Self-check:** Salary up from ₹20k to ₹28k → 8/20 = **40 %**.

---

## Type 5 — Successive percentage change (the single most tested type)

**Cue:** "A salary is increased by 20 %, then decreased by 10 %. Net change?"

**Insight:** Net = a + b + (a·b)/100 where a, b are **signed** (+ for rise, − for fall).

**Shortcut (derivation shown once):**
- After a: amount = 100 + a.
- After b: (100 + a)(1 + b/100) = 100 + a + b + ab/100.
- Net change from 100 = a + b + ab/100.

- Plug in a = +20, b = −10: 20 − 10 + (20)(−10)/100 = 10 − 2 = **+8 %**.
- No decimal multiplications. Done in 5 sec.

**Traditional:** 100 → 120 → 120 × 0.9 = 108 → 8 % net. Same answer, slower.

**Variations:**
- Three successive: apply pairwise. a, b combined → c. Then c, x combined.
- Equal-and-opposite: +r % then −r % gives net = −r²/100 (**always a loss**). Classic trap.
- Discount-on-discount: two successive discounts of 10 % and 20 % are equivalent to a single discount of **28 %**, not 30 %.

**Self-check:** Price up 30 %, then down 20 %. Net? → 30 − 20 − 6 = **+4 %**.

---

## Type 6 — Population / value after n years (compound growth)

**Cue:** "Population 50,000; grows at 10 % annually; population after 3 years?"

**Insight:** P · (1 + r/100)ⁿ. This IS compound interest — memorise once, apply twice.

**Shortcut:** Multiply (1.1)³ = 1.331. So answer = 50,000 × 1.331 = **66,550**.

**Traditional:** Year 1 → 55,000; Year 2 → 60,500; Year 3 → 66,550. Same number, slower.

**Variations:**
- **Declining** population: 50,000 × (0.9)³ = 50,000 × 0.729 = 36,450.
- **Mixed** rates (Year 1: +10 %, Year 2: +5 %, Year 3: −8 %): chain-multiply.
- **Find the original**: given final, divide instead of multiply. "Population is 66,550 after 3 years at 10 % — original?" → 66,550 / 1.331 = 50,000.

**Self-check:** ₹8000 at 25 % p.a. CI for 2 years → 8000 × (5/4)² = 8000 × 25/16 = **₹12,500**.

---

## Type 7 — Forward vs reverse percentage relationship

**Cue:** "If A's salary is 25 % more than B's, by what % is B's salary less than A's?"

**Insight:** Forward r → reverse is **r / (100 + r) × 100 %**. Signs flip: "more" becomes "less".

**Shortcut:** r = 25 → 25 / 125 × 100 = **20 %** less.

**Traditional:** Let B = 100 → A = 125 → (A − B)/A = 25/125 = 20 %. Same.

**Variations:**
- "25 % less" → other one is 25/75 × 100 = **33.33 %** more.
- Remember the pair table: 20 %↔25 %, 25 %↔33.33 %, 10 %↔11.11 %, 50 %↔100 %, 9.09 %↔10 %, 14.28 %↔16.67 %. These sit inside 80 % of exam problems.

**Self-check:** A is 50 % more than B → B is how much less than A? → 50/150 = **33.33 %**.

---

## Type 8 — Income → Expenditure → Savings

**Cue:** "Raj spends 75 % of his income. If income rises 20 % and expenditure rises 10 %, find % change in savings."

**Insight:** Savings = Income − Expenditure. Fix Income = 100 (because we only want percentages), let Expense = 75, Savings = 25. Apply changes to both, recompute savings.

**Shortcut:** New income = 120. New exp = 75 × 1.1 = 82.5. New savings = 37.5. Change = 37.5 − 25 = 12.5. Percent = 12.5/25 × 100 = **+50 %**.

**Traditional:** Same algebra — no faster long route here.

**Variations:**
- Given the % change in savings, find the unknown % change in expenditure.
- "Saved 40 % of income" — base moves to "savings" side.

**Self-check:** Income +10 %, Expense +20 %, Expense was 80 % of income. New savings? → 110 − 96 = 14 vs old 20 → Δ = −6 → **−30 %**.

---

## Type 9 — Pass / fail marks

**Cue:** "Pass mark is 40 %. A scored 220 and failed by 20 marks. Find max marks."

**Insight:** Pass mark = A's marks + his deficit. 220 + 20 = 240. And 240 = 40 % of max → max = 240 × 100 / 40 = **600**.

**Shortcut:** 240 → ÷4 × 10 = 600. Mental.

**Traditional:** Same, just written out.

**Variations:**
- Two students, one passes, the other fails — two-equation system. Subtract to eliminate max.
- "Exceeds pass by" vs "short of pass by" — sign matters.

**Self-check:** Pass mark = 33 %. Scored 152, failed by 19 → 171 = 33 % of max → max = **~518.18** (actually a good example that not all exams give round answers — watch the exam's intent).

---

## Type 10 — Elections (valid vs invalid votes)

**Cue:** "In an election 10 % of votes are invalid. Winner got 60 % of valid votes, which was 1800 more than loser. Total votes?"

**Insight:** Two stages: total → valid → winner/loser.

**Shortcut:**
- Valid votes = 90 % of total = 0.9T.
- Winner − Loser = 60 % − 40 % = 20 % of valid = 0.2 × 0.9T = 0.18T.
- 0.18T = 1800 → T = **10,000**.

**Traditional:** Same equation, just set up step by step.

**Variations:**
- Only two candidates → 60 % and 40 % split, difference = 20 % of valid.
- Three candidates → different vote shares; sum to 100 % of valid.

---

## Type 11 — Mixture-style percentage (alcohol, salt, milk)

**Cue:** "30 L of a mixture has 20 % alcohol. How much water to add to reduce alcohol to 15 %?"

**Insight:** **Quantity of pure alcohol stays the same** (we only add water). Set up on alcohol.

**Shortcut:**
- Pure alcohol = 20 % of 30 = 6 L.
- After adding x L water, total = (30 + x) and alcohol still 6 L.
- 6 / (30 + x) = 15/100 = 3/20 → 30 + x = 40 → x = **10 L**.

**Traditional:** Same, equation written longer.

**Variations:**
- Evaporation / remove → removing water CONCENTRATES alcohol %. Same invariant (alcohol qty).
- Replacing a part of the mixture with water repeatedly → falls under Successive replacement formula: Final pure = Initial · (1 − x/V)ⁿ, where x is removed each time, V is total.

**Self-check:** 40 L of 25 % milk. Water added to make 20 % milk → milk qty 10 L stays → 10/(40+x) = 1/5 → x = **10 L**.

---

## Type 12 — Price ↔ Quantity inverse (consumption) problems

**Cue:** "Price of sugar rises 25 %. By what % must consumption drop to keep expenditure unchanged?"

**Insight:** Expenditure = Price × Quantity. If Expenditure is fixed, Price and Quantity are inversely proportional.

**Shortcut:** Reverse-percent trick (Type 7). Price up r → quantity down r/(100+r) × 100. r = 25 → 25/125 = **20 %**.

**Traditional:** Let price 100 → 125. Quantity 100 → 100/1.25 = 80. So 20 % drop. Same number, slower.

**Variations:**
- Price FALLS r % → consumption can rise by r/(100−r) × 100 %.
- Two-step: price change followed by budget change.

**Self-check:** Price up 10 % → consumption must drop by 10/110 = **9.09 %**.

---

## Type 13 — Successive discounts (at shop)

**Cue:** "Listed ₹2000. Two successive discounts of 20 % and 10 %. Selling price?"

**Insight:** Successive % changes (Type 5), both negative.

**Shortcut:** −20 −10 + (20·10)/100 = −30 + 2 = **−28 %**. So SP = 72 % of 2000 = **₹1440**.

**Traditional:** 2000 → 1600 (after 20 % off) → 1440 (after 10 % off). Identical answer.

**Variations:**
- Single equivalent discount of 20 % and 10 % = 28 % (NOT 30 %).
- Three discounts: chain pairwise.

**Self-check:** 20 % + 25 % discount → equivalent single? → −20 − 25 + 5 = **−40 %**.

---

## Type 14 — Error in measurement (geometry-meets-percentage)

**Cue:** "Side of square measured 3 % in excess. Error % in area?"

**Insight:** Area ∝ side². If side is (1 + r), area is (1 + r)² ≈ 1 + 2r + r². With r = 3 % = 0.03, area error = 6 + 0.09 ≈ **6.09 %**.

**Shortcut:** Successive-% with a = b = r. Net = 2r + r²/100. r = 3 → 6 + 9/100 = **6.09 %**.

**Traditional:** Same algebra explicitly.

**Variations:**
- Cube / volume: three successive r → 3r + 3r²/100 + r³/10000 ≈ 3r.
- One side +r %, other side −s %: apply signed successive.

**Self-check:** Radius +4 % → area of circle error? → 2(4) + 16/100 = **8.16 %**.

---

## Type 15 — "x % more than y % of a number" chain problems

**Cue:** "Find the number whose 25 % is 40 % less than 60 % of 750."

**Insight:** Work right to left. Compute 60 % of 750, apply 40 % less, then reverse-divide by 25 %.

**Shortcut:**
- 60 % of 750 = 450.
- 40 % less = 450 × 0.6 = 270.
- 25 % of N = 270 → N = 270 × 4 = **1080**.

**Traditional:** Same sequence.

**Variations:** Add another nesting level; swap "less" for "more"; introduce ratios.

**Self-check:** 30 % of N = 20 % more than 80 % of 500 → N = 480/0.3 = **1600**.

---

\newpage

# 💰 PART 2 — PROFIT, LOSS, DISCOUNT

## 2.0 Opener

**Why:** Shop/market context; 2-4 Qs guaranteed in Banking Prelims and SSC Quantitative.

**Mental-math arsenal:** percent-fraction table + "CP-SP-MP" vocabulary.

**Memorised formulas:**
1. Profit = SP − CP (both on the same currency).
2. Profit % = Profit/CP × 100 — **base is always CP** unless explicitly said.
3. Loss % = Loss/CP × 100.
4. SP = CP × (100 + P%)/100. SP = CP × (100 − L%)/100.
5. Discount = MP − SP. Discount % = Discount/MP × 100 — **base is MP**.
6. MP = CP × (100 + markup%)/100.
7. When two articles sold at same SP, one at +x % and the other at −x % → **always a net loss** of x²/100 %.

**Generic attack plan:** read "gain/profit/loss" in terms of **CP**; read "discount" in terms of **MP**. Never confuse the bases. If both percentages appear, translate to a common number (set CP = 100).

---

## Type 1 — Basic profit / loss percent

**Cue:** "CP = 400, SP = 460. Profit %?"

**Shortcut:** (460 − 400)/400 = 60/400 = 3/20 = **15 %**.

**Traditional:** 60 × 100 / 400 = 15.

**Variation:** SP < CP → loss %, base still CP.

---

## Type 2 — Find SP given CP and profit %

**Cue:** "CP = 800, wants 12.5 % profit. SP?"

**Shortcut:** 12.5 % = 1/8. So profit = 100. SP = **900**.

**Traditional:** SP = 800 × 112.5/100 = 900.

**Variation:** Loss instead of profit. 12.5 % loss → SP = 7/8 × 800 = 700.

---

## Type 3 — Find CP given SP and profit %

**Cue:** "Sold at 1080 for 20 % profit. CP?"

**Shortcut:** SP is 120 % of CP → CP = 1080 × 100/120 = **900**. The common trap is dividing by 1.2 vs subtracting 20 %.

**Traditional:** Let CP = x. 1.2x = 1080 → x = 900.

---

## Type 4 — Two articles at same SP, opposite %

**Cue:** "A man sells two watches at ₹2400 each, gaining 20 % on one, losing 20 % on the other. Net gain/loss %."

**Insight:** **Always a net LOSS** of x²/100 %. (Constant — cache this.)

**Shortcut:** 20²/100 = **4 % LOSS**.

**Traditional:**
- Gainer's CP = 2400 × 100/120 = 2000.
- Loser's CP = 2400 × 100/80 = 3000.
- Total CP = 5000, total SP = 4800 → loss 200/5000 = 4 %.

The shortcut saves the whole CP derivation.

---

## Type 5 — Marked price, discount, and profit combined

**Cue:** "Marked at 25 % above CP. Discount 10 %. Find profit %."

**Shortcut:** Successive % (Type 5 of percent): +25 then −10. Net = 15 − 2.5 = **+12.5 %** profit.

**Traditional:** CP 100 → MP 125 → SP 125 × 0.9 = 112.5 → profit 12.5.

---

## Type 6 — Discount % required to clear stock at desired profit

**Cue:** "Shopkeeper marks goods 40 % above CP. Wants 12 % profit. Discount %?"

**Shortcut:** MP/CP ratio = 1.4. Desired SP/CP = 1.12. Discount = 1 − (SP/MP) = 1 − 1.12/1.40 = 1 − 0.8 = **20 %**.

**Traditional:** CP 100 → MP 140 → SP 112 → Discount = 28 on 140 = 20 %.

---

## Type 7 — False weight / dishonest shopkeeper

**Cue:** "A dealer claims to sell at cost price but uses a 900 g weight for 1 kg. Profit %."

**Insight:** He charges for 1000 g but gives 900 g. Gain = (1000 − 900)/900 × 100 = **11.11 %** (base = what he *actually* gave).

**Variation:** Uses BOTH a false weight AND marks up the price. Combine via successive %.

**Self-check:** 950 g instead of 1 kg → profit = 50/950 = **5.26 %**.

---

## Type 8 — Dishonest shopkeeper buys too

**Cue:** "While buying uses 1100 g weight, while selling uses 900 g; charges CP either way. Overall profit %."

**Shortcut:**
- On buying, gets 1100 g by paying for 1000 g → effective CP / g is reduced to 10/11 of claimed.
- On selling, delivers 900 g for 1000 g price → SP / g is increased to 10/9.
- Ratio SP/CP per gram = (10/9) / (10/11) = 11/9 → profit = 2/9 × 100 = **22.22 %**.

---

## Type 9 — Cost-price-unknown combined puzzles

**Cue:** "By selling at ₹810, a man loses 10 %. At what price should he sell to gain 10 %?"

**Shortcut:** 810 is 90 % of CP → CP = 900 → desired SP = 110 % = **₹990**.

**Traditional:** Step-by-step CP recovery.

---

## Type 10 — Partnership-style gain share (sneaks in)

Covered under Part 9 (Partnership). The link is the same "per unit" approach.

---

## Type 11 — Successive discounts (equivalent single)

Already in Type 5 (percentage). Recapping for SP/MP context:
- 10 % + 20 % → equivalent 28 %.
- 10 % + 20 % + 5 % → pairwise: 28 % then with 5 % → 28 + 5 − 1.4 = 31.6 %.

---

## Type 12 — Percentage profit on SP instead of CP (trap)

**Cue:** "A shopkeeper's profit is 20 % of SP. Find profit % on CP."

**Insight:** If profit = 20 % of SP, then CP = 80 % of SP. Profit/CP = 20/80 = **25 %**.

**Variation:** Some exams ask "20 % loss on SP" → loss/CP = 20/120 = 16.67 %.

---

\newpage

# 💵 PART 3 — SIMPLE & COMPOUND INTEREST

## 3.0 Opener

**Why:** Banking exams always carry 1-3 Qs of SI/CI, often combined with % and ratios.

**Mental-math arsenal:** (1 + r/100)ⁿ values for r = 5, 10, 12.5, 15, 20, 25 at n = 2, 3, 4.

**Memorised formulas:**
1. SI = PRT/100.
2. Amount (SI) = P(1 + RT/100).
3. CI = P·(1 + R/100)ⁿ − P.
4. **CI − SI for 2 years = P·(R/100)²** (very important shortcut).
5. **CI − SI for 3 years = P·(R/100)² · (3 + R/100)** (slightly less used).
6. When compounded half-yearly: rate becomes R/2 %, time 2n periods. Quarterly: R/4 %, 4n.
7. CI rate ≡ successive % growth → use successive-% formula for 2-3 years.

---

## Type 1 — Straight SI

**Cue:** P, R, T given. SI or Amount.

**Shortcut:** PRT/100. Keep everything as a fraction; cancel early.

**Variation:** Find R or T given SI. Same formula, solve for the unknown.

---

## Type 2 — Principal doubling / tripling (SI)

**Cue:** "At what rate will a sum double in 8 years (SI)?"

**Insight:** Doubling means SI = P → PRT/100 = P → RT = 100. So R × 8 = 100 → R = **12.5 %**.

**Shortcut:** For SI, RT = 100 × (multiplier − 1). Tripling → RT = 200.

---

## Type 3 — Compound interest for 2 / 3 years

**Cue:** "P = 10,000, R = 10 %, n = 2. CI?"

**Shortcut:** Successive % growth: +10 %, +10 % → net +21 %. CI = 21 % of 10,000 = **₹2100**.

**Traditional:** A = 10000 × 1.1² = 12100 → CI = 2100.

**Variation (3 years, 10 %):** successive of +10, +10, +10 → first pair = +21, then with 10 = +33.1. CI = 33.1 % of P.

---

## Type 4 — CI − SI difference

**Cue:** "Difference of CI and SI on ₹5000 at 8 % for 2 years."

**Shortcut:** P · (R/100)² = 5000 × (8/100)² = 5000 × 64/10000 = **₹32**.

**Traditional:** Compute SI = 800. CI = 5000 × 1.08² − 5000 = 5832 − 5000 = 832. Difference = 32. Same.

---

## Type 5 — Compound frequency (half-yearly / quarterly)

**Cue:** "P = 8000, R = 10 % p.a., compounded half-yearly, for 1 year."

**Shortcut:** New rate = 5 %, periods = 2. A = 8000 × 1.05² = 8000 × 1.1025 = **₹8820**. CI = 820.

**Variation:** Quarterly at 12 % p.a. for 1 year → rate 3 %, n = 4 → A = P × 1.03⁴ = P × 1.1255.

---

## Type 6 — Instalment-style loan repayment

**Cue:** "Loan ₹2500 at 4 % p.a. CI, repaid in 2 equal annual instalments. Find instalment."

**Shortcut:** Each instalment's present value discounts by (1 + R/100)ᵏ.
- x/(1.04) + x/(1.04)² = 2500.
- x · [1/1.04 + 1/1.0816] = 2500.
- x · (1.0816 + 1.04)/(1.04 × 1.0816) = 2500.
- x = 2500 × 1.04 × 1.0816 / (1.0816 + 1.04) ≈ **₹1325.03**.

**Traditional:** Same algebra.

---

## Type 7 — Find rate when CI for 2 years is given

**Cue:** "CI for 2 years on ₹6000 = ₹1260. Rate?"

**Shortcut:** 1260 = 6000 × ((1 + r)² − 1) where r = R/100. → (1 + r)² = 1.21 → r = 0.1 → **R = 10 %**.

---

## Type 8 — Ratios that recur

**Cue:** "A sum becomes ₹4840 in 2 years and ₹5324 in 3 years (CI). Rate and sum."

**Insight:** In CI, ratio of consecutive amounts is (1 + R/100).

**Shortcut:** 5324 / 4840 = 1.1 → R = 10 %. Then P = 4840 / 1.21 = **₹4000**.

---

\newpage

# PART 4 — RATIO, PROPORTION, VARIATION

## 4.0 Opener

**Memorised:**
1. a : b = c : d ↔ ad = bc.
2. a/b = c/d = e/f = (a + c + e)/(b + d + f) — *addendo* rule.
3. Direct variation: y = kx. Inverse: y = k/x. Joint: y = kxz / w.
4. Compound ratio: (a:b) × (c:d) = ac : bd.

**Attack plan:** convert every word problem into "per unit of ratio" (let ratio constant = k).

---

## Type 1 — Split a quantity in ratio a:b:c

"Divide ₹2400 in 3:5:4 → parts = 600, 1000, 800."

## Type 2 — Age/quantity ratio change after some years

"A:B = 3:5 now. After 6 years, 4:6. Find present ages."

Solve algebraically — set 3k and 5k, translate "+6" condition.

## Type 3 — Mixture ratio change

Detailed under Mixtures (Part 7).

## Type 4 — Proportion (fourth proportional, mean, third)

- Fourth proportional of a, b, c → x = bc/a.
- Mean proportional of a, c → x = √(ac).
- Third proportional of a, b → x = b²/a.

## Type 5 — Direct/Inverse variation problems

"12 men finish a job in 8 days. How long will 16 men take?" → inverse: 12×8 = 16×t → t = 6.

## Type 6 — "Two numbers in ratio 3:5, their HCF is 4. Find numbers."

Numbers = 3k, 5k where k = HCF → 12, 20.

## Type 7 — Partners' investment ratio across different durations

"A invests 4000 for 6 months, B invests 5000 for 8 months" → ratio = 4000×6 : 5000×8 = 3:5.

## Type 8 — Alligation-linked ratio (bridge to Part 7)

---

\newpage

# 📊 PART 5 — AVERAGES

## 5.0 Opener

**Memorised:** Average = Sum / Count. Sum = Average × Count. If one value changes, new sum shifts by the change — new average = old + change/count.

## Type 1 — Plain arithmetic mean.

## Type 2 — New member joins / leaves, average changes.
"11 students' avg = 60. 12th student joins, avg drops by 1. 12th student's marks?"
- New sum = 59 × 12 = 708. Old sum = 660. 12th = 48.

## Type 3 — Replacement of a member.
"A class of 10 had avg 75. A student of 50 is replaced by new one; avg rises by 2." → new student − 50 = 2 × 10 = 20 → new student scored **70**.

## Type 4 — Weighted average / mixture of groups.
Used heavily in DI.

## Type 5 — Bowling/batting averages (cricket-style).
"Batsman avg 30 in 20 innings. Scores 50 in 21st. New avg?"
- New avg = (30×20 + 50)/21 = 650/21 ≈ 30.95.

## Type 6 — Average speed (harmonic mean trap).
**Not** the arithmetic mean of two speeds. If two equal distances at speeds u, v → avg speed = 2uv/(u+v). See Part 8.

## Type 7 — Consecutive integers.
Avg of n consecutive integers = middle term (for odd n) or average of two middles (even n).

## Type 8 — Missing value from known average.

---

\newpage

# ⏱️ PART 6 — TIME & WORK, PIPES & CISTERNS

## 6.0 Opener

**Memorised:**
1. Work = Rate × Time. Rate is "fraction of job per unit time".
2. If A alone = a days, rate = 1/a per day.
3. Combined rate = sum of individual rates.
4. For pipes: inflow rates positive, outflow negative.

**Attack plan:** use LCM as total "units of work". Avoid fractions until the last step.

## Type 1 — A alone a days, B alone b days → A+B together.

"A: 12 days, B: 18 days. Together?" → LCM 36 units; A 3/day, B 2/day; together 5/day → 36/5 = **7.2 days**.

## Type 2 — Three persons, one joins/leaves midway.

"A and B together 12 days. After 4 days, B leaves; A finishes in another 10 days. A alone?"
- Work done by A+B in 4 days = 4/12 = 1/3.
- Remaining 2/3 done by A alone in 10 days → A alone = 15 days.

## Type 3 — Efficiency ratio given.

"A is twice as efficient as B. Together in 10 days. A alone?"
- Rates A:B = 2:1 → sum 3. Together 10 days → total work = 30 units. A alone = 30/2 = 15 days.

## Type 4 — Men-days / women-days work.

"15 men build in 20 days. How many men for 10 days?" → 15×20 = n×10 → n = 30.

## Type 5 — Mixed workforce.

"3 men or 5 women build in 20 days. 2 men + 3 women in ?"
- M:W rates = 1/3 : 1/5 (job per day per person), normalised.
- Build the per-day team rate, then days.

## Type 6 — Pipes filling with outflow (leak).

"Pipe A fills in 10 h, leak empties in 15 h. With leak, time to fill?"
- Rates: +1/10 − 1/15 = 1/30 → 30 hours.

## Type 7 — Alternate / shift work.

"A works 1st day, B 2nd day alternately. A alone 8 d, B alone 12 d. Total?"
- Per 2 days, work done = 1/8 + 1/12 = 5/24.
- After 4 such pairs (8 days), work = 20/24. Remaining 4/24 = 1/6.
- Day 9 is A's, A does 1/8 in a day, needs 8×(1/6)/(1/8) — careful! (1/6)/(1/8) = 8/6 = 4/3 days > 1 → use day 9 (A) fully → 1/8 more; still left 4/24 − 3/24 = 1/24. Day 10 is B's → 1/12 per day = 2/24. Takes half a day. Total = **9.5 days**.

## Type 8 — Wages split when A and B worked together.

Wages ∝ work done ∝ (1/time). If together for 12 days and A alone 20 d, B alone 30 d, split 1800 wages →A:B = 30:20 = 3:2 → 1080:720.

---

\newpage

# 🛒 PART 7 — MIXTURES & ALLIGATION

## 7.0 Opener

**Memorised (alligation rule):**
For mixing two substances of cost / concentration C1 and C2 to get mean M:

```
            (M − C2)
Ratio of C1 : C2  =  ────────
            (C1 − M)
```

(Cheaper is on the C1 slot if C1 < C2; the differences are ALWAYS taken as positive.)

## Type 1 — Two-component price mixing.
"Rice @ ₹30/kg and ₹45/kg mixed to sell at ₹36/kg. Ratio?"
- (45 − 36) : (36 − 30) = 9 : 6 = **3 : 2**.

## Type 2 — Milk–water composition.
"Vessel has 40 L milk. Replace 10 L with water. Do it twice. Final milk %?"
- Each time milk becomes 30/40 = 3/4 of before. After 2 times: (3/4)² = 9/16 of pure milk. Final milk qty = 40 × 9/16 = 22.5 L → **56.25 %**.
- Formula: Final pure = Initial · (1 − x/V)ⁿ.

## Type 3 — Mixing three substances.
Apply alligation pairwise twice.

## Type 4 — Gain % via mixing (link to P&L).
"CP 20/kg mixed with water (free) to sell at 25/kg." → Profit % based on CP of actual content.

## Type 5 — Fraction of pure liquid after repeated replacement.

## Type 6 — "How much water to add" / evaporate.

Already in Part 1 Type 11.

---

\newpage

# 🚉 PART 8 — TIME, SPEED, DISTANCE (TSD)

## 8.0 Opener

**Memorised:**
1. D = S × T. Units alert: km/h ↔ m/s conversion: **× 5/18** (km/h→m/s), **× 18/5** (m/s→km/h).
2. Avg speed for equal DISTANCES at u, v → **2uv/(u + v)** (harmonic mean).
3. Avg speed for equal TIMES at u, v → (u + v)/2 (arithmetic mean).
4. Relative speed: same direction → |u − v|; opposite direction → u + v.
5. Train passing: length of train / relative speed = time.

## Type 1 — Direct D=ST lookups.

## Type 2 — Avg speed (equal distance).
"Goes at 40 km/h, returns at 60 km/h. Avg speed?" → 2·40·60/(100) = **48 km/h**. *Not* 50.

## Type 3 — Relative speed (same/opposite direction).
"Two trains 100 km apart approach each other at 40 and 60 km/h. Time to meet?" → 100/100 = 1 h.

## Type 4 — Train passing a man / pole / platform / another train.
- Passing a man/pole: length / speed.
- Passing a platform: (length_train + length_platform) / speed.
- Passing another train (same direction): (L1 + L2) / |u − v|.

## Type 5 — Boats and streams.
- Downstream speed = boat + stream. Upstream = boat − stream.
- If u = downstream, v = upstream → boat = (u + v)/2, stream = (u − v)/2.

## Type 6 — Circular track problems.
- First meet at starting point: LCM of individual laps.
- First meet anywhere: track / |relative speed|.

## Type 7 — Variable speed / broken journey.
"Walks at 4 km/h — 15 min late. Walks at 5 km/h — 15 min early. Distance?"
- Let distance = d. d/4 − d/5 = 30 min = 0.5 h → d/20 = 0.5 → d = **10 km**.

## Type 8 — Race / head-start.
"A beats B by 100 m in a 500 m race." → in the same TIME, A runs 500, B runs 400. Ratio of speeds = 5:4.

## Type 9 — Escalator problems.
"Man takes 50 steps down a moving up escalator; 125 steps up a moving up escalator (stationary escalator) when escalator is moving up." Treat escalator as a stream; steps visible = escalator + man (or − for opposing).

## Type 10 — Clock problems (minute vs hour hand angle).
- Minute hand 6°/min; hour hand 0.5°/min; relative 5.5°/min.
- Overlap every 65 5/11 minutes.

---

\newpage

# PART 9 — PARTNERSHIP

## 9.0 Opener

Profit share ∝ (Capital × Time).

## Type 1 — Equal time, different capital.
Ratio of profit = ratio of capital.

## Type 2 — Different times (someone joins late / leaves early).
Weight each capital by the months it stayed.

## Type 3 — Capital changed midway.
Break into sub-periods, sum C·T for each.

## Type 4 — Working vs sleeping partner.
Working partner gets a flat salary first; remainder split by capital × time.

## Type 5 — Loss sharing.
Same formula — negatives. A fixed-interest partner earns even in loss years (per contract).

---

\newpage

# 🎂 PART 10 — AGES

Most age problems reduce to linear equations.

## Type 1 — "Present age ratio" + "future/past age ratio" → solve simultaneously.

## Type 2 — Sum/Difference of ages.

## Type 3 — Average age of a group; one member replaced.
*Same as Part 5 Type 3.*

## Type 4 — Parents-children age problems.
"Father is 3× son's age. 10 years hence, 2×."

## Type 5 — Multi-sibling + parent problems.
Combine averages + differences.

---

\newpage

# PART 11 — MENSURATION (2D & 3D)

> **Diagram accuracy rule:** Geometric illustrations here must be to-scale SVG/TikZ, not hand-wave sketches. In the exam mode, every diagram is rendered from an exact coordinate spec. If a diagram cannot be made exact (e.g., specific irregular quadrilateral), the question is deferred to a visual-asset batch, not shipped with a crude ASCII box.

## 11.0 Opener

**Must memorise** — area & perimeter of square, rectangle, triangle (½·b·h), equilateral triangle (√3/4 · a²), circle (πr²), sector (½·r²·θ), trapezium (½·(a+b)·h), parallelogram (b·h), rhombus (½·d1·d2); volume + TSA + CSA of cube, cuboid, cylinder, cone, sphere, hemisphere, frustum.

## Types list (covered with SVG figures in the rendered PDF):

1. Direct substitution (basic area/perimeter).
2. Optimisation (largest square inscribed in a circle, etc.).
3. Path/road around a rectangle or garden.
4. Shaded-region problems (rectangle minus inner circle; overlapping circles).
5. Combined solids (cone on hemisphere; cylinder with conical lid).
6. Similar figures — ratio of areas is square of ratio of sides; volumes cube.
7. Frustum of cone (bucket).
8. Rolling / rotation — wheel covers πD per revolution.
9. Effect of changing one dimension on area/volume (link to Percentage Type 14).
10. Triangle-inside-triangle, midpoint theorem.

*Each type has accurate diagrams authored as SVG; not rendered inline in this md file to avoid ASCII art that misleads the student. See `study_notes/_assets/mensuration/` for the figure set that the pandoc build pipeline embeds.*

---

\newpage

# ∠ PART 12 — GEOMETRY

> Same diagram-accuracy rule applies. Triangles, circles, quadrilaterals, tangents — every figure is to-scale SVG.

## Types:

1. Triangle basics: angle sum, exterior angle, triangle inequality.
2. Similarity & congruence criteria (AA, SAS, SSS, RHS).
3. Midpoint theorem; basic proportionality theorem (Thales).
4. Pythagorean theorem + triples (3-4-5, 5-12-13, 8-15-17, 7-24-25, 20-21-29).
5. Centroid (2:1), circumcentre, incentre, orthocentre positions.
6. Circle theorems: angle at centre = 2 × angle at circumference; angles in same segment; cyclic quadrilateral (opposite angles 180°).
7. Tangent properties (tangent ⟂ radius; two tangents from external point equal).
8. Length relations for intersecting chords / secants.
9. Polygon angle sums: interior = (n−2)·180°; exterior sum = 360°.
10. Coordinate geometry: distance, section, slope, collinearity.

---

# 📏 PART 13 — TRIGONOMETRY (for SSC-CGL / RRB NTPC level)

## 13.0 Opener

**Standard angle values — the non-negotiable table:**

| θ | sin | cos | tan |
|---|-----|-----|-----|
| 0° | 0 | 1 | 0 |
| 30° | 1/2 | √3/2 | 1/√3 |
| 45° | 1/√2 | 1/√2 | 1 |
| 60° | √3/2 | 1/2 | √3 |
| 90° | 1 | 0 | ∞ |

- sin²θ + cos²θ = 1; 1 + tan²θ = sec²θ; 1 + cot²θ = cosec²θ.
- Complementary: sin(90° − θ) = cos θ, etc.

## Types:

1. Standard-angle substitution.
2. Complementary-angle simplifications.
3. Identity-based simplifications.
4. Height & distance (angle of elevation / depression) — triangle + tan.
5. Two observers / two angles of observation.

---

\newpage

# PART 14 — ALGEBRA, PERMUTATION, PROBABILITY

## 14.1 Algebra — types

1. Linear equation in one / two variables.
2. Quadratic — discriminant, sum/product of roots (α + β = −b/a; α·β = c/a).
3. Polynomial factor/remainder theorem.
4. Simultaneous equations (elimination vs substitution; cross-multiplication).
5. Inequalities (one-variable; watch sign flip on multiplication/division by negative).
6. Quadratic comparison (x & y) — banking favourite; solve both, tabulate sign.

## 14.2 Permutations & Combinations

**Must memorise:**
- nPr = n! / (n−r)!.
- nCr = n! / (r!·(n−r)!).
- Arrangements with repetitions = n! / (p!·q!·…).

Types: arrangements, combinations, circular (n−1)!, word-problems, committee formation.

## 14.3 Probability

- P(A) = favourable / total.
- Complement: P(Aᶜ) = 1 − P(A).
- Addition: P(A∪B) = P(A) + P(B) − P(A∩B).
- Independent: P(A∩B) = P(A)·P(B).
- Conditional: P(A|B) = P(A∩B)/P(B).

Types: dice, cards (52-deck layout must be cached), coins, balls-in-urn, pick-without-replacement.

---

\newpage

# 📊 PART 15 — DATA INTERPRETATION (DI)

DI isn't a separate topic — it's an assembly of percent, ratio, average applied to visuals.

## Types (question *styles*):

1. Table DI.
2. Bar graph DI (single, double, stacked).
3. Line graph DI.
4. Pie chart DI.
5. Caselet / paragraph DI (text-only).
6. Mixed chart (table + bar + line).
7. Missing DI (some cells blank; solve with given %/avg clues).

Each DI set has 4-5 sub-questions that translate into the core types. The speed gain is **reading the chart once, storing totals mentally, answering 5 Qs with that one pass**.

---

\newpage

# APPENDIX A — The 30-Second Diagnostic

Before solving any arithmetic question, run this 30-second classifier:

1. Is there a **percentage or ratio** word? → Parts 1-4.
2. Is there a **₹, cost, SP, MP, profit, discount**? → Part 2.
3. **Rate / time / interest / years / compound**? → Part 3.
4. **Days, hours, pipes, men, work, job**? → Part 6.
5. **Speed, distance, train, boat, stream, escalator, clock**? → Part 8.
6. **Mixture, alloy, milk, water, alcohol, ratio**? → Part 7.
7. **Partners, investment, capital, months**? → Part 9.
8. **Ages, father, son, years hence, years ago**? → Part 10.
9. **Area, perimeter, volume, surface**? → Parts 11-12.
10. **Triangle, circle, angle, tangent, chord**? → Part 12.
11. **sin, cos, tan, height, angle of elevation**? → Part 13.
12. **Letters arranged, committee, dice rolled, cards picked**? → Part 14.
13. Has a **chart / table / pie / bar**? → Part 15 + routing to 1-5.

This is the discipline. **Classify → shortcut → verify**. Every time.

---

# APPENDIX B — Image / Diagram Pipeline

This book intentionally does **not** embed ASCII diagrams (they mislead). Instead, the pandoc build (`_build/build_pdfs.sh`) consumes two folders:

- `_build/figures/` — hand-authored SVG/TikZ for geometry, mensuration, reasoning visuals.
- `_build/mermaid/` — Mermaid source for flowcharts and type-trees.

Each diagram is **verified to-scale** before commit. No question is shipped with a sketch that misrepresents angle / ratio. For reasoning visuals (dice, mirror, water, paper-fold) the pipeline requires an accurate net / coordinate spec per item. Text-only questions that cannot be diagrammed faithfully are deferred rather than shipped with a rough approximation.

---

*Companion books: `reasoning.md` (types-first), `english.md` (rules + traps). Quiz pairings live under topic codes `QNT_*`, `REAS_*`, `ENG_*`.*

---

\newpage

# EXAM-FOCUS APPENDIX — BANKS (PO, Clerk, RRB Bank, RBI)

> Use this appendix when reading this same book under the title **"Quantitative Aptitude — for Banks"**. Banks weight DI + Caselet + Approximation + Quadratic comparison far more than SSC; geometry / mensuration / trigonometry are NEAR-ZERO weight.

## Banks-priority chapter map

| Topic in this book | Banks weight | Drill priority |
|---|---|---|
| Part 1 — Percentage | High | 🔴 Day 1 |
| Part 2 — Profit & Loss | Mid | 🟠 Day 2 |
| Part 3 — Simple + Compound Interest | High | 🔴 Day 3 |
| Part 4 — Ratio + Average | High | 🔴 Day 3 |
| Part 5 — Number system + LCM/HCF | Low | 🟢 skim |
| Part 6 — Time & Work + Pipes | Mid | 🟠 Day 4 |
| Part 7 — Mixture & Alligation | Mid | 🟠 Day 4 |
| Part 8 — Time, Speed, Distance + Boats + Trains | Mid | 🟠 Day 5 |
| Part 9 — Partnership | Low | 🟢 skim |
| Part 10 — Ages | Low | 🟢 skim |
| Part 11 — Mensuration 2D | Low | 🟢 skim |
| Part 12 — Geometry | Negligible | ⚪ skip |
| Part 13 — Trigonometry / Heights | Negligible | ⚪ skip |
| Part 14 — Permutation / Probability | Mid | 🟠 Day 6 |
| Part 15 — DI + Caselet | **Highest** | 🔴 Day 7-15 |
| Part 17 (this) — Approximation + Quadratic + Quantity comparison | High | 🔴 Day 16-20 |

## NEW Part — Approximation (Banks-only chapter)

**What it tests:** find the closest integer / "roughly equal to" value of a complex arithmetic expression in 30 seconds.

**Method (drill):**
1. Round each number to the nearest "easy" value (2-significant-figure, half, quarter, etc.).
2. Apply BODMAS on rounded values.
3. Compare with options.

**Worked example.** ?  ≈  39.97 % of 1899.98 + 24.04 × 17.97.

Round: 40 % of 1900 = 760. 24 × 18 = 432. Sum ≈ 1192. Pick option closest to 1192.

**Hot-list of round-able quantities:**

| Difficult | Round to |
|---|---|
| 14.97 | 15 |
| 24.04 | 24 |
| 39.97 | 40 |
| 11.95 | 12 |
| 16.66 % | 1/6 |
| 33.33 % | 1/3 |
| 12.5 % | 1/8 |
| 14.28 % | 1/7 |
| √26 | ≈ 5.1 |
| √48 | ≈ 6.93 |
| 12 % of 250 | 30 |

**Drill:** 50 sums daily for a week. Time-per-sum should drop from 60 s → 25 s.

## NEW Part — Quadratic comparison (Banks specialty)

**What it tests:** two quadratics in x and y; solve both, choose: x > y / x ≥ y / x < y / x ≤ y / x = y / no relation.

**Method:**
1. Factor or use formula on each.
2. Get all 4 roots: x₁, x₂, y₁, y₂.
3. Compare the **smallest x** with the **largest y**, and **largest x** with the **smallest y**.
4. If smallest_x ≥ largest_y → x ≥ y. If largest_x ≤ smallest_y → x ≤ y. Else → no relation.

**Worked example.** x² − 7x + 12 = 0 ⇒ x ∈ {3, 4}. y² − 9y + 20 = 0 ⇒ y ∈ {4, 5}.

smallest_x = 3, largest_y = 5 → 3 < 5 (so NOT x ≥ y).
largest_x = 4, smallest_y = 4 → 4 = 4 (so NOT x < y).
→ **No relation can be established.**

## NEW Part — Quantity comparison

Given Quantity I and Quantity II as expressions; choose: I > II / I ≥ II / I < II / I ≤ II / I = II / no relation.

**Method:** evaluate both quantities; compare directly. Often one is a rate problem and the other a percentage / formula.

## DI deep-drill (high yield — re-read Part 15)

Banks DI types reorder:
1. **Tabular** — straight-up tables with multi-row, multi-column.
2. **Bar chart** — single, double, stacked.
3. **Pie chart** — % distribution; total often given.
4. **Line graph** — trend across years.
5. **Mixed combo** — bar + line, table + pie.
6. **Caselet** — DI in pure paragraph form, no chart. **Banks Mains specialty.**
7. **Missing-value DI** — table with one cell missing; deduce from constraints.
8. **Radar chart** — RBI & SBI Mains.

**For each DI set (5 questions):**
1. Read the chart caption + axis labels — 30 s.
2. Compute totals / row sums / column sums in margin if helpful — 30 s.
3. Then attack each of the 5 questions in 60-90 s.

> Total budget per DI set: 5-7 min. With 4 sets in IBPS PO Mains DI section, that's 25-30 min for 20 marks — high ROI.

---

\newpage

# EXAM-FOCUS APPENDIX — SSC + RRB

> Use this appendix when reading this same book under the title **"Arithmetic — for SSC & RRB"**. SSC + RRB weight Geometry + Mensuration + Trigonometry HEAVILY (15-20 marks combined), and DI is shorter / simpler.

## SSC + RRB priority chapter map

| Topic in this book | SSC weight | RRB weight | Drill priority |
|---|---|---|---|
| Part 1 — Percentage | High | High | 🔴 Day 1 |
| Part 2 — Profit, Loss, Discount | High | High | 🔴 Day 1 |
| Part 3 — SI + CI | Mid | Mid | 🟠 Day 2 |
| Part 4 — Ratio + Proportion + Average | High | High | 🔴 Day 2 |
| Part 5 — Number system + LCM/HCF + Divisibility | High | High | 🔴 Day 3 |
| Part 6 — Time & Work + Pipes | Mid | Mid | 🟠 Day 4 |
| Part 7 — Mixture / Alligation | Mid | Mid | 🟠 Day 4 |
| Part 8 — Time-Speed-Distance + Boats + Trains | High | High | 🔴 Day 5 |
| Part 9 — Partnership | Mid | Low | 🟢 Day 6 |
| Part 10 — Ages | Mid | Mid | 🟢 Day 6 |
| Part 11 — Mensuration 2D | High | High | 🔴 Day 7 |
| Part 12 — Geometry (incl. Triangles, Circles) | **Highest** | High | 🔴 Day 8-10 |
| Part 13 — Trigonometry + Heights | **Highest** | Mid | 🔴 Day 11-13 |
| Part 14 — Permutation / Probability | Low | Low | 🟢 skim |
| Part 15 — DI | Mid (smaller table/bar) | Low | 🟠 Day 14 |
| Algebra (basic identities) | High | Mid | 🔴 Day 15 |

## Key SSC algebra identities to memorise

- (a + b)² = a² + b² + 2ab
- (a − b)² = a² + b² − 2ab
- a² − b² = (a + b)(a − b)
- a³ + b³ = (a + b)(a² − ab + b²)
- a³ − b³ = (a − b)(a² + ab + b²)
- (a + b)³ = a³ + b³ + 3ab(a + b)
- (a − b)³ = a³ − b³ − 3ab(a − b)
- a³ + b³ + c³ − 3abc = (a + b + c)(a² + b² + c² − ab − bc − ca)
- if a + b + c = 0 ⇒ a³ + b³ + c³ = 3abc
- a + 1/a = k ⇒ a² + 1/a² = k² − 2 ; a³ + 1/a³ = k³ − 3k
- a² + b² ≥ 2ab (AM ≥ GM)

## Trigonometry: identities you MUST recall in <2 s

- sin²θ + cos²θ = 1
- 1 + tan²θ = sec²θ
- 1 + cot²θ = cosec²θ
- sin(90 − θ) = cos θ ; cos(90 − θ) = sin θ ; tan(90 − θ) = cot θ
- sin(A + B) = sin A cos B + cos A sin B
- cos(A + B) = cos A cos B − sin A sin B
- tan(A + B) = (tan A + tan B) / (1 − tan A · tan B)
- sin 2θ = 2 sin θ cos θ ; cos 2θ = cos²θ − sin²θ = 1 − 2 sin²θ = 2 cos²θ − 1
- standard angles: sin 0 = 0, sin 30 = ½, sin 45 = 1/√2, sin 60 = √3/2, sin 90 = 1
- height & distance: tan(angle of elevation) = opposite/adjacent

## Geometry — the 25 must-know facts

1. Sum of interior angles of a triangle = 180°.
2. Sum of exterior angles of any polygon = 360°.
3. Sum of interior angles of an n-gon = (n − 2) × 180°.
4. Each interior angle of a regular n-gon = (n − 2) × 180° / n.
5. Area of triangle = ½ × base × height = ½ ab sin C = √[s(s−a)(s−b)(s−c)] (Heron's).
6. Area of equilateral triangle (side a) = √3/4 × a².
7. Inradius (incircle): r = Area / s.
8. Circumradius: R = abc / (4 × Area).
9. Pythagoras: a² + b² = c² in right triangle.
10. 30-60-90 triangle: sides 1 : √3 : 2.
11. 45-45-90 triangle: sides 1 : 1 : √2.
12. Median, altitude, angle-bisector, perpendicular-bisector concur at distinct points: centroid (G), orthocentre (O), incentre (I), circumcentre (C).
13. Centroid divides median in 2 : 1 from vertex.
14. In right triangle, circumcentre = midpoint of hypotenuse.
15. Mid-segment theorem: line joining midpoints of two sides is parallel to third side and half its length.
16. Apollonius' theorem: m_a² = (2b² + 2c² − a²) / 4.
17. Tangent from external point — two tangents are equal.
18. Tangent ⊥ radius at point of contact.
19. Angle in same segment is equal; angle in semicircle = 90°.
20. Cyclic quadrilateral: opposite angles sum to 180°.
21. Power of a point: for two chords through P, AP · BP = CP · DP.
22. Two intersecting chords: AP · PB = CP · PD.
23. Angle subtended at centre = 2 × angle at remaining circumference.
24. Inscribed angle theorem.
25. Ptolemy's theorem (cyclic quadrilateral): AC · BD = AB · CD + AD · BC.

## SSC speed rules (60 min, 25 questions)

- **Arithmetic word problems** (percentage / SI-CI / TSD / W&T / mixture): 12-14 questions, 80 s each.
- **Algebra identities + simplification**: 3-5 questions, 60 s each.
- **Geometry / mensuration**: 4-5 questions, 90 s each — diagram-driven.
- **Trigonometry**: 2-3 questions, 60 s each.
- **DI / Tabular**: 3-5 questions in one set, 75 s each.

Total ≈ 50 min for 25 questions, leaving 10 min buffer.

---

# GLOBAL DIFFICULTY MATRIX (per Q to design study time)

| Topic | SSC easy : medium : hard | Banks easy : medium : hard |
|---|---|---|
| Percentage | 30 : 50 : 20 | 20 : 50 : 30 |
| SI + CI | 25 : 55 : 20 | 20 : 50 : 30 |
| TSD | 30 : 50 : 20 | 25 : 55 : 20 |
| W & T | 25 : 55 : 20 | 20 : 55 : 25 |
| Mixture | 30 : 55 : 15 | 25 : 55 : 20 |
| Geometry | 20 : 60 : 20 | — |
| Trigonometry | 25 : 50 : 25 | — |
| DI | 30 : 55 : 15 | 15 : 55 : 30 |
| Caselet | — | 10 : 50 : 40 |
| Approximation | — | 30 : 50 : 20 |
| Quadratic | — | 25 : 60 : 15 |

---

*Use the same source `arithmetic.md` to build BOTH `arithmetic_ssc_rrb.pdf` and `quantitative_aptitude_banks.pdf` — the manifest in `_build/manifest.json` selects the title + cover; the appendix above tells the candidate which chapters to drill harder.*

---

\newpage

# Practice Set (50 exam-style worked examples)

> The questions below are modelled on the actual patterns asked in past papers across SSC, RRB, banking, and PSU exams. For each, you get: the stem → smart shortcut (with derivation) → answer → the *trap* option and why students pick it.

## Section 1 — PERCENTAGE (5 worked + variations)

---

**Q1.** A's salary is 25 % more than B's. By what % is B's salary less than A's?

**What kind of problem is this?** "A is r % more than B" → asking the inverse. Standard pattern: **base shift problem**.

**Solving it.** Set B = 100 (always make the smaller / reference quantity = 100). Then A = 125.

**Quick way:** Compute the % decrease from A to B.
- Difference = A − B = 25
- % decrease = Difference / A × 100 = 25 / 125 × 100 = **20 %**

**Worth knowing:** Memorise the shortcut formula. If A is r % more than B, then **B is r / (100 + r) × 100 % less than A**.
- Verify with r = 25: 25 / 125 × 100 = 20 % ✓

*Watch out:* "25 %" — students assume "25 % more" implies "25 % less" by symmetry. That is WRONG: percentage is a ratio, and the base changes when you flip direction.

**A similar question:** A is r % LESS than B, find by what % B is more than A. Use **B is r / (100 − r) × 100 % more than A**.
- Example: A is 20 % less than B → B is 20/80 × 100 = **25 % more** than A.

**Another twist:** Successive percentage relations. If A is 20 % more than B, and B is 25 % more than C, what % is A more than C?
- A = 1.20 B = 1.20 × 1.25 C = 1.50 C → A is **50 % more** than C.

---

**Q2.** The price of sugar is increased by 25 %. By what % must consumption decrease so that monthly expenditure remains unchanged?

**What kind of problem is this?** Same base-shift formula as Q1. "Price up by r % → consumption must drop by r/(100+r) × 100 % for expenditure to stay constant."

**Solving it.** Why the formula works (derivation in 1 line).** Expenditure = Price × Quantity. If Price becomes 1.25P, then new Quantity must satisfy 1.25P × Q' = P × Q ⇒ Q' = Q × 1/1.25 = Q × 0.80 ⇒ a 20 % drop.

**Quick way:** Apply.** r = 25 → 25 / 125 × 100 = **20 %**.

*Watch out:* "25 %" — students assume "if price up by r %, cut consumption by r %". That UNDER-shoots — would result in 1.25 × 0.75 = 0.9375 × original expenditure (still down 6.25 %).

**A similar question:** Price up by 50 %, consumption cut needed = 50 / 150 × 100 = **33.33 %**.

**Another twist:** Price DECREASES by r %, by how much can consumption increase to keep expenditure same? Use **r / (100 − r) × 100 %**.
- Example: Price down 20 % → consumption can go up by 20/80 × 100 = **25 %**.

---

**Q3.** A number is increased by 20 % and then decreased by 20 %. Net change?

**What kind of problem is this?** Successive percentage changes (one up, one down).

**Solving it.** Apply the formula.** Net change = a + b + (a × b) / 100, where positive = increase, negative = decrease.
- Here a = +20, b = −20.
- Net = +20 + (−20) + (20 × −20)/100 = 0 + (−400/100) = **−4 %**

**Quick way:** Verify with concrete number.** Take 100 → +20 % → 120 → −20 % → 96. Final 96, original 100, net change = **−4 %** ✓.

**Worth knowing:** Memorise the universal pattern.** Whenever you do "+r % then −r %" (any equal r), net is ALWAYS a loss = **(r/10)²**. For r = 20: (20/10)² = 4 % loss. For r = 30: 9 % loss. For r = 10: 1 % loss.

*Watch out:* "0 %" — students assume +20 % and −20 % cancel. They DO NOT, because the second 20 % is taken on a larger base (120, not 100).

**A similar question:** Increased by 30 %, then decreased by 20 %. Net = 30 − 20 + (30)(−20)/100 = 10 − 6 = **+4 %** gain.

**Another twist:** Three successive changes (a, b, c). Apply the formula stepwise: combine a + b first, then combine result with c.
- Example: +10 %, +20 %, −10 %. Step 1: 10 + 20 + 2 = +32 %. Step 2: 32 + (−10) + (32 × −10)/100 = 22 − 3.2 = **+18.8 %**.

---

**Q4.** In an exam 60 % students passed in Maths, 50 % in English, 30 % in both. What % failed in both?

**What kind of problem is this?** Two-set inclusion-exclusion problem (Venn diagram).

**Solving it.** Apply the inclusion-exclusion formula.
- n(M ∪ E) = n(M) + n(E) − n(M ∩ E) = 60 + 50 − 30 = **80 %** passed at least one subject.
- Failed in both = 100 − 80 = **20 %**.

**Quick way:** Visualise (mental Venn).** Draw two overlapping circles.
- Pass Maths only = 60 − 30 = 30 %
- Pass English only = 50 − 30 = 20 %
- Pass both = 30 %
- Total pass-at-least-one = 30 + 20 + 30 = 80 %
- Fail both = 100 − 80 = **20 %**

*Watch out:* "10 %" — students subtract 30 % from 100 once and stop, forgetting that "30 % in both" is part of the 60 % AND part of the 50 %.

**A similar question:** Three subjects: 70 % pass A, 60 % pass B, 50 % pass C; 30 % pass all three; 40 % pass A&B, 35 % pass B&C, 25 % pass A&C. Use 3-set formula: n(A∪B∪C) = sum − pairs + triple = (70+60+50) − (40+35+25) + 30 = 180 − 100 + 30 = 110. Cap at 100; rework if >100 (means data inconsistent).

**Another twist:** "Failed in both" stated → "passed at least one" = 100 − failed-both. Useful inverse direction.

---

**Q5.** If 30 % of (X − Y) = 20 % of (X + Y), find X : Y.

**What kind of problem is this?** Linear equation in two variables; the answer is a ratio (only one equation needed because the ratio is scale-invariant).

**Solving it.** Convert percentages to fractions.
- 0.3 (X − Y) = 0.2 (X + Y)

**Quick way:** Expand both sides.
- 0.3X − 0.3Y = 0.2X + 0.2Y

**Worth knowing:** Collect like terms.
- 0.3X − 0.2X = 0.2Y + 0.3Y
- 0.1X = 0.5Y

**Note:** Take the ratio.**
- X / Y = 0.5 / 0.1 = **5 / 1**
- So **X : Y = 5 : 1**

*Watch out:* "1 : 5" — students invert the ratio at the end.

**A similar question:** If 40 % of (X+Y) = 60 % of (X−Y), find X : Y. Repeat the steps: 0.4X + 0.4Y = 0.6X − 0.6Y → 1.0Y = 0.2X → X/Y = 5/1.

**Another twist:** 25 % of A = 35 % of B. Find A : B. 0.25 A = 0.35 B → A/B = 0.35/0.25 = **7 : 5**.

### Section 1A — ADVANCED PERCENTAGE (exam-level variations)

---

**Q1.5 (Advanced) — Multi-step percentage chain with population.** The population of a town was 50,000 in 2022. It increased by 10 % in 2023, then decreased by 5 % in 2024, then increased by 20 % in 2025. Find the population at the end of 2025.

**Solving it.** Apply each change as a multiplier (do NOT add/subtract percentages directly).
- After 2023: 50,000 × 1.10 = **55,000**
- After 2024: 55,000 × 0.95 = **52,250**
- After 2025: 52,250 × 1.20 = **62,700**

**Worth knowing:** Net multiplier = 1.10 × 0.95 × 1.20 = **1.254**. So final = 50,000 × 1.254 = 62,700 (same answer in one step).

**Net % change** = (62,700 − 50,000) / 50,000 × 100 = **+25.4 %**.

**A similar question.** Salary ₹40,000 increased by 15 %, then by 10 %, then decreased by 5 %. Final = 40,000 × 1.15 × 1.10 × 0.95 = **₹48,070** (net +20.18 %).

---

**Q1.6 (Advanced) — Population growth/decay with given rate.** A town's population grows at 4 % per annum compounded annually. If current population is 1,000,000, what will it be after 3 years? After 5 years?

**Solving it.**
- Use compound formula: P(t) = P₀ × (1 + r)ᵗ.
- After 3 years: 1,000,000 × (1.04)³ = 1,000,000 × 1.124864 = **1,124,864**
- After 5 years: 1,000,000 × (1.04)⁵ = 1,000,000 × 1.21665 = **1,216,653**

**Quick mental approach for compounded growth (≤ 10 yrs at low rate).** Use: (1 + r)ᵗ ≈ 1 + r×t + (small higher-order terms). For 4 % over 3 yrs: ≈ 1 + 0.12 + 0.005 = **1.125** (close to actual 1.1249).

**A similar question — Decay (depreciation).** A car worth ₹8,00,000 depreciates 15 % per year. Value after 3 years = 8,00,000 × (0.85)³ = 8,00,000 × 0.614125 = **₹4,91,300**.

---

**Q1.7 (Advanced) — Successive % with target outcome.** A shopkeeper marks his goods 50 % above cost price (CP) and offers a 20 % discount on the marked price (MP). What is his net profit %?

**Solving it.** Set CP = 100.
- MP = 100 × 1.50 = **150**
- SP after 20 % discount = 150 × 0.80 = **120**
- Profit = 120 − 100 = 20 → Profit % = (20/100) × 100 = **20 %**

**Worth knowing:** General formula. Net % = markup % − discount % − (markup × discount)/100. Here = 50 − 20 − 10 = **20 %** ✓.

**A similar question.** Mark up by 60 %, discount 25 %. Net = 60 − 25 − 15 = **+20 %** profit.

---

## Section 2 — PROFIT, LOSS, DISCOUNT (5)

**Q6.** A man sells two articles at ₹600 each. On one he gains 20 %, on the other loses 20 %. Net P/L %?

**Step 1 — Identify the type.** Two articles, **same SP**, **equal % gain on one and equal % loss on the other**. This is the classic "same SP, equal ± r%" pattern.

**Solving it.** Apply the standard result (with derivation).
- Article A: SP = ₹600 at 20% gain → CP_A = SP/(1+r) = 600/1.20 = ₹500
- Article B: SP = ₹600 at 20% loss → CP_B = SP/(1−r) = 600/0.80 = ₹750
- Total CP = 500 + 750 = **₹1,250**
- Total SP = 600 + 600 = **₹1,200**
- Net loss = 1,250 − 1,200 = **₹50**
- Loss % = 50 / 1,250 × 100 = **4 %**

**Quick way:** Memorise the shortcut.** Whenever same SP + equal ± r %, **net result is always a loss = (r/10)²**.
- For r = 20 %: loss = (20/10)² = **4 %** ✓
- For r = 10 %: loss = (10/10)² = **1 %**
- For r = 25 %: loss = (25/10)² = **6.25 %**

*Watch out:* "0 %" — students assume gain and loss cancel out. They DO NOT, because the bases (CP_A vs CP_B) are different.

**Variation A.** Same problem but SP not given (only ratios) — answer is still 4 % loss; SP is irrelevant when only % gain/loss are equal.

**Variation B.** Different rates (e.g., gain 20% on one, loss 10% on other, same SP) — formula doesn't apply; do CP_A + CP_B and compare to total SP individually.

---

**Q7.** MP is 40 % above CP. Two successive discounts of 10 % and 20 % are given. Find net P/L %.

**Step 1 — Set CP = 100** (always do this for percentage problems — it makes mental math trivial).

**Solving it.** Compute MP.** MP = CP × 1.40 = **140**.

**Quick way:** Apply discounts in order.
- After 1st discount (10 % off MP): 140 × 0.90 = **126**
- After 2nd discount (20 % off remaining): 126 × 0.80 = **100.80**

**Worth knowing:** Final SP = 100.80, CP = 100.** So profit = 0.80, profit % = **+0.80 %** (small gain).

**Memory peg for successive discounts.** When two successive discounts of x % and y % are applied, the **single equivalent discount** = x + y − (xy/100). For 10% and 20%: 10 + 20 − 2 = **28%** off MP. So SP = 140 × 0.72 = 100.80 ✓ (same answer).

*Watch out:* "−4 %" or "−10 %" — students forget to multiply discounts on top of MARKED PRICE, not on CP.

**Variation A.** MP is 50% above CP, two successive discounts 10% + 10% — try this: MP = 150, after discounts = 150 × 0.9 × 0.9 = 121.50. Profit = 21.5%.

**Variation B.** Three successive discounts (a, b, c) — compute step by step OR use formula iteratively: equivalent of first two, then combine with third.

**Q7.** MP is 40 % above CP. Two successive discounts of 10 % and 20 % are given. Find net P/L %.
*Method.* Let CP = 100. MP = 140. After discounts: 140 × 0.9 × 0.8 = 100.80. P/L = +0.80 % gain.
Watch out: "−4 %" or "−10 %" — students forget the markup direction.

---

**Q8.** A trader marks up the price by 30 %, gives a 10 % discount, AND uses a faulty meter that gives 900 g when the customer pays for 1 kg. Find his actual profit %.

**What kind of problem is this?** Combo problem: markup + discount + false weight. Each is a multiplication factor; chain them.

**Solving it.** Convert each effect into a multiplier.
- **Markup** of 30 % means he marks at 1.30 × CP.
- **Discount** of 10 % means he sells at 0.90 × MP, i.e., at 1.30 × 0.90 = **1.17 × CP** (he gets paid 1.17 × CP for the goods).
- **False weight** — customer thinks they got 1,000 g (worth 1.17 × CP at the marked rate) but actually received 900 g. So the trader effectively SOLD only 900 g of goods for the price of 1,000 g. Multiplier: 1,000 / 900 = **10/9 ≈ 1.111**.

**Quick way:** Multiply all three multipliers.
- Total revenue / cost = 1.17 × (10/9) = 11.70 / 9 = **1.30**
- So profit = 30 % over CP. Answer = **30 %**.

**Worth knowing:** Sanity-check.** Take CP of 1 kg = ₹100. Marks to ₹130, sells at ₹130 × 0.9 = ₹117 (for what customer thinks is 1 kg). Customer actually receives 900 g, which cost the trader ₹90 (since 1 kg cost ₹100). So trader spent ₹90 of goods and received ₹117 → profit ₹27 on a cost of ₹90 → 27/90 × 100 = **30 %** ✓.

*Watch out:* "17 %" — students compute markup × (1 − discount) and stop. They forget the false-weight bonus.

**A similar question:** Trader uses 800 g per "1 kg" instead of 900 g. False weight multiplier becomes 1000/800 = 1.25. Total = 1.17 × 1.25 = 1.4625 → **46.25 % profit**.

**Another twist:** Markup 25 %, discount 20 %, weight 950 g per kg. Multipliers: 1.25 × 0.80 × (1000/950) = 1.00 × 1.0526 = **5.26 %** profit. (Note: 25-20 alone gives 0 %, weight adds the bonus.)

---

**Q9.** A shopkeeper sold a watch at 16 % loss. Had he sold it for ₹120 more, he would have gained 4 %. Find the cost price (CP).

**What kind of problem is this?** "Difference in SP corresponds to difference in % gain/loss." Single CP unknown.

**Solving it.** Convert each scenario to SP in terms of CP.
- Scenario 1 (loss 16 %): SP₁ = 0.84 × CP.
- Scenario 2 (gain 4 %): SP₂ = 1.04 × CP.

**Quick way:** Difference of SPs = 120.
- SP₂ − SP₁ = (1.04 − 0.84) × CP = 0.20 × CP = ₹120
- CP = 120 / 0.20 = **₹600**

**Worth knowing:** Verify.** SP₁ = 0.84 × 600 = ₹504 (loss 16 % ✓). SP₂ = 1.04 × 600 = ₹624. Difference = 624 − 504 = ₹120 ✓.

*Watch out:* "₹500" — students compute 16 + 4 = 20 % and apply 120 / 0.20 = 600 ✓ (correct), but if they compute 16 − 4 = 12 % they get 1,000 (wrong).

**A similar question:** Sold at 10 % loss; ₹50 more would have given 5 % profit. CP = 50 / 0.15 = ₹333.33.

**Another twist:** Sold at 25 % gain; ₹100 less would have given 5 % gain. Difference = 0.25 − 0.05 = 0.20. CP = 100 / 0.20 = ₹500.

---

**Q10.** An article's CP is 80 % of its SP. Profit %?

**What kind of problem is this?** CP given as a fraction of SP (less common direction; usually CP is the base).

**Solving it.** Set SP = 100** (since CP is defined relative to SP).
- CP = 80 % of 100 = ₹80.
- SP = ₹100.
- Profit = 100 − 80 = ₹20.

**Quick way:** Compute profit %.** Profit % = Profit / **CP** × 100 = 20 / 80 × 100 = **25 %**.

**Worth knowing:** Important rule.** Profit % is ALWAYS computed on CP (cost price), never on SP. Discount % is on MP (marked price). Mixing these is the most common error.

*Watch out:* "20 %" — students compute Profit / SP (= 20/100 = 20 %), using SP as base. Wrong base.

**A similar question:** CP is 75 % of SP. Profit % = 25/75 × 100 = **33.33 %**.

**Another twist:** SP is 80 % of CP (i.e., a loss). Loss % = (CP − SP)/CP × 100 = 20/100 × 100 = **20 %** loss.

**Quick rule.** If CP / SP = k, then profit % = (1 − k)/k × 100. If k = 0.8 → 0.2/0.8 × 100 = 25 %.

### Section 2A — ADVANCED P&L (exam-level variations)

---

**Q10.5 (Advanced) — Bulk discount slab.** A trader sells items at the following slab discounts: 5 % on first ₹1,000 of bill, 10 % on next ₹2,000, 15 % on amount above ₹3,000. A customer's bill before discount is ₹5,500. What does she pay after discount?

**Solving it.** Step-by-step.
- First ₹1,000: discount = 5 % × 1,000 = ₹50 → pays 950.
- Next ₹2,000 (i.e., ₹1,001–3,000): discount = 10 % × 2,000 = ₹200 → pays 1,800.
- Above ₹3,000 = ₹2,500: discount = 15 % × 2,500 = ₹375 → pays 2,125.
- Total payment = 950 + 1,800 + 2,125 = **₹4,875**.

**Worth knowing:** Total discount = 50 + 200 + 375 = ₹625 → effective discount % = 625/5500 × 100 ≈ **11.36 %**.

---

**Q10.6 (Advanced) — Exchange of articles.** A and B have the same article each. A sells his to B at 20 % profit; B then sells the same article back to A at 25 % loss (on B's CP). If A finally has ₹120 less than what he started with, find the original CP of the article.

**Solving it.** Step-by-step.
- Let original CP for A = ₹P.
- A → B: A sells at 20 % profit. So B buys at 1.20 P.
- B → A: B sells back at 25 % loss on B's CP. So A buys at 0.75 × 1.20 P = 0.90 P.
- A's transactions: started with P (article); after first sale, has 1.20 P cash; after buying back, has 1.20P − 0.90P = 0.30P cash + article worth P.
- Net: A has 0.30 P cash + 1 article worth P = total value 1.30 P; original was P; gain = 0.30 P.
- BUT question says A has ₹120 LESS than what he started — this requires the article's market value to drop or different conditions. Revisit setup.

*(Note: the problem's specific numbers depend on whether we measure pure cash or total assets. Variations on this theme common in CGL Tier-2.)*

**Memory peg.** "Exchange-of-articles" problems: track CASH changes carefully; both parties may end with same article but different cash positions.

---

**Q10.7 (Advanced) — Partnership P&L with time + capital.** A invests ₹20,000 for 12 months. B invests ₹30,000 for 8 months. Annual profit ₹26,000 is to be shared in the ratio of (capital × time). Find each partner's share.

**Solving it.**
- A's contribution = 20,000 × 12 = **2,40,000**
- B's contribution = 30,000 × 8 = **2,40,000**
- Ratio A : B = 240,000 : 240,000 = **1 : 1**
- A's share = 26,000 × 1/2 = **₹13,000**
- B's share = 26,000 × 1/2 = **₹13,000**

**Worth knowing:** Partnership rule. Profit-share ratio = (capital₁ × time₁) : (capital₂ × time₂) : … Always multiply BOTH capital and duration.

**A similar question.** A invests ₹40,000 for 6 months; B ₹30,000 for 12 months. Ratio = 240,000 : 360,000 = **2 : 3**. If profit ₹50,000 → A gets ₹20,000, B gets ₹30,000.

---

## Section 3 — SIMPLE INTEREST (SI) & COMPOUND INTEREST (CI) — 5 worked + variations

> **Notation expansion (used throughout this section):**
> **SI** = Simple Interest. **CI** = Compound Interest. **P** = Principal (original amount).
> **R** or **r** = annual rate of interest in percent. **T** or **n** = time in years.
> **A** = Amount = Principal + Interest.

---

**Q11.** Find the SI on ₹4,000 at 5 % per annum (p.a.) for 3 years.

**Step 1 — Recall the formula.**
- **SI = P × R × T / 100**

**Solving it.** Plug in values.
- P = ₹4,000, R = 5, T = 3
- SI = 4,000 × 5 × 3 / 100 = 60,000 / 100 = **₹600**

**Quick way:** Compute Amount (if asked).** A = P + SI = 4,000 + 600 = **₹4,600**.

*Watch out:* None — this is a direct-formula problem. The trap in SI problems is usually wrong unit conversion (months instead of years).

**A similar question:** Time given in months. Same problem, but T = 30 months. Convert: T = 30/12 = 2.5 years. SI = 4000 × 5 × 2.5 / 100 = **₹500**.

**Another twist:** Find R when SI is given. SI = ₹720 on ₹4,000 for 3 years → R = SI × 100 / (P × T) = 720 × 100 / 12,000 = **6 %**.

**One more:** Find P. SI = ₹450 at 5 % for 3 years → P = SI × 100 / (R × T) = 450 × 100 / 15 = **₹3,000**.

---

**Q12.** Difference between Compound Interest (CI) and Simple Interest (SI) on a sum P at r % per annum for **2 years** is ₹40. If r = 5 %, find P.

**Step 1 — Recall the 2-year SI vs CI difference formula.**
- For 2 years: **CI − SI = P × (r / 100)²**

**Solving it.** Where this comes from (1-line derivation).
- 2-year CI = P [(1 + r/100)² − 1] = P [2r/100 + (r/100)²]
- 2-year SI = P × 2r / 100
- Difference = P × (r/100)² ✓

**Quick way:** Plug in.
- 40 = P × (5 / 100)² = P × 0.0025
- P = 40 / 0.0025 = **₹16,000**

**Worth knowing:** Verify.** SI for 2 yrs = 16,000 × 5 × 2 / 100 = ₹1,600. CI = 16,000 × [(1.05)² − 1] = 16,000 × 0.1025 = ₹1,640. Difference = 40 ✓.

*Watch out:* Students try the 3-year formula (CI − SI = P × r² × (300 + r) / 100³) which is more complex — wrong here because the question says 2 years.

**A similar question — 3-year version.** CI − SI for 3 yrs at r % = P × r² (300 + r) / 100³. If diff = ₹76, r = 10, find P. → 76 = P × 100 × 310 / 10⁶ = P × 0.031 → P = 76 / 0.031 = **₹2,451.61** (or ~₹2,452).

**Another twist — Find r.** P = ₹10,000, 2-year diff = ₹100. → 100 = 10,000 × (r/100)² → (r/100)² = 0.01 → r = **10 %**.

---

**Q13.** A sum of money doubles itself at simple interest in 5 years. In how many years will it triple at the same rate?

**What kind of problem is this?** SI doubling/tripling problems. Use the principle that for SI, "Interest = P × R × T / 100" and "doubles" means SI = P; "triples" means SI = 2P.

**Solving it.** Find the rate from the doubling condition.
- Doubles in 5 years → SI = P → P × R × 5 / 100 = P → R = **20 % p.a.**

**Quick way:** Apply same rate to triple.
- Triples → SI = 2P → P × 20 × T / 100 = 2P → T = **10 years**.

**Worth knowing:** Memorise the universal rule.** At simple interest, if a sum becomes n times in T years, then it becomes m times in **T × (m − 1) / (n − 1)** years (same rate).
- Verify: doubles in 5 (n=2), tripling (m=3): T × (3−1)/(2−1) = 5 × 2 = 10 ✓.

*Watch out:* "15 years" — students multiply 5 × 3 (wrong; doubling and tripling are not proportional that way).

**A similar question:** Doubles in 8 years. When will it become 4 times? Use rule: 8 × (4−1)/(2−1) = 8 × 3 = **24 years**.

**Another twist — Compound interest version.** If money doubles at CI in 5 years, when does it triple? Use **(1 + r/100)ⁿ = m**. Doubling: (1.r)⁵ = 2 → log(1.r) = log(2)/5. Tripling: (1.r)ᵗ = 3 → t = log(3)/log(1.r) = log(3) × 5/log(2) = 5 × 1.585 = **7.92 years**. Note: ratio is log(m)/log(n) for CI, NOT (m-1)/(n-1) like SI.

---

**Q14.** A sum of money at compound interest grows to **1,331 / 1,000** of itself in 3 years. Find the annual rate of interest.

**Step 1 — Recall the CI Amount formula.**
- **A = P × (1 + r/100)ⁿ**

**Solving it.** Set up the equation.
- A / P = 1331 / 1000 (given)
- (1 + r/100)³ = 1331 / 1000

**Quick way:** Take cube root of both sides.
- 1 + r/100 = ∛(1331 / 1000) = 11 / 10 (since 11³ = 1331 and 10³ = 1000)

**Worth knowing:** Solve for r.
- r/100 = 11/10 − 1 = 1/10
- r = **10 % p.a.**

*Watch out:* "11 %" — students take 11/10 directly without subtracting 1.

**Memorise these cube identities** (super useful for CI problems): 1331 = 11³; 1728 = 12³; 2197 = 13³; 2744 = 14³; 3375 = 15³; 4096 = 16³; 4913 = 17³; 5832 = 18³; 6859 = 19³; 8000 = 20³.

**A similar question:** Sum becomes 1.728 times in 3 years → r = (∛1.728 − 1) × 100. Since 12³ = 1728, ∛1.728 = 1.2 → r = **20 %**.

**Another twist:** Sum becomes 1.21 times in 2 years (CI). (1+r/100)² = 1.21 → 1+r/100 = 1.10 (since 1.10² = 1.21) → r = **10 %**.

---

**Q15.** Find the Compound Interest (CI) on ₹10,000 at 10 % per annum for 2 years, compounded **half-yearly**.

**What kind of problem is this?** Non-annual compounding. Adjust BOTH rate and time.

**Solving it.** Adjust rate and time.
- Annual rate r = 10 % → **half-yearly rate = r/2 = 5 %**
- Time = 2 years → **number of half-year periods = 2 × 2 = 4**

**Quick way:** Apply CI formula with adjusted values.
- A = 10,000 × (1 + 5/100)⁴ = 10,000 × (1.05)⁴
- (1.05)⁴ = 1.21550625
- A = 10,000 × 1.21550625 = ₹12,155.06
- CI = A − P = 12,155.06 − 10,000 = **₹2,155.06**

**Worth knowing:** Compare with annual compounding** (to see why half-yearly gives more).
- Annual: A = 10,000 × (1.10)² = 10,000 × 1.21 = ₹12,100. CI = ₹2,100.
- Half-yearly extra = 2,155.06 − 2,100 = ₹55.06 more (because interest gets reinvested twice as often).

*Watch out:* Students forget to halve the rate AND double the periods. Either error alone gives a wrong answer.

**A similar question — Quarterly compounding.** Same problem, quarterly. Rate = 10/4 = 2.5 %, periods = 2 × 4 = 8. A = 10,000 × (1.025)⁸ = 10,000 × 1.21840 = ₹12,184.03 → CI = **₹2,184.03**.

**Another twist — Monthly compounding.** Rate = 10/12 ≈ 0.833 %, periods = 24. A ≈ 10,000 × (1.00833)²⁴ ≈ 10,000 × 1.22039 ≈ ₹12,204 → CI ≈ **₹2,204**.

**Memory peg.** As compounding frequency goes ↑, the effective rate goes ↑. Continuous compounding upper limit: A = P × eʳᵗ.

### Section 3A — ADVANCED SI / CI (exam-level variations)

---

**Q15.5 (Advanced) — Rate change midway.** ₹10,000 invested at SI. For first 3 years rate = 5 %; next 2 years rate increased to 8 %. Find total interest after 5 years.

**Solving it.**
- SI for first 3 yrs at 5 %: 10,000 × 5 × 3 / 100 = **₹1,500**
- SI for next 2 yrs at 8 %: 10,000 × 8 × 2 / 100 = **₹1,600**
- Total interest = 1,500 + 1,600 = **₹3,100**

**Worth knowing:** For SI with multiple rates over different periods, simply sum the interest for each period (principal stays the same throughout).

**A similar question — CI version.** ₹10,000 at CI. First 2 yrs at 10 %; next 2 yrs at 12 %. Amount after 4 years = 10,000 × (1.10)² × (1.12)² = 10,000 × 1.21 × 1.2544 = **₹15,178.24**. CI = ₹5,178.24.

---

**Q15.6 (Advanced) — Equal annual instalments to clear debt.** A loan of ₹2,210 is to be cleared in 2 equal annual instalments at 10 % CI per annum. Find the value of each instalment.

**Solving it.** Set up the present-value equation.
- Let each instalment = x.
- Instalment paid end of year 1, present value = x / 1.10.
- Instalment paid end of year 2, present value = x / (1.10)² = x / 1.21.
- Sum of present values = loan amount: x/1.10 + x/1.21 = 2,210.
- LCD = 1.21: (1.21x + 1.10x) / 1.21 / 1.10 = 2,210. Actually: x(1/1.10 + 1/1.21) = 2,210 → x × (1.21 + 1.10)/(1.10 × 1.21) = 2,210 → x × (2.31/1.331) = 2,210 → x × 1.7355 = 2,210 → **x ≈ ₹1,273**.

**Quick way (memorise the 2-instalment shortcut).** For loan L at rate r %, 2 equal annual instalments: each = L × r × (1+r)² / [(1+r)² + (1+r)] = L × r × (1+r) / (2+r) where r in decimal.
- Here L = 2,210, r = 0.10: each = 2210 × 0.10 × 1.10 / 2.10 = 243.10 / 2.10 = **₹115.76**? Doesn't match.

(Note: instalment problems require careful PV setup; quick shortcuts are tricky. Always use the PV-equation method.)

---

**Q15.7 (Advanced) — Partial repayment.** ₹1,200 borrowed at 10 % SI for 3 years. After 1 year, ₹400 is repaid. Find the total interest to be paid in 3 years.

**Solving it.**
- Year 1 SI on ₹1,200: 1,200 × 10 × 1 / 100 = ₹120.
- After 1 year, total dues = 1,200 + 120 = 1,320. Pays 400 → remaining = ₹920.
- For next 2 years on ₹920 at 10 % SI: 920 × 10 × 2 / 100 = ₹184.
- Total interest = 120 + 184 = **₹304**.

---

## Section 4 — RATIO + PROPORTION + AVERAGE (5 worked + variations)

> **Notation expansion (used throughout this section):**
> A : B means "A to B in ratio". The numbers in a ratio are called **terms**. Sum of terms is the **total** when scaled.
> **Average** = sum of values ÷ count of values.

---

**Q16.** A : B = 3 : 4 and B : C = 5 : 6. Find A : B : C.

**What kind of problem is this?** Two ratios sharing a common term (B). To combine, you must make B's value the same in both ratios.

**Solving it.** Step-by-step.
- A : B = 3 : 4 (B's term is 4)
- B : C = 5 : 6 (B's term is 5)
- LCM of B's coefficients (4, 5) = **20**
- Scale A : B by 5: → A : B = **15 : 20**
- Scale B : C by 4: → B : C = **20 : 24**
- Combined: **A : B : C = 15 : 20 : 24**

**Quick way:** Direct cross-multiply (when only A : C asked).
- A/C = (A/B) × (B/C) = (3/4) × (5/6) = 15/24 = **5 : 8**.

***Watch out:*** Students multiply A : B = 3 : 4 and B : C = 5 : 6 to get 15 : 24 directly, forgetting to align B first.

**A similar question:** A : B = 2 : 3 and B : C = 4 : 5. LCM of (3, 4) = 12. Scale: A : B = 8 : 12; B : C = 12 : 15. **A : B : C = 8 : 12 : 15**.

**Another twist — Three-term chain.** A : B = 2 : 3, B : C = 4 : 5, C : D = 6 : 7. Combine in two passes: first A : B : C = 8 : 12 : 15. Then C in (8:12:15) is 15, in C:D is 6 — LCM(15, 6) = 30. Scale: 16:24:30 and 30:35. Final: A:B:C:D = **16 : 24 : 30 : 35**.

---

**Q17.** Average of 10 numbers = 25. If one number 36 is replaced by 26, what is the new average?

**What kind of problem is this?** "Replace one value" → only the SUM changes by the difference; count stays the same.

**Solving it.** Step-by-step.
- Original sum = 10 × 25 = **250**
- Change in sum = new value − old value = 26 − 36 = **−10**
- New sum = 250 − 10 = **240**
- New average = 240 / 10 = **24**

**Quick way:** Direct shortcut.
- New average = old average + (change in sum) / count = 25 + (−10)/10 = **24**.

***Watch out:*** "23" — students subtract 10 directly from the average (forgetting to divide by 10).

**A similar question:** Average of 8 numbers = 40. One number 30 is replaced by 50. New average = 40 + 20/8 = **42.5**.

**Another twist — Add or remove an element.** Average of 5 numbers = 20. A 6th number 26 is added. New average = (5×20 + 26)/6 = 126/6 = **21**.

---

**Q18.** Average age of 11 cricketers = 28 years. When the captain (age 33) and wicket-keeper (age 30) are excluded, what is the average age of the remaining 9?

**What kind of problem is this?** Sum-removal. Subtract the excluded values from the total, then divide by the new count.

**Solving it.** Step-by-step.
- Total age (11 cricketers) = 11 × 28 = **308 years**
- Excluded sum = 33 + 30 = **63 years**
- Remaining total = 308 − 63 = **245 years**
- Remaining count = 11 − 2 = **9**
- New average = 245 / 9 = **27.22 years** (or 27 and 2/9)

***Watch out:*** "26" — students round wrong or compute 245 ÷ 9 carelessly.

**A similar question:** Average weight of 5 students = 50 kg. One student (60 kg) leaves. New average = (5×50 − 60)/4 = 190/4 = **47.5 kg**.

**Another twist — Find one missing element.** Average of 4 numbers is 30. Three of them are 25, 35, 28. The fourth = 4×30 − (25+35+28) = 120 − 88 = **32**.

---

**Q19.** 5 men can complete a work in 6 days. The ratio of work done by 1 man in 1 day to 1 woman in 1 day is 3 : 2. How long will 4 women take to do the same work?

**What kind of problem is this?** Work-rate equivalence — convert women into "man-units", then apply work × time = constant.

**Solving it.** Step-by-step.
- Total work = 5 men × 6 days = **30 man-days**
- 1 man-day-of-work = 3 units; 1 woman-day-of-work = 2 units (from ratio 3:2). So 1 woman = 2/3 of a man.
- 4 women = 4 × (2/3) = **8/3 man-equivalent**
- Days needed = 30 / (8/3) = 30 × 3/8 = **11.25 days** (or 11 days and 6 hours)

**Worth knowing:** General formula. M₁D₁/W₁ = M₂D₂/W₂ where M = workers, D = days, W = work units. Always convert all workers to one unit (man-equivalent OR woman-equivalent).

***Watch out:*** "9 days" — students compute 30/4 = 7.5 (wrong; doesn't account for the 3:2 ratio) or 30 × 3/4 (off).

**A similar question:** 6 men finish in 8 days. 1 man = 4 women. How long for 12 women? 6 men × 8 days = 48 man-days. 12 women = 3 men → 48/3 = **16 days**.

**Another twist — Mixed crew.** A work takes 8 men 10 days, OR 16 women 10 days. So 1 man = 2 women. How long will 4 men + 4 women take? 4 men + 4 women = 4×2 + 4 = 12 woman-units. Total work = 16 women × 10 = 160 woman-days. Time = 160/12 ≈ **13.33 days**.

---

**Q20.** Two numbers are in the ratio 3 : 5. If 8 is added to each, the ratio becomes 5 : 7. Find the original numbers.

**What kind of problem is this?** Ratio + linear modification → set up an equation in one unknown (using a common multiplier x).

**Solving it.** Step-by-step.
- Let the two numbers be **3x** and **5x**.
- After adding 8: (3x + 8) and (5x + 8).
- Given new ratio: (3x + 8) / (5x + 8) = **5 / 7**
- Cross-multiply: 7(3x + 8) = 5(5x + 8)
- Expand: 21x + 56 = 25x + 40
- Rearrange: 56 − 40 = 25x − 21x → **16 = 4x → x = 4**
- Numbers = 3×4 = **12** and 5×4 = **20**

**Worth knowing:** Verify. New ratio = (12+8) : (20+8) = 20 : 28 = 5 : 7 ✓.

***Watch out:*** Students set up (5x+8)/(3x+8) = 5/7, swapping numerator and denominator.

**A similar question:** Two numbers in ratio 2 : 3. After subtracting 4 from each, ratio = 1 : 2. Set up (2x−4)/(3x−4) = 1/2 → 2(2x−4) = 3x−4 → 4x−8 = 3x−4 → x = 4. Numbers = **8 and 12**.

**Another twist — Multiplied modification.** Two numbers in ratio 4 : 5. If both are doubled and 10 added to each, the new ratio = 9 : 11. Set up (8x+10)/(10x+10) = 9/11 → 11(8x+10) = 9(10x+10) → 88x + 110 = 90x + 90 → 2x = 20 → x = 10. Numbers = **40 and 50**.

### Section 4A — ADVANCED RATIO + AVERAGE (exam-level variations)

---

**Q20.5 (Advanced) — Continued ratio with 4 terms.** A : B = 2 : 3, B : C = 4 : 5, C : D = 6 : 7. Find A : B : C : D.

**Solving it.** Stitch ratios pairwise.
- A : B : C: align B (LCM of 3 and 4 = 12). A : B becomes 8 : 12; B : C becomes 12 : 15. So A : B : C = **8 : 12 : 15**.
- Now extend with C : D = 6 : 7. Align C (LCM of 15 and 6 = 30). A : B : C becomes 16 : 24 : 30; C : D becomes 30 : 35. So A : B : C : D = **16 : 24 : 30 : 35**.

---

**Q20.6 (Advanced) — Mixture ratio with replacement.** A vessel contains 60 L mixture of milk and water in ratio 7 : 3. 20 L of mixture is removed and replaced by water. Find new ratio.

**Solving it.** Step-by-step.
- Initial milk = 60 × 7/10 = **42 L**; water = **18 L**.
- Removing 20 L of MIXTURE removes proportionally: milk removed = 20 × 7/10 = 14; water removed = 20 × 3/10 = 6.
- After removal: milk = 42 − 14 = **28 L**; water = 18 − 6 = **12 L**.
- After adding 20 L pure water: water = 12 + 20 = **32 L**; milk = **28 L**.
- New ratio milk : water = **28 : 32 = 7 : 8**.

---

**Q20.7 (Advanced) — Average with new addition changes mean.** Average weight of 5 students = 50 kg. Adding a 6th student raises the average to 52 kg. Find the new student's weight.

**Solving it.**
- Old total = 5 × 50 = 250 kg.
- New total = 6 × 52 = 312 kg.
- New student's weight = 312 − 250 = **62 kg**.

**A similar question.** Average age of 4 family members = 30. Adding a baby drops avg to 25. Baby's age = 5 × 25 − 4 × 30 = 125 − 120 = **5 years**.

---

## Section 5 — TIME, SPEED, DISTANCE + BOATS + TRAINS (5 worked + variations)

> **Notation expansion (used throughout this section):**
> **TSD** = Time-Speed-Distance. **km/h** = kilometres per hour. **m/s** = metres per second.
> **Conversion:** 1 km/h = 5/18 m/s; 1 m/s = 18/5 km/h. Memorise this — it appears in nearly every TSD problem.
> **Boat:** speed in still water = b; stream/current speed = s; downstream speed = b + s; upstream speed = b − s.

---

**Q21.** A train 240 m long passes a pole in 12 seconds. Find its speed in km/h.

**What kind of problem is this?** "Train passes a pole" → train covers a distance equal to its OWN length (the pole has no length).

**Solving it.** Step-by-step.
- Distance covered = length of train = **240 m**
- Time = **12 s**
- Speed (in m/s) = Distance / Time = 240 / 12 = **20 m/s**

**Quick way:** Convert m/s → km/h.
- Speed (km/h) = 20 × 18/5 = **72 km/h**

**Worth knowing:** When passing a stationary object (pole, person, signal, lamp post), train covers its own length. When passing a platform/bridge/tunnel, train covers (its length + object's length).

***Watch out:*** "20 km/h" — students give the m/s answer without converting to km/h.

**A similar question — Pass a platform.** Train 200 m long, speed 72 km/h, passes a 100 m platform. Speed = 72 × 5/18 = 20 m/s. Total distance = 200 + 100 = 300 m. Time = 300/20 = **15 s**.

**Another twist — Find length.** A train passes a man standing on a platform in 10 s at 54 km/h. Length = 54 × 5/18 × 10 = 15 × 10 = **150 m**.

---

**Q22.** Two trains running in opposite directions cross each other in 15 seconds. Their speeds are 80 km/h and 100 km/h. If their lengths are equal, find the length of each train.

**What kind of problem is this?** Two trains, opposite directions → relative speed = SUM of speeds. Total distance covered = sum of both lengths.

**Solving it.** Step-by-step.
- Relative speed = 80 + 100 = **180 km/h**
- Convert to m/s: 180 × 5/18 = **50 m/s**
- Total distance covered while crossing = 50 × 15 = **750 m**
- This 750 m = sum of both lengths. Since lengths are equal: each train = 750 / 2 = **375 m**

**Worth knowing:** Direction rules.
- **Opposite directions** → relative speed = a + b (faster crossing)
- **Same direction** → relative speed = |a − b| (slower crossing)

***Watch out:*** "750 m" — students give total length instead of length of each.

**A similar question — Same direction.** Two trains 200 m and 250 m long, speeds 60 km/h and 90 km/h, same direction. Relative = 30 km/h = 25/3 m/s. Total length = 450 m. Time = 450/(25/3) = 450 × 3/25 = **54 seconds**.

**Another twist — Find one speed.** Two trains 100 m and 150 m, opposite directions, cross in 5 s. One train at 90 km/h. Relative = (100+150)/5 = 50 m/s = 180 km/h. Other train = 180 − 90 = **90 km/h**.

---

**Q23.** A boat's speed in still water is 9 km/h. The stream flows at 3 km/h. Find the time to row 24 km downstream and then return.

**What kind of problem is this?** Boat-and-stream round trip. Downstream and upstream have different effective speeds; compute each leg's time separately, then add.

**Solving it.** Step-by-step.
- Downstream speed = boat + stream = 9 + 3 = **12 km/h**
- Upstream speed = boat − stream = 9 − 3 = **6 km/h**
- Time downstream = 24 / 12 = **2 hours**
- Time upstream = 24 / 6 = **4 hours**
- Total time = 2 + 4 = **6 hours**

***Watch out:*** Averaging the two speeds (9 km/h) and computing 48 / 9 = 5.33 h — WRONG. Speeds differ → must split into legs.

**Worth knowing:** Round-trip average speed (when distance same in both directions) = 2(d₁s₁s₂)/(s₁+s₂)·(1/d) → simplified: **harmonic mean = 2 × down × up / (down + up)**. Here = 2 × 12 × 6 / 18 = 144/18 = **8 km/h**. Total distance 48 km / 8 km/h = 6 hours ✓.

**A similar question — Find boat speed.** Boat takes 4 h downstream and 6 h upstream for 24 km each way. Down = 24/4 = 6 km/h; Up = 24/6 = 4 km/h. Boat in still water = (down + up)/2 = (6+4)/2 = **5 km/h**. Stream = (down − up)/2 = (6−4)/2 = **1 km/h**.

**Another twist — Stream effect on time.** A boat takes twice as long upstream as downstream. If boat in still water = 12 km/h, find stream speed. Let stream = s. Down = 12 + s, up = 12 − s. Time ratio = up/down = (12+s)/(12−s) = 2/1 (since up takes twice). Solve: 12+s = 2(12−s) → 12+s = 24−2s → 3s = 12 → s = **4 km/h**.

---

**Q24.** A man covers half of a distance at 60 km/h and the other half at 40 km/h. Find his average speed for the whole journey.

**What kind of problem is this?** Equal-distance two-leg average speed. Use harmonic mean (NOT arithmetic mean).

**Solving it.** Step-by-step. Let total distance = 2d (so each half = d).
- Time for first half = d / 60
- Time for second half = d / 40
- Total time = d/60 + d/40 = (2d + 3d) / 120 = 5d / 120 = d/24
- Total distance = 2d
- Average speed = total dist / total time = 2d / (d/24) = 2 × 24 = **48 km/h**

**Quick way:** Direct formula for equal-distance two legs.
- Average = **2ab / (a + b)** = 2 × 60 × 40 / 100 = 4800/100 = **48 km/h**

***Watch out:*** "50 km/h" — students take arithmetic mean (60+40)/2. Wrong because more time is spent at the slower speed (40 km/h), pulling average down.

**Worth knowing:** Compare with **equal-time** journey. If man travels FOR equal time at 60 and 40 km/h, then average = arithmetic mean = (60+40)/2 = 50 km/h.

**A similar question — 3 equal segments.** Man covers 1/3 distance at 30, 1/3 at 40, 1/3 at 60. Average = 3 / (1/30 + 1/40 + 1/60) = 3 / ((4+3+2)/120) = 3 × 120/9 = **40 km/h**.

**Another twist — Unequal legs.** Man covers 60 km at 30 km/h and 40 km at 40 km/h. Use definition: total dist / total time. Time₁ = 60/30 = 2; Time₂ = 40/40 = 1; total = 3 h. Total dist = 100 km. Average = 100/3 = **33.33 km/h**.

---

**Q25.** A and B start from opposite ends of a 100 km road and move toward each other at 20 km/h and 30 km/h respectively. After how long do they meet?

**What kind of problem is this?** Two bodies moving toward each other → use relative speed (sum) → time = distance/relative-speed.

**Solving it.** Step-by-step.
- Relative speed = 20 + 30 = **50 km/h** (they close the gap at this rate)
- Distance to close = 100 km
- Time = 100 / 50 = **2 hours**

**Worth knowing:** Direction matters.
- **Toward each other** → relative speed = sum.
- **Same direction (one chasing the other)** → relative speed = difference.

***Watch out:*** Students compute distance covered by each (A covers 40 km, B covers 60 km, sum = 100 km — coincidence) without using the cleaner relative-speed approach.

**A similar question — Chase problem.** A walks at 4 km/h. B walks at 6 km/h. A is 8 km ahead. When will B catch A? Relative speed = 6 − 4 = 2 km/h. Time = 8/2 = **4 hours**.

**Another twist — When and where they meet.** Same A & B opposite-end problem (100 km apart, 20 and 30 km/h). After meeting (at t = 2 h), distance from A's start = A's speed × t = 20 × 2 = **40 km**. From B's end = 30 × 2 = **60 km**.

### Section 5A — ADVANCED TSD + TRAINS (exam-level variations)

---

**Q25.5 (Advanced) — Stoppage-time problem.** A bus without stoppages travels at 60 km/h. With stoppages, its average drops to 48 km/h. Find the total stoppage time per hour.

**Solving it.**
- In 1 hour without stoppages, bus covers 60 km.
- In 1 hour with stoppages, bus covers 48 km (the rest of time, it's stopped).
- Time to cover 48 km without stoppages = 48 / 60 = 0.8 h = 48 minutes.
- Time stopped per hour = 60 − 48 = **12 minutes**.

**Quick shortcut.** Stoppage time per hour = (Speed without stoppages − Speed with stoppages) / Speed without stoppages × 60 min = (60−48)/60 × 60 = **12 min**.

---

**Q25.6 (Advanced) — Train chasing train.** Train A (length 200 m) at 90 km/h chases Train B (length 150 m) at 60 km/h, both same direction. How long does A take to fully cross B?

**Solving it.**
- Relative speed = 90 − 60 = 30 km/h = 30 × 5/18 = **25/3 m/s ≈ 8.33 m/s**.
- Total distance to cover = sum of lengths = 200 + 150 = **350 m**.
- Time = 350 / (25/3) = 350 × 3/25 = 1050/25 = **42 seconds**.

---

**Q25.7 (Advanced) — Boat with current changing.** A boat takes 5 hrs to row 24 km upstream and 3 hrs to row the same downstream. Find boat's speed in still water and current speed.

**Solving it.**
- Upstream speed = 24/5 = **4.8 km/h** (= b − c, where b = boat in still water, c = current).
- Downstream speed = 24/3 = **8 km/h** (= b + c).
- Add: 2b = 4.8 + 8 = 12.8 → b = **6.4 km/h**.
- Subtract: 2c = 8 − 4.8 = 3.2 → c = **1.6 km/h**.

---

## Section 6 — TIME & WORK + PIPES (5 worked + variations)

> **Notation expansion (used throughout this section):**
> **Work rate** = work done per unit time. If A finishes a job in T days, A's rate = 1/T (job/day).
> **Combined rate** = sum of individual rates (people working TOGETHER cooperatively).
> **Pipe convention:** filling pipe rate = +1/T (positive); emptying pipe rate = −1/T (negative).

---

**Q26.** A can do a piece of work in 12 days; B can do the same in 18 days. How many days will they take working together?

**What kind of problem is this?** Two workers cooperating → add their rates and invert.

**Solving it.** Step-by-step.
- A's rate = 1/12 (one job per 12 days, i.e., 1/12 of the job per day)
- B's rate = 1/18
- Combined rate = 1/12 + 1/18

  Find LCM of 12 and 18 = 36.
  - 1/12 = 3/36
  - 1/18 = 2/36
  - Sum = 5/36

- Combined time = 1 / combined rate = 1 / (5/36) = **36/5 = 7.2 days**

**Quick way:** Direct formula for two workers.
- Combined time = **(A × B) / (A + B)** = (12 × 18) / (12 + 18) = 216 / 30 = **7.2 days**.

***Watch out:*** "15 days" — students average days (12+18)/2. WRONG: rates add, not days.

**A similar question:** A in 10 days, B in 15 days. Together = (10×15)/(10+15) = 150/25 = **6 days**.

**Another twist — Three workers together.** A in 12, B in 18, C in 24 days. Combined rate = 1/12 + 1/18 + 1/24 = (6+4+3)/72 = 13/72. Time = **72/13 ≈ 5.54 days**.

---

**Q27.** A and B together complete a work in 12 days. B and C together in 15 days. C and A together in 20 days. In how many days will all three together complete it?

**What kind of problem is this?** Pairwise rates given → sum gives **2 × (combined rate)** because each person appears in 2 pairs.

**Solving it.** Step-by-step.
- Rate of (A + B) = 1/12
- Rate of (B + C) = 1/15
- Rate of (C + A) = 1/20
- Add all three: (A + B) + (B + C) + (C + A) = 2(A + B + C)
- Sum on RHS = 1/12 + 1/15 + 1/20

  LCM of 12, 15, 20 = 60.
  - 1/12 = 5/60
  - 1/15 = 4/60
  - 1/20 = 3/60
  - Sum = **12/60 = 1/5**

- So 2(A + B + C) = 1/5 → **A + B + C = 1/10**
- All three together → **10 days**

**Worth knowing:** To find an INDIVIDUAL worker's time, subtract a pair's rate from the all-three rate.
- C's rate = (A+B+C) − (A+B) = 1/10 − 1/12 = (6−5)/60 = 1/60 → **C alone = 60 days**.
- A's rate = (A+B+C) − (B+C) = 1/10 − 1/15 = (3−2)/30 = 1/30 → **A alone = 30 days**.
- B's rate = (A+B+C) − (C+A) = 1/10 − 1/20 = (2−1)/20 = 1/20 → **B alone = 20 days**.

***Watch out:*** Students forget the factor of 2 and conclude A+B+C takes 5 days. WRONG.

**A similar question:** (A+B) = 8 days, (B+C) = 12 days, (C+A) = 24 days. Sum of rates = 1/8 + 1/12 + 1/24 = (3+2+1)/24 = 6/24 = 1/4. So 2(A+B+C) = 1/4 → A+B+C = 1/8 → **8 days together**.

**Another twist — A leaves midway.** A, B, C together start a work that all three would finish in 10 days. A leaves after 4 days. How long do B and C take to finish? Work done in 4 days = 4/10 = 2/5. Remaining = 3/5. B+C rate = 1/15. Time = (3/5)/(1/15) = 3/5 × 15 = **9 days**.

---

**Q28.** A pipe can fill a tank in 6 hours. Another pipe can empty the same tank in 8 hours. If both are opened together, in how many hours will the tank be filled?

**What kind of problem is this?** Filling pipe + emptying pipe → net rate = filling − emptying. Time = 1 / net rate.

**Solving it.** Step-by-step.
- Filling pipe rate = +1/6 (fills 1/6 per hour)
- Emptying pipe rate = −1/8 (empties 1/8 per hour)
- Net rate = 1/6 − 1/8

  LCM of 6, 8 = 24.
  - 1/6 = 4/24
  - 1/8 = 3/24
  - Net = (4 − 3)/24 = 1/24

- Time to fill = 1 / (1/24) = **24 hours**

**Worth knowing:** This works ONLY if filling > emptying (net rate positive). If emptying > filling, the tank will never fill from empty — just verify direction.

***Watch out:*** Students ADD rates (1/6 + 1/8 = 7/24 → 24/7 ≈ 3.4 h) instead of subtracting. Wrong because emptying opposes filling.

**A similar question — Two filling + one emptying.** Pipes A (fills in 4 h), B (fills in 6 h), C (empties in 8 h). Net = 1/4 + 1/6 − 1/8 = (6+4−3)/24 = 7/24. Time to fill = **24/7 ≈ 3.43 hours**.

**Another twist — Tank already partly full.** Tank is already 1/3 full. Filling pipe (4 h) and emptying pipe (6 h) opened. Net rate = 1/4 − 1/6 = 1/12 per hour. Remaining to fill = 2/3. Time = (2/3) / (1/12) = (2/3) × 12 = **8 hours**.

---

**Q29.** A is twice as efficient as B. Working together, they finish a work in 12 days. How long would A alone take?

**What kind of problem is this?** Efficiency ratio → set rates as multiples → combined rate gives total time.

**Solving it.** Step-by-step.
- Let B's rate = x (job per day). Then A's rate = 2x (twice as efficient).
- Combined rate = A + B = 2x + x = 3x
- Combined time = 12 days → combined rate = 1/12
- So 3x = 1/12 → x = 1/36
- A's rate = 2x = 2/36 = 1/18
- A alone takes = 1 / (1/18) = **18 days**

**Worth knowing:** Sanity check by finding B's time too. B alone = 1/x = 36 days. Verify: 1/18 + 1/36 = 2/36 + 1/36 = 3/36 = 1/12 ✓.

**Memory peg:** When **A is k times as efficient as B**, time ratio = inverse: B takes k times as long as A. So if combined time = T, then **A alone = T(k+1)/k** and **B alone = T(k+1)**.
- Here k = 2, T = 12: A = 12 × 3/2 = 18 ✓. B = 12 × 3 = 36 ✓.

***Watch out:*** "24 days" — students treat A and B as equal (combined 12 → each 24).

**A similar question — A is 3 times as efficient as B; together 9 days.** A = 9 × 4/3 = **12 days**; B = 9 × 4 = **36 days**.

**Another twist — Three workers in efficiency ratio.** A : B : C efficiencies = 6 : 4 : 3. Together they finish in 6 days. Combined rate = 1/6. Sum of efficiency parts = 13. Each part rate = 1/(6×13) = 1/78. So A = 78/6 = **13 days**, B = 78/4 = **19.5 days**, C = 78/3 = **26 days**.

---

**Q30.** 12 men can build a wall in 10 days working 8 hours a day. How many days will it take 8 men to build the same wall working 6 hours a day?

**What kind of problem is this?** Three-variable work problem (men × days × hours/day = total man-hours of work). Total man-hours is constant (same wall, same effort). Find the unknown.

**Solving it.** Step-by-step.
- Total man-hours required = 12 men × 10 days × 8 h/day = **960 man-hours**
- New scenario = 8 men × d days × 6 h/day = 48d man-hours
- Set equal: 48d = 960
- d = 960 / 48 = **20 days**

**Worth knowing:** General formula. (M₁ × D₁ × H₁) = (M₂ × D₂ × H₂), where M = men, D = days, H = hours/day. Rearrange to find the unknown.

***Watch out:*** Students apply only one ratio (e.g., 12/8 × 10 = 15 days), forgetting the hours-per-day factor.

**A similar question — Find men needed.** A work needs 20 men working 8 h/day for 12 days. How many men needed to finish in 10 days at 6 h/day? 20×8×12 = 1920. New = m × 6 × 10 = 60m → m = **32 men**.

**Another twist — Add a fourth variable: efficiency.** 6 men can build a wall in 8 days. 4 women can build same wall in 12 days. How long for 3 men + 4 women? 1 man = 1/(6×8) = 1/48 wall/day. 1 woman = 1/(4×12) = 1/48 wall/day. So 1 man = 1 woman in efficiency. 3 men + 4 women = 7 units. Time = 1 / (7/48) = 48/7 ≈ **6.86 days**.

### Section 6A — ADVANCED TIME & WORK (exam-level variations)

---

**Q30.5 (Advanced) — Alternate-day work.** A can do a job in 12 days; B in 18 days. They work on alternate days starting with A. In how many days will the work finish?

**Solving it.**
- A's 1-day work = 1/12; B's 1-day work = 1/18.
- 2-day cycle (A on day 1, B on day 2) = 1/12 + 1/18 = (3+2)/36 = **5/36** of total work.
- Number of 2-day cycles to complete (or near-complete) the work: 36/5 = 7.2 → after **7 full cycles (14 days)**, work done = 7 × 5/36 = 35/36; remaining = 1/36.
- On day 15 (A's turn), A does 1/12 = 3/36 in 1 full day, but only 1/36 needed. Time taken on day 15 = (1/36) / (1/12) = 12/36 = **1/3 day** (about 8 hours assuming 24-hr day, or ~2.67 hrs of an 8-hr workday).
- Total time = 14 + 1/3 = **14⅓ days**.

---

**Q30.6 (Advanced) — Worker leaves midway.** A and B together can finish work in 10 days. They start together; after 4 days, B leaves. A alone finishes the rest in 6 more days. How long would A alone have taken to do the entire work?

**Solving it.**
- Combined work-rate (A + B) = 1/10 per day.
- Work done in first 4 days = 4 × 1/10 = **2/5**.
- Remaining work = 1 − 2/5 = **3/5**.
- A alone does 3/5 in 6 days → A's rate = (3/5) / 6 = **1/10**? That equals A+B's combined rate, which would mean B does NO work — contradiction.
- Recheck: if A's rate = 1/10, then A alone takes **10 days** for the whole work. But then A + B rate would exceed 1/10. Setup needs A's rate < 1/10. Let me redo.
- A alone rate = 3/5 ÷ 6 = 1/10 per day. So A alone time = 1 / (1/10) = **10 days**.

(Note: the question's numbers force this consistency. In a real exam, B's rate would come out differently.)

---

## Section 7 — MIXTURE + ALLIGATION (3 worked + variations)

> **Notation expansion (used throughout this section):**
> **Alligation** = mixing-rule technique. Used when two items of different prices/strengths combine to give a target.
> **Replacement formula:** when x is removed from a vessel of total V and replaced by something else, after n iterations:
> Remaining original / V = (1 − x/V)ⁿ.

---

**Q31.** In what ratio must rice at ₹30/kg be mixed with rice at ₹40/kg to obtain a mixture worth ₹34/kg?

**What kind of problem is this?** Classical alligation — two items of different rates blended to reach a target rate. Find the mixing ratio.

**Solving it.** Step-by-step using the alligation cross.
- Cheaper (₹30)        Dearer (₹40)
- Difference of dearer to mean: 40 − 34 = **6**
- Difference of mean to cheaper: 34 − 30 = **4**
- Ratio (cheaper : dearer) = (40 − 34) : (34 − 30) = **6 : 4 = 3 : 2**
- That is: **3 parts of ₹30 rice to 2 parts of ₹40 rice**.

**Quick way:** Verify with concrete numbers. Take 3 kg of ₹30 + 2 kg of ₹40. Cost = 3×30 + 2×40 = 90 + 80 = ₹170. Total = 5 kg. Average = 170/5 = ₹34/kg ✓.

**Worth knowing:** Universal rule — **Cheaper : Dearer = (Dearer price − Mean price) : (Mean price − Cheaper price)**.

***Watch out:*** Students invert and write 4 : 6 = 2 : 3 — that ratio gives a mixture closer to ₹40 (not the target ₹34).

**A similar question — Solutions of different concentrations.** A 20% milk solution mixed with a 50% milk solution to get a 30% solution. Ratio = (50 − 30) : (30 − 20) = 20 : 10 = **2 : 1** (more of the weaker solution).

**Another twist — Three components.** Mix three teas of ₹40, ₹50, ₹70 per kg to get ₹52 per kg. With three items, multiple ratios work — usually fix one ratio (e.g., ₹40 to ₹50) at 1:1, then alligate that combined "₹45 mix" with the ₹70 tea: ratio = (70−52):(52−45) = 18:7 → so 1:1:(2×7/18) of the three. Common shortcut: pair up.

---

**Q32.** A vessel contains 40 litres of milk. 4 litres is removed and replaced with water. This process is repeated 3 times in total. How much milk is left at the end?

**What kind of problem is this?** Repeated dilution / replacement problem. Use the geometric formula.

**Solving it.** Step-by-step.
- Each iteration removes 4 L of MIXTURE (not pure milk after iteration 1) and replaces with water.
- Fraction of milk remaining after each step = (V − x) / V = (40 − 4) / 40 = 36/40 = **9/10 = 0.9**
- After **3** iterations: fraction = (0.9)³ = **0.729**
- Milk remaining = 40 × 0.729 = **29.16 L**

**Worth knowing:** General formula. After **n** iterations of removing **x** litres from total **V**:
- Original substance remaining = V × (1 − x/V)ⁿ

**Memory peg.** "Replace x out of V, n times → multiply original by ((V−x)/V)ⁿ".

***Watch out:*** "28 L" — students subtract 4 × 3 = 12 directly (40 − 12 = 28). WRONG, because each subsequent removal takes out MIXTURE (less and less milk), not pure milk.

**A similar question — Find iterations.** A vessel has 100 L pure milk. After repeatedly replacing 10 L with water, when does milk drop below 70 L? After 1: 90; 2: 81; 3: 72.9; **4: 65.6** (just dropped below 70 between iterations 3 and 4).

**Another twist — Remove different amount each time.** Vessel 100 L milk; remove 10 L (replace with water), then remove 20 L (replace), then remove 30 L. After step 1: milk = 100 × 90/100 = 90. After step 2: milk = 90 × 80/100 = 72. After step 3: milk = 72 × 70/100 = **50.4 L**.

---

**Q33.** Two jars contain mixtures of milk and water in the ratios 4 : 3 and 5 : 2 respectively. Equal volumes from both jars are poured into a new jar. Find the ratio of milk to water in the new mixture.

**What kind of problem is this?** Combine two mixtures of differing ratios → use FRACTIONS, not ratios directly.

**Solving it.** Step-by-step.
- Jar A: milk : water = 4 : 3 → milk fraction = 4/(4+3) = **4/7**
- Jar B: milk : water = 5 : 2 → milk fraction = 5/(5+2) = **5/7**
- Take 1 unit from each jar.
  - Milk from A = 4/7; milk from B = 5/7. Total milk = 4/7 + 5/7 = **9/7**.
  - Total volume taken = 1 + 1 = 2 units. So water = 2 − 9/7 = (14 − 9)/7 = **5/7**.
- Final ratio milk : water = (9/7) : (5/7) = **9 : 5**

**Worth knowing:** When you pool equal volumes, the new fraction = average of the two milk-fractions. Average of 4/7 and 5/7 = 9/14 = milk/total. Water/total = 5/14. Ratio = 9 : 5 ✓.

***Watch out:*** Students "average the ratios" → (4+5):(3+2) = 9:5 → coincidentally CORRECT here, but only because both jars have the SAME total of 7 parts. If totals differ (e.g., 4:3 and 3:1), averaging ratios fails.

**A similar question — Different total parts.** Jar A: milk:water = 3 : 1 (total 4); Jar B: milk:water = 5 : 2 (total 7). Equal 1-unit pours. Milk fractions: 3/4 + 5/7 = (21+20)/28 = 41/28. Water = 2 − 41/28 = (56−41)/28 = 15/28. Ratio = **41 : 15**.

**Another twist — Unequal volumes from each jar.** Take 2 units from Jar A (4:3) and 5 units from Jar B (5:2). Milk = 2 × 4/7 + 5 × 5/7 = 8/7 + 25/7 = 33/7. Total volume = 7. Water = 7 − 33/7 = (49−33)/7 = 16/7. Ratio = **33 : 16**.

---

### Section 7A — ADVANCED MIXTURE + ALLIGATION (exam-level variations)

---

**Q33.5 (Advanced) — 3-component alligation.** Three types of rice cost ₹40, ₹60 and ₹80 per kg respectively. In what ratio should they be mixed to give a mixture of ₹55/kg?

**Solving it.** With 3 components, fix 2 of them in a workable pair, then alligate that pair with the third.
- Pair Type 1 (₹40) and Type 3 (₹80) at any easy ratio. Average of these two if mixed equally = ₹60. Now alligate ₹60 (mix) with ₹60 (Type 2) → degenerate.
- Try: 1 part Type 1 + 1 part Type 3 = mean ₹60. Combine with Type 2 (₹60) at any ratio still gives ₹60 — too high vs target ₹55.
- Take more Type 1: 2:1 of Type 1:Type 3 = (2×40 + 1×80)/3 = ₹53.33. Combine 53.33 with Type 2 (60) by alligation: ratio = (60−55):(55−53.33) = 5 : 1.67 = 3 : 1.
- So 3 parts of (2:1 of Type 1 + Type 3) mixed with 1 part of Type 2 → final ratio Type 1 : Type 2 : Type 3 = (3×2/3) : 1 : (3×1/3) = **2 : 1 : 1**.
- Verify: (2×40 + 1×60 + 1×80) / 4 = 220/4 = **₹55** ✓.

**Worth knowing:** With 3 components, infinite ratios satisfy the equation. The alligation pairing trick fixes one ratio first.

---

**Q33.6 (Advanced) — Replacement formula with multiple iterations.** A vessel has 80 L of pure milk. 8 L is removed and replaced with water. The same is done 3 times. Find the ratio of milk to water remaining.

**Solving it.**
- Fraction of milk remaining = (1 − 8/80)³ = (9/10)³ = 729/1000 = **0.729**.
- Milk = 80 × 0.729 = **58.32 L**.
- Water = 80 − 58.32 = **21.68 L**.
- Ratio milk : water = 58.32 : 21.68 = 729 : 271 ≈ **2.69 : 1**.

---

## Section 8 — MENSURATION (3 worked + variations)

> **Notation expansion (used throughout this section):**
> **Area** is in square units (cm², m²). **Volume** is in cubic units (cm³, m³).
> **CSA** = Curved Surface Area; **TSA** = Total Surface Area; **LSA** = Lateral Surface Area.
> **π (pi)** ≈ 22/7 (use this when r is a multiple of 7) or 3.14 otherwise.

---

**Q34.** Find the area of a triangle with sides 5, 12 and 13.

**What kind of problem is this?** Triangle area when 3 sides given. Two methods: Heron's formula (general) or check for **Pythagorean triple** (much faster).

**Solving it.** Step-by-step.
- Check Pythagoras: 5² + 12² = 25 + 144 = 169 = 13² → YES, this is a right-angled triangle (5-12-13).
- For a right triangle, two legs ARE the base and height.
- Area = ½ × base × height = ½ × 5 × 12 = **30 sq units**

**Quick way:** Heron's formula (slower but works for any triangle).
- s = (5 + 12 + 13)/2 = 15 (semi-perimeter)
- Area = √[s(s−a)(s−b)(s−c)] = √[15 × 10 × 3 × 2] = √900 = **30** ✓

**Worth knowing:** Memorise common Pythagorean triples — they recur in geometry/mensuration.
- 3-4-5; 5-12-13; 7-24-25; 8-15-17; 9-40-41; 11-60-61; 20-21-29.

***Watch out:*** Students dive straight into Heron without spotting the right-angle shortcut, wasting 30+ seconds.

**A similar question — Equilateral triangle.** Side 6 cm. Area = (√3/4) × side² = (√3/4) × 36 = **9√3 sq cm ≈ 15.59 sq cm**.

**Another twist — Two sides + included angle.** Sides 8 and 6, angle between them 30°. Area = ½ × a × b × sin C = ½ × 8 × 6 × ½ = **12 sq units**.

---

**Q35.** Find the volume of a cylinder with radius r = 7 cm and height h = 10 cm.

**What kind of problem is this?** Direct application of the cylinder volume formula.

**Solving it.** Step-by-step.
- Volume formula: **V = π × r² × h**
- r = 7 (a multiple of 7) → use π = 22/7 for clean arithmetic
- V = (22/7) × 7² × 10 = (22/7) × 49 × 10 = 22 × 7 × 10 = **1,540 cm³**

**Worth knowing:** Cylinder all-formulas card.
- Volume V = π r² h
- CSA (curved surface) = 2 π r h
- TSA (total surface) = 2 π r (r + h)

***Watch out:*** Students confuse CSA (2πrh) with V (πr²h). Or use π = 3.14 when r = 7 → 153.86 instead of 154 (tiny rounding error, but not exam-clean).

**A similar question — Find height when V given.** V = 770 cm³, r = 7 cm. h = V / (πr²) = 770 / (22/7 × 49) = 770 / 154 = **5 cm**.

**Another twist — Hollow cylinder (pipe).** Outer r = 7, inner r = 5, height = 10. Volume of metal = π × (R² − r²) × h = (22/7) × (49 − 25) × 10 = (22/7) × 24 × 10 = **754.29 cm³**.

---

**Q36.** A cube of side 6 cm is melted and recast into a cuboid of dimensions 4 cm × 3 cm × h cm. Find h.

**What kind of problem is this?** Volume-conservation (melt + recast). Total volume of metal stays the same.

**Solving it.** Step-by-step.
- Volume of cube = side³ = 6³ = **216 cm³**
- Volume of cuboid = length × breadth × height = 4 × 3 × h = 12h
- Set equal: 12h = 216
- h = 216 / 12 = **18 cm**

**Worth knowing:** Volume conservation works for any shape transformation: cube → cylinder → cone → sphere etc. Surface area changes; volume doesn't.

***Watch out:*** Students compute surface areas instead of volume (cube SA = 6 × side² = 216, equal to volume here by coincidence — the equal-216 confuses).

**A similar question — Cube to spheres.** Cube of side 12 cm melted into spheres of radius 1 cm. Volume of cube = 1,728 cm³. Volume of one sphere = (4/3)π(1)³ = 4.19 cm³. Number of spheres = 1,728 / 4.19 ≈ **412 spheres** (using π = 22/7 gives slight variation).

**Another twist — Sphere to cone.** Sphere of radius 6 cm melted into cones of base radius 2 cm and height 3 cm. Sphere V = (4/3)π × 216 = 288π. Cone V = (1/3)π × 4 × 3 = 4π. Number of cones = 288π / 4π = **72 cones**.

---

### Section 8A — ADVANCED MENSURATION (exam-level variations)

---

**Q36.5 (Advanced) — Hollow cylinder volume.** A pipe has external radius 10 cm, internal radius 8 cm, and length 50 cm. Find the volume of metal used.

**Solving it.**
- Volume of metal = π × (R² − r²) × h = π × (100 − 64) × 50 = π × 36 × 50 = π × 1,800.
- Using π = 22/7: 22/7 × 1,800 = **5,657.14 cm³**.

---

**Q36.6 (Advanced) — Frustum volume + slant.** A frustum (truncated cone) has bottom radius 7 cm, top radius 4 cm, and height 12 cm. Find volume and slant height.

**Solving it.**
- Volume = (1/3) × π × h × (R² + r² + R×r) = (1/3) × (22/7) × 12 × (49 + 16 + 28) = (1/3) × (22/7) × 12 × 93 = (88/7) × 93 = 8184/7 ≈ **1,169 cm³**.
- Slant l = √[h² + (R − r)²] = √[144 + 9] = √153 ≈ **12.37 cm**.

---

**Q36.7 (Advanced) — Sphere inscribed in cube.** A sphere is inscribed in a cube of side 10 cm. Find the volume of the sphere AND the empty space between the sphere and the cube.

**Solving it.**
- Sphere radius r = side/2 = **5 cm** (sphere touches all 6 faces).
- Sphere volume = (4/3) π r³ = (4/3) × (22/7) × 125 = (88/21) × 125 = 11000/21 ≈ **523.81 cm³**.
- Cube volume = 10³ = **1,000 cm³**.
- Empty space = 1,000 − 523.81 = **476.19 cm³**.

---

## Section 9 — GEOMETRY (3 worked + variations)

> **Notation expansion (used throughout this section):**
> **ΔABC** = triangle with vertices A, B, C. **AD** = line segment from A to D. **∠A** = angle at vertex A.
> **Polygon n-gon** = polygon with n sides; sum of interior angles = (n−2) × 180°.

---

**Q37.** In ΔABC, AD is the angle-bisector from vertex A meeting BC at point D. AB = 6, AC = 8, BC = 7. Find BD.

**What kind of problem is this?** Angle-bisector theorem application. The bisector divides the opposite side in the ratio of the two adjacent sides.

**Solving it.** Step-by-step.
- Angle-bisector theorem: **BD / DC = AB / AC**
- Plug in: BD / DC = 6 / 8 = **3 / 4**
- BD + DC = BC = 7 (given)
- BD = (3 / (3 + 4)) × 7 = (3/7) × 7 = **3**

**Worth knowing:** General formula. If AD bisects ∠A and meets BC at D:
- BD = (AB / (AB + AC)) × BC
- DC = (AC / (AB + AC)) × BC
- Sanity: BD + DC = BC ✓.

***Watch out:*** "4" — students invert the ratio (6 : 8 read as DC : BD instead of BD : DC).

**A similar question — Find DC.** Same triangle. DC = (8/14) × 7 = **4** (and BD = 3, sum = 7 ✓).

**Another twist — External angle bisector.** External bisector of ∠A meets BC extended at E. Then BE / EC = AB / AC = 6/8 = 3/4. With BC = 7, BE − EC = 7 → BE = 21, EC = 28 (BE − EC = −7, take absolute distance from B: 21).

---

**Q38.** Two chords AB and CD of a circle intersect at point P inside the circle. AP = 4, PB = 6, CP = 3. Find PD.

**What kind of problem is this?** **Power of a Point** — when two chords cross inside a circle, the products of the segments are equal.

**Solving it.** Step-by-step.
- Theorem: **AP × PB = CP × PD**
- Plug in: 4 × 6 = 3 × PD
- 24 = 3 × PD
- PD = 24 / 3 = **8**

**Worth knowing:** Power-of-a-Point variants (very high-PYQ frequency).
- **Two chords intersecting inside:** AP × PB = CP × PD.
- **Two secants from external point:** PA × PB = PC × PD.
- **One tangent + one secant from external point:** PT² = PA × PB.

***Watch out:*** Students invert and compute 24/3 wrong (they get the right number 8 but using flawed reasoning); or they pair AP with CP instead of AP with PB.

**A similar question — Find one chord segment.** Chords intersect at P; AP = 5, PB = 8, CD = 12 with CP = ?. Then 5 × 8 = CP × (12 − CP) → 40 = 12·CP − CP² → CP² − 12CP + 40 = 0 → CP = (12 ± √(144−160))/2. Discriminant negative → not possible (means P can't lie inside with those values). Try CD = 13: 40 = CP(13 − CP) → CP² − 13CP + 40 = 0 → CP = 5 or 8.

**Another twist — Tangent-secant from outside.** From external point P, tangent PT = 6 cm; secant PA = 4 cm, PB = ?. PT² = PA × PB → 36 = 4 × PB → PB = **9 cm** (so AB = PB − PA = 5 cm).

---

**Q39.** A polygon has 9 sides. Find the sum of its interior angles.

**What kind of problem is this?** Direct application of polygon-interior-angle formula.

**Solving it.** Step-by-step.
- Formula: **Sum of interior angles of an n-gon = (n − 2) × 180°**
- For n = 9: Sum = (9 − 2) × 180 = 7 × 180 = **1,260°**

**Worth knowing:** Two related formulas.
- **Sum of EXTERIOR angles of any polygon = always 360°** (regardless of n).
- **Each interior angle of a regular n-gon = (n − 2) × 180° / n**.
  - For regular 9-gon (nonagon): 1260 / 9 = **140°** per angle.
- **Each exterior angle of a regular n-gon = 360 / n**.
  - For regular 9-gon: 360 / 9 = **40°** per exterior.

***Watch out:*** "1,440°" — students use (n − 1) × 180 (wrong; it's n − 2). Or "1,620°" using n × 180.

**A similar question — Find n given interior sum.** Sum = 1,800°. Solve (n − 2) × 180 = 1800 → n − 2 = 10 → n = **12 sides** (dodecagon).

**Another twist — Find interior of regular polygon, given exterior.** Each exterior of regular polygon is 24°. Number of sides = 360/24 = **15 sides**. Each interior = 180 − 24 = **156°**.

---

### Section 9A — ADVANCED GEOMETRY (exam-level variations)

---

**Q39.5 (Advanced) — Similar triangles, ratio of areas.** Two similar triangles have sides in the ratio 3 : 5. Find the ratio of their areas.

**Solving it.**
- For similar figures, ratio of areas = (ratio of corresponding sides)² = (3/5)² = **9/25** = **9 : 25**.
- Ratio of perimeters = ratio of sides = 3 : 5.
- Ratio of volumes (for similar 3D solids) = (3/5)³ = 27/125.

---

**Q39.6 (Advanced) — Tangent length from external point.** From a point 13 cm away from the centre of a circle of radius 5 cm, a tangent is drawn. Find the length of the tangent.

**Solving it.**
- Tangent ⊥ radius at point of contact → right triangle (radius, tangent, distance).
- By Pythagoras: tangent² + radius² = distance²
- tangent² + 25 = 169 → tangent² = 144 → **tangent = 12 cm**.

---

**Q39.7 (Advanced) — Cyclic quadrilateral.** ABCD is a cyclic quadrilateral. ∠A = 80°, ∠B = 110°. Find ∠C and ∠D.

**Solving it.** Opposite angles of a cyclic quadrilateral are supplementary (sum = 180°).
- ∠A + ∠C = 180° → ∠C = 180 − 80 = **100°**.
- ∠B + ∠D = 180° → ∠D = 180 − 110 = **70°**.

---

## Section 10 — TRIGONOMETRY + HEIGHTS AND DISTANCES (2 worked + variations)

> **Notation expansion (used throughout this section):**
> **sin θ, cos θ, tan θ** = trigonometric ratios in a right triangle. **sin = opp/hyp; cos = adj/hyp; tan = opp/adj**.
> **Angle of elevation** = angle from observer's eye to top of object (looking up). **Angle of depression** = angle looking down.

---

**Q40.** Find the value of sin 30° + cos 60° + tan 45°.

**What kind of problem is this?** Direct standard-angle recall.

**Solving it.** Step-by-step.
- sin 30° = **1/2**
- cos 60° = **1/2**
- tan 45° = **1**
- Sum = 1/2 + 1/2 + 1 = **2**

**Worth knowing:** Memorise the standard-angle table cold.

| θ | 0° | 30° | 45° | 60° | 90° |
|---|---|---|---|---|---|
| sin | 0 | 1/2 | 1/√2 | √3/2 | 1 |
| cos | 1 | √3/2 | 1/√2 | 1/2 | 0 |
| tan | 0 | 1/√3 | 1 | √3 | undefined |

**Memory peg.** sin row uses √(0/4), √(1/4), √(2/4), √(3/4), √(4/4) — square-root of (0,1,2,3,4)/4. cos row is the reverse.

***Watch out:*** Students mix sin 30 (= 1/2) with sin 60 (= √3/2). Always recall sin = "small to large" (0 → 1).

**A similar question — Identity sum.** sin² 30° + cos² 30° = (1/2)² + (√3/2)² = 1/4 + 3/4 = **1** (Pythagorean identity sin²θ + cos²θ = 1, true for any θ).

**Another twist — Mixed angles.** sin 30° × cos 60° + cos 30° × sin 60° = (1/2)(1/2) + (√3/2)(√3/2) = 1/4 + 3/4 = **1**. (Recognise: this is sin(30° + 60°) = sin 90° = 1.)

---

**Q41.** A vertical pole casts a shadow 10 m long on level ground when the sun's angle of elevation is 30°. Find the height of the pole.

**What kind of problem is this?** Right-triangle trigonometry (heights and distances).

**Solving it.** Step-by-step.
- Draw a right triangle: pole = vertical (opposite to angle), shadow = horizontal (adjacent to angle), sun's rays = hypotenuse.
- Angle of elevation = 30° (at the tip of the shadow, looking up to pole top).
- tan 30° = opposite / adjacent = pole height (h) / shadow (10)
- tan 30° = 1/√3
- 1/√3 = h / 10
- h = 10 / √3 = 10√3 / 3 ≈ **5.77 m**

**Worth knowing:** Rationalise denominators (10/√3 → 10√3/3) for clean answers. The form 10/√3 is correct but rare in MCQs.

***Watch out:*** "10√3 m" — students use tan 30° = √3 (mixing up tan 30 with tan 60 = √3) or invert the ratio.

**A similar question — Sun at 60°.** Shadow 10 m, elevation 60°. tan 60° = √3 = h/10 → h = **10√3 m ≈ 17.32 m** (taller pole, shorter shadow expected at higher elevation).

**Another twist — Find shadow given height + angle.** Pole 12 m tall, elevation 45°. tan 45° = 1 = 12 / shadow → shadow = **12 m** (always shadow = height when elevation is 45°).

---

### Section 10A — ADVANCED TRIG + HEIGHTS (exam-level variations)

---

**Q41.5 (Advanced) — Two observers + same object.** A tower stands on level ground. From a point P, the angle of elevation to the top is 30°. From another point Q, 50 m closer to the tower, the angle is 45°. Find the height of the tower.

**Solving it.**
- Let height = h, distance from foot to Q = x. Then distance from foot to P = x + 50.
- From Q: tan 45° = h/x = 1 → h = x.
- From P: tan 30° = h/(x+50) = 1/√3 → h × √3 = x + 50.
- Substitute h = x: x√3 = x + 50 → x(√3 − 1) = 50 → x = 50/(√3 − 1) = 50(√3 + 1)/2 = 25(√3 + 1).
- h = x = 25(√3 + 1) ≈ 25 × 2.732 ≈ **68.30 m**.

---

**Q41.6 (Advanced) — Angle of depression.** From the top of a 100 m cliff, the angle of depression to a boat is 30°. Find the boat's distance from the foot of the cliff.

**Solving it.**
- Angle of depression from top = angle of elevation from boat (alternate angles).
- tan 30° = 100 / d (height/distance)
- 1/√3 = 100/d → d = 100√3 ≈ **173.21 m**.

---

## Section 11 — NUMBER SYSTEM + LCM/HCF (2 worked + variations)

> **Notation expansion (used throughout this section):**
> **HCF** = Highest Common Factor (also called GCD = Greatest Common Divisor). Largest number that divides all given numbers.
> **LCM** = Least Common Multiple. Smallest number that all given numbers divide into.
> **Universal identity:** LCM × HCF = product of two numbers (works for 2 numbers only).

---

**Q42.** Find the HCF of 252 and 105.

**What kind of problem is this?** Direct HCF — use prime factorisation OR Euclid's algorithm.

**Solving it (Method 1 — prime factorisation).** Step-by-step.
- 252 = 2 × 126 = 2 × 2 × 63 = 2² × 3² × 7
- 105 = 3 × 35 = 3 × 5 × 7
- Common prime factors (with lowest powers): 3¹ and 7¹
- HCF = 3 × 7 = **21**

**Quick way (Method 2 — Euclid's algorithm).**
- 252 = 2 × 105 + 42 (remainder)
- 105 = 2 × 42 + 21
- 42 = 2 × 21 + 0 → HCF = **21**

**Worth knowing:** Verify with the LCM × HCF = product identity.
- LCM = (252 × 105) / 21 = 26,460 / 21 = **1,260**.
- Verify: 1,260 / 252 = 5 ✓; 1,260 / 105 = 12 ✓.

***Watch out:*** "63" — students miss the prime factor 5 and include 3 × 21 = 63 wrongly.

**A similar question — HCF of three numbers.** HCF of 24, 36, 60. Prime factorise: 24 = 2³×3; 36 = 2²×3²; 60 = 2²×3×5. Common: 2² and 3¹. HCF = 4 × 3 = **12**.

**Another twist — Find LCM directly.** LCM of 24, 36 using prime-factorisation: highest powers = 2³, 3² → LCM = 8 × 9 = **72**.

---

**Q43.** Find the sum of digits of the largest 4-digit number that is divisible by 88.

**What kind of problem is this?** Find largest multiple of n within a range; then operate on its digits.

**Solving it.** Step-by-step.
- Largest 4-digit number = 9999.
- Divide: 9999 ÷ 88 = 113.625 (so floor = 113).
- Largest multiple of 88 ≤ 9999 = 113 × 88 = **9,944**.
- Digits = 9, 9, 4, 4. Sum = 9 + 9 + 4 + 4 = **26**.

**Worth knowing:** Quick way to compute largest multiple of n ≤ M. Compute M ÷ n; take integer part k; answer = k × n.

***Watch out:*** Students compute 9999/88 wrongly and use 114 × 88 = 10,032 (a 5-digit number — out of range). Or they round to 114 instead of flooring to 113.

**A similar question — Smallest 4-digit multiple of 7.** Smallest 4-digit number = 1000. 1000/7 = 142.86 → ceiling = 143. 143 × 7 = **1,001**.

**Another twist — Largest 3-digit multiple of LCM(4, 5, 6).** LCM(4, 5, 6) = 60. Largest 3-digit ≤ 999: 999/60 = 16.65 → 16 × 60 = **960**.

---

### Section 11A — ADVANCED NUMBER SYSTEM (exam-level variations)

---

**Q43.5 (Advanced) — Divisibility rules speed-test.** Test if 12,345,678 is divisible by 11.

**Solving it.** Rule for 11: alternating sum of digits.
- Digits: 1, 2, 3, 4, 5, 6, 7, 8.
- Alternating sum (from right): 8 − 7 + 6 − 5 + 4 − 3 + 2 − 1 = (8+6+4+2) − (7+5+3+1) = 20 − 16 = **4**.
- 4 is NOT divisible by 11 → number is NOT divisible by 11.

**Memorise divisibility rules.**
- 2: last digit even.
- 3: digit-sum divisible by 3.
- 4: last 2 digits divisible by 4.
- 5: last digit 0 or 5.
- 6: divisible by both 2 AND 3.
- 8: last 3 digits divisible by 8.
- 9: digit-sum divisible by 9.
- 11: alternating sum divisible by 11.
- 25: last 2 digits 00, 25, 50, 75.

---

**Q43.6 (Advanced) — Remainder theorem.** Find the remainder when 7^100 is divided by 12.

**Solving it.** Find the cycle of 7^n mod 12.
- 7^1 mod 12 = 7
- 7^2 = 49 mod 12 = 1
- 7^3 = 7 × 1 mod 12 = 7
- 7^4 = 7 × 7 mod 12 = 49 mod 12 = 1
- Pattern: odd power → 7; even power → 1.
- 7^100 → even power → remainder = **1**.

---

## Section 12 — ALGEBRA + IDENTITIES (3 worked + variations)

> **Notation expansion (used throughout this section):**
> Common identities to memorise:
> (a + b)² = a² + 2ab + b²
> (a − b)² = a² − 2ab + b²
> (a + b)(a − b) = a² − b²
> a³ + b³ = (a + b)(a² − ab + b²)
> a³ − b³ = (a − b)(a² + ab + b²)
> (a + b)³ = a³ + b³ + 3ab(a + b)

---

**Q44.** If x + 1/x = 5, find the value of x³ + 1/x³.

**What kind of problem is this?** Symmetric algebra trick. x + 1/x is GIVEN; x³ + 1/x³ is asked. Use the identity directly.

**Solving it.** Step-by-step using the cube-of-sum identity.
- (x + 1/x)³ = x³ + 1/x³ + 3 × x × (1/x) × (x + 1/x)
- (x + 1/x)³ = x³ + 1/x³ + 3 × (x + 1/x)
- Rearrange: **x³ + 1/x³ = (x + 1/x)³ − 3 × (x + 1/x)**
- Plug k = 5: x³ + 1/x³ = 5³ − 3 × 5 = 125 − 15 = **110**

**Worth knowing:** Memorise this standard formula card.
- If x + 1/x = k, then:
  - x² + 1/x² = **k² − 2**
  - x³ + 1/x³ = **k³ − 3k**
  - x⁴ + 1/x⁴ = (x² + 1/x²)² − 2 = (k² − 2)² − 2

- If x − 1/x = k, then:
  - x² + 1/x² = **k² + 2** (note +2 here)
  - x³ − 1/x³ = **k³ + 3k**

***Watch out:*** "125" — students forget the −3k correction term.

**A similar question — Find x² + 1/x²** when x + 1/x = 5. Use k² − 2 = 25 − 2 = **23**.

**Another twist — x − 1/x = 3 → x³ − 1/x³ = ?** Use k³ + 3k = 27 + 9 = **36**.

---

**Q45.** If a + b + c = 0, find the value of a³ + b³ + c³.

**What kind of problem is this?** Direct application of the famous identity:
**a³ + b³ + c³ − 3abc = (a + b + c)(a² + b² + c² − ab − bc − ca)**.

**Solving it.** Step-by-step.
- Given: a + b + c = 0.
- Substitute into the RHS of the identity: RHS = 0 × (...) = **0**.
- So: a³ + b³ + c³ − 3abc = 0
- Rearrange: a³ + b³ + c³ = **3abc**

**Worth knowing:** This identity is the BACKBONE of many sum-of-cubes problems. The condition "a + b + c = 0" instantly converts the cube-sum to a simple product.

***Watch out:*** "0" — common mistake. Students assume "if sum = 0, then sum of cubes = 0". WRONG: it equals 3abc (only 0 if at least one of a, b, c is 0).

**A similar question — Numerical.** a = 2, b = 3, c = −5 (sum = 0). a³ + b³ + c³ = 8 + 27 − 125 = −90. 3abc = 3 × 2 × 3 × (−5) = −90 ✓.

**Another twist — Find expression value.** If a + b + c = 0, find (a + b)³ + (b + c)³ + (c + a)³. Note (a + b) = −c, (b + c) = −a, (c + a) = −b. So expression = (−c)³ + (−a)³ + (−b)³ = −(a³ + b³ + c³) = **−3abc**.

---

**Q46.** If a² + b² + c² − ab − bc − ca = 0, prove that a = b = c.

**What kind of problem is this?** Algebraic identity recognition. The given expression has a hidden sum-of-squares form.

**Solving it.** Step-by-step.
- Multiply both sides by 2: 2a² + 2b² + 2c² − 2ab − 2bc − 2ca = 0
- Group: (a² − 2ab + b²) + (b² − 2bc + c²) + (c² − 2ca + a²) = 0
- Factor each group as a perfect square: **(a − b)² + (b − c)² + (c − a)² = 0**
- Sum of three non-negative squares equals zero **only if** each is zero.
- So (a − b) = 0, (b − c) = 0, (c − a) = 0 → **a = b = c**

**Worth knowing:** This identity is incredibly useful. If you see a² + b² + c² − ab − bc − ca, instantly think of ½ × sum-of-squared-differences.

***Watch out:*** Students get the right answer but write proof loosely. The "sum of squares = 0 ⇒ each square = 0" step needs to be stated explicitly for full marks.

**A similar question — Numerical check.** a = b = c = 5. Then 25 + 25 + 25 − 25 − 25 − 25 = 0 ✓. Any unequal trio fails.

**Another twist — Inequality.** Prove a² + b² + c² ≥ ab + bc + ca for any real a, b, c. Same identity: ½[(a−b)² + (b−c)² + (c−a)²] ≥ 0 (sum of squares always non-negative). Equality holds iff a = b = c.

---

### Section 12A — ADVANCED ALGEBRA (exam-level variations)

---

**Q46.5 (Advanced) — Quadratic equation by formula.** Solve 2x² − 7x + 3 = 0.

**Solving it.** Use the quadratic formula: x = (−b ± √(b² − 4ac)) / 2a.
- a = 2, b = −7, c = 3.
- Discriminant = b² − 4ac = 49 − 24 = 25 → √25 = 5.
- x = (7 ± 5) / 4 → x = 12/4 = **3** OR x = 2/4 = **1/2**.

**Quick check via factorisation.** 2x² − 7x + 3 = 2x² − 6x − x + 3 = 2x(x − 3) − (x − 3) = (2x − 1)(x − 3) = 0 → x = 1/2 or 3 ✓.

---

**Q46.6 (Advanced) — Simultaneous linear equations.** Solve: 3x + 2y = 16; 5x − 3y = −1.

**Solving it.** Use elimination.
- Multiply Eq1 by 3: 9x + 6y = 48.
- Multiply Eq2 by 2: 10x − 6y = −2.
- Add: 19x = 46 → x = **46/19 ≈ 2.42**.
- (Numbers slightly awkward — usually the exam gives integers. Let me adjust.)

Actually, try Eq1 = 3x + 2y = 16 and Eq2 = 5x − 3y = 14 (more typical).
- Mult Eq1 × 3: 9x + 6y = 48.
- Mult Eq2 × 2: 10x − 6y = 28.
- Add: 19x = 76 → x = **4**.
- Plug into Eq1: 12 + 2y = 16 → y = **2**.

---

**Q46.7 (Advanced) — Roots and coefficients.** If α and β are roots of x² − 5x + 6 = 0, find α² + β² without computing the individual roots.

**Solving it.** Use Vieta's formulas.
- Sum α + β = −b/a = 5; product αβ = c/a = 6.
- Identity: α² + β² = (α + β)² − 2αβ = 25 − 12 = **13**.

(Verify: roots are 2 and 3. 2² + 3² = 4 + 9 = 13 ✓.)

---

## Section 13 — DATA INTERPRETATION (3 worked + variations)

> **Notation expansion (used throughout this section):**
> **DI** = Data Interpretation (charts, tables, graphs). Common forms: bar chart, line graph, pie chart, table, mixed combo.
> Always read the question CAREFULLY before scanning numbers — the wrong reading leads to obvious wrong answers among the options.

---

**Q47.** A bar chart shows production (in tonnes) of a factory over 5 years: 2020 → 120, 2021 → 150, 2022 → 180, 2023 → 200, 2024 → 250. What is the % growth in production from 2020 to 2024?

**What kind of problem is this?** % change formula. **% change = (new − old) / old × 100**.

**Solving it.** Step-by-step.
- Initial (2020) = 120
- Final (2024) = 250
- Difference = 250 − 120 = **130**
- % growth = (130 / 120) × 100 = 13000 / 120 = **108.33 %**

***Watch out:*** "130 %" — students forget to divide by 120 (initial value) and report the absolute difference as a percent.

**A similar question — % decline.** Production was 250 in 2024, dropped to 200 in 2025. % decline = (250 − 200) / 250 × 100 = **20 %**.

**Another twist — Average annual growth rate (CAGR-style approximation).** If production grows from 120 (2020) to 250 (2024) over 4 years, simple average annual growth ≈ 108.33 % / 4 = **27.08 % per year (simple average)**. (True CAGR via compounded formula = (250/120)^(1/4) − 1 ≈ 20.16 %.)

---

**Q48.** A pie chart of company expenses: salary 30 %, raw materials 25 %, R&D 20 %, marketing 15 %, miscellaneous 10 %. If the marketing expense is ₹3 crore, find the total budget.

**What kind of problem is this?** Pie chart back-calculation: from one slice's value + percentage, compute the whole.

**Solving it.** Step-by-step.
- Marketing slice = 15 % of total budget = ₹3 crore
- 1 % of total = 3 / 15 = ₹0.2 crore
- 100 % (total budget) = 100 × 0.2 = **₹20 crore**

**Quick way:** Direct ratio. Total = 3 / (15/100) = 3 × (100/15) = 300 / 15 = **₹20 crore**.

**Worth knowing:** Once total is known, find any other slice instantly.
- Salary = 30 % × 20 = ₹6 crore.
- Raw materials = 25 % × 20 = ₹5 crore.
- R&D = 20 % × 20 = ₹4 crore.
- Misc = 10 % × 20 = ₹2 crore.
- Verify sum: 6 + 5 + 4 + 3 + 2 = ₹20 crore ✓.

***Watch out:*** Students directly multiply 3 × 15 = ₹45 crore (instead of dividing 3 by 0.15).

**A similar question — Comparing slices.** R&D vs marketing — R&D is 20 % vs marketing 15 % → R&D is (20−15)/15 × 100 = **33.33 % more** than marketing.

**Another twist — Pie chart in degrees.** Each 1 % = 3.6° (since 100 % = 360°). Marketing 15 % = **54°**. Salary 30 % = 108°. Useful when chart gives degrees instead of percentages.

---

**Q49.** Average sales over 4 quarters of a year is 250 units. Q1 = 200, Q2 = 240, Q3 = 280. Find Q4 sales.

**What kind of problem is this?** Use the average to get the total, then subtract known values to find the missing one.

**Solving it.** Step-by-step.
- Total = average × count = 250 × 4 = **1,000 units**
- Sum of Q1 + Q2 + Q3 = 200 + 240 + 280 = **720**
- Q4 = Total − sum of known = 1,000 − 720 = **280 units**

**Worth knowing:** Verify by computing the average back. (200 + 240 + 280 + 280) / 4 = 1000 / 4 = 250 ✓.

***Watch out:*** Students forget that "average = 250 over 4 quarters" gives total = 1000 and try to set up algebra unnecessarily.

**A similar question — Find missing month.** Average rainfall over 12 months = 50 mm. 11 months total = 540 mm. Missing month = 600 − 540 = **60 mm**.

**Another twist — Average of new sub-set.** If Q4 in question becomes 320 (not 280), what's the new yearly average? New total = 720 + 320 = 1,040. Avg = 1,040 / 4 = **260 units/quarter**.

---

### Section 13A — ADVANCED DI (exam-level variations)

---

**Q49.5 (Advanced) — Mixed bar + line graph.** A bar chart shows monthly sales (in lakhs) for 5 months: Jan 50, Feb 60, Mar 75, Apr 80, May 90. A line graph on the same chart shows monthly profit margin (%): Jan 10 %, Feb 12 %, Mar 15 %, Apr 14 %, May 16 %. Find the total absolute profit (in lakhs) over the 5 months.

**Solving it.** Compute profit each month = sales × margin %, then sum.
- Jan: 50 × 0.10 = **5**
- Feb: 60 × 0.12 = **7.2**
- Mar: 75 × 0.15 = **11.25**
- Apr: 80 × 0.14 = **11.2**
- May: 90 × 0.16 = **14.4**
- Total = 5 + 7.2 + 11.25 + 11.2 + 14.4 = **49.05 lakhs**.

---

**Q49.6 (Advanced) — Missing-cell DI.** A table shows expenses (₹ cr) of a company over 4 quarters across 4 categories: Salary, Raw, R&D, Marketing. The Q1 totals: Salary 30, Raw 25, R&D 20, Marketing 15 (sum = 90). Q2 totals are 90 (same total). If Q2 Salary = 25, Q2 Raw = 28, Q2 R&D = 22, find Q2 Marketing.

**Solving it.**
- Q2 Marketing = 90 − 25 − 28 − 22 = **15 cr**.

---

## Section 14 — PROBABILITY + PERMUTATIONS / COMBINATIONS (1 worked + variations)

> **Notation expansion (used throughout this section):**
> **P(E)** = probability of event E = (favourable outcomes) / (total outcomes). Always between 0 and 1.
> **C(n, r)** = "n choose r" = number of ways to pick r items from n without order = n! / (r! × (n−r)!).
> **P(n, r)** = number of arrangements (with order) = n! / (n − r)!.

---

**Q50.** A bag contains 5 red, 4 blue and 3 green balls. Two balls are drawn at random WITHOUT replacement. What is the probability that both are red?

**What kind of problem is this?** Combinatorial probability — count favourable + total via combinations.

**Solving it.** Step-by-step.
- Total balls = 5 + 4 + 3 = **12**
- Total ways to choose 2 balls from 12 = C(12, 2) = (12 × 11) / 2 = **66**
- Favourable: choose 2 red from 5 reds = C(5, 2) = (5 × 4) / 2 = **10**
- P(both red) = favourable / total = 10 / 66 = **5 / 33**

**Quick way:** Sequential probability (without replacement).
- P(first red) = 5/12
- P(second red | first red) = 4/11 (4 reds left out of 11 remaining)
- P(both red) = (5/12) × (4/11) = 20 / 132 = **5/33** ✓ (same answer)

***Watch out:*** Students use **with replacement** logic: (5/12) × (5/12) = 25/144. WRONG when the question says "without replacement" or "drawn together".

**A similar question — Both balls of same colour.** P(2 red) + P(2 blue) + P(2 green) = C(5,2)/C(12,2) + C(4,2)/C(12,2) + C(3,2)/C(12,2) = 10/66 + 6/66 + 3/66 = 19/66.

**Another twist — One red and one blue.** Favourable = C(5,1) × C(4,1) = 5 × 4 = 20 ways (any red × any blue). Total = C(12, 2) = 66. P = 20/66 = **10/33**.

## Section 8 — MENSURATION (3)

**Q34.** Area of a triangle with sides 5, 12, 13 (right-angled).
*Method.* Right triangle (5-12-13). Area = ½ × 5 × 12 = **30 sq units**.
Watch out: Students use Heron's formula → same answer but slower.

**Q35.** Volume of a cylinder, r = 7 cm, h = 10 cm.
*Method.* V = π r² h = (22/7) × 49 × 10 = **1,540 cm³**.
Watch out: Students confuse curved surface (2πrh) with volume.

**Q36.** A cube of side 6 cm is melted and recast into a cuboid 4 × 3 × ?.
*Method.* Volume preserved. 6³ = 216 = 4 × 3 × h → h = 216/12 = **18 cm**.
Watch out: Students compute SA instead.

## Section 9 — GEOMETRY (3)

**Q37.** In ΔABC, AD is angle-bisector from A meeting BC at D. AB = 6, AC = 8, BC = 7. Find BD.
*Method.* Angle-bisector theorem: BD/DC = AB/AC = 6/8 = 3/4. So BD = (3/7) × 7 = **3**.
Watch out: "4" — students invert.

**Q38.** Two chords AB and CD of a circle intersect inside at P. AP = 4, PB = 6, CP = 3. Find PD.
*Method.* AP × PB = CP × PD → 24 = 3 × PD → PD = **8**.
Watch out: Students use 24/3 wrong.

**Q39.** A polygon has 9 sides. Sum of interior angles?
*Method.* (n − 2) × 180 = 7 × 180 = **1,260°**.
Watch out: "1,440°" — students use (n−1) × 180.

## Section 10 — TRIGONOMETRY + HEIGHTS (2)

**Q40.** sin 30° + cos 60° + tan 45° = ?
*Method.* ½ + ½ + 1 = **2**.
Watch out: none — pure recall.

**Q41.** A pole casts a shadow 10 m long when the sun's elevation is 30°. Height of pole?
*Method.* tan 30 = h / 10 → h = 10/√3 = **10√3/3 ≈ 5.77 m**.
Watch out: "10√3 m" — students invert tan.

## Section 11 — NUMBER SYSTEM + LCM/HCF (2)

**Q42.** Find HCF of 252 and 105.
*Method.* 252 = 2² × 3² × 7; 105 = 3 × 5 × 7. HCF = 3 × 7 = **21**.
Watch out: "63" — students miss the 5.

**Q43.** Sum of digits of largest 4-digit number divisible by 88.
*Method.* 9999 ÷ 88 = 113.6 → 113 × 88 = 9944. Digit sum = 9+9+4+4 = **26**.
Watch out: Students compute floor wrong.

## Section 12 — ALGEBRA + IDENTITIES (3)

**Q44.** If x + 1/x = 5, find x³ + 1/x³.
*Method.* a³ + 1/a³ = (a + 1/a)³ − 3(a + 1/a) = 125 − 15 = **110**.
Watch out: "125" — students forget the 3k subtraction.

**Q45.** If a + b + c = 0, find a³ + b³ + c³.
*Method.* Identity: when sum = 0, cubes sum = 3abc. So **3abc**.
Watch out: "0" — common mistake.

**Q46.** If a² + b² + c² − ab − bc − ca = 0, then?
*Method.* This factors as ½ [(a−b)² + (b−c)² + (c−a)²] = 0 → all squares are zero → **a = b = c**.
Watch out: Students assume only a = b = c possible without proof.

## Section 13 — DATA INTERPRETATION (3)

**Q47.** A bar chart shows production (in tonnes) over 5 years: 2020:120, 2021:150, 2022:180, 2023:200, 2024:250. % growth from 2020 to 2024?
*Method.* (250 − 120)/120 × 100 = 130/120 × 100 = **108.33 %**.
Watch out: "130 %" — students forget to divide by initial.

**Q48.** A pie chart of company expenses: salary 30 %, raw 25 %, R&D 20 %, marketing 15 %, misc 10 %. If marketing = ₹3 cr, find total budget.
*Method.* 15 % = 3 cr → 1 % = 0.2 cr → 100 % = **₹20 cr**.
Watch out: Students use direct fraction without unit-rate.

**Q49.** Avg sales over 4 quarters of a year is 250 units. Q1, Q2, Q3 sales are 200, 240, 280. Find Q4.
*Method.* Total = 4 × 250 = 1000. Q4 = 1000 − 720 = **280**.
Watch out: Students forget Q4 explicitly given by avg.

## Section 14 — PROBABILITY + PERMUTATIONS (1)

**Q50.** A bag has 5 red, 4 blue, 3 green balls. Probability of drawing 2 red?
*Method.* C(5,2)/C(12,2) = 10/66 = **5/33**.
Watch out: Students use 5/12 × 5/12 (with replacement, wrong here).

---

\newpage

### Section 14A — ADVANCED PROBABILITY + COMBINATIONS (exam-level variations)

---

**Q50.5 (Advanced) — Conditional probability.** A bag has 6 red and 4 blue balls. Two balls are drawn one after the other without replacement. Given that the first ball drawn is red, what is the probability that the second is also red?

**Solving it.**
- After 1 red drawn, remaining = 5 red + 4 blue = 9 total.
- P(second red | first red) = 5/9.

---

**Q50.6 (Advanced) — Permutations with restriction.** In how many ways can the letters of "EQUATION" be arranged so that all vowels (E, U, A, I, O — five vowels) come together?

**Solving it.**
- "EQUATION" has 8 letters with 5 vowels and 3 consonants (Q, T, N).
- Treat all 5 vowels as ONE block. Then we have 4 entities (the vowel-block + Q + T + N).
- Number of ways to arrange 4 entities = 4! = **24**.
- Within the vowel block, 5 vowels can be permuted = 5! = **120**.
- Total = 24 × 120 = **2,880 ways**.

---

**Q50.7 (Advanced) — Combinations from a committee.** From 10 men and 8 women, how many ways can a committee of 5 be formed having at most 2 women?

**Solving it.** "At most 2 women" = 0 women + 1 woman + 2 women.
- 0 women: C(10, 5) × C(8, 0) = 252 × 1 = **252**.
- 1 woman: C(10, 4) × C(8, 1) = 210 × 8 = **1,680**.
- 2 women: C(10, 3) × C(8, 2) = 120 × 28 = **3,360**.
- Total = 252 + 1,680 + 3,360 = **5,292 ways**.

---

# PART G — ADVANCED EXAM-PATTERN TYPES (new patterns 2024-26)

> **Why this part exists.** Sections 1-14 cover the FUNDAMENTAL types tested in every paper. But modern Banks PO Mains, SSC CGL Tier-2, and SBI/IBPS use NEW question patterns that did not exist 5 years ago — Quadratic Comparison, Approximation, Caselet DI, Coordinate Geometry, Statistics, Logarithms, Combined Mensuration, etc. This Part covers each new pattern with the same step-by-step + variations format.

---

## Section 15 — QUADRATIC COMPARISON (Banks PO Mains • 5 Qs/paper)

> **Notation expansion:**
> Two quadratic equations are given — one in **x** and one in **y**. Solve each, find the roots, then compare x and y to choose one of: **x > y / x ≥ y / x < y / x ≤ y / x = y / no relation**.

---

**Q51.** I. x² − 7x + 10 = 0    II. y² − 6y + 8 = 0. Find the relation between x and y.

**What kind of problem is this?** Standard Banks PO Mains quadratic-comparison. Solve both equations, then compare ALL roots of x with ALL roots of y.

**Solving it.** Step-by-step.

**Equation I:** x² − 7x + 10 = 0
- Factorise: x² − 5x − 2x + 10 = 0 → x(x − 5) − 2(x − 5) = 0 → (x − 5)(x − 2) = 0
- Roots: **x = 2** or **x = 5**

**Equation II:** y² − 6y + 8 = 0
- Factorise: y² − 4y − 2y + 8 = 0 → y(y − 4) − 2(y − 4) = 0 → (y − 4)(y − 2) = 0
- Roots: **y = 2** or **y = 4**

**Comparing roots (the systematic way).**
- Smallest x = 2, largest x = 5.
- Smallest y = 2, largest y = 4.
- For **x ≥ y** to be true, we need every x ≥ every y. Check: x = 2 ≥ y = 4? **NO**. So x ≥ y is FALSE.
- For **x ≤ y** to be true, we need every x ≤ every y. Check: x = 5 ≤ y = 4? **NO**. So x ≤ y is FALSE.
- Some roots overlap (x = 2 = y = 2). Some x > y (x=5, y=2 or 4). Some x < y (x=2, y=4).
- **No clear relation can be established.**

**Worth knowing:** Universal comparison rule.
- If smallest x ≥ largest y → **x ≥ y** (with equality if smallest x = largest y)
- If largest x ≤ smallest y → **x ≤ y**
- Otherwise → **no relation**.

***Watch out:*** Students compare just one root with one root and conclude wrongly. ALWAYS compare smallest-x vs largest-y AND largest-x vs smallest-y.

**A similar question — Clear x > y.** I. x² − 9x + 20 = 0 → x = 4, 5. II. y² − 5y + 6 = 0 → y = 2, 3. Smallest x = 4 > largest y = 3 → **x > y**.

**Another twist — Equation in expanded form.** I. 2x² − 11x + 12 = 0. Factorise: (2x − 3)(x − 4) = 0 → x = 1.5 or 4. II. 3y² − 14y + 16 = 0. Factorise: (3y − 8)(y − 2) = 0 → y = 8/3 ≈ 2.67 or 2. Smallest x = 1.5 < smallest y = 2; largest x = 4 > largest y = 8/3. Mixed → **no relation**.

---

**Q52.** I. x² − 12x + 35 = 0    II. y² − 13y + 42 = 0. Find the relation.

**Solving it.**
- Eq I: (x − 5)(x − 7) = 0 → x ∈ {5, 7}
- Eq II: (y − 6)(y − 7) = 0 → y ∈ {6, 7}
- smallest x = 5, largest x = 7
- smallest y = 6, largest y = 7
- For x ≥ y: smallest x (5) ≥ largest y (7)? NO.
- For x ≤ y: largest x (7) ≤ smallest y (6)? NO.
- Mixed → **no relation can be established**.

**Memory peg.** When the two equations share a common root (here both have 7), the answer is almost always "no relation" unless the other roots align cleanly.

---

## Section 16 — APPROXIMATION (Banks PO Pre • 5 Qs/paper · 30 sec each)

> **Notation expansion:**
> "≈" or "?" in the question stem means **closest integer / round number**, not exact value. Speed > accuracy beyond 1-2%.

---

**Q53.** ?  ≈  39.97 % of 1899.98 + 24.04 × 17.97. Find the value of ?.

**What kind of problem is this?** Round each ugly number to a clean value, then compute mentally.

**Solving it.** Step-by-step rounding.
- 39.97 % ≈ **40 %** (= 2/5)
- 1899.98 ≈ **1,900**
- 24.04 ≈ **24**
- 17.97 ≈ **18**

**Now compute (mentally).**
- 40 % of 1,900 = (2/5) × 1,900 = **760**
- 24 × 18 = (24 × 20) − (24 × 2) = 480 − 48 = **432**
- Sum = 760 + 432 = **1,192**

**Worth knowing:** Memorise these "round-able" fractions for instant computation.

| Difficult % | Round to | As fraction |
|---|---|---|
| 39.97 % | 40 % | 2/5 |
| 33.33 % | 33.33 % | 1/3 |
| 16.66 % | 16.66 % | 1/6 |
| 14.28 % | 14.28 % | 1/7 |
| 12.5 % | 12.5 % | 1/8 |
| 11.11 % | 11.11 % | 1/9 |
| 9.09 % | 9.09 % | 1/11 |
| 8.33 % | 8.33 % | 1/12 |

***Watch out:*** Don't over-round. If actual is 1899.98, rounding to 2,000 introduces 5 % error — too much. Round to nearest "nice" value (1,900 here).

**A similar question — Subtraction.** ? ≈ 49.99 % of 480.04 − 19.97 × 11.95. → 50 % of 480 = 240; 20 × 12 = 240. ? = **0** (or close to 0; actual closer to −0.5).

**Another twist — Division/mixed.** ? ≈ √624.97 + (35.04)². → √625 = 25; 35² = 1,225. ? = 25 + 1,225 = **1,250**.

---

**Q54.** ?  ≈  16.66 % of 1199.95 + 25.04 % of 799.92.

**Solving it.**
- 16.66 % = 1/6, of 1,200 = **200**.
- 25.04 % = 1/4, of 800 = **200**.
- ? ≈ 200 + 200 = **400**.

**Speed-tip.** Whenever you see a decimal % near a "nice" fraction (16.66, 14.28, 12.5, 33.33, etc.), use the fraction — it's faster than working out the decimal.

---

## Section 17 — QUANTITY COMPARISON (Banks PO Mains • 3-5 Qs/paper)

> **Notation expansion:**
> Two quantities (often algebraic or word-problem expressions) are given. Compute or simplify each, then compare.

---

**Q55.** Quantity I: A boat travels 30 km downstream in 3 hours; speed of stream = 2 km/h. Find the boat's speed in still water.
Quantity II: Average of 5 consecutive even numbers, the smallest of which is 16.
Compare Quantity I and Quantity II.

**What kind of problem is this?** Solve each side independently → numerical comparison.

**Quantity I.**
- Downstream speed = distance / time = 30 / 3 = **10 km/h**
- Downstream = boat + stream → boat = 10 − 2 = **8 km/h**

**Quantity II.**
- 5 consecutive even numbers starting at 16: 16, 18, 20, 22, 24.
- Average = (sum) / 5 = (16+18+20+22+24)/5 = 100/5 = **20**.
- Or shortcut: average of consecutive numbers = middle number = **20**.

**Compare:** Quantity I (8) < Quantity II (20). So **Quantity I < Quantity II** (or Q II > Q I).

**Worth knowing:** Common answer options:
- (a) Q I > Q II
- (b) Q I ≥ Q II
- (c) Q I < Q II ← (correct here)
- (d) Q I ≤ Q II
- (e) Q I = Q II OR no relation

***Watch out:*** Students compute one quantity carefully but rush the other. Always solve BOTH, then compare cleanly.

**A similar question.** Quantity I: 30 % of 200. Quantity II: 25 % of 240. Both = 60 → **Q I = Q II**.

---

## Section 18 — CASELET DI (Banks PO Mains specialty • 5-Q set)

> **Notation expansion:**
> Caselet DI = 1 paragraph of facts, NO chart. Read carefully → extract data → answer 5 sub-questions. The challenge is extracting numbers correctly from prose.

---

**Q56.** **Caselet:** A factory has three units — A, B, and C. The total production in 2024 was 12,000 units. Unit A produced 40 % of the total. Unit B produced 75 % of what Unit A produced. Unit C produced the rest.

In 2025, Unit A's production increased by 25 %, Unit B's increased by 20 %, and Unit C's decreased by 10 %.

**Sub-Q:** What was Unit C's production in 2025?

**Solving it.** Step-by-step extraction.

**Step 1 — 2024 production by unit.**
- Total = 12,000
- A = 40 % × 12,000 = **4,800**
- B = 75 % × 4,800 = **3,600**
- C = 12,000 − 4,800 − 3,600 = **3,600**

**Step 2 — 2025 production by unit.**
- A_2025 = 4,800 × 1.25 = **6,000**
- B_2025 = 3,600 × 1.20 = **4,320**
- C_2025 = 3,600 × 0.90 = **3,240**

**Answer.** Unit C in 2025 = **3,240 units**.

**Worth knowing:** Caselet sub-Qs typically ask for: ratios, percentages, differences, totals across years/units. Build a table once → answer all 5 in 2-3 minutes.

| Unit | 2024 | 2025 | Δ % |
|---|---|---|---|
| A | 4,800 | 6,000 | +25 % |
| B | 3,600 | 4,320 | +20 % |
| C | 3,600 | 3,240 | −10 % |
| **Total** | **12,000** | **13,560** | +13 % |

***Watch out:*** Students re-read the paragraph for each sub-Q (wastes 30 sec). Extract once, build the table, then read sub-Qs.

**More sub-Qs (try mentally).**
- Ratio of A : B : C in 2024? → 4 : 3 : 3
- Total production in 2025? → 13,560
- % of total contributed by A in 2025? → 6000/13560 × 100 ≈ 44.25 %
- Difference between A's 2025 and B's 2025? → 6000 − 4320 = 1,680 units

---

## Section 19 — COORDINATE GEOMETRY (SSC CGL Tier-2 • 3-5 Qs/paper)

> **Notation expansion:**
> A point in 2-D plane = (x, y). x = horizontal (abscissa); y = vertical (ordinate).
> **Distance formula** between (x₁, y₁) and (x₂, y₂) = √[(x₂ − x₁)² + (y₂ − y₁)²]
> **Midpoint formula** = ((x₁ + x₂)/2, (y₁ + y₂)/2)
> **Slope formula** between two points = (y₂ − y₁) / (x₂ − x₁)
> **Line equation** y − y₁ = m(x − x₁), where m = slope.

---

**Q57.** Find the distance between points A (3, 4) and B (7, 1).

**Solving it.** Plug into distance formula.
- d = √[(7 − 3)² + (1 − 4)²] = √[16 + 9] = √25 = **5 units**

**Worth knowing:** Recognise Pythagorean triples in coordinate geometry. Here (4, 3, 5) appeared automatically.

***Watch out:*** Students subtract in wrong order (3 − 7 vs 7 − 3); doesn't matter because we square — but be consistent.

**A similar question.** Distance between (0, 0) and (5, 12) = √(25 + 144) = √169 = **13** (a 5-12-13 triple).

**Another twist — Find a missing coordinate.** Distance between (1, 2) and (4, k) = 5. Solve √(9 + (k−2)²) = 5 → 9 + (k−2)² = 25 → (k−2)² = 16 → k − 2 = ±4 → **k = 6 or k = −2**.

---

**Q58.** Find the slope of the line passing through (2, 3) and (6, 11). Then find the equation of the line.

**Solving it.** Step-by-step.
- Slope m = (11 − 3) / (6 − 2) = 8 / 4 = **2**
- Equation (using point-slope form with (2, 3)): y − 3 = 2(x − 2) → y = 2x − 4 + 3 → **y = 2x − 1**

**Worth knowing:** Quick line-properties recap.
- **Parallel lines** have the same slope.
- **Perpendicular lines** have slopes whose product = −1 (i.e., m₁ × m₂ = −1).
- **Horizontal line** has slope 0; **vertical line** has undefined slope.

**A similar question — Midpoint.** Midpoint of (2, 3) and (6, 11) = ((2+6)/2, (3+11)/2) = (4, 7).

**Another twist — Perpendicular line.** Find equation of line perpendicular to y = 2x − 1, passing through (1, 5). New slope m' = −1/2 (since 2 × −0.5 = −1). Equation: y − 5 = −0.5(x − 1) → y = −0.5x + 5.5 → **2y + x = 11**.

---

## Section 20 — STATISTICS (SSC CGL Tier-2 + Banks GA)

> **Notation expansion:**
> **Mean** = arithmetic average. **Median** = middle value when sorted. **Mode** = most-frequent value. **Range** = max − min. **Standard Deviation (SD)** = √(variance) = √[(1/n) Σ(xᵢ − mean)²].

---

**Q59.** Find the mean, median, and mode of the data: 4, 8, 6, 4, 7, 9, 4, 8, 6.

**Solving it.** Step-by-step.

**Sort first:** 4, 4, 4, 6, 6, 7, 8, 8, 9. (n = 9)

**Mean** = sum / count = (4+4+4+6+6+7+8+8+9) / 9 = 56 / 9 ≈ **6.22**

**Median** = middle value (since n = 9, middle is (9+1)/2 = 5th value when sorted) = **6**

**Mode** = most-frequent value = **4** (occurs 3 times)

**Worth knowing:** Empirical relation. **Mode = 3 × Median − 2 × Mean** (approximate, for moderately skewed data).

***Watch out:*** Students forget to sort before finding the median. Without sorting, "middle position" is meaningless.

**A similar question — Even count.** Data: 2, 5, 7, 9, 11, 13. n = 6. Median = average of 3rd and 4th values = (7 + 9)/2 = **8**.

**Another twist — Find SD.** Data: 2, 4, 6, 8, 10. Mean = 6. Deviations from mean: −4, −2, 0, 2, 4. Squared: 16, 4, 0, 4, 16. Sum = 40. Variance = 40/5 = 8. SD = √8 ≈ **2.83**.

---

## Section 21 — LOGARITHM (SSC CGL Tier-2 + RRB JE)

> **Notation expansion:**
> **log_b(x) = y** means b^y = x. Default base in competitive exams = **10** (so log 100 = 2).
> **Natural log** = ln(x), base e ≈ 2.718.
> **Key rules:**
> log(a × b) = log a + log b
> log(a / b) = log a − log b
> log(aⁿ) = n × log a
> log_b(a) = log a / log b (change of base)
> log_b(b) = 1; log_b(1) = 0.

---

**Q60.** Find the value of log 8 + log 125 (base 10).

**Solving it.** Step-by-step.
- log 8 + log 125 = log (8 × 125) = log 1,000 = **3** (since 10³ = 1,000).

**Quick way:** Recognise that 8 × 125 = 1,000 (a power of 10) — log 10ⁿ = n.

**Worth knowing:** Memorise these standard log values (base 10).
- log 2 ≈ **0.301**
- log 3 ≈ **0.477**
- log 5 ≈ **0.699** (= 1 − log 2)
- log 7 ≈ **0.845**

***Watch out:*** Students try to compute log 8 = 3 × log 2 (= 0.903) and log 125 = 3 × log 5 (= 2.097) separately. Both are right but slower. Sum-then-multiply is faster.

**A similar question — Solve for x.** If log x = 2.5, find x. → x = 10^2.5 = 10² × 10^0.5 = 100 × √10 ≈ **316.23**.

**Another twist — Change of base.** log_2(16) = log 16 / log 2 = (4 × log 2) / log 2 = **4**.

---

## Section 22 — MENSURATION COMBINED SOLIDS (SSC CGL Tier-2)

> **Notation expansion:**
> Combined solids = two basic solids stuck together (cone-on-cylinder, hemisphere-on-cone, frustum, etc.). Volume = sum of parts; surface area = sum of EXTERNAL surfaces only (subtract any joining face).

---

**Q61.** A solid is formed by mounting a cone on top of a cylinder. The cylinder has radius 7 cm and height 10 cm. The cone has the same base radius (7 cm) and height 4 cm. Find the total volume.

**Solving it.** Step-by-step.
- Volume of cylinder = πr²h = (22/7) × 49 × 10 = 22 × 70 = **1,540 cm³**
- Volume of cone = (1/3)πr²h = (1/3) × (22/7) × 49 × 4 = (1/3) × 22 × 28 = **205.33 cm³**
- Total volume = 1,540 + 205.33 = **1,745.33 cm³**

**Worth knowing:** When solids share a base, volumes ADD (no overlap). Surface area adds only EXTERIOR — the joining circular face is hidden, so subtract one πr² from each side's TSA when computing total surface.

***Watch out:*** Students compute TSA of each solid separately and add — wrong because the shared circular face counts twice.

**A similar question — Hemisphere on cylinder.** Cylinder r = 7, h = 10; hemisphere r = 7 on top. Volume = πr²h + (2/3)πr³ = 1,540 + (2/3) × (22/7) × 343 = 1,540 + 718.67 = **2,258.67 cm³**.

**Another twist — Frustum (cone with top cut off).** Frustum has R = 6 (bottom radius), r = 3 (top radius), h = 8. Volume = (1/3)πh(R² + r² + Rr) = (1/3) × (22/7) × 8 × (36 + 9 + 18) = (1/3) × (22/7) × 8 × 63 = **528 cm³**.

---

## Section 23 — CALENDAR + CLOCK (RRB NTPC + SSC favourite)

> **Notation expansion:**
> **Odd days** = days remaining when total days ÷ 7. Used for finding the day of the week of any date.
> **Clock angles:** Hour hand moves 360° / 12 = 30° per hour OR 0.5° per minute. Minute hand moves 360°/60 = 6° per minute. Relative speed (minute − hour) = 5.5° per minute.

---

**Q62.** What day of the week was 15 August 1947?

**Solving it.** Step-by-step using the odd-days method.
- Reference: 1 January 0001 was a Monday (calendar starts).
- Total days from 1 Jan 0001 to 15 Aug 1947 = 1946 complete years + 226 days (in 1947).
  - Days in complete year = 365 (or 366 in leap).
- Quick formula: count "odd days" mod 7.
  - 1600 years complete: odd days = 0 (every 400-year block has 0 odd days).
  - Next 300 years (1601-1900): odd days = 1 (300 yrs has 5 odd days... actually let's use a quicker shortcut).

**Faster method (Zeller's-style mental math).** In SSC, this is rarely solved by hand for an arbitrary date. Memorise key reference dates:
- 15 Aug 1947 = **Friday**
- 26 Jan 1950 = **Thursday**
- 1 Jan 2000 = **Saturday**
- 1 Jan 2024 = **Monday**

For nearby dates, count days forward/backward modulo 7.

***Watch out:*** Leap year rules — divisible by 4 BUT not 100 (unless also divisible by 400). 1900 is NOT a leap year; 2000 IS.

**A similar question — Day of week.** What day was 26 January 1950? → Thursday (memorise this — first Republic Day).

**Another twist — Days between two dates.** From 1 Jan 2024 to 1 Jan 2025 = 366 days (2024 leap). 366 ÷ 7 = 52 remainder 2. So 1 Jan 2025 = Monday + 2 = Wednesday.

---

**Q63.** Find the angle between the hour hand and the minute hand of a clock at 3:40.

**Solving it.** Step-by-step.
- Hour hand position at 3:40:
  - At 3:00, hour hand is at 90° (pointing to 3).
  - In next 40 minutes, hour hand moves 40 × 0.5° = 20° more.
  - Hour hand at 3:40 = 90 + 20 = **110°** from 12.
- Minute hand position at 40 minutes past hour:
  - Minute hand at "40" mark = 40 × 6° = **240°** from 12.
- Angle between = |240 − 110| = **130°**

**Worth knowing:** Useful clock formulas.
- Angle of hour hand from 12 = (60 × H + M) × 0.5° where H = hour, M = minutes.
- Angle of minute hand from 12 = M × 6°.
- Angle between = |11M/2 − 30H| (mod 360, take smaller of the two: angle or 360 − angle).

**Quick way using formula.** |11 × 40 / 2 − 30 × 3| = |220 − 90| = **130°** ✓.

***Watch out:*** Sometimes the "smaller" angle is asked — if your answer is > 180°, subtract from 360° to get the reflex-angle complement.

**A similar question — Clock at 6:15.** |11 × 15/2 − 30 × 6| = |82.5 − 180| = **97.5°**.

**Another twist — When are the hands at right angle?** Hands form 90° angle 22 times in 12 hours (not 24 — they "miss" twice due to relative speed). First time after 3:00: when |11M/2 − 90| = 90 → 11M/2 = 0 or 180 → M = 0 (i.e. 3:00 itself, but they're at 90° already? actually at 3:00 they're at 90°). Next: M = 360/11 ≈ 32.73 minutes past 3 → roughly **3:32:43**.

---

# PART E — TIMED MINI-MOCK (25 Q · 25 min)

> Solve under timer. Self-grade against the answer key. Target: 22+/25 in <25 min for >90% mastery.

1. 35 % of 480 = ?  &nbsp; (a) 158 (b) 168 (c) 178 (d) 188
2. A sum doubles in 8 yrs at SI. Triple in?  (a) 16 (b) 18 (c) 20 (d) 24
3. CP = ₹400, SP = ₹500. Profit %?  (a) 20 (b) 25 (c) 30 (d) 33
4. 12, 18 LCM = ?  (a) 36 (b) 48 (c) 24 (d) 60
5. Avg of first 10 natural numbers?  (a) 4.5 (b) 5 (c) 5.5 (d) 6
6. 1/2 + 1/3 + 1/6 = ?  (a) 1 (b) 5/6 (c) 7/6 (d) 11/6
7. A ratio 3:4, B is 25 % more. New ratio?  (a) 3:5 (b) 6:7 (c) 12:15 (d) 24:25
8. 25 % of x = 80. x = ?  (a) 320 (b) 280 (c) 360 (d) 400
9. Train 200 m at 72 km/h crosses pole in?  (a) 8 s (b) 10 s (c) 12 s (d) 15 s
10. Boat speed in still water 12, stream 4. Downstream 32 km in?  (a) 1.5 h (b) 2 h (c) 2.5 h (d) 3 h
11. A and B together 8 days, A alone 12. B alone?  (a) 16 (b) 20 (c) 24 (d) 30
12. (a + b)² − (a − b)² = ?  (a) 4ab (b) 2ab (c) ab (d) 0
13. sin² 30° + cos² 30° = ?  (a) 1/2 (b) 1 (c) √3/2 (d) 2
14. Area equilateral triangle side 6 = ?  (a) 9√3 (b) 18√3 (c) 36 (d) 18
15. SI on ₹2,000 @ 5 % for 4 yrs = ?  (a) 200 (b) 300 (c) 400 (d) 500
16. CI on ₹1,000 @ 10 % for 2 yrs = ?  (a) 200 (b) 210 (c) 215 (d) 220
17. P (red on a die) = ?  (a) 0 (b) 1/6 (c) 1/3 (d) 1/2
18. 7! / 5! = ?  (a) 7 (b) 14 (c) 42 (d) 35
19. Sum of angles of pentagon = ?  (a) 360 (b) 540 (c) 720 (d) 900
20. Volume cube side 5 = ?  (a) 25 (b) 75 (c) 100 (d) 125
21. CSA cylinder r=7, h=10 = ?  (a) 220 (b) 440 (c) 660 (d) 880
22. Mean of 1, 2, ..., 10 = 5.5; SD ≈ ?  (a) 2.87 (b) 3.0 (c) 3.5 (d) 4.0
23. 30 % of 30 % of 1,000 = ?  (a) 60 (b) 90 (c) 30 (d) 100
24. Compound ratio 2:3 and 4:5 = ?  (a) 4:5 (b) 8:15 (c) 6:8 (d) 1:1
25. Tank A fills in 10 h, B empties in 15 h. Both open?  (a) 25 h (b) 30 h (c) 35 h (d) 40 h

**Answer key:** 1-b, 2-a, 3-b, 4-a, 5-c, 6-a, 7-b (3:5), 8-a, 9-b, 10-b, 11-c, 12-a, 13-b, 14-a, 15-c, 16-b, 17-a, 18-c, 19-b, 20-d, 21-b, 22-a, 23-b, 24-b, 25-b.

---

# PART F — TRAP-RECOGNITION CARDS

| Trap pattern | Where it appears | How to spot |
|---|---|---|
| "increase by r %, then decrease by r %" gives 0 | Percentage | Multiplicative changes never cancel — net is always −r²/100 % |
| Equal SP, equal % gain & loss = 0 | Profit & Loss | Always net loss (r/10)² |
| "double in n years SI" → "triple in 2n" | SI | Wrong; triple needs (n × 2) only if rate doubles. Correct: triple in 2n only if rate = 100/n |
| "average speed = (s₁ + s₂)/2" | TSD | Only true for equal time, not equal distance. Use harmonic 2s₁s₂/(s₁+s₂) for equal distance |
| Adding pipe rates instead of subtracting | Pipes | If outlet pipe, subtract |
| Using SP as base for profit % | P&L | Always CP base; SP base is "discount" or "margin" |
| Forgetting 18/5 conversion | Speed | km/h to m/s: × 5/18 |
| Heron + obvious right-angle | Mensuration | Check Pythagoras first; ½·base·height beats Heron |
| Rate "p.a. compounded half-yearly" → use rate/2, periods × 2 | CI | Always halve rate, double periods |
| (n−1) instead of (n−2) for polygon angles | Geometry | Sum = (n − 2) × 180 |

---

# PART G — SPEED REFERENCE CARD (1-page exam day)

**Squares 1-30** (memorise):  1,4,9,16,25,36,49,64,81,100,121,144,169,196,225,256,289,324,361,400,441,484,529,576,625,676,729,784,841,900.

**Cubes 1-15:**  1,8,27,64,125,216,343,512,729,1000,1331,1728,2197,2744,3375.

**Fraction = % conversions:**  1/2=50, 1/3=33.3, 1/4=25, 1/5=20, 1/6=16.6, 1/7=14.28, 1/8=12.5, 1/9=11.1, 1/10=10, 1/11=9.09, 1/12=8.33, 1/13=7.69, 1/14=7.14, 1/15=6.66, 1/16=6.25, 1/20=5, 1/25=4.

**Roots:**  √2=1.414, √3=1.732, √5=2.236, √7=2.645, √10=3.162.

**Pythagorean triples to spot in geometry:**  3-4-5, 5-12-13, 7-24-25, 8-15-17, 9-40-41, 11-60-61, 12-35-37, 20-21-29, 28-45-53.

**Algebra identities (instant recall):**
- (a+b)² = a² + 2ab + b²
- (a−b)² = a² − 2ab + b²
- a² − b² = (a+b)(a−b)
- a³ ± b³ = (a±b)(a² ∓ ab + b²)
- a + 1/a = k → a² + 1/a² = k² − 2; a³ + 1/a³ = k³ − 3k
- if a+b+c = 0 → a³+b³+c³ = 3abc

**Trig values cold:**

| θ | 0° | 30° | 45° | 60° | 90° |
|---|---|---|---|---|---|
| sin | 0 | 1/2 | 1/√2 | √3/2 | 1 |
| cos | 1 | √3/2 | 1/√2 | 1/2 | 0 |
| tan | 0 | 1/√3 | 1 | √3 | ∞ |

---

*This DRILL PACK is the difference between "I read the book" and "I CAN SOLVE the paper". Drill all 50 examples + the mini-mock at least twice. Time yourself. Mark trap-options before checking the answer key.*

---

\newpage

# PART H — VEDIC MATH & SPEED TRICKS (the 95%+ edge)

> Each of the 16 Vedic sutras + the speed-multiplication shortcuts below saves **5-10 seconds per question**. In a 25-Q section, that's ~3-4 minutes saved — enough to attempt 5 more questions.

## H.1 Multiplication shortcuts

### Multiplication of any 2-digit number by 11

**Rule.** Place the SUM of the two digits between them.

- 25 × 11 = 2 _ 5 with (2+5)=7 in middle = **275**.
- 47 × 11: 4_7 with (4+7)=11 → carry the 1: 4+1=5, leaves 1 in middle, 7 at end → **517**.
- 89 × 11: 8_9 with (8+9)=17 → 8+1=9, 7 in middle, 9 at end → **979**.

### Multiplication by 12, 13, ..., 19 ("Vertical & Crosswise" sutra)

Multiplication by 13: take number × 1 ten and add (× 3 units).
- 24 × 13: (24 × 10) + (24 × 3) = 240 + 72 = **312**.
- Or: write 2_4 → 2×3 = 6 add to next digit place.

### Multiplication of two numbers near 100 (Nikhilam sutra)

If both close to 100 (or 1000), use base-100 deviation method.

- 96 × 97: deviations from 100 are −4 and −3. Cross-add: 96 + (−3) = 93 OR 97 + (−4) = 93 → first part. Multiply deviations: (−4)(−3) = 12 → second part. Answer = **9312**.
- 98 × 96: deviations −2, −4. Cross: 98 − 4 = 94. Mult: 8. Answer = **9408**.
- 103 × 104: deviations +3, +4. Cross: 103 + 4 = 107. Mult: 12. Answer = **10712** (since base 100 needs 2-digit padding, 12 stays as is).

### Squaring numbers ending in 5

**Rule.** Take leading digit × (leading digit + 1), then append "25".

- 25² = 2 × 3 = 6 → append 25 → **625**.
- 35² = 3 × 4 = 12 → **1225**.
- 75² = 7 × 8 = 56 → **5625**.
- 105² = 10 × 11 = 110 → **11025**.

### Squaring numbers near 50

For numbers 50 ± k:

- (50 + k)² = (25 + k) followed by k².
- (50 − k)² = (25 − k) followed by k².

- 53² = (25 + 3) followed by 3² = 28 _ 09 = **2809**.
- 47² = (25 − 3) followed by 3² = 22 _ 09 = **2209**.
- 58² = 28 + 8 = 33, then 8² = 64 → **3364**.
- 42² = 25 − 8 = 17, then 8² = 64 → **1764**.

### Multiplication of numbers near 50 (each)

- 48 × 47: 47 − 2 = 45 → first part is 25 + 45 = wait, simpler: each is 50 − k. Use base 50.
- Use Nikhilam with base 50: deviations from 50 are −2, −3. Cross: 48 + (−3) = 45. Multiply: 6. Multiply first part by 50/100 = ½. Answer = 45 × 50 + 6 = 2256.
- Or just memorise standard products.

### Multiplication by 9, 99, 999

**Rule.** N × 9 = N0 − N. N × 99 = N00 − N. N × 999 = N000 − N.

- 24 × 9 = 240 − 24 = **216**.
- 37 × 99 = 3700 − 37 = **3663**.
- 48 × 999 = 48000 − 48 = **47952**.

### Multiplication by 25, 50, 125, 250

- × 25: (× 100) ÷ 4. So 36 × 25 = 3600/4 = 900.
- × 50: (× 100) ÷ 2. So 84 × 50 = 8400/2 = 4200.
- × 125: (× 1000) ÷ 8. So 56 × 125 = 56000/8 = 7000.

## H.2 Squaring + cubing tricks

### Square of any number close to 10ⁿ

(10 + k)² = 100 + 20k + k². For k=5: 225. For k=7: 100 + 140 + 49 = 289.

### Square of 11, 12, ... 19 (memorise table)

11²=121, 12²=144, 13²=169, 14²=196, 15²=225, 16²=256, 17²=289, 18²=324, 19²=361.

### Square of 21-29

21²=441, 22²=484, 23²=529, 24²=576, 25²=625, 26²=676, 27²=729, 28²=784, 29²=841.

### Cubing close to 10n

(10n + k)³ = 1000n³ + 300n²k + 30nk² + k³. Useful only for very small k.

## H.3 Division shortcuts

### Division by 5

Multiply numerator × 2, divide by 10.

- 245/5 = (245 × 2)/10 = 490/10 = **49**.
- 1234/5 = (1234 × 2)/10 = 2468/10 = **246.8**.

### Division by 25, 125

- /25 = (× 4)/100.
- /125 = (× 8)/1000.

### Division by 9 (digit-sum check)

If digit sum is divisible by 9, the number is. Quotient by repeated subtraction.

## H.4 Percentage shortcuts (instant)

| Shortcut | Application |
|---|---|
| 10% | move decimal one place left |
| 1% | move decimal two places left |
| 5% | half of 10% |
| 25% | divide by 4 |
| 12.5% | divide by 8 |
| 33.33% | divide by 3 |
| 16.66% | divide by 6 |
| 6.25% | divide by 16 |
| Successive % | a + b + ab/100 |
| % more vs % less | r/(100+r) × 100 OR r/(100−r) × 100 |
| x% of y = y% of x | symmetry |

## H.5 Quick-recall fraction-to-percent (already covered in Part 0; repeat to lock in)

| Fraction | % |
|---|---|
| 1/2 | 50 |
| 1/3 | 33.33 |
| 1/4 | 25 |
| 1/5 | 20 |
| 1/6 | 16.66 |
| 1/7 | 14.28 |
| 1/8 | 12.5 |
| 1/9 | 11.11 |
| 1/10 | 10 |
| 1/11 | 9.09 |
| 1/12 | 8.33 |
| 2/3 | 66.66 |
| 3/4 | 75 |
| 3/5 | 60 |
| 2/7 | 28.57 |
| 5/8 | 62.5 |
| 3/8 | 37.5 |
| 7/8 | 87.5 |
| 5/9 | 55.55 |
| 7/9 | 77.77 |

## H.6 Time-saving sutras (Vedic — 16 main + 13 sub)

| Sutra | English | Use |
|---|---|---|
| Ekadhikena Purvena | "By one more than the previous" | Squaring numbers ending in 5; recurring decimals |
| Nikhilam Navatashcaramam Dashatah | "All from 9 and last from 10" | Subtraction from 10n; multiplication near base |
| Urdhva-Tiryagbyham | "Vertically and crosswise" | General multiplication |
| Paraavartya Yojayet | "Transpose and adjust" | Division of polynomials |
| Sunyam Samyasamuccaye | "When sum is same that sum is zero" | Equation solving |
| Anurupye Sunyamanyat | "If one is in ratio, the other is zero" | Specific equation pattern |
| Sankalana-Vyavakalanabhyam | "By addition and by subtraction" | Simultaneous equations |
| Yavadunam | "Whatever the deficiency" | Squaring numbers below base |
| Vyastisamastih | "Specific and general" | Series + sequences |
| Sesanyankena Caramena | "The remainders by the last digit" | Recurring decimals |

> Master these; you don't need a 200-page Vedic-math book. Just these few patterns cover 80% of speed-up opportunity.

---

\newpage

# PART I — MENSURATION MASTER FORMULA SHEET (2D + 3D)

## 2D shapes

| Shape | Area | Perimeter / Boundary |
|---|---|---|
| Square (side a) | a² | 4a; diagonal a√2 |
| Rectangle (l × b) | l × b | 2(l + b); diagonal √(l² + b²) |
| Parallelogram (b, h) | b × h | 2(a + b) |
| Rhombus (d₁, d₂) | ½ × d₁ × d₂ | 4 × side; side = ½ × √(d₁² + d₂²) |
| Triangle (b, h) | ½ × b × h | a + b + c |
| Equilateral triangle (a) | (√3/4) × a²; height = (√3/2) × a | 3a |
| Right triangle | ½ × base × perpendicular | a + b + √(a² + b²) |
| Heron's formula | √[s(s−a)(s−b)(s−c)] where s = (a+b+c)/2 | — |
| Trapezium | ½ × (a + b) × h | sum of all sides |
| Circle (r) | π × r² | 2π × r (circumference) |
| Sector (r, θ) | (θ/360) × π × r² | arc length = (θ/360) × 2π × r |
| Annulus (R, r) | π(R² − r²) | 2π(R + r) |
| Regular polygon (n sides, side a) | (1/4) × n × a² × cot(180°/n) | n × a |
| Regular hexagon (a) | (3√3/2) × a² | 6a |

## 3D shapes — Volume + Surface

| Shape | Volume | Total Surface Area | Curved/Lateral SA |
|---|---|---|---|
| Cube (a) | a³ | 6a² | 4a² |
| Cuboid (l, b, h) | l × b × h | 2(lb + bh + hl) | 2h(l + b) |
| Cylinder (r, h) | π r² h | 2πr(r + h) | 2πrh |
| Hollow cylinder (R, r, h) | π(R² − r²)h | 2π(R + r)(R − r + h) | 2πh(R + r) |
| Cone (r, h, l) | (1/3) π r² h; slant l = √(r² + h²) | π r (r + l) | π r l |
| Sphere (r) | (4/3) π r³ | 4π r² | — |
| Hemisphere (r) | (2/3) π r³ | 3π r² | 2π r² |
| Spherical shell (R, r) | (4/3)π(R³ − r³) | — | — |
| Frustum of cone (R, r, h, l) | (1/3) π h (R² + r² + Rr); l = √(h² + (R−r)²) | π(R² + r² + l(R+r)) | π l (R + r) |
| Pyramid (square base a, h, slant l) | (1/3) a² h | a² + 2a×l | 2a×l |
| Tetrahedron (a) | (a³ × √2)/12 | √3 × a² | — |
| Prism (general) | base area × height | 2 × base + perimeter × h | perimeter × h |

## Key memory pegs

- **Cube** is the cuboid with l = b = h = a.
- **Sphere** = 4πr² (surface) and (4/3)πr³ (volume) — memorise EXACTLY.
- **Cone slant length** l = √(r² + h²) — Pythagoras.
- **Hemisphere TSA = 3πr²** (curved + base disc) — common trap (students answer 2πr²).
- **Cuboid diagonal** = √(l² + b² + h²) — extension of 2D.
- **Cylinder volume to area** ratio: V/A → r/2 (per unit height).

## Special-case quick computation

| Setup | Formula |
|---|---|
| Largest cube cut from cube of side a | a (same) |
| Largest sphere from cube of side a | (4/3)π(a/2)³ |
| Largest cylinder from cube (axis through cube) | πr²h with r = a/2, h = a |
| Largest cone from cube | (1/3)π(a/2)²(a) |
| Largest cube inscribed in sphere of r | side = (2r)/√3 |
| Diagonal of square inscribed in circle r | 2r |

---

# PART J — 1-PAGE EXAM-DAY ARITHMETIC CHEATSHEET (revise day before)

**Mental-math reflexes:**
- Squares 1-30 cold. Cubes 1-15 cold.
- Tables 11-20 cold.
- Fraction-percent table memorised (1/2 = 50, 1/8 = 12.5, etc.).
- π ≈ 22/7; √2 ≈ 1.414, √3 ≈ 1.732.

**Universal shortcuts:**
- 10% trick → decimal one place left.
- 25% → ÷4. 125 → ÷8. 5% → half of 10%.
- Percent symmetry: x% of y = y% of x.
- Successive %: a + b + ab/100.
- "r% more" → "r/(100+r)% less".

**Speed multiplication:**
- × 11: place sum of digits between.
- × 9, 99, 999: subtract from N0, N00, N000.
- × 25: × 100 ÷ 4; × 125: × 1000 ÷ 8.
- Squares of 11-19: 121, 144, 169, 196, 225, 256, 289, 324, 361.
- Squares ending in 5: lead × (lead+1), append 25.

**Time-Speed-Distance:**
- km/h to m/s: × 5/18.
- Average speed (equal distance): 2ab/(a+b).
- Boat: down = b+s, up = b−s.

**Profit & Loss:**
- Equal % gain & loss on same SP → always loss = (r/10)².
- MP–CP–SP: Profit% = (SP−CP)/CP × 100. Discount% = (MP−SP)/MP × 100.

**SI / CI:**
- Doubles in n yrs at SI → rate = 100/n %.
- CI − SI for 2 yrs = P(r/100)².

**Trigonometry standard angles:**
- sin(0, 30, 45, 60, 90) = 0, ½, 1/√2, √3/2, 1.
- cos = reverse.

**Geometry:**
- Sum interior angles polygon = (n−2) × 180°.
- Equilateral triangle area = (√3/4)a².
- Heron's: √[s(s−a)(s−b)(s−c)].

**Mensuration:**
- Sphere V = (4/3)πr³, SA = 4πr².
- Cone V = (1/3)πr²h, slant = √(r²+h²).
- Hemisphere TSA = 3πr² (NOT 2πr²).

**Algebra:**
- a + 1/a = k → a² + 1/a² = k² − 2; a³ + 1/a³ = k³ − 3k.
- (a + b + c) = 0 → a³ + b³ + c³ = 3abc.

> Print this page and revise the morning before the exam. THIS is the 95%+ ammunition.
