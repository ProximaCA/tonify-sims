---
description: Слот кефа платежей — пилот Telegram ≥200 строк, иначе диапазон открыт.
---

# Кеф платежей

**Вопрос.** Как часто преданный фан реально платит в Telegram, в музыке — не на Twitch, не на Patreon, не гифтингом Tencent.

**Правило.** Без ≥200 строк в `data/pilot_payments.csv` статус UNMEASURED и диапазон 0,38–1,25–6,31 открыт. Кеф соседних индустрий k=12 — цвет, не closer. Скрипт платежи не выдумывает.

**Запуск.** `python3 emp2/cadence_measure.py`

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
