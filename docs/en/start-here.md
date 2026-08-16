# Start here

## How to read this

The study has three layers, and you can stop at any of them.

**Plain language.** [Results in plain language](theory/plain.md) states what each of the four lemmas means for an artist, with no formulas. That page is generated from the italicised route inside the paper itself, so it cannot drift from the mathematics it summarises.

**The paper.** [Full text](theory/full.md) carries the statements, proofs, assumptions, and the correction ledger. The canonical version is English; the Russian variant of this site carries the longer source text.

**The code.** Every claim has an executable check. [Simulations](simulations/sim1.md) documents what each simulation asks, what gates it must pass, and how to run it.

## Proved, measured, open

**Proved** — statements about any fixed play matrix, independent of how the data arose: the ratio identity and its four corollaries (L1), pass-through invariance with its exact criterion (L2), tail preservation and the atom at zero (L3), the full stochastic-dominance blockade (L4). Each was attacked twice by an adversarial red team that did find errors; the retractions are on [this page](retracted.md).

**Measured** — one quantity, on public Last.fm logs: the intensity-size coupling, +0.101 overall, +0.232 at the head, +0.023 among beyond-mainstream listeners. Details and caveats: [Measurement](measurement/gamma.md). Whether anyone measured it before us: [Prior art](measurement/prior-art.md) — the answer is yes, repeatedly, since 1969.

**Open** — five questions we did not close: equilibrium versions of L1/L2 (the matrix itself moves when the rule changes), the sign of the Gini difference in general, the exact condition under which user-centric thins the tail, dominance for recurrent payments with churn, and an axiomatic characterisation of the direct mechanism.

## What this study is not

It is not a product pitch and not a proposal. It is accounting statics: the play matrix is held fixed and the operators are compared on it. Every equilibrium effect — behaviour changing because the rule changed — is outside the frame and listed as open. Numbers from the simulated world are calibration, not forecast; the one empirical number is dated (Last.fm, 2005–2014) and its sign is domain-bounded, as [Prior art](measurement/prior-art.md) shows.

## Conventions

Gates print **before** conclusions, and a failed gate exits non-zero — a run that fails cannot report results. Seeds are fixed (42). Every status is one of three: proved, refuted by counterexample, or conjecture. When something we published turned out wrong, it is retracted in the open, on [its own page](retracted.md), not in a footnote.
