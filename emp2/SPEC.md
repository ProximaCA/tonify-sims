# emp2 — cadence of real Telegram payments · SPEC v0.1

Fail-closed measurement slot. Replaces Twitch/Patreon/Tencent as a closer of
the sim1 breakeven range 0.38–1.25–6.31. No payments are invented.

## 0. What this is

A CSV of listener→artist payments on Telegram/TON (or Stars). The script
computes k (payments per superfan-pair per year) and mean check. Until
n ≥ 200 the status is **UNMEASURED** and the range stays open.

This is not a superfan-share measurement: that needs a listener denominator
the payment log does not contain. σ stays the 0.6–1.7% range (CRITIC §7).

## 1. File

`data/pilot_payments.csv` (not in git — may contain user ids). Schema:

| column | type | rule |
|---|---|---|
| ts | ISO-8601 | timezone-aware or UTC |
| user_id | string | opaque |
| artist_id | string | opaque |
| amount_usd | float | > 0 |
| is_recurring | 0 or 1 | 1 = subscription/autopay |

Example header: `data/pilot_payments.example.csv`.

## 2. Estimators

Window W = max(1 day, t_max − t_min).
Pairs = unique (user_id, artist_id).
k = (payments / pairs) × (365 / W).
check = mean(amount_usd).
share_recurring = mean(is_recurring).

## 3. Gates

| Gate | Rule | Fail |
|---|---|---|
| G0 | file missing or n < 200 | status=UNMEASURED, exit 0 (pipeline stays green) |
| G1 | header exactly the five columns | UNMEASURED, note names the defect |
| G2 | n ≥ 200, all rows parse | status=measured, k and check printed |

UNMEASURED is not a failed experiment. Substituting Twitch k=12 for a missing
CSV is a failed experiment — the script refuses to do it.

## 4. Falsifier

If a measured k < 0.38, the direct economy loses to the independent pool on
every corner of the remaining axes (PAPER §6 honest negative).
If 0.38 ≤ k < 6.31, the range narrows but does not close.
If k ≥ 6.31, recurring-or-not, the worst corner of the old range is beaten
by measurement, not by analogy.
