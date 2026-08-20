---
description: One cascade, then money — sim2 reach times conversion times cadence into the sim3 treasury.
---

# sim5 — glue

**The question.** Does a fired cascade on the synthetic graph produce enough listeners that a calibrated superfan share, paying at a measured (or still-open) cadence, funds $100/month — and what fee hits the treasury?

**The gates.** The frozen sim2 reach-per-seed table must still match `sim2/README.md`; emp2 status is printed (UNMEASURED is valid; Twitch k=12 is not substituted); `L = B·(1+rps)` is an identity.

**The headline.** At B=5 hub seeds, k=4, check $6.89: σ* = 0.242%, inside the 0.6–1.7% band. The same budget at random seeding does not. The worst open corner (k=0.38, $3.10) pushes even hubs above 1.7%. Cadence is UNMEASURED.

**Run it.** `python3 sim5/glue.py` (after `python3 emp2/cadence_measure.py`).

***

{{INCLUDE:README.md|## sim5 — glue: one cascade, then money|## sim6 — Direct + guaranteed discovery floor}}
