---
description: Payout mechanisms as operators on attention distributions — proofs, simulations, and one measured number.
---

# Tonify Research

Three ways exist to move listener money to artists: **pro-rata** (one pool, paid by share of all plays), **user-centric** (each wallet split only across what its owner played), and **direct** (no pool — fans pay artists). This site is the documentation of a study that treats all three as mathematical operators and asks what each one actually does.

Everything here is reproducible from one public repository. No number on this site is typed by hand: every figure below is extracted from the source files at build time.

## Three findings

**1. Who wins from user-centric is computable in advance.** An artist's user-centric income divided by their pro-rata income equals the mean of `P̄/Pᵤ` over that artist's own audience — an exact identity, verified to 8.9e-16 on random matrices and to 5.8e-15 on real Last.fm logs (31 040 artists). What decides the winner is not niche-ness but how *lightly* and how *unevenly* an artist's listeners listen.

**2. A payout reform cannot touch the label gap.** The income ratio between a signed and an independent artist equals the contract pass-through, whatever the pool rule is. In the simulated world the rule axis moves artist viability ×1.34; the contract moves it ×14.8. Six named channels can break this invariance — none of them is the choice of formula.

**3. The direct economy relocates inequality rather than reducing it.** Under its assumptions it does not make the income tail any lighter — the tail index is unchanged — and it adds a mass of artists earning literally zero: at the calibrated superfan share, 75% of artists get nothing from direct payments. Whether the summary Gini rises or falls turns out to be a property of the world rather than of the mechanism — at zero coupling it barely moves, at the measured coupling direct *lowers* it (0.9714 → 0.9651). What does not move is the composition: 73.3% of artists with an audience earn exactly nothing, while the median among those who do earn is 0.124 of the average income against 0.005 under the pool.

## One measured number

The coupling between how big an artist is and how intensely their audience listens — the dial that decides who gains from a user-centric switch — is **+0.101 ± 0.004** on Last.fm panel logs. It is not our discovery: this is the *double jeopardy* law, known since 1969, and our value lands on the Dirichlet-model prediction of +0.1032 and next to washing powders (+0.1028) and mobile apps (+0.110). What is new is turning it into a payout-model parameter — and what that yields:

| Coupling | Artists better off under user-centric | Among the top 0.28% |
|---|---|---|
| 0 (independence — the convenient assumption) | 37.1% | **33.9%** |
| +0.12 (measured centre) | 45.6% | **8.9%** |
| +0.28 (measured head) | 52.8% | **3.6%** |

At the measured coupling, user-centric takes from the head four times harder than the independence assumption predicts.

## What this implies

The three findings above are accounting. The decision they support is a [policy reading](policy/what-next.md), labeled as such: an acceptable reform of the pool formula (four steps, all computed) still leaves the play as the cash register. The unit of value is the fan. What used to be a royalty becomes the price of a thing — a drop, a ticket, patronage. Tonify is the wedge; Unify is the rail. None of that is a theorem.

## Reproduce it in 45 seconds

```bash
git clone https://github.com/ProximaCA/tonify-sims && cd tonify-sims
python3 paper/theory_check.py
```

Every proved claim is re-derived numerically; gates print before conclusions and a failure exits non-zero. The full chain (five simulations, twenty figures) is `python3 run_all.py`.

***

[Start here →](start-here.md) · [Repository](https://github.com/ProximaCA/tonify-sims) · [What we retracted](retracted.md)
