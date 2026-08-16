---
description: The bipartite substrate — one graph, three intensity regimes, the lemmas checked as unit tests.
---

# sim4 — the play matrix

**The question.** The lemmas hold for any play matrix. Do they hold on a *large* one, built to match the anchors of the real distribution — and what happens to the crossover when the intensity–size coupling takes its measured value?

**The world.** {{sim4.N}} artists, {{sim4.U}} listeners, {{sim4.pairs}} active pairs, {{sim4.streams}} streams. Artist popularity is drawn piecewise (lognormal body, log-bridge, Pareto tail) and calibrated to three anchors; listeners pick artists by exact weighted sampling without replacement — preferential attachment.

**Three regimes on one graph**, so the comparison is ceteris paribus: an ergodic control where every listener has identical intensity, the heterogeneous canonical substrate, and the coupled family where pair intensity scales with audience size by the measured `γ`.

## Gates — printed before any conclusion

| Gate | Check | Result | Tolerance |
|---|---|---|---|
| G1 | control regime: max abs(UC/PR − 1) | {{sim4.g1}} | ≤ 1e-12 |
| G2.1 | share of artists below {{sim4.thr_lo|comma}} streams | {{sim4.t1}}% | {{sim4.t1_lo}}–{{sim4.t1_hi}}% |
| G2.2 | share above {{sim4.thr_hi|comma}} | {{sim4.t2}}% | {{sim4.t2_lo}}–{{sim4.t2_hi}}% |
| G2.3 | share of streams held by the top 0.28% | {{sim4.t3}}% | 40–55% |
| G2.4 | the Theorem 1 identity across all pairs | {{sim4.ident}} | ≤ 1e-9 |
| G2.5 | zero sum: abs(ΣUC − ΣPR)/ΣPR | {{sim4.zerosum}} | ≤ 1e-12 |
| G3 | crossover sign violations | 0 | 0 |

The control gate is the sharp one: with identical listener intensities the two pool rules must coincide *exactly*, and they do — to the last bit.

## The crossover at measured coupling

| Coupling γ | Artists with UC > PR | Among the top 0.28% |
|---|---|---|
| 0 — independence control | {{cross.g0.all}}% | {{cross.g0.top}}% |
| +0.12 — measured centre | {{cross.g12.all}}% | {{cross.g12.top}}% |
| +0.28 — measured head | {{cross.g28.all}}% | {{cross.g28.top}}% |

![L1 identity and the measured coupling]({{RAW}}/figures/fig16_L1_crossover.png)

## Three mechanisms on one substrate

Pool rules pay every stream something; the direct mechanism pays {{atom.direct}}% of artists exactly nothing, while {{atom.pool}}% earn zero under every mechanism because their audience is empty.

![Three mechanisms]({{RAW}}/figures/fig15_three_mechanisms.png)

## Listener composition beats artist size

A companion run gives every listener their own coupling — measured separately for mainstream and beyond-mainstream listeners — and asks who gains. Controlling for artist size, moving an audience from all-mainstream to all-beyond multiplies the user-centric gain by roughly three (coefficient +{{grp.coef}} ± {{grp.se}}, against a size coefficient of −0.018). And the share of artists better off peaks at the *most mixed* population — {{grp.peak}}% at a 50/50 split against {{grp.all_main}}% and {{grp.all_beyond}}% at the extremes. That peak is the dispersion premium of corollary (d) showing up in a cut the model was never built to test.

![Group-level coupling]({{RAW}}/figures/fig18_group_gamma.png)

## Run it

```bash
python3 sim4/bipartite_gen.py    # gates G1–G3, exports, fig15–16  (~7 min)
python3 sim4/group_gamma.py      # gates H1–H4, fig18              (~8 min)
```

Specification, changelog and the red-team ledger: [sim4/SPEC.md]({{REPO}}/blob/main/sim4/SPEC.md), [sim4/README.md]({{REPO}}/blob/main/sim4/README.md).
