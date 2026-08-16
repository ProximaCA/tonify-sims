---
description: The bipartite substrate — one graph, three intensity regimes, the lemmas checked as unit tests.
---

# sim4 — the play matrix

**The question.** The lemmas hold for any play matrix. Do they hold on a *large* one, built to match the anchors of the real distribution — and what happens to the crossover when the intensity–size coupling takes its measured value?

**The world.** 20 000 artists, 1 101 981 listeners, 21 820 434 active pairs, 462.4M streams. Artist popularity is drawn piecewise (lognormal body, log-bridge, Pareto tail) and calibrated to three anchors; listeners pick artists by exact weighted sampling without replacement — preferential attachment.

**Three regimes on one graph**, so the comparison is ceteris paribus: an ergodic control where every listener has identical intensity, the heterogeneous canonical substrate, and the coupled family where pair intensity scales with audience size by the measured `γ`.

## Gates — printed before any conclusion

| Gate | Check | Result | Tolerance |
|---|---|---|---|
| G1 | control regime: max abs(UC/PR − 1) | 0.000e+00 | ≤ 1e-12 |
| G2.1 | share of artists below 1000 streams | 86.6% | 86–88% |
| G2.2 | share above 225 734 | 2.60% | 2.4–2.8% |
| G2.3 | share of streams held by the top 0.28% | 40.3% | 40–55% |
| G2.4 | the Theorem 1 identity across all pairs | 7.105e-15 | ≤ 1e-9 |
| G2.5 | zero sum: abs(ΣUC − ΣPR)/ΣPR | 1.838e-14 | ≤ 1e-12 |
| G3 | crossover sign violations | 0 | 0 |

The control gate is the sharp one: with identical listener intensities the two pool rules must coincide *exactly*, and they do — to the last bit.

## The crossover at measured coupling

| Coupling γ | Artists with UC > PR | Among the top 0.28% |
|---|---|---|
| 0 — independence control | 37.1% | 33.9% |
| +0.12 — measured centre | 45.6% | 8.9% |
| +0.28 — measured head | 52.8% | 3.6% |

![L1 identity and the measured coupling](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig16_L1_crossover.png)

## Three mechanisms on one substrate

Pool rules pay every stream something; the direct mechanism pays 75% of artists exactly nothing, while 7% earn zero under every mechanism because their audience is empty.

![Three mechanisms](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig15_three_mechanisms.png)

## Listener composition beats artist size

A companion run gives every listener their own coupling — measured separately for mainstream and beyond-mainstream listeners — and asks who gains. Controlling for artist size, moving an audience from all-mainstream to all-beyond multiplies the user-centric gain by roughly three (coefficient +1.123 ± 0.048, against a size coefficient of −0.018). And the share of artists better off peaks at the *most mixed* population — 62.4% at a 50/50 split against 49.5% and 39.3% at the extremes. That peak is the dispersion premium of corollary (d) showing up in a cut the model was never built to test.

![Group-level coupling](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig18_group_gamma.png)

## Run it

```bash
python3 sim4/bipartite_gen.py    # gates G1–G3, exports, fig15–16  (~7 min)
python3 sim4/group_gamma.py      # gates H1–H4, fig18              (~8 min)
```

Specification, changelog and the red-team ledger: [sim4/SPEC.md](https://github.com/ProximaCA/tonify-sims/blob/main/sim4/SPEC.md), [sim4/README.md](https://github.com/ProximaCA/tonify-sims/blob/main/sim4/README.md).
