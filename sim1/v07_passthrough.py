# -*- coding: utf-8 -*-
"""v0.7 pass-through sensitivity: ρ ∈ {6.772%, 10.6%, 20%} at fixed independent
$4.43/1k. The hero 188,590 lives on one significant digit of $0.0003/stream;
this grid replaces that digit with the two vault-backed corroborations (AEPO-ARTIS
~10.6%, Rose 2024 upper 20%). Analytic — no RNG. fig19."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

P, C, K, Y = "#6B2FFF", "#00D4F5", "#FF4D8D", "#FFD426"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures") + "/"
plt.rcParams.update({
    "figure.facecolor": "#0D0A1A", "axes.facecolor": "#0D0A1A",
    "axes.edgecolor": "#B8C8DC", "axes.labelcolor": "#B8C8DC",
    "text.color": "#B8C8DC", "xtick.color": "#B8C8DC", "ytick.color": "#B8C8DC",
    "font.size": 11,
})

TARGET, PL, RATE_IND, RULE_MULT = 1200.0, 21.21, 4.43 / 1000, 1.34
RHO_DERIVED = 0.0003 / RATE_IND  # 6.77201% — not an input (PAPER CHANGELOG v0.5.1)
GRID = [
    ("derived 6.772%  ($0.0003)", RHO_DERIVED, P),
    ("AEPO-ARTIS ~10.6%",          0.106,       C),
    ("Rose 2024 upper 20%",        0.20,        K),
]

mva_ind = TARGET / (PL * RATE_IND)
rows = []
for name, rho, color in GRID:
    rate_s = RATE_IND * rho
    mva_s = TARGET / (PL * rate_s)
    rows.append((name, rho, rate_s, mva_s, 1.0 / rho, color))

# Gate: derived cell is the published 188,590 (v05 / v04 identity).
got = rows[0][3]
assert abs(got - TARGET / (PL * 0.0003)) < 0.5, f"v07 derived MVA {got:.1f} ≠ 188,590 identity"
print("V07 GATE: derived ρ cell = 188,590 identity — PASS")

print("\nPass-through grid (independent rate fixed at $4.43/1k; signed = ρ × independent):")
print(f"{'ρ source':<32} {'ρ':>8} {'signed $/stream':>16} {'MVA signed':>12} {'×1/ρ':>8} {'vs rule ×1.34':>14}")
for name, rho, rate_s, mva_s, mult, _ in rows:
    print(f"{name:<32} {100*rho:7.3f}% {rate_s:16.6f} {mva_s:12,.0f} {mult:8.2f} {mult/RULE_MULT:14.2f}×")
print(f"{'pro-rata independent (unchanged)':<32} {'—':>8} {RATE_IND:16.6f} {mva_ind:12,.0f} {'1.00':>8}")
print("\nReading: even at Rose's 20% the contract still outweighs the rule "
      f"({rows[2][4]:.1f} vs {RULE_MULT}). Order of the gap survives; 188,590 does not.")
print("Holding $0.0003 fixed and varying ρ would move the *independent* rate instead; "
      "that inverts the two calibration anchors and is not this grid (SPEC sim1 §3.1).")

L19 = {
    "en": dict(xl="label pass-through ρ", yl="Listeners needed for $100/mo (log)",
               t="Signed MVA vs pass-through (independent rate fixed at $4.43/1k)",
               signed="signed (ρ × $4.43/1k)", ind="independent (unchanged)"),
    "ru": dict(xl="лейбловый проход ρ", yl="Слушателей для $100/мес (log)",
               t="MVA подписанного против прохода (инди-ставка фикс. $4.43/1k)",
               signed="signed (ρ × $4.43/1k)", ind="independent (без изменений)"),
}
labels = ["6.772%\nderived", "10.6%\nAEPO-ARTIS", "20%\nRose upper"]
for lang, out in (("en", OUT), ("ru", OUT + "ru/")):
    os.makedirs(out, exist_ok=True)
    L = L19[lang]
    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    x = np.arange(len(rows))
    ax.bar(x, [r[3] for r in rows], color=[r[5] for r in rows], width=0.62, label=L["signed"])
    ax.axhline(mva_ind, color=Y, lw=2, ls="--", label=L["ind"] + f" {mva_ind:,.0f}")
    for i, r in enumerate(rows):
        ax.text(i, r[3] * 0.62, f"{r[3]:,.0f}\n×{r[4]:.1f}", ha="center", va="center",
                fontsize=9, color="#0D0A1A")
    ax.set_yscale("log")
    ax.set_ylim(8_000, 280_000)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel(L["xl"])
    ax.set_ylabel(L["yl"])
    ax.set_title(L["t"])
    ax.grid(alpha=0.15, axis="y")
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(out + "fig19_passthrough.png", dpi=150)
    plt.close(fig)
print("fig19 → figures/fig19_passthrough.png (+ ru)")
