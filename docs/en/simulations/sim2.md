---
description: How music spreads — complex contagion on a synthetic Telegram-like graph.
---

# sim2 — how music spreads

**The question.** If adoption needs social proof rather than a single exposure, what does that do to reach — and do chat groups change the answer?

**The gates.** A falsifier is built in: if hubs alone reproduced the cascade, the chat layer would be decoration. The pure-hub control is run explicitly and reported whatever it says.

**The frame.** This is a model of a Telegram-like structure, not Telegram data — stated in the repository and repeated here because the distinction is the difference between a simulation and a measurement.

**Run it.** `python3 sim2/tonify_graph_sim.py` (~36 s).

***

### sim2 — how music spreads: complex contagion on a synthetic Telegram-like graph

A 50,000-node Barabási–Albert graph with 3,460 planted overlapping
chat-cliques (a model, not Telegram data). Adoption is complex contagion: a
track converts a listener only after k=2 distinct adopted neighbours. Full
protocol and validation: [sim2 README](https://github.com/ProximaCA/tonify-sims/blob/main/sim2/README.md),
[sim2 SPEC](https://github.com/ProximaCA/tonify-sims/blob/main/sim2/SPEC.md).

**Finding 5 — seeding hubs beats random seeding, on a model.** Top-hub
seeding beats random at every budget B ∈ [2; 500] at p = p* = 0.15 (B=5:
4,509 vs 0 reach-per-seed; B=500: 55.4 vs 46.5), and the verdict survives a
pure-BA-hub control (B=1 is structurally degenerate for complex contagion and
excluded). Chats change the *reliability* of complex contagion, not its
possibility: P_macro = 1.00 / 0.15 / 1.00 (simple on bare BA / complex on
bare BA / complex with chats) ([sim2/README](https://github.com/ProximaCA/tonify-sims/blob/main/sim2/README.md); falsifier
verdict [SPEC](https://github.com/ProximaCA/tonify-sims/blob/main/sim2/SPEC.md) §6; experiment C).

![fig8_reach_per_seed](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig8_reach_per_seed.png)

*fig8 — reach-per-seed by seeding strategy (simulation, 30 runs/point,
mean ± 1 SEM; log x-axis of seeding budget B). Reach-per-seed =
(adopters − B)/B, i.e. organic adoptions per seeded node; the yellow y=0 line
is "seeding without multiplication".*

**Finding 6 — the hub advantage is a small-budget effect.** The hub-vs-random
gap is not a constant premium: at B=5 it is the difference between a cascade
and none (4,509 vs 0 reach-per-seed — random seeds simply fail to ignite
complex contagion), while at B=500 it compresses to +19% (55.4 vs 46.5 — the
converging tails on fig8). Strategy is decisive exactly when the seeding
budget is small; at B ≤ 20 part of the hub win is seed density in general,
and the clean hub effect (+14–19%, up to +27.7% for the top-BA control)
isolates at B ≥ 100 (experiment A; [sim2/README](https://github.com/ProximaCA/tonify-sims/blob/main/sim2/README.md) §4.1 v1.3).

**Finding 7 — the model's critical point is the product's K-factor.** R_eff —
adoptions caused per adoption — crosses 1.0 between p = 0.15 and p = 0.20
(0.891 → 1.354 at k=2): below that per-exposure conversion a seeded track
dies out; above it macro-cascades become near-certain (P_macro 0.500 →
0.775). The model knob p ("a neighbour's adoption converts me") is, in
product terms, the viral K-factor of a share — so the phase boundary at
p* = 0.15 is a measurable product target, not a simulation abstraction: an
MVP that lifts per-exposure conversion past ~0.15–0.20 carries the product
across the cascade threshold (experiment B; fig9).

![fig9_phase_diagram](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig9_phase_diagram.png)

*fig9 — the phase diagram (simulation, 40 runs/point) with analytic
references: complex-contagion critical point p* = 0.15 (grid precision)
against the simple-contagion mean-field 0.018 and the chat-layer upper bound
0.53. P_macro = probability of reaching ≥5% of the graph; R_eff crossing 1.0
between p=0.15 and p=0.20 is the K-factor threshold of Finding 7.*

![fig10_cascade](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig10_cascade.gif)

*fig10 — one complex-contagion cascade spreading through chat cliques
(simulation, a single cascade on a 4,000-node illustrative subgraph, 48.3%
reach, seeded from a single chat). Inline above is the full animation;
direct file: [fig10_cascade.gif](https://github.com/ProximaCA/tonify-sims/blob/main/figures/fig10_cascade.gif)
(2.6 MB, 15 frames, round 0 → 14).*
