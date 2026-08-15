#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EMP 1-M — сверка с Moreau et al. (2024) на наших данных.

Moreau, Wikström, Haampland & Johannessen (2024, Inf. Econ. & Policy 68:101103;
HAL hal-04679366) меряют на 890 млн стримов норвежской платформы ДРУГИЕ
величины, чем emp1, и обе входят в нашу Теорему 1:

  их intensity_it = (1/N)·Σ_n S_nt  — средняя ОБЩАЯ интенсивность слушателей
      песни (наше m_i, арифметическое среднее P_u под аудиторией);
  их concentration_it = (1/N)·Σ_n HHI_nt — средняя концентрация внимания
      слушателя (у нас сидит внутри плэй-весов w^i);
  их ucps·log(intensity) = −0.754*** — эластичность выигрыша от UC по
      интенсивности аудитории (N = 52 045 144, song FE + month FE).

Теорема 1 (THEORY §3.4.1): UC_i/PR_i = P̄/H_i, где H_i — ГАРМОНИЧЕСКОЕ
среднее P_u под плэй-весами ⟹ d log(UC/PR)/d log H_i = −1 ТОЧНО (тождество).
ВНИМАНИЕ (поймано этим же скриптом): из AM ≥ HM НЕ следует, что эластичность
по m_i по модулю меньше единицы — регрессионный коэффициент равен
−cov(log H, log m)/var(log m) и зависит от ковариации, а не от порядка
средних. На наших данных он равен −1.089. Прежняя версия этой шапки
утверждала обратное — утверждение ОТОЗВАНО.

Скрипт считает на LFM-BeyMS: (1) наклоны m_i и H_i по log A_i — прямой
аналог их Table A1; (2) фактическую эластичность UC/PR по m_i и по H_i —
проверка предсказания −1 и коридора; (3) эффект UC по ранговым группам
артистов — прямой аналог их Table A2. Ворота ДО выводов; FAIL = exit 1.
"""
import sys, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
FIGS = os.path.join(HERE, "..", "figures")
FAILS = []

def gate(name, ok, detail):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok: FAILS.append(name)

# ---------- данные: пары (u, i, plays) из BeyMS ----------
def load_pairs():
    path = os.path.join(RAW, "events.csv")
    pair = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        f.readline()
        for line in f:
            p = line.split(",", 2)
            try: k = (int(p[0]), int(p[1]))
            except (ValueError, IndexError): continue
            pair[k] = pair.get(k, 0) + 1
    users, artists = {}, {}
    uu, ii, pp = [], [], []
    for (u, a), c in pair.items():
        uu.append(users.setdefault(u, len(users)))
        ii.append(artists.setdefault(a, len(artists)))
        pp.append(c)
    return (np.array(uu, np.int64), np.array(ii, np.int64), np.array(pp, np.float64))

def apply_filters(uu, ii, pp, a_min=5, u_min=10):
    while True:
        n0 = len(uu)
        A = np.bincount(ii); keep = A[ii] >= a_min
        uu, ii, pp = uu[keep], ii[keep], pp[keep]
        K = np.bincount(uu); keep = K[uu] >= u_min
        uu, ii, pp = uu[keep], ii[keep], pp[keep]
        if len(uu) == n0:
            return (np.unique(uu, return_inverse=True)[1],
                    np.unique(ii, return_inverse=True)[1], pp)

def ols_log(x, y, cluster=None):
    """наклон + SE (кластерная, если дан cluster)."""
    xc = x - x.mean(); yc = y - y.mean()
    b = (xc @ yc) / (xc @ xc)
    r = yc - b*xc
    if cluster is None:
        se = np.sqrt((xc**2 @ r**2) / (xc @ xc)**2 * len(x)/(len(x)-2))
    else:
        g = np.bincount(cluster, weights=xc*r)
        G = int((np.bincount(cluster) > 0).sum())
        se = np.sqrt((g @ g) / (xc @ xc)**2 * G/max(G-1, 1))
    return b, se

print("="*74)
print("EMP1-M · сверка с Moreau et al. (2024) — ворота ДО выводов")
print("-"*74)
uu, ii, pp = apply_filters(*load_pairs())
N = ii.max()+1; U = uu.max()+1
P_u = np.bincount(uu, weights=pp)                    # интенсивность слушателя
P_i = np.bincount(ii, weights=pp)                    # плэи артиста
A_i = np.bincount(ii).astype(np.float64)             # аудитория артиста
T = pp.sum(); Pbar = T/U
print(f"  BeyMS после канон-фильтров: артистов {N:,}, слушателей {U:,}, пар {len(pp):,}")

# m_i (AM) и H_i (HM) интенсивности аудитории под плэй-весами w^i
w = pp / P_i[ii]
m_i = np.bincount(ii, weights=w*P_u[uu])
H_i = 1.0/np.bincount(ii, weights=w/P_u[uu])
UC = np.bincount(ii, weights=pp/P_u[uu])             # W=1
PR = U*P_i/T
ratio = UC/PR

# ---------- ворота ----------
ok_ident = np.abs(ratio - Pbar/H_i).max()
gate("M1 тождество Теоремы 1 на данных (max|UC/PR − P̄/H|)",
     ok_ident < 1e-9, f"{ok_ident:.3e} < 1e-9")
gate("M2 AM ≥ HM на каждом артисте (следствие d)",
     (m_i >= H_i - 1e-9).all(), f"min(m/H) = {(m_i/H_i).min():.6f} ≥ 1")
zsum = abs(UC.sum() - PR.sum())/PR.sum()
gate("M3 нулевая сумма |ΣUC−ΣPR|/ΣPR", zsum < 1e-12, f"{zsum:.3e} < 1e-12")

print("-"*74)
if FAILS:
    print(f"FAIL ворот: {FAILS} — выводы заблокированы."); sys.exit(1)
print("ВСЕ ВОРОТА PASS.\n")

# ---------- 1) их Table A1: интенсивность аудитории по размеру артиста ----------
lA = np.log(A_i)
b_m, se_m = ols_log(lA, np.log(m_i), cluster=None)
b_h, se_h = ols_log(lA, np.log(H_i), cluster=None)
print("1) Наклон интенсивности АУДИТОРИИ по размеру артиста (аналог их Table A1):")
print(f"   d log m_i / d log A_i (AM, их 'intensity') = {b_m:+.4f} ± {se_m:.4f}")
print(f"   d log H_i / d log A_i (HM, вход Теоремы 1) = {b_h:+.4f} ± {se_h:.4f}")
print(f"   для сравнения: наш b (плэи ПАРЫ p_iu) = +0.101 — это другая величина")

# их ранговые группы: 1-10 / 11-100 / 101-1k / 1k-10k / >10k по стримам
order = np.argsort(P_i)[::-1]
rank = np.empty(N, np.int64); rank[order] = np.arange(N)
groups = [("rank1–10", rank < 10), ("rank11–100", (rank >= 10) & (rank < 100)),
          ("rank101–1k", (rank >= 100) & (rank < 1000)),
          ("rank1k–10k", (rank >= 1000) & (rank < 10000)),
          ("rank>10k", rank >= 10000)]
ref = np.exp(np.log(m_i[groups[2][1]]).mean())
print("\n   по их ранговым группам (exp средних log m_i, ref = rank101–1k):")
for name, sel in groups:
    if sel.sum() == 0: continue
    print(f"     {name:12s} {np.exp(np.log(m_i[sel]).mean())/ref:6.3f}   (артистов {sel.sum():,})")
print("     их Table A1:  rank1–10 1.284 · rank11–100 1.088 · rank1k–10k 0.973 · rank>10k 0.898")

# ---------- 2) эластичность UC/PR по интенсивности: проверка предсказания −1 ----------
print("\n2) Эластичность выигрыша от UC по интенсивности аудитории:")
e_h, se_eh = ols_log(np.log(H_i), np.log(ratio))
e_m, se_em = ols_log(np.log(m_i), np.log(ratio))
print(f"   по H_i (гармоническая): {e_h:+.4f} ± {se_eh:.4f}  — Теорема 1 предсказывает РОВНО −1")
print(f"   по m_i (арифметическая): {e_m:+.4f} ± {se_em:.4f}  — Moreau на кассовых данных: −0.754")
print(f"   (наивное «AM≥HM ⟹ |эластичность по m|<1» ОТОЗВАНО: коэффициент =")
print(f"    −cov(log H, log m)/var(log m), здесь {e_m:+.3f}; сравнимость с их −0.754")
print(f"    ограничена спецификацией: у них within-song FE по месяцам, у нас")
print(f"    кросс-секция между артистами — это разные оценки)")

# ---------- 3) их Table A2: эффект UC по ранговым группам ----------
print("\n3) Эффект UC по ранговым группам (медиана UC/PR, аналог их Table A2):")
ref_med = np.median(ratio[groups[2][1]])
for name, sel in groups:
    if sel.sum() == 0: continue
    rel = np.median(ratio[sel])/ref_med
    print(f"     {name:12s} {rel:6.3f}  ({(rel-1)*100:+5.1f}% относительно ref) · UC>PR у {(ratio[sel]>1).mean()*100:5.1f}%")
print("     их Table A2:  rank1–10 0.912 · rank11–100 1.029 · rank1k–10k 0.925 · rank>10k 0.888")
print("     (их немонотонность: топ теряет, середина выигрывает, хвост теряет СИЛЬНЕЕ топа)")

# ---------- 4) канал концентрации (то, чего в sim4 нет) ----------
K_u = np.bincount(uu).astype(np.float64)             # артистов у слушателя
conc = np.bincount(ii, weights=w*(1.0/K_u[uu]))      # ~ средняя 1/K аудитории
b_c, se_c = ols_log(lA, np.log(conc))
print(f"\n4) Канал концентрации (у Moreau — второй регрессор, у нас внутри w^i):")
print(f"   d log(средняя 1/K_u аудитории) / d log A_i = {b_c:+.4f} ± {se_c:.4f}")
print(f"   их concentration по рангам: rank1–10 1.241 · rank>10k 0.829 (Table A1)")
print("="*74)
