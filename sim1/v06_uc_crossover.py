# -*- coding: utf-8 -*-
"""v0.6 UC-CROSSOVER (external review §2): user-centric как функция интенсивности
слушателя u, а не скаляр. Сетка u × PAID_SHARE, точка безразличия u*, fig14.
RNG-порядок: [5k,10k,20k] — байт-в-байт поток v04/v05 (канон 4,807/9,512/18,341),
затем [2k,50k], затем уточняющие [14k,15k]. PAID_SHARE — скаляр вне MC:
uc(u,ps) = uc(u,0.40)·ps/0.40 (см. sim1/SPEC.md §3.2)."""
import os, math
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rng = np.random.default_rng(42)
P,C,K,Y = "#6B2FFF","#00D4F5","#FF4D8D","#FFD426"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures") + "/"
plt.rcParams.update({"figure.facecolor":"#0D0A1A","axes.facecolor":"#0D0A1A","axes.edgecolor":"#B8C8DC",
 "axes.labelcolor":"#B8C8DC","text.color":"#B8C8DC","xtick.color":"#B8C8DC","ytick.color":"#B8C8DC","font.size":11})

TARGET = 1200.0; PL = 21.21
PR_IND = PL * 4.43/1000                       # pro-rata independent, $/listener-yr
SUB_NET_YR = 11.99*12*0.70; PS_BASE = 0.40    # база PAID_SHARE (assumed, SPEC §1)

def uc_raw(u, n=200_000):
    """Доля кошелька × пул; тянет 2×n сэмплов из ГЛОБАЛЬНОГО потока rng (порядок фиксирован)."""
    p = rng.lognormal(np.log(5.16), 1.676, n)
    o = rng.lognormal(np.log(u), 1.0, n)
    return PS_BASE * SUB_NET_YR * float((p/(p+o)).mean())

U_CANON = [5_000, 10_000, 20_000]             # порядок v04/v05 — канон
U_EXT   = [2_000, 50_000]                     # расширение сетки (review §2)
U_FINE  = [14_000, 15_000]                    # уточнение кроссовера
uc = {}
for u in U_CANON + U_EXT + U_FINE: uc[u] = uc_raw(u)

# --- ворота: канон v04/v05 воспроизведён байт-в-байт ---
CANON = {5_000: 4806.7, 10_000: 9512.2, 20_000: 18341.4}
for u, m in CANON.items():
    got = TARGET/uc[u]
    assert abs(got - m) < 1.0, f"v06 разошёлся с каноном v04: u={u}: {got:.1f} vs {m}"
print("V06 GATE: канон v04 воспроизведён (4,807 / 9,512 / 18,341) — PASS")

def crossover(ps):
    """u*: MVA_uc(u,ps) = MVA_pro-rata-ind. Лог-интерполяция между соседями сетки."""
    tgt = PR_IND * PS_BASE / ps               # uc_raw на кроссовере
    us = sorted(uc)
    for a, b in zip(us, us[1:]):
        if (uc[a] - tgt) * (uc[b] - tgt) <= 0:
            f = (uc[a] - tgt) / (uc[a] - uc[b])
            return math.exp(math.log(a) + f * math.log(b/a))
    return None

PS_GRID = [0.25, 0.40, 0.60]
print("\nUC как функция u (MVA для $100/мес; PAID_SHARE по колонкам):")
print(f"{'u':>7} | " + " | ".join(f"ps={ps:.2f}" for ps in PS_GRID) + " | pro-rata ind = 12,771")
for u in sorted(uc):
    row = " | ".join(f"{TARGET/(uc[u]*ps/PS_BASE):>7,.0f}" for ps in PS_GRID)
    print(f"{u:>7,} | {row}")
stars = {ps: crossover(ps) for ps in PS_GRID}
for ps, s in stars.items():
    print(f"u*(ps={ps:.2f}) ≈ {s:,.0f} плэев/год — выше UC ХУЖЕ pro-rata independent" if s
          else f"u*(ps={ps:.2f}): вне сетки")
print(f"Смена знака (review §2): u=20k, ps=0.40 → MVA {TARGET/uc[20_000]:,.0f} ХУЖЕ pro-rata 12,771")

# --- fig14: MVA(UC) vs u, кроссовер (обе локали) ---
L14 = {"en": dict(curve="user-centric, PAID_SHARE={ps}", pr="pro-rata independent: 12,771",
    star="u* ≈ {v:,.0f} (PAID_SHARE=0.40)",
    xl="Listener's other listening u, plays/yr (log)", yl="MVA for $100/mo (log)",
    t="User-centric is not a scalar: the rule effect flips sign at u*"),
 "ru": dict(curve="user-centric, PAID_SHARE={ps}", pr="pro-rata independent: 12 771",
    star="u* ≈ {v:,.0f} (PAID_SHARE=0.40)",
    xl="Прочее прослушивание слушателя u, плэев/год (log)", yl="MVA для $100/мес (log)",
    t="User-centric — не скаляр: эффект правила меняет знак на u*")}
us_sorted = sorted(uc)
for _lang, _out in (("en", OUT), ("ru", OUT + "ru/")):
    os.makedirs(_out, exist_ok=True); L = L14[_lang]
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    for ps, c in zip(PS_GRID, (C, P, K)):
        ax.plot(us_sorted, [TARGET/(uc[u]*ps/PS_BASE) for u in us_sorted], color=c, lw=3,
                marker="o", ms=4, label=L["curve"].format(ps=ps))
    ax.axhline(TARGET/PR_IND, color=Y, lw=2, ls="--", label=L["pr"])
    s40 = stars[0.40]
    ax.axvline(s40, color="#B8C8DC", lw=1.2, ls=":")
    s40_txt = L["star"].format(v=s40)
    if _lang == "ru": s40_txt = s40_txt.replace(",", " ")  # RU-разделитель тысяч
    ax.text(s40*1.04, TARGET/PR_IND*2.6, s40_txt, fontsize=9, color="#B8C8DC")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.grid(alpha=0.15)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.set_xlabel(L["xl"]); ax.set_ylabel(L["yl"]); ax.set_title(L["t"])
    fig.tight_layout(); fig.savefig(_out + "fig14_uc_crossover.png", dpi=150)
    plt.close(fig)
