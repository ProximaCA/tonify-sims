*🇬🇧 English | [🇷🇺 Русский](CRITIC.ru.md)*

*English translation of [CRITIC.ru.md](CRITIC.ru.md); the Russian original is the source of truth, numbers are identical.*

# CRITIC.md — the red team against our own model (v0.2 → v0.3)

A pass over the entire vault. Format: accusation → verdict → action.

## 1. "Status quo = 0.42 donations/year" — REFUTED, taken off the board
Accusation: the P6 inversion was built on SoundCloud's 29% FPR, but their 29% is the superfans'
share of ROYALTIES (their subscription money under user-centric), not of donations. A category error.
Verdict: the critic is right. The 0.42 figure has been removed from the results; in its place —
measured rate-k benchmarks from adjacent industries (see RESULTS §2). (Throughout, rate k =
payments per superfan per year; "kef" in the Russian original.)

## 2. "Plays/listener = 21.21 per year" — CORRECTED
LFM-1b measures user×artist pairs over the panel's entire history, not per year. 21.2 is an upper
bound. Sensitivity added (8–21). The direction of the error is AGAINST the direct economy (the
"till", *касса* in the original) — conservative: with fewer plays the pool needs even more
listeners, and the direct economy's breakeven drops to 0.38.

## 3. fig2 "the tail is too smooth" — CONFIRMED, fixed
v0.2 produced deterministic fractional superfans. v0.3: binomial sampling —
an artist with 30 listeners now has an honest ~60% chance of zero direct-economy income.

## 4. fig3 "too pretty a straight line" — CLARIFIED
It is the analytical dilution curve F/(1+F) for a fixed pool with no detection,
not a simulation — and it is labeled as such. A caveat has been added: the direct economy has
losses of its own (chargebacks, stolen cards), but they are not smeared across the innocent —
the qualitative difference stands.

## 5. "$1000 Loud & Clear is the artist's pocket" — CAVEAT
It is royalties to the rightsholder. The comparison is valid only in the independent mode
(artist = rightsholder). In the signed mode the in-pocket threshold is even harsher.

## 6. The $5 ticket — CORRECTED TO A RANGE
The only music-specific PWYW experiment: mean €3.10, ≈87% of fixed-price WTP,
and the share of outright refusal RISES (24.4% vs 17.3%) — the social norm crushes the variance.
Ticket sensitivity: $3.1 / $5 / $6.9.

## 7. Superfans 1.7% — CORRECTED TO A RANGE
Under direct measurement the 90-9-1 rule turns out to be 97-2-1 (0.6–0.75% active).
Sensitivity: 0.6% / 1% / 1.7%.

## Red team bottom line
The central conclusion SURVIVED, but became a range: the direct economy's breakeven against the
independent pool — **0.38 … 1.25 … 6.31 payments/superfan/year** (min/median/max across 18
combinations). All three axes of the range are exactly the quantities the MVP measures. None of
them requires a miracle: Twitch's recurring mechanics give a paying fan rate k = 12 automatically.
