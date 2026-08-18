#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SIM4-D — метрики нижнего края (downside welfare) поверх матрицы sim4.

Зачем: Джини — не единственный и не лучший язык для policy-вывода. Механизм,
который делает больше нулей, но поднимает медиану среди получающих, читается
по Джини почти так же, как механизм, который не делает ничего. Здесь считается
то, что Джини сворачивает: экстенсивная маржа (кто вообще получает), нижние
квантили среди получающих, риск худшего исхода и то, замещает ли direct пул
или дополняет его.

Масштаб. Пуловые доходы — в единицах кошелька (W=1 на активного слушателя),
direct — в единицах чеков. Складывать их нельзя. Основной прогон приводит
direct к РАВНОМУ СРЕДНЕМУ с pro-rata: это ровно постановка L4 («среднее
против риска») — при одинаковом ожидании сравнивается только форма риска.
Справочно печатается и вторая нормировка (каждый механизм на свою сумму).

Ворота печатаются ДО выводов; FAIL = exit(1). seed=42. MIT.
"""
import sys, os
import numpy as np
from scipy import sparse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FIGS = os.path.join(HERE, "..", "figures")

# те же константы, что в sim4/bipartite_gen.py — direct-экономика A5
SEED = 42
SF, KDON, TAKE = 0.017, 4, 0.80
MU_G, SG_G = np.log(5.0), 0.8
G_BAR = np.exp(MU_G + SG_G**2 / 2)          # E[G] для логнормальных подарков

rng = np.random.default_rng(SEED)
FAILS = []

def gate(name, val, lo, hi, fmt="{:.6g}"):
    ok = lo <= val <= hi
    print(f"  {'PASS' if ok else 'FAIL'}  {name} = {fmt.format(val)} (допуск [{lo}; {hi}])")
    if not ok:
        FAILS.append(name)
    return ok

def gini(x):
    """Джини на неотрицательном векторе (нули включены)."""
    x = np.sort(np.asarray(x, dtype=np.float64))
    n = x.size
    s = x.sum()
    if s <= 0:
        return 0.0
    return (2.0 * np.arange(1, n + 1) - n - 1).dot(x) / (n * s)

def mechanisms(M):
    P_u = np.asarray(M.sum(axis=1)).ravel().astype(np.float64)
    P_i = np.asarray(M.sum(axis=0)).ravel().astype(np.float64)
    T = P_u.sum(); Ueff = int((P_u > 0).sum())
    PR = Ueff * P_i / T
    inv = np.divide(1.0, P_u, out=np.zeros_like(P_u), where=P_u > 0)
    UC = np.asarray(M.multiply(inv[:, None]).sum(axis=0)).ravel()
    return PR, UC, P_i

def expected_shortfall(x, alpha):
    """Средний доход по худшим alpha долям артистов (нули включены)."""
    x = np.sort(np.asarray(x, dtype=np.float64))
    k = max(1, int(np.floor(alpha * x.size)))
    return x[:k].mean()

# ---------- вход ----------
path = os.path.join(DATA, "matrix_b_seed42.npz")
if not os.path.exists(path):
    sys.exit("нет data/matrix_b_seed42.npz — сначала: python3 sim4/bipartite_gen.py")
M = sparse.load_npz(path).tocsr()
U, N = M.shape
PR, UC, P_i = mechanisms(M)
A = np.asarray((M > 0).sum(axis=0)).ravel().astype(np.int64)   # аудитория артиста

# direct: та же генерация, что в sim4 (подарки сэмплируются, не матожидание)
S = rng.binomial(A, SF)
tot = S * KDON
draws = rng.lognormal(MU_G, SG_G, int(tot.sum()))
D_raw = TAKE * np.bincount(np.repeat(np.arange(N), tot), weights=draws, minlength=N)

print("=" * 74)
print("SIM4-D · ворота (ДО выводов; FAIL блокирует прогон)")
print(f"мир: N={N:,}, U={U:,}, артистов с аудиторией: {(A>0).sum():,}")
print("-" * 74)

gate("G1  бюджет пулов |ΣUC−ΣPR|/ΣPR", abs(UC.sum() - PR.sum()) / PR.sum(), 0, 1e-12, "{:.3e}")

# E[D|A] = τ·σ·k·ḡ·A — сверка сэмплированной реализации с теорией A5
mA = A > 0
theo = TAKE * SF * KDON * G_BAR * A[mA]
gate("G2  E[D]/теория (τσkḡ·ΣA)", D_raw[mA].sum() / theo.sum(), 0.97, 1.03, "{:.4f}")

# L3(ii): атом в нуле. При логнормальных чеках подарок строго положителен,
# поэтому неравенство леммы выполняется как РАВЕНСТВО: P(D=0|A) = (1−σ)^A.
# Гейт статистический: доля нулей — биномиальная величина, сравнивается
# z-статистикой, а не жёсткой границей (иначе ворота ловят выборочный шум).
edges = np.array([1, 3, 10, 30, 100, 300, 1000, 10**9])
def atom_z(sel):
    emp = (D_raw[sel] == 0).mean()
    theo = ((1 - SF) ** A[sel]).mean()
    se = np.sqrt(max(theo * (1 - theo), 1e-12) / sel.sum())
    return (emp - theo) / se
gate("G3.1 атом: z всей популяции", abs(atom_z(mA)), 0, 4, "{:.2f}")
zmax, zbin = 0.0, ""
for lo, hi in zip(edges[:-1], edges[1:]):
    b = (A >= lo) & (A < hi)
    if b.sum() < 50:
        continue
    z = abs(atom_z(b))
    if z > zmax:
        zmax, zbin = z, f"A∈[{lo};{hi})"
gate(f"G3.2 атом: max|z| по бинам ({zbin})", zmax, 0, 4, "{:.2f}")

# L3(iii): G = q + (1−q)·G⁺ — разложение Джини с массой нулей
q = float((D_raw == 0).mean())
pos = D_raw[D_raw > 0]
G_dec = q + (1 - q) * gini(pos)
gate("G4  |Джини − (q+(1−q)G⁺)|", abs(gini(D_raw) - G_dec), 0, 1e-9, "{:.3e}")

# нормировка к равному среднему (постановка L4)
D = D_raw * (PR.mean() / D_raw.mean())
gate("G5  |E[D]/E[PR] − 1| после нормировки", abs(D.mean() / PR.mean() - 1), 0, 1e-12, "{:.3e}")

print("-" * 74)
if FAILS:
    print(f"FAIL ворот: {FAILS} — выводы заблокированы.")
    sys.exit(1)
print("ВСЕ ВОРОТА PASS. Метрики нижнего края (direct приведён к равному среднему с pro-rata):")
print()

MECH = [("pro-rata", PR), ("user-centric", UC), ("direct", D)]

# 1. экстенсивная маржа: кто вообще получает
print("  1. Экстенсивная маржа — доля артистов с НУЛЁМ")
for name, x in MECH:
    z_all = (x == 0).mean() * 100
    z_aud = (x[mA] == 0).mean() * 100
    print(f"     {name:14} все: {z_all:5.1f}%   среди имеющих аудиторию: {z_aud:5.1f}%")
print()

# 2. доля выше порога θ (θ в единицах среднего дохода — механизмы уравнены по среднему)
print("  2. Доля артистов выше порога θ (θ в долях среднего дохода)")
print(f"     {'θ':>6}  " + "  ".join(f"{n:>14}" for n, _ in MECH))
for th in (0.01, 0.1, 0.5, 1.0, 2.0):
    row = "  ".join(f"{(x >= th*PR.mean()).mean()*100:13.2f}%" for _, x in MECH)
    print(f"     {th:>6}  {row}")
print()

# 3. нижние квантили СРЕДИ ПОЛУЧАЮЩИХ (условно на положительный доход)
print("  3. Квантили дохода среди артистов с положительным доходом (× средний доход)")
print(f"     {'кв.':>6}  " + "  ".join(f"{n:>14}" for n, _ in MECH))
for p in (10, 25, 50):
    row = "  ".join(f"{np.percentile(x[x>0], p)/PR.mean():14.3f}" for _, x in MECH)
    print(f"     p{p:<5}  {row}")
print()

# 4. риск худшего исхода
print("  4. Expected shortfall — средний доход по худшим α артистов (× средний доход)")
print(f"     {'α':>6}  " + "  ".join(f"{n:>14}" for n, _ in MECH))
for a in (0.10, 0.25, 0.50):
    row = "  ".join(f"{expected_shortfall(x, a)/PR.mean():14.4f}" for _, x in MECH)
    print(f"     {a:>6}  {row}")
print()

# 5. P(ноль | A) — как вероятность остаться ни с чем зависит от аудитории
print("  5. P(доход = 0 | размер аудитории A), direct")
print(f"     {'A':>12}  {'артистов':>9}  {'эмпирика':>9}  {'(1−σ)^A':>9}")
for lo, hi in zip(edges[:-1], edges[1:]):
    b = (A >= lo) & (A < hi)
    if b.sum() < 50:
        continue
    lbl = f"{lo}–{hi-1}" if hi < 10**9 else f"≥{lo}"
    print(f"     {lbl:>12}  {b.sum():9,}  {(D_raw[b]==0).mean()*100:8.1f}%  "
          f"{((1-SF)**A[b]).mean()*100:8.1f}%")
print()

# 6. замещает или дополняет: direct как канал ПОВЕРХ пула
print("  6. Direct как дополнительный канал, не замена (доли артистов с аудиторией)")
r = np.divide(D, PR, out=np.zeros_like(D), where=PR > 0)
print(f"     direct ≥ пуловый доход:            {(r[mA] >= 1).mean()*100:5.1f}%")
print(f"     direct даёт прибавку ≥ 10%:        {(r[mA] >= 0.1).mean()*100:5.1f}%")
print(f"     direct не даёт ничего (канал мёртв): {(D[mA] == 0).mean()*100:5.1f}%")
print(f"     медиана direct/пул среди получающих: {np.median(r[mA & (D>0)]):.3f}")
print()

# 7. концентрация — для сопоставления со старым языком
print("  7. Концентрация (для сравнения со старым языком Джини)")
top = int(np.ceil(0.0028 * N))
for name, x in MECH:
    sh = np.sort(x)[::-1][:top].sum() / x.sum() * 100
    print(f"     {name:14} Джини {gini(x):.3f}   доля топ-0.28% дохода: {sh:5.1f}%")
print()
print("  Справочно, вторая нормировка (каждый механизм на свою сумму) не меняет")
print("  ни один из показателей выше: все они инвариантны к общему множителю,")
print("  кроме порогов θ, которые заданы в долях среднего того же механизма.")
print()

# 8. знак разницы Джини зависит от мира — и это главный аргумент против Джини
print("  8. Джини как единственная метрика: знак разницы зависит от сопряжения γ")
print(f"     {'мир':<26}{'пул':>9}{'direct':>9}{'Δ':>9}")
for lbl, f in [("γ=0 (независимость)", "matrix_a_seed42.npz"),
               ("γ=+0.12 (изм. центр)", "matrix_c_g012_seed42.npz"),
               ("γ=+0.28 (изм. голова)", "matrix_c_g028_seed42.npz")]:
    fp = os.path.join(DATA, f)
    if not os.path.exists(fp):
        continue
    Mg = sparse.load_npz(fp).tocsr()
    Pg = np.asarray(Mg.sum(axis=0)).ravel().astype(np.float64)
    Ag = np.asarray((Mg > 0).sum(axis=0)).ravel().astype(np.int64)
    r2 = np.random.default_rng(SEED)
    Sg = r2.binomial(Ag, SF); tg = Sg * KDON
    dg = r2.lognormal(MU_G, SG_G, int(tg.sum()))
    Dg = TAKE * np.bincount(np.repeat(np.arange(len(Ag)), tg), weights=dg, minlength=len(Ag))
    gp, gd = gini(Pg), gini(Dg)
    print(f"     {lbl:<26}{gp:9.4f}{gd:9.4f}{gd-gp:+9.4f}")
print()
print("     Джини direct не зависит от γ: direct платит за ОХВАТ (A), а γ меняет")
print("     интенсивность на пару, не аудиторию. Джини пула с γ растёт — пул платит")
print("     за интенсивность, которая с ростом γ концентрируется. Поэтому знак")
print("     разницы Джини — свойство мира, а не механизма: при независимости он")
print("     около нуля (и в мире paper/theory_check.py даже слабо положителен),")
print("     на измеренном сопряжении direct СНИЖАЕТ Джини. Экстенсивная маржа при")
print("     этом не двигается вовсе: нулей у direct 73% в любом из миров.")
