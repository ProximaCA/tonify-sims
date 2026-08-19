# -*- coding: utf-8 -*-
"""SIM 5 — glue: sim2 cascade → σ conversion → k/check (emp2, not Twitch) → sim3 treasury.

Does not rebuild the 50k graph. Reach-per-seed numbers are the published
sim2 seed=42 table (experiment A, k=2, p=p*=0.15); a gate checks them
against sim2/README.md. Cadence comes from emp2: measured k/check if the
pilot is full, otherwise the open 0.38–1.25–6.31 range — never Twitch k=12.
"""
import os, re, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "emp2"))
from cadence_measure import load_pilot  # noqa: E402

P, C, K, Y = "#6B2FFF", "#00D4F5", "#FF4D8D", "#FFD426"
OUT = os.path.join(ROOT, "figures") + "/"
plt.rcParams.update({
    "figure.facecolor": "#0D0A1A", "axes.facecolor": "#0D0A1A",
    "axes.edgecolor": "#B8C8DC", "axes.labelcolor": "#B8C8DC",
    "text.color": "#B8C8DC", "xtick.color": "#B8C8DC", "ytick.color": "#B8C8DC",
    "font.size": 11,
})

# sim2 experiment A, published table (README.md). B=1 is structurally 0.
B = np.array([1, 2, 5, 10, 20, 50, 100, 200, 500])
RPS_RANDOM = np.array([0.0, 0.0, 0.0, 0.8, 145.5, 322.9, 220.0, 111.2, 46.5])
RPS_HUBS = np.array([0.0, 1856.7, 4509.1, 2269.4, 1150.6, 484.1, 251.0, 130.0, 55.4])
N_GRAPH = 50_000
TARGET = 1200.0          # $100/mo
TAKE = 0.80              # direct artist take (sim1)
FEE = 0.05               # Tonify fee
MEAN_GIFT = float(np.exp(np.log(5.0) + 0.8 ** 2 / 2))  # $6.8859 — sim1 MG
CHECK_LO, CHECK_HI = 3.10, MEAN_GIFT
K_RANGE = (0.38, 1.25, 6.31)
SIGMA_BAND = (0.006, 0.017)
K_MILESTONE = 4.0        # sim1/sim3 working point, not a closer
SIM3_MRR_1M = 1955.0     # 1M MAU × 1.7% × k=4 × $6.9 × 5%


def listeners(b, rps):
    return b * (1.0 + rps)


def sigma_star(L, k, check, take=TAKE, target=TARGET):
    denom = L * k * check * take
    return np.inf if denom <= 0 else target / denom


def gate_frozen_table():
    """The frozen rps numbers must still be the ones printed in sim2/README.md."""
    path = os.path.join(ROOT, "sim2", "README.md")
    text = open(path, encoding="utf-8").read()
    # row B=5: random 0,0 · hubs 4 509,1  (nbsp/narrow spaces possible)
    row = re.search(
        r"\|\s*5\s*\|\s*0,0\s*±\s*0,0\s*\|\s*([\d\s]+),(\d)\s*±",
        text,
    )
    assert row, "sim2/README.md B=5 hubs cell not found — table moved?"
    hubs5 = float(row.group(1).replace(" ", "").replace("\u202f", "") + "." + row.group(2))
    assert abs(hubs5 - 4509.1) < 0.05, f"frozen hubs B=5 {hubs5} ≠ 4509.1"
    print(f"S5 G1: frozen sim2 table B=5 hubs = {hubs5} — PASS")


def main():
    gate_frozen_table()
    pilot = load_pilot()
    print(f"S5 G2: emp2 status = {pilot['status']} (n={pilot['n']}) — PASS")
    if pilot["status"] == "measured":
        k_grid = (("measured", pilot["k"]),)
        check = pilot["check"]
        cadence_src = f"emp2 measured k={pilot['k']}, check=${pilot['check']}"
    else:
        k_grid = (("min 0.38", 0.38), ("median 1.25", 1.25), ("milestone 4", 4.0),
                  ("max 6.31", 6.31))
        check = MEAN_GIFT
        cadence_src = "UNMEASURED — open range 0.38–6.31, check=$6.89 (not Twitch k=12)"
    print(f"  cadence: {cadence_src}")

    L_h = listeners(B, RPS_HUBS)
    L_r = listeners(B, RPS_RANDOM)
    # identity gate on B=5 hubs
    assert abs(L_h[2] - 5 * (1 + 4509.1)) < 1e-9
    print("S5 G3: L = B·(1+rps) identity — PASS")

    print("\nσ* to hit $100/mo from ONE cascade on the N=50k graph "
          f"(take={TAKE}, check=${check:.2f}):")
    print(f"{'B':>4} {'L hubs':>10} {'L random':>10}", end="")
    for name, _ in k_grid:
        print(f" {'σ* hubs '+name:>18} {'σ* rand '+name:>18}", end="")
    print()
    table = []
    for i, b in enumerate(B):
        line = f"{int(b):4d} {L_h[i]:10,.1f} {L_r[i]:10,.1f}"
        rec = {"B": int(b), "L_hubs": float(L_h[i]), "L_rand": float(L_r[i]), "sig": {}}
        for name, k in k_grid:
            sh = sigma_star(L_h[i], k, check)
            sr = sigma_star(L_r[i], k, check)
            rec["sig"][name] = (sh, sr)
            def fmt(x):
                return "      inf" if x == np.inf else f"{100*x:17.3f}%"
            line += f"{fmt(sh)} {fmt(sr)}"
        print(line)
        table.append(rec)

    # Headline cells at B=5, k=4 (or measured), mean check.
    k_head = pilot["k"] if pilot["status"] == "measured" else K_MILESTONE
    sh5 = sigma_star(L_h[2], k_head, check)
    sr5 = sigma_star(L_r[2], k_head, check)
    sh5_lo = sigma_star(L_h[2], k_head, CHECK_LO)
    print(f"\nHeadline B=5, k={k_head}, check=${check:.2f}:")
    print(f"  hubs  L={L_h[2]:,.1f}  σ*={100*sh5:.3f}%   "
          f"(at ${CHECK_LO} check: {100*sh5_lo:.3f}%)")
    print(f"  random L={L_r[2]:,.1f}  σ*={100*sr5:.3f}%")
    print(f"  calibrated σ band: {100*SIGMA_BAND[0]:.1f}–{100*SIGMA_BAND[1]:.1f}%")
    hubs_in = SIGMA_BAND[0] <= sh5 <= SIGMA_BAND[1] or sh5 < SIGMA_BAND[0]
    rand_in = SIGMA_BAND[0] <= sr5 <= SIGMA_BAND[1] or sr5 < SIGMA_BAND[0]
    print("  hubs:  σ* "
          + ("INSIDE/BELOW the band — a fired cascade is enough at this k,c"
             if hubs_in else "ABOVE the band — conversion would have to beat 1.7%"))
    print("  random: σ* "
          + ("INSIDE/BELOW the band" if rand_in else
             "ABOVE the band — random seed at this B does not fund $100/mo"))

    # Worst-corner hubs B=5: k=0.38, check=$3.10
    sh5_worst = sigma_star(L_h[2], 0.38, CHECK_LO)
    print(f"  worst corner (k=0.38, ${CHECK_LO}): hubs σ*={100*sh5_worst:.2f}%  "
          f"{'LOSES to the 1.7% ceiling' if sh5_worst > SIGMA_BAND[1] else 'still inside'}")

    # Platform fee from one cascade vs sim3 $1,955 at 1M MAU.
    # Scale: one cascade covers L/N of a graph; at U=1M with the same density,
    # fee scales by U/N_GRAPH if the product is one such graph of size U.
    sigma_plat = SIGMA_BAND[1]
    annual = L_h[2] * sigma_plat * k_head * check
    fee_month_50k = annual * FEE / 12.0
    fee_month_1M = fee_month_50k * (1_000_000 / N_GRAPH)
    print(f"\nTreasury, one hub-cascade at B=5, σ=1.7%, k={k_head}, check=${check:.2f}, fee 5%:")
    print(f"  on the 50k graph: ${fee_month_50k:,.2f}/mo")
    print(f"  scaled to 1M MAU (same density): ${fee_month_1M:,.2f}/mo  "
          f"(sim3 full-MAU milestone formula: ${SIM3_MRR_1M:,.0f}/mo)")
    print("  sim3 assumes every MAU is in the donating pool; sim5 donates only "
          "from cascade listeners. The ratio is coverage L/N.")

    # fig20 — σ*(B) hubs vs random at the working k, plus the σ band.
    L20 = {
        "en": dict(xl="seeding budget B (log)", yl="σ* to hit $100/mo (log)",
                   t="Conversion needed after a cascade — hubs vs random",
                   hubs=f"hubs, k={k_head:g}, check=${check:.2f}",
                   rand=f"random, k={k_head:g}",
                   band="calibrated σ 0.6–1.7%"),
        "ru": dict(xl="бюджет посева B (log)", yl="σ* для $100/мес (log)",
                   t="Нужная конверсия после каскада — хабы против random",
                   hubs=f"хабы, k={k_head:g}, чек ${check:.2f}",
                   rand=f"random, k={k_head:g}",
                   band="калиброванная σ 0,6–1,7%"),
    }
    sig_h = np.array([sigma_star(L_h[i], k_head, check) for i in range(len(B))])
    sig_r = np.array([sigma_star(L_r[i], k_head, check) for i in range(len(B))])
    # B=1 is inf-ish (L=1); start plot at B=2
    m = B >= 2
    for lang, out in (("en", OUT), ("ru", OUT + "ru/")):
        os.makedirs(out, exist_ok=True)
        L = L20[lang]
        fig, ax = plt.subplots(figsize=(8.8, 5.4))
        ax.plot(B[m], 100 * sig_h[m], color=P, lw=2.8, marker="o", label=L["hubs"])
        ax.plot(B[m], 100 * sig_r[m], color=K, lw=2.8, marker="o", label=L["rand"])
        ax.axhspan(100 * SIGMA_BAND[0], 100 * SIGMA_BAND[1], color=Y, alpha=0.18, label=L["band"])
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel(L["xl"])
        ax.set_ylabel(L["yl"])
        ax.set_title(L["t"])
        ax.grid(alpha=0.15)
        ax.legend(frameon=False, fontsize=9)
        fig.tight_layout()
        fig.savefig(out + "fig20_glue_sigma.png", dpi=150)
        plt.close(fig)
    print("fig20 → figures/fig20_glue_sigma.png (+ ru)")

    print("\nFalsifier: if even hub B=5 at the *best* open corner "
          "(k=6.31, check=$6.89, σ=1.7%) cannot hit $100/mo — GTM+econ jointly fail.")
    sh_best = sigma_star(L_h[2], 6.31, MEAN_GIFT)
    print(f"  that σ* = {100*sh_best:.3f}%  "
          f"{'FAILS the joint claim' if sh_best > SIGMA_BAND[1] else 'does not fire — cascade is large enough at the best corner'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
