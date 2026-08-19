---
description: The payment-cadence slot — a Telegram pilot of ≥200 rows, or the range stays open.
---

# Payment cadence

**The question.** How often does a devoted fan actually pay, on Telegram, in music — not on Twitch, not on Patreon, not in Tencent gifting.

**The rule.** Without ≥200 rows in `data/pilot_payments.csv` the status is UNMEASURED and the 0.38–1.25–6.31 range stays open. Adjacent-industry k=12 is colour, not a closer. The script will not invent payments.

**Run it.** `python3 emp2/cadence_measure.py`

***

Replaces Twitch/Patreon/Tencent as a closer of the sim1 breakeven range
0.38–1.25–6.31. Fail-closed: without ≥200 rows the status is UNMEASURED and
the range stays open. The script will not invent payments and will not
substitute k=12.

```
python3 emp2/cadence_measure.py
```

CSV: `data/pilot_payments.csv` (not in git). Header in
`data/pilot_payments.example.csv`:

```
ts,user_id,artist_id,amount_usd,is_recurring
```

Spec: [SPEC.md](https://github.com/ProximaCA/tonify-sims/blob/main/emp2/SPEC.md). Status written to `emp2/STATUS.json` on every run.
`sim5/glue.py` reads the same loader: measured k/check in, otherwise the open
range — never Twitch.
