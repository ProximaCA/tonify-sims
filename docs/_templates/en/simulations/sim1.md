---
description: What a listener is worth — pricing the payout mechanisms against the label contract.
---

# sim1 — what a listener is worth

**The question.** How much does a listener deliver to an artist under each payout mechanism, and how does that compare with what the label contract takes?

**The gates.** The synthetic world must reproduce three independently measured anchors before any conclusion is printed: the share of artists below {{sim4.thr_lo|comma}} streams a year, the share above the top threshold, and the share of all streams held by the top fraction. A run that misses them exits non-zero.

**The headline.** The rule axis moves artist viability ×{{sim1.rule}} at the baseline wallet. The contract axis moves it ×{{sim1.contract}}. The industry argues about the first number.

**Run it.** `python3 sim1/tonify_cash_sim.py` — then `v04_full.py`, `v05_matrix.py`, `v06_uc_crossover.py`, `v07_passthrough.py` for the world ladder, the rule×contract matrix, the crossover, and the pass-through grid.

***

{{INCLUDE:README.md|## sim1 — what a listener is worth|## sim2 — how music spreads}}
