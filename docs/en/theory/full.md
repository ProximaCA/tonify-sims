---
description: The paper in full — statements, proofs, assumptions, and the correction ledger.
---

# Full text

Converted from the canonical LaTeX source at build time. The typeset PDF is [paper/THEORY.pdf](https://github.com/ProximaCA/tonify-sims/blob/main/paper/THEORY.pdf); the Russian source of truth, which carries a longer red-team ledger, is [paper/THEORY.md](https://github.com/ProximaCA/tonify-sims/blob/main/paper/THEORY.md) and is served on the Russian variant of this site.

Machine verification of every proved claim lives in [paper/theory_check.py](https://github.com/ProximaCA/tonify-sims/blob/main/paper/theory_check.py) — 200 random matrices for the identity, Monte Carlo for the dominance blockade, the calibrated world for the Gini decomposition.

***

A streaming platform collects listener money and delivers it to artists.
There are essentially three delivery mechanisms. *Pro-rata*: all money
goes into one pool and an artist is paid their share of total platform
plays — how Spotify and nearly every major service works.
*User-centric*: each listener’s wallet is split only across the artists
that listener actually played — the perennially proposed “fairer” model.
*Direct*: no pool at all; money arrives from devoted fans (donations,
artist subscriptions), as on Patreon or Twitch. On top of any mechanism
may sit a label contract taking the lion’s share. This paper treats the
three mechanisms as operators: input — the table of “who played whom how
many times” over a period; output — each artist’s income over the same
period.

Four questions are answered. *First*: who gains from a
pro-rata $$\to$$ user-centric switch, and is it predictable in advance
(Theorem 1: audience listening intensity decides, by an exact formula)?
*Second*: can a pool-rule reform close the gap between a signed and an
independent artist (Lemma 2: the income gap — never; the
minimum-viable-audience gap — sometimes)? *Third*: does the direct
economy reduce top-end concentration (it does not: it preserves the
upper tail and adds a mass of exact zeros at the bottom — inequality is
relocated, not reduced)? *Fourth*: is direct income more reliable than
the pool (on small audiences it is a lottery, and no parameter values
make it unconditionally better — Theorem 4)?

*What counts as an answer*: a proved statement under explicitly listed
assumptions, plus machine verification — every identity and bound is
recomputed by a deterministic script whose numbers are quoted in the
text. Every claim carries one of three statuses: proved, refuted by
counterexample, or conjecture. All four lemmas survived two adversarial
red-team passes that did find errors — the correction history is
Section 5. *Scope*: accounting statics at a fixed play matrix;
equilibrium effects (a rule change altering behavior and hence the
matrix) are outside and listed as open. The italicized paragraphs (“Why
this matters” / “What it says”) form a complete non-technical route;
proofs are set in small type.

## Conceptual formulation

*Entities*: artist (payee); listener (paying subscriber); the
artist–listener pair (active if played at least once in the period); the
play (one stream — the primitive cell); the wallet (a subscriber’s net
contribution); the pool (sum of wallets; exists only under pool
mechanisms); the contract (a post-rule multiplier); the superfan (an
audience member paying directly; direct economy only); the gift (one
direct payment; a superfan makes several per period).

*Primary vs derived vs assumed*: the play table over a period is the
single primary object (a platform log, or a generated matrix); listener
intensity, artist plays, audience and streams are measured from it;
platform averages and per-artist audience statistics are derived
arithmetic; model assumptions (equal wallets, the direct-economy
probability model, contract multiplicativity, tail class of audiences)
are collected in Section 3.3.

*“Artist popularity”* is not a latent parameter: audience $$A_i$$ and
streams $$s_i$$ are measured properties of one specific play matrix over
one period. In the synthetic world sim4 they are induced by a generative
model calibrated to external anchors — same status: properties of the
generated matrix. *The fork carried through the whole paper*: Lemmas
L1–L4 (Section 3.4) are statements about ANY fixed play matrix,
independent of how it arose; the sim4 generator (Section 4.1) produces
one concrete matrix so that identities can be machine-checked at scale.
No proof uses the generator. Prior art: the type-model crossover belongs
to Alaei, Makhdoumi, Malekian & Pekeč (*Mgmt. Sci.* 2022; their notation
is mapped to ours in
Table <a href="#tab:notation" data-reference-type="ref"
data-reference="tab:notation">1</a>); budget balance to Bergantiños &
Moreno-Ternero (2025); the tail machinery is cited from Breiman (1965),
Jessen & Mikosch (2006), Faÿ et al. (2006), Robert & Segers (2008),
Denisov–Foss–Korshunov (2010), Maulik–Resnick–Rootzén (2002); what is
new here: the general-matrix identity with the AM–HM frame, the Jensen
dispersion premium, the kernel coincidence criterion, the invariance
formalization, and the distributional direct-vs-pool comparison.

## Mathematical formulation

### Notation

<table id="tab:notation">
<caption>Notation. Status: M = measured, D = derived, A = assumed, P =
model parameter.</caption>
<thead>
<tr>
<th style="text-align: left;">Symbol</th>
<th style="text-align: left;">Type / range</th>
<th style="text-align: left;">Verbal definition</th>
<th style="text-align: left;">Period / units</th>
<th style="text-align: left;">Status</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;">Symbol</td>
<td style="text-align: left;">Type / range</td>
<td style="text-align: left;">Verbal definition</td>
<td style="text-align: left;">Period / units</td>
<td style="text-align: left;">Status</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>i</em></span>, <span
class="math inline"><em>N</em></span></td>
<td style="text-align: left;">index; finite set</td>
<td style="text-align: left;">artist; set (and number) of artists</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">M</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>u</em></span>, <span
class="math inline"><em>U</em></span></td>
<td style="text-align: left;">index; finite set</td>
<td style="text-align: left;">listener; set (and number) of
listeners</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">M</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>p</em></span>, <span
class="math inline"><em>p</em><sub><em>i</em><em>u</em></sub></span></td>
<td style="text-align: left;"><span
class="math inline">ℤ<sub>+</sub><sup><em>N</em> × <em>U</em></sup></span></td>
<td style="text-align: left;">play matrix; plays of pair <span
class="math inline">(<em>i</em>, <em>u</em>)</span></td>
<td style="text-align: left;">period (year); plays</td>
<td style="text-align: left;">M</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>P</em><sub><em>u</em></sub></span></td>
<td style="text-align: left;">integer <span
class="math inline"> ≥ 1</span> (A1)</td>
<td style="text-align: left;">listener <span
class="math inline"><em>u</em></span>’s intensity: <span
class="math inline">∑<sub><em>i</em></sub><em>p</em><sub><em>i</em><em>u</em></sub></span></td>
<td style="text-align: left;">year; plays</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>P</em><sub><em>i</em></sub></span></td>
<td style="text-align: left;">integer <span
class="math inline"> ≥ 0</span></td>
<td style="text-align: left;">artist <span
class="math inline"><em>i</em></span>’s plays: <span
class="math inline">∑<sub><em>u</em></sub><em>p</em><sub><em>i</em><em>u</em></sub></span></td>
<td style="text-align: left;">year; plays</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>T</em></span></td>
<td style="text-align: left;">integer <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">total platform plays: <span
class="math inline">∑<sub><em>u</em></sub><em>P</em><sub><em>u</em></sub> = ∑<sub><em>i</em></sub><em>P</em><sub><em>i</em></sub></span></td>
<td style="text-align: left;">year; plays</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>P̄</em></span></td>
<td style="text-align: left;">real <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">mean intensity <span
class="math inline"><em>T</em>/<em>U</em></span></td>
<td style="text-align: left;">year; plays</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>A</em><sub><em>i</em></sub></span></td>
<td style="text-align: left;">integer <span
class="math inline"> ≥ 0</span></td>
<td style="text-align: left;">audience: number of <span
class="math inline"><em>u</em></span> with <span
class="math inline"><em>p</em><sub><em>i</em><em>u</em></sub> &gt; 0</span></td>
<td style="text-align: left;">year; listeners</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>s</em><sub><em>i</em></sub></span></td>
<td style="text-align: left;">real <span
class="math inline"> ≥ 0</span></td>
<td style="text-align: left;">artist streams (sim worlds: target yearly
volume)</td>
<td style="text-align: left;">year; plays</td>
<td style="text-align: left;">M / P</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>W</em></span>, <span
class="math inline"><em>W</em><sub><em>u</em></sub></span></td>
<td style="text-align: left;">real <span
class="math inline"> &gt; 0</span>; <span
class="math inline"> ≥ 0</span></td>
<td style="text-align: left;">wallet (net subscriber contribution);
unequal-wallet version</td>
<td style="text-align: left;">year; $</td>
<td style="text-align: left;">A (A2)</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>R</em></span></td>
<td style="text-align: left;">real <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">the pool: <span
class="math inline"><em>U</em> ⋅ <em>W</em></span></td>
<td style="text-align: left;">year; $</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>w</em><sub><em>u</em></sub><sup><em>i</em></sup></span></td>
<td style="text-align: left;">probability vector</td>
<td style="text-align: left;">listener <span
class="math inline"><em>u</em></span>’s share of artist <span
class="math inline"><em>i</em></span>’s plays: <span
class="math inline"><em>p</em><sub><em>i</em><em>u</em></sub>/<em>P</em><sub><em>i</em></sub></span></td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>m</em><sub><em>i</em></sub></span>, <span
class="math inline"><em>H</em><sub><em>i</em></sub></span></td>
<td style="text-align: left;">reals <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">arithmetic / harmonic mean audience
intensity under <span
class="math inline"><em>w</em><sup><em>i</em></sup></span></td>
<td style="text-align: left;">year; plays</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline">PR<sub><em>i</em></sub></span></td>
<td style="text-align: left;">real <span
class="math inline"> ≥ 0</span></td>
<td style="text-align: left;">artist <span
class="math inline"><em>i</em></span>’s payout for the period under
pro-rata, in wallet units ($)</td>
<td style="text-align: left;">year; $</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline">UC<sub><em>i</em></sub></span></td>
<td style="text-align: left;">real <span
class="math inline"> ≥ 0</span></td>
<td style="text-align: left;">artist <span
class="math inline"><em>i</em></span>’s payout for the period under
user-centric, in wallet units ($)</td>
<td style="text-align: left;">year; $</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>D</em><sub><em>i</em></sub></span>, <span
class="math inline"><em>Y</em><sub><em>A</em></sub></span></td>
<td style="text-align: left;">random <span
class="math inline"> ≥ 0</span></td>
<td style="text-align: left;">artist <span
class="math inline"><em>i</em></span>’s direct-economy payout for the
period, $ (<span
class="math inline"><em>Y</em><sub><em>A</em></sub></span>: at audience
<span class="math inline"><em>A</em></span>)</td>
<td style="text-align: left;">year; $</td>
<td style="text-align: left;">model</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>S</em><sub><em>i</em></sub></span></td>
<td style="text-align: left;">random, <span
class="math inline">Bin(<em>A</em><sub><em>i</em></sub>, <em>σ</em>)</span></td>
<td style="text-align: left;">number of superfans of artist <span
class="math inline"><em>i</em></span></td>
<td style="text-align: left;">year; people</td>
<td style="text-align: left;">model</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>σ</em></span></td>
<td style="text-align: left;">real <span
class="math inline"> ∈ (0, 1)</span></td>
<td style="text-align: left;">superfan share: probability a listener
pays directly</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">A (0.017)</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>k</em></span></td>
<td style="text-align: left;">integer <span
class="math inline"> ≥ 1</span></td>
<td style="text-align: left;">gifts per superfan per period</td>
<td style="text-align: left;">year; payments</td>
<td style="text-align: left;">A (4)</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>G</em></span>, <span
class="math inline"><em>G</em><sub><em>f</em><em>t</em></sub></span>,
<span class="math inline"><em>ḡ</em></span></td>
<td style="text-align: left;">random <span
class="math inline"> &gt; 0</span>; real</td>
<td style="text-align: left;">gift size; gift <span
class="math inline"><em>t</em></span> of fan <span
class="math inline"><em>f</em></span>; mean gift <span
class="math inline">𝔼<em>G</em></span></td>
<td style="text-align: left;">$</td>
<td style="text-align: left;">A (lognormal; <span
class="math inline"><em>ḡ</em> = 6.886</span>)</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>τ</em></span></td>
<td style="text-align: left;">real <span
class="math inline"> ∈ (0, 1]</span></td>
<td style="text-align: left;">artist’s share of a gift</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">A (0.80)</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>ρ</em></span></td>
<td style="text-align: left;">real <span
class="math inline"> ∈ (0, 1]</span></td>
<td style="text-align: left;">contract pass-through to a signed
artist</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">D (0.06772)</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>F</em></span>, <span
class="math inline"><em>F</em><sub><em>i</em></sub>(<em>p</em>)</span></td>
<td style="text-align: left;">operator</td>
<td style="text-align: left;">arbitrary pool rule; its payout to artist
<span class="math inline"><em>i</em></span></td>
<td style="text-align: left;">year; $</td>
<td style="text-align: left;">model</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>θ</em></span></td>
<td style="text-align: left;">real <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">payout threshold ($13 Stars)</td>
<td style="text-align: left;">$</td>
<td style="text-align: left;">P</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>A</em><sub>0</sub></span></td>
<td style="text-align: left;">integer <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">boost threshold in the artist-centric
counterexample (15 000)</td>
<td style="text-align: left;">listeners</td>
<td style="text-align: left;">P</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>V</em></span></td>
<td style="text-align: left;">real <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">target yearly income defining MVA
($1 200/yr)</td>
<td style="text-align: left;">year; $</td>
<td style="text-align: left;">P</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline">MVA<sub><em>s</em></sub></span>, <span
class="math inline">MVA<sub><em>ι</em></sub></span></td>
<td style="text-align: left;">integers <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">minimum viable audience (signed /
independent)</td>
<td style="text-align: left;">listeners</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>c</em></span>, <span
class="math inline">rate</span></td>
<td style="text-align: left;">reals <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">pool rate per listener <span
class="math inline"><em>c</em> = PL ⋅ rate</span>; external per-stream
anchor</td>
<td style="text-align: left;">$/listener/yr; $/play</td>
<td style="text-align: left;">D / M</td>
</tr>
<tr>
<td style="text-align: left;"><span class="math inline">PL</span></td>
<td style="text-align: left;">real <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">plays per active pair (21.21, LFM-1b,
caveat CRITIC §2)</td>
<td style="text-align: left;">year; plays/pair</td>
<td style="text-align: left;">M</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>X</em><sub><em>A</em></sub></span></td>
<td style="text-align: left;">real <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">pool income at audience <span
class="math inline"><em>A</em></span>: <span
class="math inline"><em>c</em><em>A</em></span> (deterministic)</td>
<td style="text-align: left;">year; $</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>d</em><sup>*</sup></span></td>
<td style="text-align: left;">real <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">direct-vs-pool breakeven: <span
class="math inline">PL ⋅ rate/(<em>σ</em><em>ḡ</em><em>τ</em>)</span>
payments/superfan/yr</td>
<td style="text-align: left;">payments/yr</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>φ</em>(<em>t</em>)</span></td>
<td style="text-align: left;">function, <span
class="math inline"><em>t</em> &gt; 0</span></td>
<td style="text-align: left;">gift Laplace transform <span
class="math inline">𝔼<em>e</em><sup>−<em>t</em><em>τ</em><em>G</em></sup> &lt; 1</span></td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>α</em></span>, <span
class="math inline"><em>α</em><sub><em>G</em></sub></span></td>
<td style="text-align: left;">reals</td>
<td style="text-align: left;">tail index of audiences; of gifts</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">A (1.4) / M</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>L</em>(<em>x</em>)</span></td>
<td style="text-align: left;">function</td>
<td style="text-align: left;">slowly varying part of <span
class="math inline">ℙ(<em>A</em> &gt; <em>x</em>) = <em>x</em><sup>−<em>α</em></sup><em>L</em>(<em>x</em>)</span></td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">A</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>M</em><sub><em>i</em></sub></span>, <span
class="math inline"><em>m</em><sup>*</sup></span></td>
<td style="text-align: left;">random <span
class="math inline"> ∈ (0, 1]</span>; real</td>
<td style="text-align: left;">UC multiplier <span
class="math inline">𝔼<sub><em>w</em><sup><em>i</em></sup></sub>[1/<em>P</em><sub><em>u</em></sub>]</span>;
its tail limit in (C)</td>
<td style="text-align: left;">1/plays</td>
<td style="text-align: left;">D / A</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>q</em></span>, <span
class="math inline"><em>q</em><sub><em>m</em></sub></span></td>
<td style="text-align: left;">reals <span
class="math inline"> ∈ [0, 1)</span></td>
<td style="text-align: left;">zero mass of direct <span
class="math inline">𝔼[(1 − <em>σ</em>)<sup><em>A</em></sup>]</span>;
measured zero share</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">D / M</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>G</em><sub>pool</sub></span>, <span
class="math inline"><em>G</em><sub>direct</sub></span>, <span
class="math inline"><em>G</em><sup>+</sup></span></td>
<td style="text-align: left;">reals <span
class="math inline"> ∈ [0, 1]</span></td>
<td style="text-align: left;">Gini of pool incomes; of direct; among
positive incomes</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>n</em></span>, <span
class="math inline"><em>n</em><sup>+</sup></span>, <span
class="math inline"><em>μ</em></span>, <span
class="math inline"><em>μ</em><sup>+</sup></span></td>
<td style="text-align: left;">integers; reals</td>
<td style="text-align: left;">artist counts (all / positive-income);
mean incomes (Gini decomposition)</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>δ</em><sub>0</sub></span>, <span
class="math inline"><em>F</em><sup>+</sup></span>, <span
class="math inline"><em>F</em><sub><em>X</em></sub></span>, <span
class="math inline"><em>F</em><sub><em>Y</em></sub></span></td>
<td style="text-align: left;">distributions / CDFs</td>
<td style="text-align: left;">point mass at zero; CDF of positive part;
CDFs of <span
class="math inline"><em>X</em><sub><em>A</em></sub></span>, <span
class="math inline"><em>Y</em><sub><em>A</em></sub></span></td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">notation</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline">RV(<em>α</em>)</span>, <span
class="math inline"><em>o</em><sub><em>p</em></sub>(1)</span></td>
<td style="text-align: left;">classes</td>
<td style="text-align: left;">regular variation of index <span
class="math inline"><em>α</em></span>; vanishing in probability</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">notation</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>ℓ</em><sub><em>i</em></sub></span>, <span
class="math inline"><em>Ã</em><sub><em>i</em></sub></span></td>
<td style="text-align: left;">real <span
class="math inline"> ≥ 1</span>; integer</td>
<td style="text-align: left;">sim4 target listeners <span
class="math inline">max (1, <em>s</em><sub><em>i</em></sub>/PL)</span>;
realized audience</td>
<td style="text-align: left;">year; listeners</td>
<td style="text-align: left;">D (sim4)</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>K</em><sub><em>u</em></sub></span></td>
<td style="text-align: left;">integer <span
class="math inline"> ∈ [1, 2000]</span></td>
<td style="text-align: left;">sim4 listener’s yearly playlist size</td>
<td style="text-align: left;">year; artists</td>
<td style="text-align: left;">A (LN(<span
class="math inline">ln 12</span>, 1.0))</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>γ</em></span>, <span
class="math inline"><em>Ā</em><sub><em>g</em></sub></span></td>
<td style="text-align: left;">real; real <span
class="math inline"> &gt; 0</span></td>
<td style="text-align: left;">sim4 intensity–size coupling dial <span
class="math inline">{−0.3, 0, +0.3}</span>; geometric-mean audience</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">P / D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>U</em><sub>sil</sub></span>, <span
class="math inline"><em>U</em><sub>act</sub></span>, <span
class="math inline"><em>U</em><sub>tot</sub></span></td>
<td style="text-align: left;">integers</td>
<td style="text-align: left;">silent, active, all subscribers (without
A1)</td>
<td style="text-align: left;">people</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>ε</em></span>, <span
class="math inline"><em>a</em></span>, <span
class="math inline"><em>t</em></span>, <span
class="math inline"><em>x</em></span>, <span
class="math inline"><em>z</em></span></td>
<td style="text-align: left;">reals</td>
<td style="text-align: left;">local variables of limits and
integrals</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">notation</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>ρ</em><sub>eff</sub></span></td>
<td style="text-align: left;">real <span
class="math inline"> ∈ (0, 1]</span></td>
<td style="text-align: left;">effective pass-through under
component-heterogeneous contracts: <span
class="math inline">∑<sub><em>m</em></sub><em>ρ</em><sub><em>m</em></sub><em>w</em><sub><em>i</em><em>m</em></sub>(<em>F</em>)</span></td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">D</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>Δ</em></span></td>
<td style="text-align: left;">operator</td>
<td style="text-align: left;">change of a quantity (e.g. <span
class="math inline"><em>Δ</em></span>Gini pool<span
class="math inline">→</span>direct)</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">notation</td>
</tr>
<tr>
<td style="text-align: left;"><span class="math inline">Bin</span>,
LogNormal, <span class="math inline">corr</span></td>
<td style="text-align: left;">standard</td>
<td style="text-align: left;">binomial and lognormal laws; Pearson
correlation</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">notation</td>
</tr>
<tr>
<td colspan="5" style="text-align: left;"><em>Foreign notation (Alaei et
al. 2022 type model) and dictionary to ours:</em></td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>q</em><sub><em>i</em></sub></span>, <span
class="math inline"><em>λ</em><sub><em>i</em></sub></span></td>
<td style="text-align: left;">real; real</td>
<td style="text-align: left;">mass and intensity of listener type <span
class="math inline"><em>i</em></span> <span class="math inline">↔︎</span>
our group with <span
class="math inline"><em>P</em><sub><em>u</em></sub> = <em>λ</em><sub><em>i</em></sub></span></td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">foreign</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>π</em><sub><em>i</em><em>j</em></sub></span></td>
<td style="text-align: left;">real</td>
<td style="text-align: left;">type <span
class="math inline"><em>i</em></span>’s preference share for artist
<span class="math inline"><em>j</em></span> <span
class="math inline">↔︎</span> the type’s play distribution</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">foreign</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>λ̄</em></span></td>
<td style="text-align: left;">real</td>
<td style="text-align: left;"><span
class="math inline">∑<sub><em>i</em></sub><em>q</em><sub><em>i</em></sub><em>λ</em><sub><em>i</em></sub></span>
<span class="math inline">↔︎</span> our <span
class="math inline"><em>P̄</em></span> on a type population</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">foreign</td>
</tr>
<tr>
<td style="text-align: left;"><span
class="math inline"><em>β</em><sub><em>p</em><em>r</em></sub></span>,
<span
class="math inline"><em>β</em><sub><em>u</em><em>c</em></sub></span></td>
<td style="text-align: left;">reals</td>
<td style="text-align: left;">their budget rates; equality holds by
construction here (one pool <span
class="math inline"><em>R</em></span>)</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">foreign</td>
</tr>
</tbody>
</table>

### The three operators: definitions, domains, edge cases

Payout operators map $$\mathbb{R}_+^{N\times U}\to\mathbb{R}_+^N$$.
*Pro-rata*: $$\mathrm{PR}_i = UW\,P_i/T$$ — artist $$i$$’s payout for
the period in wallet units; defined for $$T>0$$; $$P_i=0\Rightarrow \mathrm{PR}_i=0$$ ($$A_i=0$$ implies $$P_i=0$$). *User-centric*:
$$\mathrm{UC}_i = W\sum_u p_{iu}/P_u$$ — payout in wallet units;
requires $$P_u>0$$ for all paying $$u$$ (Assumption A1);
$$p_{iu}/P_u\le 1$$ always, so $$\mathrm{UC}_i\le W\,A_i$$: no listener,
however light, blows up the payout. *Direct*:
$$D_i=\tau\sum_{f=1}^{S_i}\sum_{t=1}^{k}G_{ft}$$ with
$$S_i\,|\,A_i\sim\mathrm{Bin}(A_i,\sigma)$$, i.i.d. gifts $$G\ge 0$$,
$$\mathbb{E}G=\bar g$$, all moments finite;
$$\mathbb{E}[D_i|A_i]=\tau\sigma k\bar g A_i$$; at $$A_i=0$$,
$$D_i\equiv 0$$; at $$A_i>0$$,
$$\mathbb{P}(D_i=0)\ge(1-\sigma)^{A_i}>0$$ — the atom at zero, the
central object of Section 3.4. *Contract*: a multiplicative layer after
the rule, $$\rho\cdot F_i(p)$$; the payout threshold $$\theta$$ is a
separate logistics layer (accumulation vs annual burn), treated as
breaking channel B3 of Lemma 2.

### Assumptions

- (payer activity) Every paying subscriber listens: $$P_u\ge 1$$. Silent
  payers are excluded from *both* pools; otherwise budget balance fails
  by exactly $$W\cdot U_{\mathrm{sil}}$$ and all ratios acquire the
  factor $$U_{\mathrm{act}}/U_{\mathrm{tot}}$$ (red-team counterexample:
  2 artists $$\times$$ 3 active listeners plus 2 silent give
  $$3/5=0.6$$). *Used by: L1 (all parts), L3 (UC bound).*

- (equal wallets) One subscription price; measured approximation. The
  unequal-wallet generalization preserves the identity’s structure
  (Section 3.4, Theorem 1 discussion). *Used by: L1, L2, L4.*

- (integer plays) $$p\in\mathbb{Z}_+^{N\times U}$$, hence $$1/P_u\le 1$$
  and $$M_i\le 1$$; with real-valued plays the weaker bound
  $$p_{iu}/P_u\le 1$$ survives. *Used by: L3 (one-sided UC tail bound).*

- (fixed matrix; accounting frame) $$p$$ is fixed: no equilibrium,
  pool-size, or welfare claims. *Used by: all lemmas.*

- (direct-economy model) $$S_i|A_i\sim\mathrm{Bin}(A_i,\sigma)$$ with
  $$\sigma\perp A_i$$; gifts i.i.d., all moments finite; $$k$$
  deterministic. *Used by: L3 (direct branch), L4.*

- (multiplicative contract, single $$\rho$$) The contract multiplies the
  payout by a constant $$\rho$$, uniform across income components and
  markets; violations are channels B1, B2, B5. *Used by: L2.*

- (rule applied at artist level) $$F$$ acts at the artist level, the
  contract strictly downstream; domain $$F_i(p)>0$$; violation is
  channel B6. *Used by: L2 (2a).*

- (heavy-tailed audiences) $$\mathbb{P}(A>x)=x^{-\alpha}L(x)$$,
  $$\alpha>1$$ (sim1 world: $$\alpha=1.4$$, gate T3; empirical caveat
  Spierdijk & Voorneveld). *Used by: L3.*

- (tail-conditional concentration; UC branch of L3 only) For every
  $$\varepsilon>0$$,
  $$\mathbb{P}(|M_i-m^\ast|>\varepsilon\,|\,A_i>a)\to 0$$ as
  $$a\to\infty$$, $$m^\ast>0$$. Measurable on full log datasets.

### Lemmas and theorems

The fork of Section 2 stands: everything here is about an arbitrary
fixed play matrix; no proof uses the sim4 generator.

##### L1: the ratio identity.

*Uses assumptions A1, A2, A4.*

**Theorem 1** (Identity). For any artist $$i$$ with $$P_i>0$$, under
equal wallets,

$$
\frac{\mathrm{UC}_i}{\mathrm{PR}_i}
=\mathbb{E}_{w^i}\!\left[\frac{\bar{P}}{P_u}\right],
\qquad w^i_u=\frac{p_{iu}}{P_i}.
$$

*Proof.* $$\mathrm{UC}_i/\mathrm{PR}_i =\bigl(W\sum_u p_{iu}/P_u\bigr)\big/\bigl(UW P_i/T\bigr) =(T/U)\sum_u (p_{iu}/P_i)(1/P_u)=\bar{P}\,\mathbb{E}_{w^i}[1/P_u]$$. ◻

With $$m_i=\mathbb{E}_{w^i}[P_u]$$ (arithmetic) and
$$H_i=1/\mathbb{E}_{w^i}[1/P_u]$$ (harmonic mean of listener intensity
under play weights),

$$
\frac{\mathrm{UC}_i}{\mathrm{PR}_i}=\frac{\bar{P}}{H_i}
=\underbrace{\frac{\bar{P}}{m_i}}_{\text{level}}\cdot
\underbrace{\frac{m_i}{H_i}}_{\text{dispersion}\ \ge 1},
$$

the second factor $$\ge 1$$ by AM–HM, with equality iff $$P_u$$ is
constant on the support of $$w^i$$. Under unequal wallets $$W_u$$ the
identity becomes
$$\mathrm{UC}_i/\mathrm{PR}_i=\mathbb{E}_{w^i}[W_u/P_u]/(\sum_u W_u/T)$$
— same structure, “intensity” replaced by “plays per dollar”.

**Corollary (a)** (Coincidence; the naive converse is false).
$$P_u\equiv\bar{P}$$ implies $$\mathrm{UC}=\mathrm{PR}$$ componentwise.
The converse fails: with one artist and two listeners, $$p=(10,20)$$,
intensities differ yet $$\mathrm{UC}_1=\mathrm{PR}_1=2W$$. Exact
criterion: $$\mathrm{UC}_i=\mathrm{PR}_i$$ for all $$i$$ iff the vector
$$c_u=1/P_u-U/T$$ lies in $$\ker p$$.

**Corollary (b)** (Zero sum).
$$\sum_i \mathrm{UC}_i=\sum_i\mathrm{PR}_i=UW$$: user-centric is a pure
redistribution of the same pool.

**Corollary (c)** (Crossover). $$\mathrm{UC}_i>\mathrm{PR}_i$$ iff
$$H_i<\bar{P}$$. On type populations this reduces to the condition of
Alaei, Makhdoumi, Malekian and Pekeč (*Mgmt. Sci.* 2022, Props. 2, 8):
artist $$j$$ weakly prefers pro-rata iff
$$\sum_i q_i\pi_{ij}(\lambda_i-\bar\lambda)\ge 0$$.

**Corollary (d)** (Dispersion premium). Fix $$m_i=\bar{P}$$. Then
$$\mathrm{UC}_i/\mathrm{PR}_i=m_i/H_i\ge 1$$, with equality iff audience
intensity is degenerate: at the same mean level, *within-audience
dispersion strictly raises* user-centric income.

##### L2: pass-through invariance.

*Uses assumptions A2, A4, A6, A7 (part 2a); A2, A4, A6 and a monotone
income with threshold $$V$$ (part 2b).*

**Lemma 2** (Two-part invariance). *(2a)* For any pool operator $$F$$
*applied at the artist level*, with the multiplicative contract strictly
downstream and on the domain $$F_i(p)>0$$: $$\rho F_i/F_i=\rho$$ — the
signed/independent *income* gap is invariant to the rule (a nonlinear
$$F$$ applied to a licensor’s *catalogue* breaks this). *(2b)* The
*minimum-viable-audience* gap satisfies
$$\mathrm{MVA}_s/\mathrm{MVA}_\iota=1/\rho$$ iff
$$F^{-1}(V/\rho)=F^{-1}(V)/\rho$$; linearity of $$F$$-income in audience
is sufficient but *not* necessary (a strictly increasing log-periodic
$$F$$ is nonlinear yet yields $$1/\rho$$ for all $$V$$). A Deezer-style
$$\times 2$$ boost above a threshold yields $$1/(2\rho)$$ instead
(counterexample in companion code) while the income ratio stays $$\rho$$
pointwise.

##### L3: tail action and the atom at zero.

*Uses assumptions A1, A3, A4, A8; condition (C) — UC branch only; A5 —
direct branch only.*

Let $$\mathbb{P}(A>x)=x^{-\alpha}L(x)$$. PR is linear: index preserved.
UC: $$\mathrm{UC}_i=WP_i\,\mathbb{E}_{w^i}[1/P_u]$$ with bounded
multiplier; under tail-conditional concentration of the multiplier the
index is preserved, and heavier tails are impossible for any dependence.
Direct: binomial thinning plus a light-tailed compound sum preserve
$$\alpha$$ (Jessen–Mikosch 2006, Lem. 3.7; Faÿ et al. 2006;
Denisov–Foss–Korshunov 2010; Breiman 1965 enters only through the
multiplicative contract layer), while
$$\mathbb{P}(D_i=0\,|\,A_i)\ge(1-\sigma)^{A_i}\ge e^{-1}(1-\sigma)$$ for
$$A_i\le 1/\sigma$$: an *atom at zero* on small audiences. With zero
mass $$q$$, $$G_{\mathrm{direct}}=q+(1-q)G^{+}$$: the mechanism
relocates inequality from the intensive to the extensive margin; no
mechanism softens the upper tail.

##### L4: dominance blockade.

*Uses assumptions A2, A4, A5; the anchor
$$c=\mathrm{PL}\cdot\mathrm{rate}$$ (independent-artist comparison).*

Fix $$A$$ with $$(1-\sigma)^A>0$$ and pooled income $$X_A=cA>0$$
(deterministic given $$A$$); $$Y_A=D_A$$ as above.

**Theorem 4** (Full blockade). (i) $$Y_A$$ never first-order
dominates $$X_A$$; (ii) $$Y_A$$ never second-order dominates $$X_A$$,
for any parameters; (iii) $$X_A\succeq_2 Y_A$$ iff
$$\mathbb{E}Y_A\le X_A$$, i.e. iff
$$k\le d^\ast=\mathrm{PL}\cdot\mathrm{rate}/(\sigma\bar g\tau)$$; (iv)
for $$k>d^\ast$$ the pair is incomparable in both orders.

*Proof.* (i) For $$x\in(0,X_A)$$: $$\mathbb{P}(X_A>x)=1$$ while
$$\mathbb{P}(Y_A>x)\le 1-(1-\sigma)^A<1$$. (ii) SSD against degenerate
$$X_A$$ requires $$\int_0^t F_Y\le\max(0,t-X_A)$$; at $$t=X_A$$ the left
side is $$\ge(1-\sigma)^A X_A>0$$. (iii) ($$\Leftarrow$$)
$$\int_0^t F_Y=t-\mathbb{E}\min(Y,t)\ge t-\mathbb{E}Y\ge t-X_A$$ and
$$\ge 0$$. ($$\Rightarrow$$) $$t\to\infty$$ gives
$$\mathbb{E}Y\le X_A$$. (iv) From (i)–(iii). ◻

*Remark 1*. The correct comparison is mean versus risk: for $$k>d^\ast$$
direct pays an expectation premium priced by small-audience lottery
risk;
$$\mathbb{P}(Y_A<X_A)\le\inf_{t>0}e^{tX_A}\bigl(1-\sigma+\sigma\varphi(t)^k \bigr)^A$$ with $$\varphi(t)=\mathbb{E}e^{-t\tau G}<1$$ — exponential
decay in $$A$$. In the companion sim1 calibration at $$A{=}30$$,
$$k{=}4$$: mean advantage $$\times 4$$, yet
$$\mathbb{P}(Y<X)\approx 0.60$$ — and on the full 2M-sample run
$$\mathbb{P}(Y<X)-\mathbb{P}(Y=0)=0$$ to machine precision: losing to
the pool is exactly the zero outcome. Under the contract layer
$$c=\mathrm{PL}\cdot\mathrm{rate}\cdot\rho$$ the threshold scales to
$$\rho\,d^\ast\approx 0.068$$: for a signed artist, direct wins in
expectation already at $$k\ge 1$$.

## Numerical implementation

*Generative model (sim4).* Artist popularity: piecewise $$s_i\sim$$
(lognormal body $$/$$ log-bridge $$/$$ Pareto($$\alpha{=}1.4$$) tail),
calibrated to anchors $$T_1{:}\,87\%$$ of artists below $$10^3$$
streams/yr, $$T_2{:}\,2.6\%$$ above $$225{,}734$$, $$T_3{:}$$ top
$$0.28\%$$ holding $$40$$–$$55\%$$ of streams (gate band; the seed-42
matrix realizes $$40.3\%$$, sim1’s larger world $$44.5\%$$); target
audiences $$\ell_i=s_i/\mathrm{PL}$$, $$\mathrm{PL}=21.21$$ plays per
pair (LFM-1b). Playlist sizes
$$K_u\sim\mathrm{LogNormal}(\ln 12,\,1.0)$$ (assumed; an MVP-measured
dial). Artist selection: exact weighted sampling without replacement,
$$\mathbb{P}(i\in S_u)\propto \ell_i$$ (Gumbel top-$$K_u$$),
i.e. preferential attachment. Pair intensity, three named regimes on one
graph:

$$
\text{(a) ergodic: integer } p_{iu},\ P_u\equiv 2048;\qquad
\text{(b) } p_{iu}=\lceil\mathrm{LN}(\ln 5.16,\,1.676)\rceil
\text{ rescaled to } s_i;\qquad
\text{(c) } p_{iu}\propto \mathrm{LN}\cdot(A_i/\bar A_g)^{\gamma}.
$$

Regime (a) has $$P_u\equiv 2048$$ exactly (a power of two: every
$$p_{iu}/P_u$$ is a dyadic rational, so the control identity is exact in
floating point) and is the control (Corollary (a)); $$\gamma$$ dials the
intensity–size coupling.

*Machine verification* (deterministic, seed 42; PASS/FAIL gates printed
before any conclusion, FAIL exits with code 1): the Theorem-1 identity
and AM–HM decomposition on 200 random matrices (max error
$$8.9\times 10^{-16}$$), on the full 21.8M-pair sim4 matrix
($$7.1\times 10^{-15}$$), and — since August 2026 — on *real* Last.fm
logs (31,040 artists, 1.02M pairs: $$5.8\times 10^{-15}$$, with AM
$$\ge$$ HM holding artist by artist); zero-sum ($$1.8\times 10^{-14}$$);
world anchors T1–T3; the exact-zero control gate
($$\max|\mathrm{UC}/\mathrm{PR}-1|=0$$); the L4 atom at $$A{=}30$$
(0.598 vs theory 0.598, 2M samples) with
$$\mathbb{P}(Y<X)-\mathbb{P}(Y=0)=0$$; the calibrated-world Gini
identity $$q_m+(1-q_m)G^{+}=G_{\mathrm{direct}}=0.973844$$ to machine
zero ($$G_{\mathrm{pool}}=0.972$$; robust to lognormal gifts); both L2
counterexamples ($$\mathrm{MVA}$$ 12 772 / 94 296, ratio $$1/(2\rho)$$;
the log-periodic $$F$$ giving exactly $$1/\rho$$); crossover-sign gate:
zero violations of Corollary (c) across all artists and regimes.

*Reproducibility*: python3/numpy/scipy/matplotlib, no external services.
`git clone https://github.com/ProximaCA/tonify-sims`;
`python3 paper/theory_check.py` (seconds; CHECK 1–6);
`python3 sim4/bipartite_gen.py` ($$\sim$$<!-- -->7 min; gates G1–G3,
exports, figures 15–16); `python3 run_all.py` (everything). All numbers
quoted above are outputs of these scripts.

## Red team: two adversarial passes

Two independent red-team passes attacked every lemma (recompute every
inequality, reproduce every derivation, hunt counterexamples). Pass one:
five attackers, verdict “sound with fixes” in all five zones — nine
confirmed lemma findings and ten consistency findings. Pass two: five
fresh attackers filed 25 accusations, all 25 confirmed by independent
verification. No lemma broke in either pass. Retracted: one inequality
(the atom bound misprint, corrected to $$e^{-1}(1-\sigma)$$), one
concentration bound (Hoeffding, violated $$\sim$$<!-- -->45$$\times$$ by
random gifts; replaced by the Chernoff bound via $$\varphi(t)$$), the
necessity claim “only if linear” in (2b) (log-periodic counterexample;
exact criterion $$F^{-1}(V/\rho)=F^{-1}(V)/\rho$$ installed), and one
simulation narrative (head saturation 5.00 — circular sampling; the real
head has $$\tilde A/\ell=1.08$$). Introduced: load-bearing assumption A1
(silent subscribers), breaking channels B5 and B6, the artist-level
assumption A7. Full protocols live in the working-session journals
outside the repo; the Russian THEORY.md carries the episode-by-episode
narrative.

## Open questions

\(1\) Equilibrium versions of L1/L2 (endogenous $$p$$); does the Jensen
premium survive? (2) The sign of $$\Delta$$Gini pool$$\to$$direct in
general (conjecture: a threshold $$\sigma^\ast(\alpha,k)$$ exists for
the positive-income Gini, never for the full one). (3) Exact
characterization of when UC thins the tail (Maulik–Resnick–Rootzén). (4)
L4 for recurrent $$k$$ with churn (dominance on income flows). (5) An
axiomatic characterization of direct alongside the B&MT axiomatizations
of PR and UC.

## Empirical bridge

Each lemma rests on a measurable quantity: $$k$$ (payments per superfan
per year; benchmarks Twitch 12, Patreon 12, breakeven median 1.25);
$$\sigma(A)$$ (superfan conversion vs audience size — tests A5);
intensity–size coupling across artist sizes (closes condition (C)) —
**now measured**: on Last.fm logs the reduced pair-intensity slope is
$$+0.101\pm0.004$$ overall, $$+0.232$$ at the head, $$+0.023$$ among
beyond-mainstream listeners, decomposing into retention $$+0.254$$ and
an *anti*-coupled per-day rate $$-0.154$$ (companion `emp1`); the gift
tail $$\alpha_G$$ (whales vs attention regime); $$\rho(F)$$
(pass-through endogeneity, channel B1 — the Deezer artist-centric switch
is a natural experiment); the threshold $$\theta$$ and its censoring
mode (channel B3).
