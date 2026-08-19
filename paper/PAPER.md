*🇬🇧 English | [🇷🇺 Русский](PAPER.ru.md)*

*English translation of [PAPER.ru.md](PAPER.ru.md). The Russian original is the source of truth; numbers are identical.*

# Payout Mechanisms Across Two Worlds: Pro-Rata, User-Centric, and the Attention Economy
### A calibrated simulation of the music market's "cash register" (payout) regimes · v0.4 · MIT License
*Tonify Research · August 2026 · reproducible: `sim1/tonify_cash_sim.py` + `sim1/v04_full.py`, seed=42*

---

## Abstract
We construct a synthetic market of 200,000 artists, calibrated to three independently measured
anchors (Luminate, Spotify Loud & Clear, CMA), and compare four payout mechanisms:
**pro-rata** (Spotify), **user-centric** (SoundCloud FPR), recurring patronage (Twitch),
and the direct **attention economy** (Tonify, World B). Main result: changing the split rule
within World A shifts an artist's minimum viable audience by at most ~1.3×,
whereas moving to the direct mechanisms of World B shifts it by **1–2 orders of magnitude** — provided
that a devoted fan's payment frequency exceeds the breakeven range of 0.38–6.31 payments/year
(median 1.25). Recurring mechanics *would* close that range if measured k ≥ 6.31; k is
UNMEASURED in music (emp2; Twitch k=12 is not a closer). The red team retracted one v0.2
number and replaced three point assumptions with ranges.

---

## 1. Introduction: two worlds
**World A** — a fixed pool of subscription money divided by a formula: pro-rata (Spotify),
user-centric (SoundCloud), artist-centric (Deezer/UMG). The core theorem (Bergantiños &
Moreno-Ternero, 2023): any stable rule divides a listener's contribution only among the artists
that listener actually played — an artist's ceiling is set by their own audience under any formula.
**World B** — money arrives on top of the subscription, directly: donations, recurring patronage,
drops (Tonify — an attention economy on Telegram/TON rails). The question of this paper: by how many orders of magnitude the worlds differ,
and under which measurable conditions World B outperforms World A.

## 2. Model and calibration
The world: N=200,000 artists; the annual-stream distribution is a piecewise construction
(lognormal body / log-bridge / Pareto tail α=1.4) fitted to the anchors:
T1 87% of tracks <1000 streams/year (Luminate 86.2%; stylized onto the artist world) → obtained 87.0% ✓
T2 2.6% of artists >$1000/year in royalties (Spotify) → 2.6% ✓
T3 top 0.28% of artists ≈50% of streams (CMA/Last.fm) → 44.5% ✓; Gini 0.97
A listener's plays for a given artist: lognormal(median 5.16; mean 21.21) [LFM-1b].
All parameters → sources: SOURCES.md; red team: CRITIC.md.

## 3. World A: results
Minimum viable audience (MVA) for $100/mo:
- **pro-rata · signed** (a signed artist's per-stream take, $0.0003/stream): **188,590** listeners
- **pro-rata · independent** ($4.43/1000, US 2026): **12,771**
- **user-centric** (Monte Carlo wallet share; 40% paying, pool = 70% of revenue):
  **9,512** at a wallet of 10,000 plays/year (5,000 → 4,800; 20,000 → 18,341)
- **Twitch mechanics** (recurring subscription, 50/50 split, rate 12): **2,353**
Conclusion A: user-centric improves on pro-rata independent by ~1.3× — consistent with
the empirics (SoundCloud: +34% money into the bottom bucket, −7% of artists out of it; Deezer:
2.4% of the pool redistributed). The rule changes — the order of magnitude does not.

## 4. World B: Tonify attention economy
Parameters: superfans at 0.6–1.7% of the audience; ticket size $3.1–6.9; artist share 0.80–0.95.
- **Breakeven against pro-rata independent: 0.38 … 1.25 … 6.31 payments/superfan/year.**
- MVA at rate 4: **3,204**; at a recurring rate of 12 on the TON rail: **900**.
- Adjacent-industry cadence (Twitch/Patreon k=12, Tencent gifting) does **not** close
  the range; emp2 is the measurement slot and is UNMEASURED.
- Rails, out of $1: TON → 94.9¢ to the artist / 5.0¢ to Tonify; Stars desktop 91.7/4.8;
  Stars mobile 64.1/3.4 (32.5¢ — app stores and spread). On a mobile payment, TON is 1.5×
  more profitable for Tonify than Stars.
- Fraud: injecting F% bot streams siphons F/(1+F) of the pool from everyone (analytical
  dilution curve, no detection); in the direct economy the losses of the innocent ≈ 0
  (its own loss classes — chargebacks — do not smear across artists).
- Logistics of the $13 threshold: 89.9% of signed artists wait >10 years for their first payout.

## 5. Milestone-solver (Tonify's cash, 5% commission)
$300K MRR is **not reached** on donation commission alone: 1M MAU × 1.7% × rate 4 × $6.9
× 5% = $1,955 MRR (a 150× gap). It is reached at: 5M MAU × 5% paying × rate 12 × $6 ×
blended take 20%; or 10M × 4% × 12 × $5 × 15%. Corollary: the milestone requires
recurring patronage and blended lines (drops/premium) — or a recalculation of the figure.

## 6. Review (red team, summary from CRITIC.md)
Retracted: "a status quo of 0.42 donations/year" (verbatim,
translated) — a category error on SoundCloud's 29%.
Replaced with ranges: plays/listener 8–21 (the LFM-1b window ≠ a year), ticket size $3.1–6.9
(PWYW experiment: mean €3.10, refusal rises 24.4% vs 17.3%), superfans 0.6–1.7%
(the 97-2-1 rule). Fixed: binomial superfans (fig2). Honest negative: at today's
payment frequency, direct loses to pro-rata independent.

## 7. What was built (spec: CLAUDE_CODE_HANDOFF.md)
- SIM 2 — Telegram social graph: BA+cliques, complex contagion, phase diagram over K, hub seeding. [x]
- SIM 3 — anti-graveyard: the "payouts ≤ inflow" law versus emission, calibrated on Hamster 300M→12M (AInvest / CryptoPotato Sep 2024, not Caladan). [x]
- SIM 4 — full bipartite user×artist (instead of Monte Carlo wallet share). [x]
- SIM 5 — glue: cascade → σ → k/check (emp2) → treasury. [x]
- emp2 — Telegram payment cadence ≥200 rows. Protocol [x]; measurement UNMEASURED.
- Artist-centric on Deezer/UMG parameters (×2 boost for 1000 plays/500 listeners). [ ]
- Fraud with detection and the cost of detection; a chargeback model for the direct economy. [ ]
- The Stars spread line and premium subscriptions in the cash layer. [ ]

The decision this study supports, labeled as policy, not as theorem: [What to do](WHAT_NEXT.md) — an acceptable formula reform, and why royalties-for-plays should still be abandoned (Tonify → Unify).

## 8. Limitations
A synthetic world: the tail shape between the anchors is a construction; UC is a wallet approximation;
cadence k is UNMEASURED in music (emp2; Twitch is not a closer); ticket size and superfan share remain ranges;
the Tencent benchmark is a blend with advertising; the regulatory risk to gifting (−66% of TME segment
revenue over 3 years) is not in the model. No conclusion is stated more strongly than its falsifier.

## Figures
fig1 MVA curve · fig2 income distribution (binomial) · fig3 fraud dilution ·
fig4 the $1 rails · **fig5 the World A→B ladder** · **fig6 MRR-solver** ·
fig19 pass-through grid · fig20 glue σ*

*MIT License. Reproduction: python3 sim1/tonify_cash_sim.py && python3 sim1/v04_full.py*

---
## Addendum v0.5 — the full {rule × contract} matrix (caught by the founder)
The split rule and the contract are orthogonal axes; previous versions conflated them.
The full per-listener-year → MVA matrix (fig7): pro-rata signed $0.0064/listener-year → 188,590;
pro-rata independent $0.0940 → 12,771; user-centric signed $0.0085 → 140,463;
user-centric independent $0.1262 → 9,512; direct·360 (rate 4) → 4,577; direct independent
(rate 4) → 3,204; recurring rate 12 TON → 900.
**The matrix's headline conclusion: the contract outweighs the rule.** The pro-rata→user-centric
move yields ×1.34; the signed→independent move yields ×14.8. World A's best formula does not
compensate for the 6.8% label pass-through: user-centric signed (140,463) is worse than pro-rata independent (12,771).
Reforming the rule without reforming the contract is a reshuffle one order of magnitude short of what is needed.
*Nature of the two multipliers (v1.1):* the contract axis is a single measured pass-through
(0.0003/0.00443 = 6.772%) applied to both rows — ×14.8 = 1/0.06772 is arithmetic by construction,
not emergent; only ×1.34 has a Monte-Carlo origin, and it is valid only at the baseline wallet
(u = 10,000, PAID_SHARE = 0.40): the rule effect flips sign at the listener-intensity crossover
u* ≈ 14,146 plays/yr (8,731 at PAID_SHARE 0.25; 21,371 at 0.60) — above u*, user-centric is worse
than pro-rata for that artist's audience (fig14; sim1/SPEC.md §3.2). What the matrix contributes
is commensurability: the two axes placed on one MVA grid.

---
## CHANGELOG v1.2 (August 2026) — glue, cadence slot, pass-through grid, hygiene

sim5 glues sim2 → σ → k/check (emp2) → sim3 treasury; sim4 already names the play
matrix. emp2 is a fail-closed Telegram cadence slot: UNMEASURED without ≥200 rows;
Twitch k=12 is retracted as a closer of 0.38–6.31 (the fig5 Twitch-mechanics rung
stays as a take-rate comparison). v07 + fig19: pass-through ρ = 6.772 / 10.6 / 20%
at fixed independent $4.43/1k. RESULTS no longer leads with the retracted 0.42.
Unify section removed (out of scope). sim2/3/4/5 marked built. Caladan attribution
removed from captions/SPEC (AInvest / CryptoPotato).

---
## CHANGELOG v1.1 (August 2026) — external review, seven findings, all accepted

An external reviewer landed seven hits on sim1; the verdicts and actions are recorded in
sim1/SPEC.md CHANGELOG (accusation → verdict → action). Summary of what changed in this paper's
claims: (1) ×14.8 explicitly reclassified as arithmetic input inversion, not an emergent result
(rank-one contract axis; the matrix's value is commensurability); (2) the rule-effect scalar ×1.34
replaced by the crossover u* — the effect flips sign (at u = 20,000 user-centric needs 18,341
listeners vs pro-rata's 12,771); new figure fig14 and script v06_uc_crossover.py; (3) hero
communication leads with the full corner range 3,204…20,161 at k=4 (worst corner loses to the
independent pool), standing rule added; (4) Twitch benchmark given on the aligned ticket (1,709
at $6.89 vs 2,353 at Twitch's fixed $5) — the direct edge is the take rate (5% vs 50%), not the
rail; (5) 3,204 → 900 decomposed: cadence ×3.0 (to 1,068 at take 0.80), TON rail ×1.19 (to 900);
(6) sim1/SPEC.md created (model equations, measured/derived/assumed parameter classes —
PAID_SHARE = 0.40 flagged as an unjustified assumption that linearly scales the UC answer;
validation gates with tolerances and non-zero-exit FAIL; the T3 tolerance [40%; 55%] declared
post-hoc with inter-source justification, relative miss to 50% is 11%); (7) figure
byte-identity scoped to a single environment (stdout stays byte-identical across environments).
Numbers of v0.5.1 unchanged; all new numbers (u*, 1,709, 1,068, 20,161) are derivatives of
existing axes.

---
## CHANGELOG v0.5.1 (August 2026) — syncing the matrix with the $0.0003/stream anchor

**Input:** the packaging red team found that the signed pool numbers diverged between
the documents and the pixels of the figures. The engineer localized the cause.

**Cause.** In `sim1/v05_matrix.py` the label pass-through was set as the constant 0.068 —
a rounding of the derived quantity 0.0003/0.00443 = 0.06772. A rounding promoted to the
status of an input parameter silently redefined the anchor itself: 0.00443 × 0.068 =
0.00030124 ≠ 0.0003. Hence 187,814 on the figures against 188,590 in §3, RESULTS v0.2
and `v04_full.py`.

**Decision (economist's verdict).** The measured anchor is primary — the signed artist's
per-stream take of $0.0003/stream. The 6.8% label pass-through is not a third parameter
but the ratio of the two anchors ($0.0003 / $0.00443 = 6.772%), externally corroborated
by the CNM estimate of ~6.8%; in the code it is now computed from them rather than
entered as a number. The reverse logic (making 6.8% the input and the signed take the
derived value) was rejected: it reduces the number of independent measurements from two
to one and makes the 188,590 claim dependent on someone else's rounding.

**Number changes.**
1. `LABEL_PASS` = 0.0677201 instead of 0.068 (one line in `v05_matrix.py`). The pool
   numbers of all three scripts converged bit-for-bit; 188,590 from RESULTS v0.2 and §3
   is preserved without edits.
2. **user-centric · signed: 140,095 → 140,463.** The number 140,095 is RETRACTED: it is
   not reproducible by any combination of the current code and implies a pass-through of
   0.0679, inconsistent with the 0.06772 of its own sibling 188,590 — that is, the
   "analytic" set of the Addendum was internally inconsistent. A draft-run artifact.
3. **Contract multiplier: ×14.7 → ×14.8** (1/0.0677201 = 14.7667). The rule multiplier
   ×1.34 did not change — the pass-through cancels in it. The Addendum's headline
   conclusion ("the contract outweighs the rule") is untouched: it rested and rests on
   the order of the gap, not on the second digit.
4. §3: user-centric at a 20,000-play wallet — 18,500 → **18,341** (the run yields 18,341;
   18,500 is not reproducible; 5,000 → 4,807, printed as 4,800 — a correct rounding, kept).
5. fig7 prints per-listener-year at 4 decimals instead of 3: at 3 decimals the two signed
   pool cells degenerated to a single significant digit ($0.006 / $0.009) and did not let
   the reader check the MVA against the figure.

**Process change.** `v05_matrix.py` now carries an assert comparing the matrix's pro-rata
signed MVA with the analytic 1200/(21.21 × 0.0003) of `v04_full.py`. The desync existed
because three scripts computed one quantity and none checked against the others; now an
anchor divergence fails the run.

**Precision caveat.** The $0.0003/stream anchor has one significant digit. All quantities
derived from it (188,590, 140,463, ×14.8) are printed at run precision, not measurement
precision; this is reproducibility of the calculation, not a claim about the precision of
the world. The limitation — §9.
