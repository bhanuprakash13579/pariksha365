---
title: "Arithmetic — The Pariksha365 Types-First Book"
subtitle: "Every topic broken into a focused set of types (no arbitrary cap) • shortcut-first • mental-math first"
author: "Pariksha365 Study Notes"
date: "2026"
---

# 📘 How To Use This Book

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

# 🧮 PART 0 — THE MENTAL-MATH ARSENAL

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

# ⚖️ PART 4 — RATIO, PROPORTION, VARIATION

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

# 🤝 PART 9 — PARTNERSHIP

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

# 📐 PART 11 — MENSURATION (2D & 3D)

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

# 🧮 PART 14 — ALGEBRA, PERMUTATION, PROBABILITY

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
