---
description: Payout mechanisms as operators on attention distributions — proofs, simulations, and one measured number.
---

# Tonify Research

Three ways exist to move listener money to artists: **pro-rata** (one pool, paid by share of all plays), **user-centric** (each wallet split only across what its owner played), and **direct** (no pool — fans pay artists). This site is the documentation of a study that treats all three as mathematical operators and asks what each one actually does.

Everything here is reproducible from one public repository. No number on this site is typed by hand: every figure below is extracted from the source files at build time.

## Three findings

**1. Who wins from user-centric is computable in advance.** An artist's user-centric income divided by their pro-rata income equals the mean of `P̄/Pᵤ` over that artist's own audience — an exact identity, verified to {{theory.ident_syn}} on random matrices and to {{moreau.ident}} on real Last.fm logs ({{moreau.artists}} artists). What decides the winner is not niche-ness but how *lightly* and how *unevenly* an artist's listeners listen.

**2. A payout reform cannot touch the label gap.** The income ratio between a signed and an independent artist equals the contract pass-through, whatever the pool rule is. In the simulated world the rule axis moves artist viability ×{{sim1.rule}}; the contract moves it ×{{sim1.contract}}. Six named channels can break this invariance — none of them is the choice of formula.

**3. The direct economy relocates inequality rather than reducing it.** Under its assumptions it does not make the income tail any lighter — the tail index is unchanged — and it adds a mass of artists earning literally zero: at the calibrated superfan share, {{atom.direct}}% of artists get nothing from direct payments. Whether the summary Gini rises or falls turns out to be a property of the world rather than of the mechanism — at zero coupling it barely moves, at the measured coupling direct *lowers* it ({{dw.gini_pool12}} → {{dw.gini_dir12}}). What does not move is the composition: {{dw.zero_dir}}% of artists with an audience earn exactly nothing, while the median among those who do earn is {{dw.med_dir}} of the average income against {{dw.med_pool}} under the pool.

## One measured number

The coupling between how big an artist is and how intensely their audience listens — the dial that decides who gains from a user-centric switch — is **+{{emp1.panel}} ± {{emp1.panel_se}}** on Last.fm panel logs. It is not our discovery: this is the *double jeopardy* law, known since 1969, and our value lands on the Dirichlet-model prediction of +{{corr.habel}} and next to washing powders (+{{corr.sharp}}) and mobile apps (+{{corr.stocchi}}). What is new is turning it into a payout-model parameter — and what that yields:

| Coupling | Artists better off under user-centric | Among the top 0.28% |
|---|---|---|
| 0 (independence — the convenient assumption) | {{cross.g0.all}}% | **{{cross.g0.top}}%** |
| +0.12 (measured centre) | {{cross.g12.all}}% | **{{cross.g12.top}}%** |
| +0.28 (measured head) | {{cross.g28.all}}% | **{{cross.g28.top}}%** |

At the measured coupling, user-centric takes from the head four times harder than the independence assumption predicts.

## What this implies

The three findings above are accounting. The decision they support is a [policy reading](policy/what-next.md), labeled as such: an acceptable reform of the pool formula (four steps, all computed) still leaves the play as the cash register. The unit of value is the fan. What used to be a royalty becomes the price of a thing — a drop, a ticket, patronage. Tonify is the wedge; Unify is the rail. None of that is a theorem.

## Reproduce it in 45 seconds

```bash
git clone {{REPO}} && cd tonify-sims
python3 paper/theory_check.py
```

Every proved claim is re-derived numerically; gates print before conclusions and a failure exits non-zero. The full chain (all four simulations, eighteen figures) is `python3 run_all.py`.

***

[Start here →](start-here.md) · [Repository]({{REPO}}) · [What we retracted](retracted.md)
