#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SIM 6 — Direct + guaranteed discovery floor.

Y_i = D_i + B · 1{A_i ≥ A_min} A_i^β / Σ_j 1{A_j ≥ A_min} A_j^β

Not a fourth pure mechanism and not sold as direct. Attacks L4's zero atom
among eligible artists. Gates print BEFORE conclusions; FAIL = exit 1.
World: sim1 N=200,000 seed=42. fig21–fig22.
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "figures") + "/"
P, C, K, Ycol = "#6B2FFF", "#00D4F5", "#FF4D8D", "#FFD426"
plt.rcParams.update({
    "figure.facecolor": "#0D0A1A", "axes.facecolor": "#0D0A1A",
    "axes.edgecolor": "#B8C8DC", "axes.labelcolor": "#B8C8DC",
    "text.color": "#B8C8DC", "xtick.color": "#B8C8DC", "ytick.color": "#B8C8DC",
    "font.size": 11,
})

SEED, N = 42, 200_000
TARGET, PL, RATE = 1200.0, 21.21, 4.43 / 1000
RHO = 0.0003 / RATE
SF, KDON, TAKE = 0.017, 4, 0.80
MU_G, SG_G = np.log(5.0), 0.8
G_BAR = float(np.exp(MU_G + SG_G ** 2 / 2))
MU = TAKE * SF * KDON * G_BAR          # E[D | A] / A
BETA_HEAD, AMIN_HEAD = 0.5, 10
BR_GRID = (0.0, 0.01, 0.02, 0.05, 0.10, 0.20)
AMIN_GRID = (1, 2, 3, 10, 30, 100)
N_FAKE = (1_000, 10_000, 50_000)

rng = np.random.default_rng(SEED)
FAILS = []


def gate(name, val, lo, hi, fmt="{:.6g}"):
    ok = lo <= val <= hi
    print(f"  {'PASS' if ok else 'FAIL'}  {name} = {fmt.format(val)} (допуск [{lo}; {hi}])")
    if not ok:
        FAILS.append(name)
    return ok


def top_share(x, frac=0.0028):
    x = np.asarray(x, dtype=np.float64)
    s = x.sum()
    if s <= 0:
        return 0.0
    k = max(1, int(round(frac * x.size)))
    return float(np.sort(x)[-k:].sum() / s)


def world():
    share_low, share_top = 0.87, 0.026
    n_low = int(N * share_low)
    n_mid = int(N * (1 - share_low - share_top))
    n_top = N - n_low - n_mid
    low = np.clip(np.exp(rng.normal(np.log(80), 1.4, n_low)), 1, 999)
    mid = np.exp(rng.uniform(np.log(1000), np.log(225_734), n_mid))
    top = 225_734 * (1 + rng.pareto(1.4, n_top))
    streams = np.concatenate([low, mid, top])
    rng.shuffle(streams)
    A = np.maximum(1, (streams / PL).astype(np.int64))
    t1 = float((streams < 1000).mean())
    t2 = float((streams > 225_734).mean())
    t3 = float(np.sort(streams)[-int(N * 0.0028):].sum() / streams.sum())
    return streams, A, t1, t2, t3


def sample_direct(A):
    S = rng.binomial(A, SF)
    tot = S * KDON
    draws = rng.lognormal(MU_G, SG_G, int(tot.sum()))
    return TAKE * np.bincount(np.repeat(np.arange(len(A)), tot),
                              weights=draws, minlength=len(A))


def floor_w(A, A_min, beta):
    elig = A >= A_min
    w = np.zeros(len(A), dtype=np.float64)
    if elig.any():
        num = np.where(elig, np.power(A.astype(np.float64), beta), 0.0)
        z = num.sum()
        if z > 0:
            w = num / z
    return w, elig


def mva_expected(B, A_min, beta, Z, V=TARGET):
    """Smallest integer A with μA + 1{A≥A_min} B A^β / Z ≥ V. B=0 → V/μ."""
    base = int(np.ceil(V / MU))
    if B <= 0 or Z <= 0 or A_min > base:
        return base
    grid = np.arange(A_min, base + 1, dtype=np.float64)
    ey = MU * grid + B * np.power(grid, beta) / Z
    hit = np.where(ey >= V)[0]
    return int(grid[hit[0]]) if hit.size else base


def main():
    streams, A, t1, t2, t3 = world()
    R = float(streams.sum() * RATE)
    D = sample_direct(A)
    mva_ind = TARGET / (PL * RATE)
    mva_signed = TARGET / (PL * RATE * RHO)
    mva_dir = int(np.ceil(TARGET / MU))

    print("=" * 74)
    print("SIM6 · Direct + guaranteed discovery floor · ворота ДО выводов")
    print(f"мир: N={N:,}, ΣA={int(A.sum()):,}, R=${R:,.0f} (инди-пул), "
          f"E[D]={D.mean():.2f}, q_direct={float((D == 0).mean()):.3f}")
    print("-" * 74)

    gate("G0.1 T1 <1000 стримов", t1, 0.86, 0.88, "{:.3f}")
    gate("G0.2 T2 >225734", t2, 0.024, 0.028, "{:.4f}")
    gate("G0.3 T3 топ-0.28%", t3, 0.40, 0.55, "{:.3f}")

    w05, elig05 = floor_w(A, AMIN_HEAD, BETA_HEAD)
    B05 = 0.05 * R
    Y05 = D + B05 * w05
    q_elig = float((Y05[elig05] == 0).mean()) if elig05.any() else 1.0
    gate("G1  q_eligible (B/R=0.05, A_min=10)", q_elig, 0.0, 0.0, "{:.3e}")
    gate("G2  |Σ floor − B| / B", abs(B05 * w05.sum() - B05) / B05, 0.0, 1e-9, "{:.3e}")
    gate("G3  max |Y − D − B w|", float(np.max(np.abs(Y05 - D - B05 * w05))), 0.0, 1e-8, "{:.3e}")
    ts_f = top_share(B05 * w05)
    ts_d = top_share(D)
    gate("G4  top-0.28% floor − top-0.28% D  (<0)", ts_f - ts_d, -1.0, -1e-12, "{:.4f}")
    Z_head = np.power(A[elig05].astype(np.float64), BETA_HEAD).sum() if elig05.any() else 0.0
    gate("G5  MVA(B=0) − MVA direct", mva_expected(0.0, AMIN_HEAD, BETA_HEAD, Z_head) - mva_dir,
         -1, 1, "{:.0f}")

    print("\n## Атом vs A_min (B/R=0.05, β=0.5; среди A_i>0 — здесь все)")
    print(f"{'A_min':>8} {'eligible':>10} {'q_all':>8} {'q_eligible':>12}")
    amin_rows = []
    for amin in AMIN_GRID:
        w, elig = floor_w(A, amin, BETA_HEAD)
        Y = D + B05 * w
        q_all = float((Y == 0).mean())
        qe = float((Y[elig] == 0).mean()) if elig.any() else 1.0
        print(f"{amin:8d} {100*elig.mean():9.1f}% {100*q_all:7.1f}% {100*qe:11.1f}%")
        amin_rows.append((amin, float(elig.mean()), q_all, qe))

    # largest A_min such that q_all ≤ target (smaller A_min ⇒ fewer zeros)
    print("\n## A_min, чтобы q_all ≤ 50% / 25% / 10% (любой B>0; B размер не вяжет атом)")
    for tgt in (0.50, 0.25, 0.10):
        ok = [r[0] for r in amin_rows if r[2] <= tgt]
        label = f"{int(100*tgt)}%"
        if ok:
            print(f"  q_all ≤ {label}: A_min ≤ {max(ok)}  (при A_min=1 атом среди A_i>0 = 0)")
        else:
            print(f"  q_all ≤ {label}: не достигнуто на сетке")

    print("\n## Цена гарантий B/R (A_min=10, β=0.5)")
    print(f"{'B/R':>8} {'q_all':>8} {'q_elig':>8} {'MVA hyb':>10} "
          f"{'Y<0.01μ':>9} {'top D':>8} {'top fl':>8} {'top Y':>8}")
    mu_pool = float((streams * RATE).mean())
    br_rows = []
    w, elig = floor_w(A, AMIN_HEAD, BETA_HEAD)
    Z = np.power(A[elig].astype(np.float64), BETA_HEAD).sum() if elig.any() else 0.0
    for br in BR_GRID:
        B = br * R
        Y = D + B * w
        q_all = float((Y == 0).mean())
        qe = float((Y[elig] == 0).mean()) if elig.any() else 1.0
        mva = mva_expected(B, AMIN_HEAD, BETA_HEAD, Z)
        below = float((Y < 0.01 * mu_pool).mean())
        print(f"{100*br:7.1f}% {100*q_all:7.1f}% {100*qe:7.1f}% {mva:10,d} "
              f"{100*below:8.1f}% {100*top_share(D):7.1f}% {100*top_share(B*w):7.1f}% "
              f"{100*top_share(Y):7.1f}%")
        br_rows.append((br, q_all, qe, mva, below, top_share(Y)))

    n_elig = int(elig.sum())
    print(f"\nB at 5% of R = ${B05:,.0f}; eligible at A_min=10: {n_elig:,}; "
          f"mean floor among eligible = ${B05 / max(n_elig, 1):.2f}")
    print(f"MVA пул independent: {mva_ind:,.0f}   signed: {mva_signed:,.0f}   "
          f"чистый direct: {mva_dir:,d}")
    print("Гибрид signed = independent: B и D не проходят через ρ (L2 на пол не садится).")

    print("\n## Хвост vs β (B/R=0.05, A_min=10)")
    print(f"{'β':>8} {'top-0.28% floor':>16} {'top-0.28% D':>14} {'top-0.28% Y':>14}")
    for beta in (0.25, 0.5, 1.0):
        w_b, _ = floor_w(A, AMIN_HEAD, beta)
        print(f"{beta:8.2f} {100*top_share(B05*w_b):15.1f}% {100*top_share(D):13.1f}% "
              f"{100*top_share(D+B05*w_b):13.1f}%")

    print("\n## Фрод: доля B у n фейковых аккаунтов с A=A_min")
    print(f"{'A_min':>8} {'n fake':>8} {'share of B':>12}")
    fraud_rows = []
    for amin in (1, 10, 30):
        w, elig = floor_w(A, amin, BETA_HEAD)
        Z0 = np.power(A[elig].astype(np.float64), BETA_HEAD).sum() if elig.any() else 0.0
        unit = float(amin) ** BETA_HEAD
        for n in N_FAKE:
            share = n * unit / (Z0 + n * unit) if (Z0 + n * unit) > 0 else 1.0
            print(f"{amin:8d} {n:8,d} {100*share:11.1f}%")
            fraud_rows.append((amin, n, share))

    # ---- figures ----
    L21 = {
        "en": dict(xl="eligibility threshold A_min", yl="share of artists with Y = 0",
                   t="Discovery floor kills the atom among eligible artists",
                   all="all artists, B/R = 5%", elig="eligible (A ≥ A_min)",
                   base="pure direct (B = 0)"),
        "ru": dict(xl="порог eligibility A_min", yl="доля артистов с Y = 0",
                   t="Discovery floor убивает атом среди eligible",
                   all="все артисты, B/R = 5%", elig="eligible (A ≥ A_min)",
                   base="чистый direct (B = 0)"),
    }
    q0 = float((D == 0).mean())
    xs = [r[0] for r in amin_rows]
    for lang, out in (("en", OUT), ("ru", OUT + "ru/")):
        os.makedirs(out, exist_ok=True)
        L = L21[lang]
        fig, ax = plt.subplots(figsize=(8.6, 5.2))
        ax.axhline(100 * q0, color=K, lw=1.6, ls="--", label=L["base"])
        ax.plot(xs, [100 * r[2] for r in amin_rows], color=P, lw=2.6, marker="o", label=L["all"])
        ax.plot(xs, [100 * r[3] for r in amin_rows], color=C, lw=2.6, marker="s", label=L["elig"])
        ax.set_xlabel(L["xl"]); ax.set_ylabel(L["yl"]); ax.set_title(L["t"])
        ax.set_xticks(xs)
        ax.grid(alpha=0.15); ax.legend(frameon=False, fontsize=9)
        fig.tight_layout()
        fig.savefig(out + "fig21_floor_zeros.png", dpi=150)
        plt.close(fig)
    print("fig21 → figures/fig21_floor_zeros.png (+ ru)")

    L22 = {
        "en": dict(xl="discovery pool B / independent-pool R", yl="Listeners for $100/mo (log)",
                   t="MVA: floor vs pool vs pure direct",
                   hyb="hybrid (A_min=10, β=0.5)",
                   ind="independent pool", sig="signed pool", d="pure direct"),
        "ru": dict(xl="фонд B / инди-пул R", yl="Слушателей для $100/мес (log)",
                   t="MVA: floor против пула и чистого direct",
                   hyb="гибрид (A_min=10, β=0.5)",
                   ind="independent пул", sig="signed пул", d="чистый direct"),
    }
    for lang, out in (("en", OUT), ("ru", OUT + "ru/")):
        os.makedirs(out, exist_ok=True)
        L = L22[lang]
        fig, ax = plt.subplots(figsize=(8.6, 5.2))
        ax.plot([100 * r[0] for r in br_rows], [r[3] for r in br_rows],
                color=P, lw=2.6, marker="o", label=L["hyb"])
        ax.axhline(mva_ind, color=Ycol, lw=1.8, ls="--", label=L["ind"] + f" {mva_ind:,.0f}")
        ax.axhline(mva_signed, color=K, lw=1.6, ls=":", label=L["sig"] + f" {mva_signed:,.0f}")
        ax.axhline(mva_dir, color=C, lw=1.6, ls="-.", label=L["d"] + f" {mva_dir:,.0f}")
        ax.set_yscale("log")
        ax.set_xlabel(L["xl"]); ax.set_ylabel(L["yl"]); ax.set_title(L["t"])
        ax.grid(alpha=0.15); ax.legend(frameon=False, fontsize=8)
        fig.tight_layout()
        fig.savefig(out + "fig22_floor_mva.png", dpi=150)
        plt.close(fig)
    print("fig22 → figures/fig22_floor_mva.png (+ ru)")

    print("\nЧтение: любой B>0 при A_min=1 обнуляет атом среди A_i>0 — цена атома "
          "это eligibility, не размер фонда. B/R двигает MVA и нижние пороги, "
          "и 5–20% пула едва сдвигают MVA, потому что B размазан по всем eligible. "
          "Одноконтактный фрод при β=0.5 крадёт мало (тяжёлый честный Σ A^β); "
          "порог A_min делает каждый фейк дороже, но увеличивает их долю B, "
          "если ферма дотягивает до порога.")
    if FAILS:
        print("МИШЕНЬ ПРОВАЛЕНА:", ", ".join(FAILS))
        sys.exit(1)
    print("SIM6 ворота PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
