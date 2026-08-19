# -*- coding: utf-8 -*-
"""emp2 — payment cadence from a Telegram pilot, not from Twitch.

Fail-closed: without ≥200 rows in data/pilot_payments.csv the cadence is
UNMEASURED. Adjacent-industry k=12 does not close the 0.38–6.31 range.
Does not invent payments. seed is irrelevant — this is a measurement slot.

CSV columns: ts, user_id, artist_id, amount_usd, is_recurring
  ts           ISO-8601
  amount_usd   float > 0
  is_recurring 0/1
"""
import csv, json, os, sys
from datetime import datetime, timezone
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV_PATH = os.path.join(ROOT, "data", "pilot_payments.csv")
STATUS_PATH = os.path.join(HERE, "STATUS.json")
N_MIN = 200
COLS = ("ts", "user_id", "artist_id", "amount_usd", "is_recurring")


def _parse_ts(s):
    s = s.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def load_pilot(path=CSV_PATH):
    """Return a status dict. Never raises on a missing file — that's UNMEASURED."""
    out = {
        "status": "unmeasured",
        "n": 0,
        "n_pairs": 0,
        "n_users": 0,
        "n_artists": 0,
        "window_days": None,
        "k": None,
        "check": None,
        "share_recurring": None,
        "path": os.path.relpath(path, ROOT),
        "n_min": N_MIN,
        "note": "UNMEASURED: data/pilot_payments.csv missing or n<200. "
                "Twitch/Patreon k=12 is adjacent-industry colour, not a closer.",
    }
    if not os.path.isfile(path):
        return out
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or tuple(c.strip() for c in reader.fieldnames) != COLS:
            out["note"] = f"UNMEASURED: header must be {','.join(COLS)} exactly."
            return out
        for i, row in enumerate(reader, 2):
            try:
                ts = _parse_ts(row["ts"])
                amount = float(row["amount_usd"])
                rec = int(row["is_recurring"])
            except (KeyError, ValueError, TypeError) as e:
                out["note"] = f"UNMEASURED: bad row {i}: {e}"
                return out
            if amount <= 0 or rec not in (0, 1):
                out["note"] = f"UNMEASURED: bad row {i}: amount must be >0, is_recurring 0/1."
                return out
            rows.append((ts, row["user_id"], row["artist_id"], amount, rec))
    out["n"] = len(rows)
    if len(rows) < N_MIN:
        out["note"] = (
            f"UNMEASURED: n={len(rows)} < {N_MIN}. "
            "The 0.38–6.31 range stays open; do not substitute Twitch k=12."
        )
        return out
    times = [r[0] for r in rows]
    window = max((max(times) - min(times)).total_seconds() / 86400.0, 1.0)
    pairs = defaultdict(int)
    users, artists, rec_n, amounts = set(), set(), 0, []
    for ts, u, a, amount, rec in rows:
        pairs[(u, a)] += 1
        users.add(u)
        artists.add(a)
        rec_n += rec
        amounts.append(amount)
    payments_per_pair = sum(pairs.values()) / len(pairs)
    k = payments_per_pair * (365.0 / window)
    out.update(
        status="measured",
        n_pairs=len(pairs),
        n_users=len(users),
        n_artists=len(artists),
        window_days=round(window, 2),
        k=round(k, 3),
        check=round(sum(amounts) / len(amounts), 3),
        share_recurring=round(rec_n / len(rows), 4),
        note="measured on the Telegram pilot CSV; superfan share still needs a listener denominator.",
    )
    return out


def main():
    st = load_pilot()
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("EMP2 GATE: cadence measurement")
    print(f"  status: {st['status']}   n={st['n']} (min {N_MIN})")
    if st["status"] == "measured":
        print(f"  k={st['k']} /yr   check=${st['check']}   "
              f"pairs={st['n_pairs']}   window={st['window_days']} d   "
              f"recurring={st['share_recurring']}")
        print("  PASS — range-closer is this k, not Twitch.")
    else:
        print(f"  {st['note']}")
        print("  PASS (fail-closed): UNMEASURED is a valid state; pipeline stays green.")
        print("  RETRACTED as closer: Twitch/Patreon k=12, Tencent gifting multiplier.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
