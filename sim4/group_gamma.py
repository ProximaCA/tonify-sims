#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SIM 4-G — гетерогенное сопряжение по ГРУППАМ СЛУШАТЕЛЕЙ (emp1 структурный факт 2).

emp1 нашёл, что наклон b различается в разы между группами слушателей:
mainstream +0.160, beyond-mainstream +0.023 (BeyMS 50/50 по конструкции —
популяционная доля неизвестна, вилка [+0.02; +0.16]). Здесь эта
гетерогенность вносится в мир: у каждого слушателя СВОЙ γ_u, и вопрос —
как реформа PR→UC бьёт по артистам с разным составом аудитории.

Ворота печатаются ДО выводов; FAIL = exit 1. seed=42. MIT.
Спека: sim4/SPEC.md §2 (тот же мир и граф) + emp1/README §Результат.
"""
import sys, os
import numpy as np
from scipy import sparse

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "..", "figures")
os.makedirs(FIGS, exist_ok=True)

# ---------- параметры мира: идентичны bipartite_gen.py (SPEC §1) ----------
N       = 20_000
PL      = 21.21
X_HI    = 225_734
MU_K, SG_K, K_CLIP = np.log(12), 1.0, (1, 2000)
MU_P, SG_P = np.log(5.16), 1.676
SEED    = 42

# ---------- измеренные наклоны по группам (emp1) → структурные γ ----------
# emp1 меряет редуцированный наклон b; recovery-инверсия на DGP sim4(c)
# дала фактор аттенюации 0.84 (ceil-дискретизация). Групповые γ получаем
# тем же фактором — ОГОВОРКА: инверсия калибровалась на общем графе,
# для подвыборок слушателей фактор может отличаться (см. §Ограничения).
ATTEN     = 0.84
B_MAIN    = 0.160          # emp1: mainstream-слушатели
B_BEYOND  = 0.023          # emp1: beyond-mainstream-слушатели
G_MAIN    = B_MAIN / ATTEN     # ≈ +0.190
G_BEYOND  = B_BEYOND / ATTEN   # ≈ +0.027
SHARES    = (0.0, 0.25, 0.50, 0.75, 1.0)   # доля beyond-слушателей в популяции

rng = np.random.default_rng(SEED)
FAILS = []

def gate(name, val, lo, hi, fmt="{:.6g}"):
    ok = lo <= val <= hi
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {fmt.format(val)}  допуск [{fmt.format(lo)}; {fmt.format(hi)}]")
    if not ok: FAILS.append(name)
    return ok

# ---------- шаг 1-2: мир и граф (та же конструкция, тот же seed) ----------
n_low = int(0.87*N); n_mid = int((1-0.87-0.026)*N); n_top = N - n_low - n_mid
s_low = np.clip(np.exp(rng.normal(np.log(80), 1.4, n_low)), 1, 999)
s_mid = np.exp(rng.uniform(np.log(1000), np.log(X_HI), n_mid))
s_top = X_HI * (1 + rng.pareto(1.4, n_top))
streams = np.concatenate([s_low, s_mid, s_top]); rng.shuffle(streams)
ell = np.maximum(1, streams/PL)

K_mean_theory = np.exp(MU_K + SG_K**2/2)
U = int(np.ceil(ell.sum()/K_mean_theory))
K_u = np.clip(np.rint(rng.lognormal(MU_K, SG_K, U)).astype(np.int64), *K_CLIP)
w = ell/ell.sum()
rows_u, rows_i = [], []
B = 1024
for lo in range(0, U, B):
    kk = K_u[lo:lo+B]; b = len(kk); kmax = int(kk.max())
    keys = rng.exponential(size=(b, N)) / w[None, :]
    part = np.argpartition(keys, kmax-1, axis=1)[:, :kmax]
    pk = np.take_along_axis(keys, part, axis=1)
    order = np.argsort(pk, axis=1)
    topsorted = np.take_along_axis(part, order, axis=1)
    for r in range(b):
        k = kk[r]
        rows_u.append(np.full(k, lo+r, dtype=np.int32))
        rows_i.append(topsorted[r, :k].astype(np.int32))
uu = np.concatenate(rows_u); ii = np.concatenate(rows_i)
E = len(uu)
A_real = np.bincount(ii, minlength=N).astype(np.int64)
base = rng.lognormal(MU_P, SG_P, E)
gm = np.exp(np.mean(np.log(np.maximum(A_real, 1))))
A_pair = (np.maximum(A_real, 1)/gm)[ii]          # (A_i/ḡm) на каждом ребре

def build(vals):
    m = sparse.csr_matrix((vals.astype(np.int32), (uu, ii)), shape=(U, N))
    m.sum_duplicates(); return m

def mechanisms(M):
    P_u = np.asarray(M.sum(axis=1)).ravel().astype(np.float64)
    P_i = np.asarray(M.sum(axis=0)).ravel().astype(np.float64)
    T = P_u.sum(); Ueff = int((P_u > 0).sum()); Pbar = T/Ueff
    PR = Ueff*P_i/T
    inv = np.divide(1.0, P_u, out=np.zeros_like(P_u), where=P_u>0)
    UC = np.asarray(M.multiply(inv[:, None]).sum(axis=0)).ravel()
    with np.errstate(divide='ignore', invalid='ignore'):
        Ew_inv = np.divide(UC, P_i, out=np.zeros(N), where=P_i>0)
        H = np.divide(1.0, Ew_inv, out=np.zeros(N), where=Ew_inv>0)
    return PR, UC, H, Pbar, P_i

# ---------- смешанные миры: γ_u по группе слушателя ----------
print("="*74)
print("SIM4-G · гетерогенный γ по группам слушателей (ворота ДО выводов)")
print(f"мир: N={N}, U={U:,}, пар={E:,}; γ_mainstream={G_MAIN:+.3f}, γ_beyond={G_BEYOND:+.3f}")
print(f"(из emp1: b_main={B_MAIN:+.3f}, b_beyond={B_BEYOND:+.3f}; инверсия аттенюации {ATTEN})")
print("-"*74)

rng_g = np.random.default_rng(SEED + 1)
uniform_draw = rng_g.random(U)      # один жребий: доля beyond растёт вложенно
worlds = {}
for share in SHARES:
    is_bey_u = uniform_draw < share          # метка слушателя
    g_u = np.where(is_bey_u, G_BEYOND, G_MAIN)
    vals = np.maximum(1, np.ceil(base * A_pair ** g_u[uu])).astype(np.int64)
    worlds[share] = dict(M=build(vals), is_bey_u=is_bey_u)

# ---------- ворота ----------
top = int(np.ceil(0.0028*N))
res = {}
for share in SHARES:
    M = worlds[share]["M"]
    PR, UC, H, Pbar, P_i = mechanisms(M)
    res[share] = dict(PR=PR, UC=UC, H=H, Pbar=Pbar, P_i=P_i)

ident_max = 0.0; zsum_max = 0.0; sign_viol = 0
for share in SHARES:
    r = res[share]; m = r["P_i"] > 0
    ident_max = max(ident_max, np.abs(r["UC"][m]/r["PR"][m] - r["Pbar"]/r["H"][m]).max())
    zsum_max = max(zsum_max, abs(r["UC"].sum() - r["PR"].sum())/r["PR"].sum())
    ratio = r["UC"][m]/r["PR"][m]
    ok = np.sign(ratio - 1) == np.sign(r["Pbar"] - r["H"][m])
    sign_viol += int((~ok & (np.abs(ratio-1) >= 1e-9)).sum())

gate("H1 L1-тождество на всех смешанных мирах", ident_max, 0, 1e-9, "{:.3e}")
gate("H2 нулевая сумма |ΣUC−ΣPR|/ΣPR", zsum_max, 0, 1e-12, "{:.3e}")
gate("H3 нарушений знака кроссовера", sign_viol, 0, 0, "{:.0f}")

# H4: предельные случаи обязаны совпасть с однородными мирами
def share_uc_gt_pr(share, idx=None):
    r = res[share]; m = r["P_i"] > 0
    sel = m if idx is None else (m & idx)
    return (r["UC"][sel] > r["PR"][sel]).mean()*100

for lim, g_lim, lbl in ((0.0, G_MAIN, "0% beyond ≡ однородный γ_main"),
                        (1.0, G_BEYOND, "100% beyond ≡ однородный γ_beyond")):
    vals = np.maximum(1, np.ceil(base * A_pair ** g_lim)).astype(np.int64)
    PRh, UCh, *_ , Pih = mechanisms(build(vals))
    mh = Pih > 0
    diff = abs((UCh[mh] > PRh[mh]).mean()*100 - share_uc_gt_pr(lim))
    gate(f"H4 предел: {lbl}", diff, 0, 1e-9, "{:.3e}")

print("-"*74)
if FAILS:
    print(f"FAIL ворот: {FAILS} — выводы заблокированы."); sys.exit(1)
print("ВСЕ ВОРОТА PASS.\n")

# ---------- результат 1: доля выигравших от UC по составу популяции ----------
print("Доля артистов с UC>PR при разной доле beyond-слушателей в популяции:")
print(f"  {'beyond':>8} | {'все артисты':>12} | {'топ-0.28%':>10}")
big = np.argsort(res[0.0]["P_i"])[::-1][:top]
for share in SHARES:
    r = res[share]; m = r["P_i"] > 0
    big_s = np.argsort(r["P_i"])[::-1][:top]
    print(f"  {share*100:7.0f}% | {(r['UC'][m] > r['PR'][m]).mean()*100:11.1f}% |"
          f" {(r['UC'][big_s] > r['PR'][big_s]).mean()*100:9.1f}%")

# ---------- результат 2: артисты по СОСТАВУ АУДИТОРИИ (главное) ----------
# «нишевость» артиста = доля beyond-слушателей среди его аудитории
print("\nГлавный разрез — артисты по составу аудитории (мир 50/50, как BeyMS):")
share_ref = 0.50
is_bey_u = worlds[share_ref]["is_bey_u"]
bey_edges = is_bey_u[uu].astype(np.float64)
bey_frac = np.bincount(ii, weights=bey_edges, minlength=N) / np.maximum(A_real, 1)
r = res[share_ref]; m = r["P_i"] > 0
ratio = np.divide(r["UC"], r["PR"], out=np.zeros(N), where=r["PR"] > 0)
qs = np.quantile(bey_frac[m], [0, .2, .4, .6, .8, 1.0])
print(f"  {'квинтиль по доле beyond в аудитории':>38} | {'UC>PR':>7} | {'медиана UC/PR':>13} | артистов")
for k in range(5):
    lo, hi = qs[k], qs[k+1]
    sel = m & (bey_frac > lo if k else bey_frac >= lo) & (bey_frac <= hi)
    if sel.sum() == 0: continue
    print(f"  Q{k+1} (доля beyond {lo:.2f}–{hi:.2f}){'':>10} | {(ratio[sel] > 1).mean()*100:6.1f}% |"
          f" {np.median(ratio[sel]):12.3f} | {sel.sum():,}")

# Немонотонность сырых квинтилей: рабочая гипотеза была «конфаунд с размером»
# (у крупных доля beyond ≈0.5 по ЗБЧ), но она ОПРОВЕРГНУТА замером ниже —
# corr(доля beyond, log A_i) ≈ 0. Фактическая причина: дискретность доли у
# малых аудиторий (при A=2 возможны только 0, 1/2, 1) сгущает массу ровно на
# 1/2, и квинтиль 0.49–0.51 смешивает разнородных артистов. Чистый эффект
# меряем регрессией с контролем размера и разрезом внутри страт.
ok = m & (bey_frac > 0) & (bey_frac < 1)
cc = np.corrcoef(bey_frac[ok], np.log(ratio[ok]))[0, 1]
lA_ok = np.log(A_real[ok].astype(np.float64))
cc_size = np.corrcoef(bey_frac[ok], lA_ok)[0, 1]
print(f"  сырая corr(доля beyond, log UC/PR) = {cc:+.3f} на {ok.sum():,} артистах")
print(f"  проверка конфаунда: corr(доля beyond, log A_i) = {cc_size:+.3f}"
      f" — {'смешан с размером' if abs(cc_size) > 0.1 else 'с размером НЕ смешан (гипотеза о конфаунде опровергнута)'}")

# чистый эффект: регрессия log(UC/PR) на долю beyond С КОНТРОЛЕМ log A_i
X = np.column_stack([np.ones(ok.sum()), bey_frac[ok], lA_ok])
y = np.log(ratio[ok])
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
res_y = y - X @ beta
sig2 = res_y @ res_y / (len(y) - 3)
se = np.sqrt(np.diag(np.linalg.inv(X.T @ X) * sig2))
print(f"  С КОНТРОЛЕМ размера: d log(UC/PR)/d(доля beyond) = {beta[1]:+.3f} ± {se[1]:.3f}"
      f"  (коэф. при log A_i = {beta[2]:+.3f} ± {se[2]:.3f})")

# и разрез по доле beyond ВНУТРИ страт по размеру (чистая картина)
print("\n  Доля артистов с UC>PR по доле beyond ВНУТРИ страт размера аудитории:")
print(f"     {'страта A_i':>16} | {'мало beyond':>11} | {'средне':>8} | {'много beyond':>12}")
a_edges = np.quantile(A_real[ok], [0, 1/3, 2/3, 1.0])
strata_out = []
for si in range(3):
    lo_a, hi_a = a_edges[si], a_edges[si+1]
    sa = ok & (A_real > lo_a if si else A_real >= lo_a) & (A_real <= hi_a)
    if sa.sum() < 100: continue
    q3 = np.quantile(bey_frac[sa], [0, 1/3, 2/3, 1.0])
    row = []
    for bi in range(3):
        sb = sa & (bey_frac > q3[bi] if bi else bey_frac >= q3[bi]) & (bey_frac <= q3[bi+1])
        row.append((ratio[sb] > 1).mean()*100 if sb.sum() else np.nan)
    strata_out.append((f"{lo_a:.0f}–{hi_a:.0f}", row))
    print(f"     {lo_a:7.0f}–{hi_a:6.0f} | {row[0]:10.1f}% | {row[1]:7.1f}% | {row[2]:11.1f}%")

# ---------- fig18 ----------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
BG, VIOLET, CYAN, PINK, YELLOW = "#0D0A1A", "#6B2FFF", "#00D4F5", "#FF4D8D", "#FFD426"
fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.9), facecolor=BG)

ax = axs[0]
allv = [share_uc_gt_pr(s) for s in SHARES]
bigv = []
for s in SHARES:
    r2 = res[s]; b2 = np.argsort(r2["P_i"])[::-1][:top]
    bigv.append((r2["UC"][b2] > r2["PR"][b2]).mean()*100)
xs = [s*100 for s in SHARES]
ax.plot(xs, allv, "o-", color=CYAN, lw=2, ms=6, label="все артисты")
ax.plot(xs, bigv, "s--", color=PINK, lw=2, ms=6, label="топ-0.28% по стримам")
ax.set_xlabel("доля beyond-mainstream слушателей в популяции, %")
ax.set_ylabel("артистов с UC > PR, %")
ax.set_title("состав популяции слушателей решает исход реформы")

ax2 = axs[1]
# КОНФАУНД учтён: показываем разрез по доле beyond ВНУТРИ страт размера
xs3 = np.arange(3); wdt = 0.26
labels = ["мелкие", "средние", "крупные"]
for si, (rng_lbl, row) in enumerate(strata_out):
    ax2.bar(xs3 + (si-1)*wdt, row, wdt, label=f"{labels[si]} (A {rng_lbl})",
            color=[VIOLET, CYAN, PINK][si], edgecolor="#222")
ax2.set_xticks(xs3)
ax2.set_xticklabels(["мало beyond", "средне", "много beyond"])
ax2.set_xlabel("доля beyond-mainstream слушателей в аудитории артиста (терцили ВНУТРИ страты размера)")
ax2.set_ylabel("артистов с UC > PR, %")
ax2.set_title("при фиксированном размере: «нишевее» аудитория — выгоднее UC")
ax2.legend(facecolor=BG, labelcolor="#EEE", edgecolor="#666", fontsize=8)

for a in axs:
    a.set_facecolor(BG)
    for sp in a.spines.values(): sp.set_color("#666")
    a.tick_params(colors="#CCC"); a.xaxis.label.set_color("#EEE"); a.yaxis.label.set_color("#EEE")
    a.title.set_color("#FFF")
axs[0].legend(facecolor=BG, labelcolor="#EEE", edgecolor="#666", fontsize=9)
fig.suptitle("fig18 · гетерогенное сопряжение по группам слушателей: γ_mainstream=+0.19 против γ_beyond=+0.03 (измерено emp1) · симуляция",
             color="#FFF", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "fig18_group_gamma.png"), dpi=150, facecolor=BG)
print("\nфигура: figures/fig18_group_gamma.png")
print("="*74)
