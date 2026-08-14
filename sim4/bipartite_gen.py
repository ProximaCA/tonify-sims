#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SIM 4 — синтетическая двудольная матрица user×artist (SPEC: sim4/SPEC.md).
Ворота печатаются ДО выводов; FAIL = exit(1). seed=42. MIT.
"""
import sys, os, csv
import numpy as np
from scipy import sparse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FIGS = os.path.join(HERE, "..", "figures")
os.makedirs(DATA, exist_ok=True); os.makedirs(FIGS, exist_ok=True)

# ---------- параметры (SPEC §1) ----------
N       = 20_000
PL      = 21.21
X_HI    = 225_734
MU_K, SG_K, K_CLIP = np.log(12), 1.0, (1, 2000)
MU_P, SG_P = np.log(5.16), 1.676
GAMMAS  = (-0.3, 0.0, +0.3)
SEED    = 42
SF, KDON, TAKE = 0.017, 4, 0.80
MU_G, SG_G = np.log(5.0), 0.8

rng = np.random.default_rng(SEED)
FAILS = []

def gate(name, val, lo, hi, fmt="{:.6g}"):
    ok = lo <= val <= hi
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {fmt.format(val)}  допуск [{fmt.format(lo)}; {fmt.format(hi)}]")
    if not ok: FAILS.append(name)
    return ok

# ---------- шаг 1: мир стримов (конструкция sim1 §2) ----------
n_low = int(0.87*N); n_mid = int((1-0.87-0.026)*N); n_top = N - n_low - n_mid
s_low = np.clip(np.exp(rng.normal(np.log(80), 1.4, n_low)), 1, 999)
s_mid = np.exp(rng.uniform(np.log(1000), np.log(X_HI), n_mid))
s_top = X_HI * (1 + rng.pareto(1.4, n_top))
streams = np.concatenate([s_low, s_mid, s_top]); rng.shuffle(streams)
ell = np.maximum(1, streams/PL)                      # целевые слушатели

# ---------- шаг 2: граф (Gumbel top-K, вес ∝ ell) ----------
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
A_real = np.bincount(ii, minlength=N).astype(np.int64)   # Ã_i

# ---------- шаг 3: режимы ----------
base = rng.lognormal(MU_P, SG_P, E)                       # общее полотно пар

def build_csr(vals, dtype):
    m = sparse.csr_matrix((vals.astype(dtype), (uu, ii)), shape=(U, N))
    m.sum_duplicates(); return m

# (a) ergodic: P_u ≡ 2048 — целые, степень двойки: p/P_u — точная двоичная
# дробь, все суммы в mechanisms() точны в float64 (C/K_u копил 1.9e-12 на
# N=20k; UC/PR инвариантно к масштабу p — уровень контроля значения не имеет)
C = 2048
pos = np.arange(E, dtype=np.int64)
starts = np.zeros(U+1, dtype=np.int64)
np.cumsum(np.bincount(uu, minlength=U), out=starts[1:])
pos -= starts[uu]
p_a = C // K_u[uu] + (pos < (C % K_u[uu])).astype(np.int64)
M_a = build_csr(p_a, np.int64)

# (b): целочисленное полотно + пер-артистный рескейл к мишени s_i
p0 = np.maximum(1, np.ceil(base)).astype(np.int64)
s_raw = np.bincount(ii, weights=p0, minlength=N)
lam = np.divide(streams, s_raw, out=np.ones(N), where=s_raw>0)
scaled = p0*lam[ii]
# суммо-точное округление наибольших остатков: Σ по артисту == round(s_i) точно
# (стохастика ловила T1-утечку через порог 1000 у массы clip=999 — см. SPEC CHANGELOG)
fl = np.floor(scaled)
frac = scaled - fl
target_int = np.rint(np.bincount(ii, weights=scaled, minlength=N)).astype(np.int64)
resid = target_int - np.bincount(ii, weights=fl, minlength=N).astype(np.int64)
order = np.lexsort((-frac, ii))          # внутри артиста — по убыванию остатка
pos = np.empty(E, dtype=np.int64)        # ранг ребра внутри своего артиста
start = np.zeros(N+1, dtype=np.int64)
np.cumsum(np.bincount(ii, minlength=N), out=start[1:])
pos[order] = np.arange(E) - start[ii[order]]
p_b = fl.astype(np.int64) + (pos < resid[ii]).astype(np.int64)
p_b = np.maximum(p_b, 1)
M_b = build_csr(p_b, np.int32)

# (c): γ-семейство, без рескейла
gm = np.exp(np.mean(np.log(np.maximum(A_real, 1))))
M_c = {}
for g in GAMMAS:
    if g == 0.0:
        vals = p0
    else:
        vals = np.maximum(1, np.ceil(base*((np.maximum(A_real,1)/gm)**g)[ii])).astype(np.int64)
    M_c[g] = build_csr(vals, np.int32)

# ---------- механизмы (THEORY §2) ----------
def mechanisms(M):
    P_u = np.asarray(M.sum(axis=1)).ravel().astype(np.float64)
    P_i = np.asarray(M.sum(axis=0)).ravel().astype(np.float64)
    T = P_u.sum(); Ueff = int((P_u > 0).sum()); Pbar = T/Ueff
    PR = Ueff*P_i/T
    inv = np.divide(1.0, P_u, out=np.zeros_like(P_u), where=P_u>0)
    UC = np.asarray(M.multiply(inv[:, None]).sum(axis=0)).ravel()
    with np.errstate(divide='ignore', invalid='ignore'):
        Ew_inv = np.divide(np.asarray(M.multiply(inv[:, None]).sum(axis=0)).ravel(), P_i,
                           out=np.zeros(N), where=P_i>0)
        H = np.divide(1.0, Ew_inv, out=np.zeros(N), where=Ew_inv>0)
    return PR, UC, H, Pbar, P_i, P_u

# ---------- ворота (SPEC §4) ----------
print("="*72)
print("SIM4 · ворота (ДО выводов; FAIL блокирует прогон)")
print(f"мир: N={N}, U={U}, пар={E:,}, стримы={streams.sum():,.0f}")
print("-"*72)

PRa, UCa, *_ = mechanisms(M_a)
mask = PRa > 0
g1 = np.max(np.abs(UCa[mask]/PRa[mask] - 1))
gate("G1  режим (a): max|UC/PR − 1|", g1, 0, 1e-12, "{:.3e}")

s_b = np.asarray(M_b.sum(axis=0)).ravel()
gate("G2.1 T1 доля s̃<1000", (s_b < 1000).mean()*100, 86, 88, "{:.1f}%")
gate("G2.2 T2 доля s̃>225 734", (s_b > X_HI).mean()*100, 2.4, 2.8, "{:.2f}%")
top = int(np.ceil(0.0028*N))
gate("G2.3 T3 доля стримов топ-0.28%", np.sort(s_b)[::-1][:top].sum()/s_b.sum()*100, 40, 55, "{:.1f}%")
PRb, UCb, Hb, Pbarb, Pib, Pub = mechanisms(M_b)
w_id = Pib > 0
ident = np.abs(UCb[w_id]/PRb[w_id] - Pbarb/Hb[w_id])
gate("G2.4 L1-тождество max|UC/PR − P̄/H|", ident.max(), 0, 1e-9, "{:.3e}")
gate("G2.5 |ΣUC−ΣPR|/ΣPR", abs(UCb.sum()-PRb.sum())/PRb.sum(), 0, 1e-12, "{:.3e}")

viol = 0
for tag, M in [("b", M_b)] + [(f"c γ={g:+.1f}", M_c[g]) for g in GAMMAS if g != 0.0]:
    PR, UC, H, Pbar, Pi, _ = mechanisms(M)
    m2 = Pi > 0
    r = UC[m2]/PR[m2]
    sgn_ok = np.sign(r-1) == np.sign(Pbar - H[m2])
    v = int((~sgn_ok & (np.abs(r-1) >= 1e-9)).sum()); viol += v
gate("G3  нарушений знака кроссовера (b + c)", viol, 0, 0, "{:.0f}")

print("-"*72)
if FAILS:
    print(f"FAIL ворот: {FAILS} — выводы заблокированы."); sys.exit(1)
print("ВСЕ ВОРОТА PASS. Справочно:")
# red team v2 (C15): топ — ПО СТРИМАМ (ℓ), не по самому насыщению; прежняя
# сортировка np.sort(sat)[::-1][:top] брала топ-56 по sat и давала фиктивные 5.00
sat = A_real/np.maximum(ell,1)
head = np.argsort(ell)[::-1][:top]
print(f"  насыщение головы: медиана Ã/ℓ у топ-{top} по ℓ = {np.median(sat[head]):.2f} (мир целиком: {np.median(sat):.2f})")
med_p = np.asarray(M_b.sum(axis=0)).ravel()/np.maximum(A_real,1)
c_ok = (A_real>0)
cc = np.corrcoef(np.log(np.maximum(A_real[c_ok],1)), np.log(np.maximum(med_p[c_ok],1e-9)))[0,1]
print(f"  вынужденное сопряжение (b): corr(log Ã, log p̄_пары) = {cc:+.3f}")
for g in GAMMAS:
    PR, UC, H, Pbar, Pi, _ = mechanisms(M_c[g] if g != 0.0 else M_c[0.0])
    m2 = Pi>0
    share = (UC[m2] > PR[m2]).mean()*100
    big = np.argsort(Pi)[::-1][:top]
    share_big = (UC[big] > PR[big]).mean()*100
    print(f"  γ={g:+.1f}: UC>PR у {share:.1f}% артистов; среди топ-0.28% — {share_big:.1f}%")

# ---------- выгрузка (SPEC §5) ----------
def dump(M, name):
    sparse.save_npz(os.path.join(DATA, f"matrix_{name}_seed42.npz"), M)
dump(M_a, "a"); dump(M_b, "b"); dump(M_c[-0.3], "c_gm03"); dump(M_c[+0.3], "c_gp03")
coo = M_b.tocoo()
order = np.lexsort((coo.col, coo.row))
with open(os.path.join(DATA, "matrix_sample.csv"), "w", newline="") as f:
    wtr = csv.writer(f); wtr.writerow(["user_id","artist_id","plays"])
    for j in order[:10_000]:
        wtr.writerow([int(coo.row[j]), int(coo.col[j]), int(coo.data[j])])
print(f"выгрузка: data/matrix_{{a,b,c_gm03,c_gp03}}_seed42.npz + matrix_sample.csv (10k троек)")

# ---------- fig15 / fig16 (SPEC §6) ----------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
BG, VIOLET, CYAN, PINK, YELLOW = "#0D0A1A", "#6B2FFF", "#00D4F5", "#FF4D8D", "#FFD426"
def styl(ax):
    ax.set_facecolor(BG)
    for sp in ax.spines.values(): sp.set_color("#666")
    ax.tick_params(colors="#CCC"); ax.xaxis.label.set_color("#EEE"); ax.yaxis.label.set_color("#EEE")
    ax.title.set_color("#FFF")

# red team R2: гифты сэмплируются, не матожидание (рецидив CRITIC §3 —
# детерминированная сумма подарков искусственно сужала хвост direct)
S = rng.binomial(A_real.astype(np.int64), SF)
tot = S*KDON
draws = rng.lognormal(MU_G, SG_G, int(tot.sum()))
D = TAKE*np.bincount(np.repeat(np.arange(N), tot), weights=draws, minlength=N)
fig, ax = plt.subplots(figsize=(9.5,5.4), facecolor=BG)
bins = np.logspace(-4, np.log10(max(PRb.max(),UCb.max(),D.max())+1), 60)
# red team R1: нули ИСКЛЮЧЕНЫ из бинов (кламп 1e-4 вмазывал их в нижний бин,
# противореча подписи); оба атома — в аннотации ниже
for arr, c, lb in [(PRb, VIOLET, "pro-rata"), (UCb, CYAN, "user-centric"), (D, PINK, f"direct (σ={SF}, k={KDON})")]:
    ax.hist(arr[arr > 0], bins=bins, histtype="step", lw=2, color=c, label=lb)
ax.set_xscale("log"); ax.set_yscale("log"); styl(ax)
ax.set_xlabel("доход артиста, усл. ед. (W=1 у пуловых; direct — по чекам)"); ax.set_ylabel("артистов в бине")
ax.set_title("fig15 · три механизма на одном субстрате — матрица (b), seed 42 · симуляция")
ax.legend(facecolor=BG, labelcolor="#EEE", edgecolor="#666")
zero_d = (D==0).mean()*100; zero_p = (PRb==0).mean()*100
ax.text(0.02, 0.03,
        f"нулевые доходы вне бинов: direct {zero_d:.0f}% артистов; пуловые {zero_p:.0f}% (пустая аудитория Ã=0 — ноль у всех трёх)",
        transform=ax.transAxes, color=YELLOW, fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(FIGS, "fig15_three_mechanisms.png"), dpi=150, facecolor=BG); plt.close(fig)

fig, axs = plt.subplots(1, 3, figsize=(14,4.8), facecolor=BG, sharey=True)
for ax, g in zip(axs, GAMMAS):
    PR, UC, H, Pbar, Pi, _ = mechanisms(M_c[g])
    m2 = Pi>0
    x = H[m2]/Pbar; y = UC[m2]/PR[m2]
    sc = ax.scatter(x, y, c=np.log10(np.maximum(A_real[m2],1)), s=4, cmap="cool", alpha=.6)
    xx = np.logspace(np.log10(max(x.min(),1e-3)), np.log10(x.max()), 100)
    ax.plot(xx, 1/xx, color=YELLOW, lw=1.2, ls="--", label="y = 1/x (Теорема 1)")
    ax.axhline(1, color="#888", lw=.8); ax.axvline(1, color="#888", lw=.8)
    ax.set_xscale("log"); ax.set_yscale("log"); styl(ax)
    ax.set_title(f"γ = {g:+.1f}"); ax.set_xlabel("H_i / P̄  (гарм. интенсивность аудитории)")
axs[0].set_ylabel("UC_i / PR_i"); axs[0].legend(facecolor=BG, labelcolor="#EEE", edgecolor="#666", fontsize=8)
cb = fig.colorbar(sc, ax=axs, fraction=.02, pad=.01); cb.set_label("log₁₀ Ã_i", color="#EEE"); cb.ax.yaxis.set_tick_params(color="#CCC")
plt.setp(plt.getp(cb.ax.axes, "yticklabels"), color="#CCC")
fig.suptitle("fig16 · тождество L1 на матрице: точки лежат на y=1/x; γ двигает артистов ВДОЛЬ кривой · симуляция", color="#FFF")
fig.savefig(os.path.join(FIGS, "fig16_L1_crossover.png"), dpi=150, facecolor=BG, bbox_inches="tight"); plt.close(fig)
print("фигуры: figures/fig15_three_mechanisms.png, fig16_L1_crossover.png")
print("="*72)
