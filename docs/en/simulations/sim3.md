---
description: Treasury survival — the "payouts never exceed inflow" law against token emission.
---

# sim3 — treasury survival

**The question.** Does a treasury that pays artists only out of real inflow survive where an emission-funded one dies?

**The gates.** Invariant violations of the law are counted across every run; the emission regime is run on the same demand path so the comparison is ceteris paribus.

**The uncomfortable finding, kept in front.** The law keeps the *platform* solvent; it does not by itself keep artists above their exit threshold — that is sim1's minimum-viable-audience problem, and the study says so rather than burying it.

**Run it.** `python3 sim3/sim3_anti_graveyard.py` (200 runs).

***

### sim3 — treasury survival: the "payouts ≤ inflow" law vs emission

Regime A pays artists only from real inflow (the Tonify treasury law); regime
B pays from token emission (the STEPN/Axie class), calibrated to be
consistent with Hamster Kombat's ×25 collapse in 6 months. 200 Monte-Carlo
runs; an artist layer of 10,000 agents. Full hierarchy of results and
falsifiers: [sim3 README](https://github.com/ProximaCA/tonify-sims/blob/main/sim3/README.md), [sim3 SPEC](https://github.com/ProximaCA/tonify-sims/blob/main/sim3/SPEC.md).

**Finding 8 — emission economies collapse in-model; the law cannot bankrupt
its treasury.** The law-bound treasury has zero invariant violations across
all runs (a structural property), while the emission regime loses ≥80% of
peak DAU in 200/200 Monte-Carlo runs — invariant across all red-team stress
forms; the sharper statistics hold only under the baseline price form: median
death month t* = 12 [IQR 11–13], and the token-denominated treasury "dies"
~6 months before the product (a denomination defect — the same treasury
marked in $ at collection grows monotonically, 0/200 deaths). The emission
regime's payout/inflow ratio crosses 1.0 in month 3 and peaks at 36.9 (it
pays out 37× what it collects) against a structural 0.50 for the law-bound
regime — which is still no immortality: net churn c − i ≥ 8.55%/month kills
the law-bound product too, by external causes
([sim3/README](https://github.com/ProximaCA/tonify-sims/blob/main/sim3/README.md) §7 v1.2; falsifier [SPEC](https://github.com/ProximaCA/tonify-sims/blob/main/sim3/SPEC.md) §8;
calibration: Hamster Kombat ×25/6 mo).

![fig11_treasury_dau](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig11_treasury_dau.png)

*fig11 — DAU and treasuries (simulation: regime A deterministic, regime B
median of 200 runs; log y-axes; IQR = middle-50% band): the law-bound
treasury plateaus at $41,700 with zero deaths while the emission treasury
collapses ×943 from its $75.8M peak; right panel — the falsifier: net churn
≥ 8.55%/month kills the law-bound product too (analytic curve, simulation
dots).*

![fig12_death_dist](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig12_death_dist.png)

*fig12 — distribution of the emission regime's death month (simulation, 200
runs; median t* = 12, IQR 11–13, baseline price form); the "36+" column is
the 18 zombie runs cycling at 4–7% of peak.*

![fig13_two_curves](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig13_two_curves.png)

*fig13 — the two-curves slide (simulation: A deterministic, B median of 200
runs; DAU as a share of each regime's peak): the direct-economy treasury
versus the emission treasury on one axis, with the emission regime's median
death month marked.*

**Finding 9 — platform indifference: the artist's contract barely moves the
platform's treasury.** Switching the artist layer from independent to
signed-360 cuts aggregate artist income by ~1/3 (regime A: $51,898 →
$36,171/month at t=36) — but moves the platform treasury by −0.19% ($41,700 →
$41,623). The platform is financially near-indifferent to the contract its
artists are on: platform revenue scales with flow, artist survival with the
artist's share of it — the party with the least skin in the contract game
holds the pen. The incentive asymmetry is structural, not moral (sim3 artist
layer, §6, both contract columns).

**Finding 10 — artist churn is the norm in both regimes.** 9,010 of 10,000
artists exit within 36 months even in regime A (990 survive; regime B
median: 950 survive — and regime B's artist incomes are paper emission, not
external money). The treasury law keeps the *platform* alive; it does not
keep the *median artist* alive — individual survival is set by audience size
against the exit threshold, which is sim1's MVA problem, not sim3's treasury
problem. The catalogue survives through its weight coefficient (w₃₆ = 0.989):
the platform lives on a long tail of small artists who individually churn.
An honest number to lead with, not to bury (sim3 artist layer, §6).
