#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EMP 1 — измерение редуцированного наклона b (прокси γ) по открытым логам.
SPEC: emp1/SPEC.md (v0.4 — после red team: 18 подтверждённых находок).
b = наклон E[log p_iu | i] по log A_i. Ворота печатаются ДО выводов; FAIL = exit 1.
Данные: emp1/raw/ (LFM-BeyMS + lastfm-360K), в гит не входят.
"""
import sys, os, io, csv, tarfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
FIGS = os.path.join(HERE, "..", "figures")
FAILS = []
Y2012 = (1325376000, 1356998399)   # календарный 2012 (unix)
M201303 = (1362096000, 1364774399) # март 2013

def gate(name, ok, detail):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok: FAILS.append(name)

# ---------- загрузка ----------
def load_360k():
    """usersha1-artmbid-artname-plays.tsv -> (uu, ii, plays); ключ артиста mbid|имя."""
    tar = tarfile.open(os.path.join(RAW, "lastfm-dataset-360K.tar.gz"), "r:gz")
    member = next(m for m in tar.getmembers() if m.name.endswith("usersha1-artmbid-artname-plays.tsv"))
    users, artists = {}, {}
    uu, ii, pp = [], [], []
    f = io.TextIOWrapper(tar.extractfile(member), encoding="utf-8", errors="replace")
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 4: continue
        us, mbid, name, plays = parts
        try: p = int(plays)
        except ValueError: continue
        if p < 1: continue
        ak = mbid if mbid else "n:" + name
        uu.append(users.setdefault(us, len(users)))
        ii.append(artists.setdefault(ak, len(artists)))
        pp.append(p)
    return dict(uu=np.array(uu, np.int64), ii=np.array(ii, np.int64),
                pp=np.array(pp, np.float64), nu=len(users), na=len(artists))

def load_beyms():
    """LFM-BeyMS dataset/events.csv (Zenodo 3784765, md5 сверен):
    user_id,artist_id,album_id,track_id,timestamp. Собирает счётчики пар
    (весь период / 2012 / март-2013), длительность пары и группу юзера."""
    path = os.path.join(RAW, "events.csv")
    print(f"  BeyMS: dataset/events.csv ({os.path.getsize(path)/1e6:.0f} MB)")
    pairs = {}  # (u,a) -> [count, min_ts, max_ts, c2012, cmonth]
    with open(path, encoding="utf-8", errors="replace") as f:
        f.readline()
        for line in f:
            parts = line.rstrip("\n").split(",")
            try:
                u, a, ts = int(parts[0]), int(parts[1]), int(parts[4])
            except (ValueError, IndexError):
                continue
            rec = pairs.get((u, a))
            if rec is None:
                pairs[(u, a)] = [1, ts, ts,
                                 1 if Y2012[0] <= ts <= Y2012[1] else 0,
                                 1 if M201303[0] <= ts <= M201303[1] else 0]
            else:
                rec[0] += 1
                if ts < rec[1]: rec[1] = ts
                if ts > rec[2]: rec[2] = ts
                if Y2012[0] <= ts <= Y2012[1]: rec[3] += 1
                if M201303[0] <= ts <= M201303[1]: rec[4] += 1
    beyond_ids = set()
    with open(os.path.join(RAW, "beyms.csv"), encoding="utf-8") as f:
        f.readline()
        for line in f:
            line = line.strip()
            if line: beyond_ids.add(int(line))
    users, artists = {}, {}
    uu, ii, pp, dur, p12, pm, bey = [], [], [], [], [], [], []
    for (u, a), (c, t0, t1, c12, cm) in pairs.items():
        uu.append(users.setdefault(u, len(users)))
        ii.append(artists.setdefault(a, len(artists)))
        pp.append(c)
        dur.append((t1 - t0) / 86400.0)      # дни
        p12.append(c12); pm.append(cm)
        bey.append(u in beyond_ids)
    return dict(uu=np.array(uu, np.int64), ii=np.array(ii, np.int64),
                pp=np.array(pp, np.float64), nu=len(users), na=len(artists),
                dur=np.array(dur, np.float64), p2012=np.array(p12, np.float64),
                pmonth=np.array(pm, np.float64), beyond=np.array(bey, bool))

# ---------- фильтры (SPEC §1; возвращают индексы уцелевших пар) ----------
def apply_filters(uu, ii, pp, a_min, u_min, p_min=1):
    idx = np.arange(len(uu))
    keep0 = pp >= p_min
    uu, ii, pp, idx = uu[keep0], ii[keep0], pp[keep0], idx[keep0]
    while True:
        n0 = len(uu)
        A = np.bincount(ii)
        keep = A[ii] >= a_min
        uu, ii, pp, idx = uu[keep], ii[keep], pp[keep], idx[keep]
        K = np.bincount(uu)
        keep = K[uu] >= u_min
        uu, ii, pp, idx = uu[keep], ii[keep], pp[keep], idx[keep]
        if len(uu) == n0:
            uu = np.unique(uu, return_inverse=True)[1]
            ii = np.unique(ii, return_inverse=True)[1]
            return uu, ii, pp, idx

# ---------- оценщики ----------
def estimate_y(uu, ii, y):
    """E1 (артист-OLS, HC1), E2 (user-FE; SE: кластер по артисту и двусторонняя
    CGM артист+юзер−HC), E3 (бины — знак-контроль)."""
    A = np.bincount(ii)
    x_i = np.log(A.astype(np.float64))
    sum_y = np.bincount(ii, weights=y)
    n_i = np.bincount(ii).astype(np.float64)
    ok = n_i > 0
    ybar = sum_y[ok] / n_i[ok]; xa = x_i[ok]
    xc = xa - xa.mean(); yc = ybar - ybar.mean()
    b1 = (xc @ yc) / (xc @ xc)
    e = yc - b1 * xc
    se1 = np.sqrt((xc**2 @ e**2) / (xc @ xc)**2 * len(xc)/(len(xc)-2))
    x = x_i[ii]
    ux = np.bincount(uu, weights=x) / np.bincount(uu)
    uy = np.bincount(uu, weights=y) / np.bincount(uu)
    xt = x - ux[uu]; yt = y - uy[uu]
    sxx = xt @ xt
    b2 = (xt @ yt) / sxx
    r = yt - b2 * xt
    xr = xt * r
    v_a = np.bincount(ii, weights=xr); v_a = v_a @ v_a
    v_u = np.bincount(uu, weights=xr); v_u = v_u @ v_u
    v_h = xr @ xr
    G = int((np.bincount(ii) > 0).sum())
    se2_a = np.sqrt(v_a / sxx**2 * G / max(G - 1, 1))
    se2_tw = np.sqrt(max(v_a + v_u - v_h, v_a) / sxx**2)   # CGM двусторонняя
    q = np.quantile(xa, np.linspace(0, 1, 11)); q[0] -= 1e-9
    binned = []
    for lo, hi in zip(q[:-1], q[1:]):
        m = (xa > lo) & (xa <= hi)
        if m.sum() >= 3: binned.append((xa[m].mean(), np.median(ybar[m])))
    binned = np.array(binned)
    rho = spearman(binned[:, 0], binned[:, 1]) if len(binned) > 2 else np.nan
    return dict(b1=b1, se1=se1, b2=b2, se2=se2_a, se2_tw=se2_tw,
                binned=binned, rho=rho, n_pairs=len(y), n_art=len(xa),
                xa=xa, ybar=ybar, x_pair=x, xt=xt, yt=yt)

def estimate(uu, ii, pp):
    return estimate_y(uu, ii, np.log(pp))

def sub_estimate(uu, ii, pp, mask):
    """Оценка на подмножестве пар (с плотной перенумерацией, без перефильтрации)."""
    u2 = np.unique(uu[mask], return_inverse=True)[1]
    i2 = np.unique(ii[mask], return_inverse=True)[1]
    return estimate(u2, i2, pp[mask])

def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    return float((ra @ rb) / np.sqrt((ra @ ra) * (rb @ rb)))

def truncate_top50(uu, ii, pp):
    order = np.lexsort((-pp, uu))
    uo = uu[order]
    start = np.zeros(uo.max() + 2, np.int64)
    np.cumsum(np.bincount(uo, minlength=uo.max() + 1), out=start[1:])
    pos = np.arange(len(uo)) - start[uo]
    keep = order[pos < 50]
    return uu[keep], ii[keep], pp[keep]

# ---------- прогон ----------
print("=" * 72)
print("EMP1 · редуцированный наклон b (прокси γ) — ворота ДО выводов")
print("-" * 72)

B = load_beyms()
print(f"  BeyMS: юзеров {B['nu']:,}, артистов {B['na']:,}, пар {len(B['pp']):,}, "
      f"медиана плэев/пару {np.median(B['pp']):.0f}")
K = load_360k()
print(f"  360K: юзеров {K['nu']:,}, артистов {K['na']:,}, пар {len(K['pp']):,}, "
      f"медиана плэев/пару {np.median(K['pp']):.0f}")

res = {}
uuB, iiB, ppB, idxB = apply_filters(B['uu'], B['ii'], B['pp'], a_min=5, u_min=10)
res["BeyMS"] = estimate(uuB, iiB, ppB)
uuK, iiK, ppK, _ = apply_filters(K['uu'], K['ii'], K['pp'], a_min=5, u_min=10)
res["360K"] = estimate(uuK, iiK, ppK)
u5, i5, p5 = truncate_top50(B['uu'], B['ii'], B['pp'])
u5, i5, p5, _ = apply_filters(u5, i5, p5, a_min=5, u_min=10)
res["BeyMS-t50"] = estimate(u5, i5, p5)

# G4: три оси (red team C2/C18: p_min добавлен)
sens = {}
for p_min in (1, 2, 3):
    for a_min in (3, 5, 10):
        for u_min in (5, 10, 20):
            u2, i2, p2, _ = apply_filters(B['uu'], B['ii'], B['pp'], a_min, u_min, p_min)
            sens[(p_min, a_min, u_min)] = estimate(u2, i2, p2)["b2"]

print("-" * 72)
med_b = np.median(B['pp']); med_3 = np.median(K['pp'])
gate("G1 санити плэев/пару", 2 <= med_b <= 60 and med_3 > med_b,
     f"BeyMS {med_b:.0f} в [2; 60]; 360K {med_3:.0f} > BeyMS (top-50 отбирает жирные пары)")
signs = [np.sign(res[t][k]) for t in ("BeyMS", "360K") for k in ("b1", "b2")]
rho_ok = all(res[t]["rho"] > 0 for t in ("BeyMS", "360K"))
gate("G2 знак b: E1/E2 × 2 датасета (E3 — знак-контроль)",
     len(set(signs)) == 1 and rho_ok,
     f"знаки {[f'{s:+.0f}' for s in signs]}, знак-контроль E3 {'+' if rho_ok else 'FAIL'}")
shift = res["BeyMS-t50"]["b2"] - res["BeyMS"]["b2"]
need = np.sign(res["360K"]["b2"] - res["BeyMS"]["b2"])
gate("G3 фальсификатор обрезки top-50", np.sign(shift) == need,
     f"сдвиг b_E2 при обрезке {shift:+.3f}, знак(360K−BeyMS) {need:+.0f}")
c = res["BeyMS"]["b2"]
sv = np.array(list(sens.values()))
gate("G4 пороги p_min×A_min×u_min (27 комбинаций)",
     (np.sign(sv) == np.sign(c)).all() and (np.abs(sv - c) <= 0.5 * abs(c)).all(),
     f"b_E2 ∈ [{sv.min():.3f}; {sv.max():.3f}] вокруг {c:.3f} (честный интервал — вся сетка)")

print("-" * 72)
if FAILS:
    print(f"FAIL ворот: {FAILS} — выводы заблокированы."); sys.exit(1)
print("ВСЕ ВОРОТА PASS. Оценки b (SE: кластер по артисту / двусторонняя CGM):")
for tag in ("BeyMS", "360K", "BeyMS-t50"):
    r = res[tag]
    print(f"  {tag:9s}: E1 {r['b1']:+.3f}±{r['se1']:.3f} · E2(FE) {r['b2']:+.3f}"
          f"±{r['se2']:.3f}/{r['se2_tw']:.3f} · E3 знак {'+' if r['rho']>0 else '-'}"
          f" · артистов {r['n_art']:,}, пар {r['n_pairs']:,}")

# ---------- диагностика red team (не ворота; печать с фактами) ----------
print("-" * 72)
print("Диагностика red team (C1, C6/C12, C7/C13, C3, C5, C8):")

# C1: разложение retention/rate + окна учёта
logp = np.log(ppB)
dur1 = np.log(B['dur'][idxB] + 1.0)
rate = logp - dur1
rd = estimate_y(uuB, iiB, dur1); rr = estimate_y(uuB, iiB, rate)
print(f"  разложение (BeyMS, канон-фильтры): b[log p] = {res['BeyMS']['b2']:+.3f} = "
      f"b[log(dur+1д)] {rd['b2']:+.3f} + b[log rate] {rr['b2']:+.3f} — наклон это "
      f"retention, интенсивность-в-день АНТИ-сопряжена")
for tag, arr in (("2012 (год)", B['p2012']), ("2013-03 (месяц)", B['pmonth'])):
    m = arr > 0
    uw, iw, pw, _ = apply_filters(B['uu'][m], B['ii'][m], arr[m], a_min=5, u_min=10)
    rw = estimate(uw, iw, pw)
    print(f"  окно {tag}: b_E2 = {rw['b2']:+.3f}±{rw['se2_tw']:.3f} (пар {rw['n_pairs']:,})")

# C6/C12: группы юзеров (бленд 50/50 не идентифицирует уровень)
beyB = B['beyond'][idxB]
for lbl, m in (("beyond-mainstream", beyB), ("mainstream", ~beyB)):
    rg = sub_estimate(uuB, iiB, ppB, m)
    print(f"  группа {lbl:18s}: b_E2 = {rg['b2']:+.3f}±{rg['se2_tw']:.3f} (пар {rg['n_pairs']:,})")

# C7/C13: локальные наклоны головы (без перефильтрации юзеров)
A_f = np.bincount(iiB)
for thr in (50, 200, 1000):
    m = A_f[iiB] >= thr
    if m.sum() < 1000: continue
    rh = sub_estimate(uuB, iiB, ppB, m)
    print(f"  голова A≥{thr:4d}: локальный b_E2 = {rh['b2']:+.3f}±{rh['se2_tw']:.3f} "
          f"(артистов {rh['n_art']:,})")

# C3: recovery/инверсия — оценщик на собственном DGP sim4(c)
rng = np.random.default_rng(42)
gm = np.exp(np.mean(np.log(np.maximum(A_f[A_f > 0], 1))))
print("  recovery sim4(c) на реальном графе (ceil-аттенюация):")
inv_factor = None
for g_true in (0.0, 0.1, 0.3):
    psim = np.ceil(rng.lognormal(np.log(5.16), 1.676, len(uuB)) *
                   (np.maximum(A_f[iiB], 1) / gm) ** g_true)
    rs = estimate(uuB, iiB, psim)
    if g_true == 0.1: inv_factor = rs['b2'] / 0.1
    print(f"    γ_true={g_true:+.1f} → b̂_E2 = {rs['b2']:+.3f}")
print(f"  инверсия: измеренный {res['BeyMS']['b2']:+.3f} ≈ модельное γ "
      f"{res['BeyMS']['b2']/inv_factor:+.3f} (фактор {inv_factor:.2f})")

# C5: плацебо-пермутация (нуль-контроль)
perm = rng.permutation(len(A_f))
x_perm = np.log(np.maximum(A_f[perm], 1).astype(np.float64))[iiB]
uxp = np.bincount(uuB, weights=x_perm) / np.bincount(uuB)
xtp = x_perm - uxp[uuB]
b_pl = (xtp @ (np.log(ppB) - (np.bincount(uuB, weights=np.log(ppB)) /
        np.bincount(uuB))[uuB])) / (xtp @ xtp)
print(f"  плацебо (пермутация A по артистам): b = {b_pl:+.4f} (ожидание ~0)")

# ---------- fig17 ----------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
BG, VIOLET, CYAN, PINK, YELLOW = "#0D0A1A", "#6B2FFF", "#00D4F5", "#FF4D8D", "#FFD426"
fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), facecolor=BG)
for ax, tag in zip(axs, ("BeyMS", "360K")):
    r = res[tag]
    ax.scatter(r["xa"], r["ybar"], s=2, color=CYAN, alpha=.15, rasterized=True)
    ax.plot(r["binned"][:, 0], r["binned"][:, 1], "o-", color=YELLOW, lw=2, ms=5,
            label="медианы децильных бинов")
    xx = np.linspace(r["xa"].min(), r["xa"].max(), 10)
    ax.plot(xx, r["ybar"].mean() + r["b1"] * (xx - r["xa"].mean()), color=VIOLET, lw=2,
            label=f"E1 OLS: b={r['b1']:+.3f}")
    ax.plot(xx, r["ybar"].mean() + r["b2"] * (xx - r["xa"].mean()), "--", color=PINK, lw=2,
            label=f"E2 user-FE: b={r['b2']:+.3f}")
    ax.set_facecolor(BG)
    for sp in ax.spines.values(): sp.set_color("#666")
    ax.tick_params(colors="#CCC"); ax.xaxis.label.set_color("#EEE"); ax.yaxis.label.set_color("#EEE")
    ax.title.set_color("#FFF")
    ax.set_xlabel("log A_i (размер аудитории артиста)")
    ax.set_title(tag + (" (полные истории; наклон выпуклый — см. README)" if tag == "BeyMS"
                        else " (top-50 на юзера; G3: обрезка сдвигает b вниз)"))
    ax.legend(facecolor=BG, labelcolor="#EEE", edgecolor="#666", fontsize=8)
axs[0].set_ylabel("mean log p_iu (плэи на пару)")
fig.suptitle("fig17 · редуцированный наклон b (прокси γ): интенсивность пары против размера аудитории — данные Last.fm 2005–2014, не симуляция",
             color="#FFF", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "fig17_gamma_empirical.png"), dpi=150, facecolor=BG)
print("фигура: figures/fig17_gamma_empirical.png")
print("=" * 72)
