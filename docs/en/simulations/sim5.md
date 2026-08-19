---
description: One cascade, then money — sim2 reach times conversion times cadence into the sim3 treasury.
---

# sim5 — glue

**The question.** Does a fired cascade on the synthetic graph produce enough listeners that a calibrated superfan share, paying at a measured (or still-open) cadence, funds $100/month — and what fee hits the treasury?

**The gates.** The frozen sim2 reach-per-seed table must still match `sim2/README.md`; emp2 status is printed (UNMEASURED is valid; Twitch k=12 is not substituted); `L = B·(1+rps)` is an identity.

**The headline.** At B=5 hub seeds, k=4, check $6.89: σ* = 0.242%, inside the 0.6–1.7% band. The same budget at random seeding does not. The worst open corner (k=0.38, $3.10) pushes even hubs above 1.7%. Cadence is UNMEASURED.

**Run it.** `python3 sim5/glue.py` (after `python3 emp2/cadence_measure.py`).

***

### sim5 — glue: one cascade, then money

sim4 is the play matrix. sim5 is the missing pipe: a fired sim2 cascade
becomes L listeners, a share σ become superfans, they pay k times a year
with check c (emp2 if measured, otherwise the open 0.38–6.31 range — never
Twitch k=12), and the fee hits the sim3 treasury.

![fig20_glue_sigma](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig20_glue_sigma.png)

*fig20 — σ* to hit $100/mo after one cascade on the N=50k graph (analytic
over the frozen sim2 reach-per-seed table, seed 42). The yellow band is the
calibrated superfan share 0.6–1.7%. Below the band a fired cascade is enough;
above it conversion would have to beat the calibration.*

**Finding 11 — a fired hub cascade is large enough at k=4; a random seed at
small B is not.** On the published sim2 table, B=5 hubs reach L=22,550.5
listeners; σ* at k=4, check $6.89, take 0.80 is **0.242%** — inside the
0.6–1.7% band. The same budget at random seeding reaches L=5 and needs
σ* ≫ 1. The worst open corner (k=0.38, check $3.10) pushes even hubs to
σ* ≈ 5.65% and loses to the 1.7% ceiling. Cadence UNMEASURED: this is a map,
not a music fact ([sim5](https://github.com/ProximaCA/tonify-sims/blob/main/sim5/SPEC.md); [emp2](https://github.com/ProximaCA/tonify-sims/blob/main/emp2/README.md)).

![fig19_passthrough](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig19_passthrough.png)

*fig19 — signed MVA if the label pass-through is the derived 6.772%, the
AEPO-ARTIS ~10.6%, or Rose 2024's 20% upper, independent rate held at
$4.43/1k (analytic). The yellow line is independent MVA 12,771.*

**Finding 12 — 188,590 is one significant digit; the order of the gap is not.**
At ρ=10.6% signed MVA drops to 120,484 (×9.43); at 20% to 63,857 (×5.00).
Even Rose's upper bound still outweighs the rule axis ×1.34. The hero cell
moves; the qualitative claim does not ([sim1/v07_passthrough.py](https://github.com/ProximaCA/tonify-sims/blob/main/sim1/v07_passthrough.py)).
