---
description: The payment-cadence slot — a Telegram pilot of ≥200 rows, or the range stays open.
---

# Payment cadence

**The question.** How often does a devoted fan actually pay, on Telegram, in music — not on Twitch, not on Patreon, not in Tencent gifting.

**The rule.** Without ≥200 rows in `data/pilot_payments.csv` the status is UNMEASURED and the 0.38–1.25–6.31 range stays open. Adjacent-industry k=12 is colour, not a closer. The script will not invent payments.

**Run it.** `python3 emp2/cadence_measure.py`

***

{{INCLUDE:emp2/README.md}}
