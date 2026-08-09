# -*- coding: utf-8 -*-
"""
SIM 3 — «Анти-кладбище»: закон «выплаты ≤ приток» против эмиссии.
Реализация 1:1 по sim3/SPEC.md v1.1 (economist → engineer; T3a в редакции v1.1,
механика/калибровка v1.0 не тронуты — см. CHANGELOG спеки).
Запуск: python3 sim3/sim3_anti_graveyard.py
stdout: блок VALIDATION (§7), затем RESULTS (§6, §3.2, §8, §2.3); фигуры → ../figures/.
Детерминизм: default_rng([42, r]) на прогон, default_rng(42) для весов артистов (§5, §10).
"""
import os, sys, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T_H = 36                 # горизонт, мес (§0)
R_RUNS = 200             # Монте-Карло прогонов B (§5)

# ---------- §1.1 — мир sim1 (готовое, не пересматривается) ----------
MEAN_GIFT = 6.9          # средний донат-чек, $ (lognormal медиана $5, σ=0,8 — агрегатом)
S_SF = 0.017             # доля суперфанов (SoundCloud FPR, CRITIC §7)
K_PAY = 4                # платежей/суперфан/год (ось «Объекта 3», milestone sim1)
FEE = 0.05               # комиссия Tonify
RAIL = 0.949             # TON-рельса: $1 → 94,9¢ артисту (RESULTS §3, fig4)
SPLIT_IND, SPLIT_SGN = 1.0, 0.70   # контрактные колонки §6 (Addendum v0.5, DEAL360)

# ---------- §1.3 — параметры sim3 ----------
U0 = 1_000_000           # P1  стартовый DAU обоих режимов
C_MIN = 0.05             # P2  базовый месячный churn
I_A = 0.06               # P3  органический приток A
RHO = 0.5                # P4  доля притока казны A в кэшбэк
C_E = 100.0              # P5  стоимость входа в B, $
Y0 = 0.5                 # P6  стартовая месячная доходность B
P0 = 1.0                 # стартовая цена токена B, $ (§3.2)
EPS = Y0 * C_E / P0      # P7  эмиссия = 50 ток./юзер/мес (производная)
DELTA_U = 0.7            # P8  доля заработка, продаваемая юзером
KAPPA = 0.5              # P9  эластичность цены (база; грид §7.1 может расширить)
# P10–P12 — калибровочные ручки: значения зафиксированы прогоном грида §7.1
# (правило выбора спеки: медиана F ближе к 25 при выполнении T1; тай-брейк |med t_peak − 9|;
#  победитель грида 27×200 при κ=0,5: medF=20,79, P10=16,25, med t_peak=5 — расширение по κ
#  не потребовалось; выбор проверяется assert'ом в main при каждом запуске)
NU = 0.8                 # P10 вирусный коэффициент притока B
U_MAX = 10e6             # P11 потолок рынка B (TAM)
LAM = 0.65               # P12 чувствительность оттока к падению доходности
C_MAX = 0.45             # P13 потолок месячного оттока B (хамстер-темп ~41,5%)
OMEGA = 0.3              # P14 доля спекулянтских покупок от входного объёма
D_TRIG_LO, D_TRIG_HI = 0.15, 0.35   # P15 drawdown-триггер паники, U[...] на прогон
PSI = 0.6                # P16 темп панического сброса инвентаря
SIG_I = 0.2              # P17 шум притока (lognormal)
SIG_P = 0.15             # P18 шум цены (lognormal)
PHI_B = 0.05             # P19 fee протокола B (в токенах, от sell-объёма)
CAP_INFLOW = 2.0         # P20 cap притока min(y/y0, 2)
ART_MIN, ART_STREAK = 1.0, 6       # P21 порог ухода артиста: < $1/мес 6 мес подряд
N_ART = 10_000           # P22 размер артистного слоя
Z0 = 10_000_000          # казна B на старте, токены (§3.2)
DEATH_FRAC = 0.04        # §4  порог смерти по DAU (12M/300M, Hamster)
TRE_DEATH_FRAC = 0.05    # §4  вторичный датчик: смерть казны
P_FLOOR = 0.001          # §3.2 floor цены токена

FALS_C = [0.02, 0.05, 0.0855, 0.12, 0.20, 0.415]   # §8 сетка оттока при i_A=0
FALS_T = 400             # горизонт фальсификатора (c=2% умирает на t≈160)
C_STAR = 1.0 - 0.04 ** (1.0 / 36.0)                # §8 порог горизонта ≈ 8,554%/мес


def build_artist_weights():
    """§2.3: веса v_j из распределения sim1 (lognormal-тело / Pareto-хвост α=1,4), Σv=1."""
    rng = np.random.default_rng(42)          # §5: общие для всех прогонов
    n_low = int(N_ART * 0.87)
    n_mid = int(N_ART * (1 - 0.87 - 0.026))
    n_top = N_ART - n_low - n_mid
    low = np.clip(np.exp(rng.normal(np.log(80), 1.4, n_low)), 1, 999)
    mid = np.exp(rng.uniform(np.log(1000), np.log(225_734), n_mid))
    top = 225_734 * (1 + rng.pareto(1.4, n_top))
    s = np.concatenate([low, mid, top])
    rng.shuffle(s)
    return s / s.sum()


def draw_noise(R=R_RUNS, T=T_H):
    """§5: прогон r ← default_rng([42, r]); порядок розыгрышей: ξ_I (36), ξ_P (36), d_trig."""
    xi_I = np.empty((R, T)); xi_P = np.empty((R, T)); d_trig = np.empty(R)
    for r in range(R):
        rng = np.random.default_rng([42, r])
        xi_I[r] = rng.lognormal(0.0, SIG_I, T)
        xi_P[r] = rng.lognormal(0.0, SIG_P, T)
        d_trig[r] = rng.uniform(D_TRIG_LO, D_TRIG_HI)
    return xi_I, xi_P, d_trig


def simulate_B(nu, u_max, lam, kappa, xi_I, xi_P, d_trig):
    """§2.1/§2.2/§3.2, векторно по прогонам. Состояния t=0..36, потоки t=0..35.
    payout (=M_t·P_t) считается и на t=36 — шума не требует."""
    R, T = xi_I.shape
    U = np.full(R, float(U0)); P = np.full(R, P0); Q = np.zeros(R)
    Z = np.full(R, float(Z0)); panic = np.zeros(R, bool); Pmax = np.full(R, P0)
    Zd = np.zeros(R)                                  # §11.12: fee в $ по цене момента сбора
    U_tr = np.empty((R, T + 1)); P_tr = np.empty((R, T + 1)); TB = np.empty((R, T + 1))
    TBd = np.empty((R, T + 1))
    payout = np.empty((R, T + 1)); inflow = np.empty((R, T))
    for t in range(T + 1):
        panic |= (1.0 - P / Pmax) >= d_trig          # §2.2: sticky, обратно не входят
        U_tr[:, t] = U; P_tr[:, t] = P; TB[:, t] = Z * P; TBd[:, t] = Zd
        payout[:, t] = EPS * U * P                    # payoutB_t = M_t·P_t, $
        if t == T:
            break
        y = EPS * P / C_E
        # §2.1 B; max(0, 1−U/U_max) — защита от отрицательного притока при перелёте U>U_max
        I = nu * np.minimum(y / Y0, CAP_INFLOW) * U * np.maximum(0.0, 1.0 - U / u_max) * xi_I[:, t]
        churn = np.clip(C_MIN + lam * np.maximum(0.0, 1.0 - y / Y0), C_MIN, C_MAX)
        sell = DELTA_U * EPS * U + PSI * Q * panic    # токены
        buy_d = C_E * I * (1.0 + OMEGA * (~panic))    # $, новые деньги
        inflow[:, t] = buy_d
        Zd = Zd + PHI_B * sell * P                    # до апдейта цены: P_t момента сбора
        Q = np.where(panic, Q * (1.0 - PSI), Q + OMEGA * C_E * I / P)
        P = np.maximum(P * (buy_d / P / sell) ** kappa * xi_P[:, t], P_FLOOR)
        Z = Z + PHI_B * sell
        U = U + I - churn * U
        Pmax = np.maximum(Pmax, P)
    return {"U": U_tr, "P": P_tr, "TB": TB, "TBd": TBd, "payout": payout, "inflow": inflow}


def death_month(U_tr, frac=DEATH_FRAC):
    """§4: U_t < frac·max_{τ≤t}U_τ два месяца подряд; t* = первый из двух. −1 = жив."""
    runmax = np.maximum.accumulate(U_tr, axis=1)
    below = U_tr < frac * runmax
    dead2 = below[:, :-1] & below[:, 1:]
    has = dead2.any(axis=1)
    tstar = np.where(has, dead2.argmax(axis=1), -1)
    return tstar, has


def peak_factor(U_tr):
    """§7 T1: F_r = U_peak / U_{peak+6}; прогоны с t_peak > T−6 исключаются."""
    R, T1 = U_tr.shape
    tp = U_tr.argmax(axis=1)
    ok = tp <= (T1 - 1) - 6
    idx = np.arange(R)
    F = np.full(R, np.nan)
    F[ok] = U_tr[idx[ok], tp[ok]] / U_tr[idx[ok], tp[ok] + 6]
    return tp, F, ok


def t1_stats(U_tr):
    tp, F, ok = peak_factor(U_tr)
    n_excl = int((~ok).sum())
    if ok.sum() == 0:
        return {"medF": np.nan, "p10F": np.nan, "med_tp": np.nan, "n_excl": n_excl, "ok": False}
    medF = float(np.median(F[ok])); p10F = float(np.percentile(F[ok], 10))
    med_tp = float(np.median(tp[ok]))
    passed = (15.0 <= medF <= 35.0) and (p10F >= 10.0) and (4.0 <= med_tp <= 14.0)
    return {"medF": medF, "p10F": p10F, "med_tp": med_tp, "n_excl": n_excl, "ok": passed}


COLS = ("ind", "sgn")
SPLIT = {"ind": SPLIT_IND, "sgn": SPLIT_SGN}


def simulate_A(v, i_a=I_A, churn=C_MIN, T=T_H):
    """§2.1 A + §3.1 казна + §2.3 артистный слой, обе контрактные колонки §6.
    Базовая казна — independent-w_t; signed-казна — справочно (дельта печатается).
    T2 hard assert на каждом шаге."""
    n = len(v)
    U = float(U0)
    act = {c: np.ones(n, bool) for c in COLS}
    cnt = {c: np.zeros(n, np.int32) for c in COLS}
    w = {c: 1.0 for c in COLS}
    treas = {c: 0.0 for c in COLS}
    U_tr = np.empty(T + 1)
    w_tr = {c: np.empty(T + 1) for c in COLS}
    T_tr = {c: np.empty(T + 1) for c in COLS}
    D_tr = {c: np.empty(T + 1) for c in COLS}
    for t in range(T + 1):
        U_tr[t] = U
        for c in COLS:
            w_tr[c][t] = w[c]
            T_tr[c][t] = treas[c]
            D = U * S_SF * (K_PAY / 12.0) * MEAN_GIFT * w[c]      # §2.1: донатный поток, $
            D_tr[c][t] = D
            inflow = FEE * D                                       # §3.1
            payout = RHO * inflow
            assert payout <= inflow + 1e-9, f"T2: payout>inflow t={t}"   # §7 T2
            assert treas[c] >= -1e-9, f"T2: T<0 t={t}"
            if t == T:
                continue
            treas[c] += inflow - payout
            inc = D * v * RAIL * SPLIT[c]                          # §2.3 + §6
            low = act[c] & (inc < ART_MIN)
            cnt[c] = np.where(low, cnt[c] + 1, 0)
            leave = act[c] & (cnt[c] >= ART_STREAK)                # P21
            if leave.any():
                act[c] &= ~leave
                w[c] = float(v[act[c]].sum())
        if t < T:
            U = U + (i_a - churn) * U
    return {"U": U_tr, "w": w_tr, "T": T_tr, "D": D_tr,
            "act": act, "n_left": {c: int(n - act[c].sum()) for c in COLS}}


def artists_B(payout_tr, v):
    """§2.3 B: inc_j,t = payoutB_t · v_j (стилизация, без обратной связи на динамику B),
    правило ухода P21, обе колонки §6. Векторно по (прогоны × артисты)."""
    R, T1 = payout_tr.shape
    out = {}
    for c in COLS:
        act = np.ones((R, N_ART), bool)
        cnt = np.zeros((R, N_ART), np.int16)
        for t in range(T1 - 1):                       # уходы месяцев 0..35 → w_36
            inc = payout_tr[:, t:t + 1] * v[None, :] * SPLIT[c]
            low = act & (inc < ART_MIN)
            cnt = np.where(low, cnt + 1, 0)
            act &= ~(act & (cnt >= ART_STREAK))
        w36 = act @ v                                 # (R,)
        n_left = N_ART - act.sum(axis=1)
        agg36 = payout_tr[:, -1] * w36 * SPLIT[c]     # агрегатный доход артистов/мес на t=36
        out[c] = {"w36": w36, "n_left": n_left, "agg36": agg36}
    return out


def falsifier(v):
    """§8: сетка c при i_A=0; смерть по DAU (§4) сим vs аналитика ln(0,04)/ln(1−c)."""
    rows = []
    for c in FALS_C:
        res = simulate_A(v, i_a=0.0, churn=c, T=FALS_T)
        tstar, has = death_month(res["U"][None, :])
        t_sim = int(tstar[0]) if has[0] else -1
        t_an = np.log(DEATH_FRAC) / np.log(1.0 - c)
        assert has[0] and abs(t_sim - t_an) <= 1.0, f"T2b: c={c} sim={t_sim} an={t_an:.2f}"
        rows.append({"c": c, "t_sim": t_sim, "t_an": t_an, "in36": t_sim <= 36})
    return rows


GRID_NU = (0.4, 0.6, 0.8)
GRID_UMAX = (10e6, 20e6, 40e6)
GRID_LAM = (0.35, 0.5, 0.65)
GRID_KAPPA_EXT = (0.35, 0.5, 0.65)   # §7.1: расширение один раз, если база не прошла


def run_grid(xi_I, xi_P, d_trig, kappas):
    rows = []
    for kap in kappas:
        for nu in GRID_NU:
            for um in GRID_UMAX:
                for lam in GRID_LAM:
                    st = t1_stats(simulate_B(nu, um, lam, kap, xi_I, xi_P, d_trig)["U"])
                    st.update(nu=nu, um=um, lam=lam, kap=kap)
                    rows.append(st)
    return rows


def calibrate(xi_I, xi_P, d_trig):
    """§7.1: среди прошедших T1 — медиана F ближе к 25; тай-брейк |med t_peak − 9|."""
    rows = run_grid(xi_I, xi_P, d_trig, (KAPPA,))
    extended = False
    if not any(r["ok"] for r in rows):
        extended = True
        rows = run_grid(xi_I, xi_P, d_trig, GRID_KAPPA_EXT)
    passed = [r for r in rows if r["ok"]]
    if not passed:
        print("СТОП §7.1: ни одна точка грида (включая расширение по κ) не прошла T1.")
        for r in rows:
            print(f"  κ={r['kap']:.2f} ν={r['nu']:.1f} Umax={r['um']/1e6:.0f}M λ={r['lam']:.2f}"
                  f" → medF={r['medF']:.1f} p10={r['p10F']:.1f} med_tp={r['med_tp']:.1f}"
                  f" excl={r['n_excl']}")
        sys.exit(1)
    best = min(passed, key=lambda r: (abs(r["medF"] - 25.0), abs(r["med_tp"] - 9.0)))
    return best, rows, extended


def mark(okay):
    return "✓" if okay else "✗"


def results_block(A, B, aB, fals, tstar, dead, med_t, q1_t, q3_t, tre_t, tre_dead):
    medU = np.median(B["U"], axis=0)
    medTB = np.median(B["TB"], axis=0)
    with np.errstate(divide="ignore"):     # inflow=0 в месяцы с U≥U_max → ratio=inf, медиана робастна
        ponziB = np.median(B["payout"][:, :T_H] / B["inflow"], axis=0)
    cross = int(np.argmax(ponziB > 1.0)) if (ponziB > 1.0).any() else -1
    n_dead = int(dead.sum())
    min_share = B["U"].min(axis=1) / B["U"].max(axis=1)
    print("==================== RESULTS ====================")
    print("-- Иерархия результатов (§7 v1.2) --")
    print(f"ФЛАГМАН (стресс-инвариант red team: обе формы цены, κ, δ_u, c_min≤12%, fee, σ_P=0):")
    print(f"   {int((min_share <= 0.20).sum())}/200 прогонов B теряют ≥80% пиковой аудитории"
          f" (худшее дно {min_share.max():.1%} пика)")
    print(f"Строгая статистика — ТОЛЬКО с квалификатором «при базовой форме цены §3.2»:")
    print(f"   {n_dead}/200 строгих смертей по §4, медиана t* = {med_t:.0f} мес"
          f" [IQR {q1_t:.0f}–{q3_t:.0f}] (форм-зависима, §11.1)")
    print("-- Режим A «Закон Tonify» (детерминированная траектория) --")
    print(f"DAU 36 мес: {A['U'][0]/1e6:.2f}M → {A['U'][T_H]/1e6:.2f}M (чистый рост +1%/мес);"
          f" смерть по DAU: не наступила (жив на горизонте)")
    print(f"казна T^A_36 = ${A['T']['ind'][T_H]:,.0f} (растущее плато; выплаты = ρ·приток);"
          f" смертей казны: 0 — структурно, T2")
    print("-- Режим B STEPN/Axie (200 прогонов) --")
    print(f"смерть по DAU (при базовой форме цены §3.2): {n_dead}/200 прогонов при t* ≤ 36;"
          f" медиана t* = {med_t:.0f} мес [IQR {q1_t:.0f}–{q3_t:.0f}];"
          f" живых на горизонте: {200 - n_dead}")
    hump = medTB[:11].max()
    print(f"пик DAU (медиана траектории): {medU.max()/1e6:.2f}M в t={int(medU.argmax())};"
          f" казна B в токене (Z·P, медиана): горб ${hump/1e6:.1f}M в t={int(medTB[:11].argmax())}"
          f" → обвал ×{hump/medTB[:20].min():.0f} (почти три порядка) к t={int(medTB[:20].argmin())};"
          f" поздняя накачка до ${medTB.max()/1e6:.1f}M (t={int(medTB.argmax())}) — артефакт феникса, §11.11")
    tre_med = float(np.median(np.asarray(tre_t)[tre_dead]))
    medTBd = float(np.median(B["TBd"][:, T_H]))
    print(f"смерть казны B (Z·P, порог 5% пика, §4): {int(tre_dead.sum())}/200, медиана t = {tre_med:.0f}"
          f" — раньше смерти продукта (медиана {med_t:.0f}) на ~{med_t - tre_med:.0f} мес. Это дефект")
    print(f"ДЕНОМИНАЦИИ, не расхода (§11.12): та же казна в $ по цене момента сбора монотонна —"
          f" 0/200 смертей,")
    print(f"медиана ${medTBd/1e6:.0f}M к t=36 (верхняя оценка: мгновенная конвертация без price"
          f" impact). Катастрофу")
    print(f"продукта создаёт эмиссия — два разных дефекта B. Казна A не умирает вообще (структурно, T2)")
    # --- T3a-iii (§7 v1.1): разбивка dead/zombie ---
    u36_share = B["U"][:, T_H] / B["U"].max(axis=1)
    zomb = np.where(~dead)[0]
    print(f"-- Разбивка dead/zombie (T3a-iii, §7 v1.1) --")
    print(f"строго мертвы (§4, 4% пика два мес подряд): {n_dead}/200;"
          f" зомби (потеряли ≥80% пика, но живы по §4): {len(zomb)}/200")
    print(f"зомби: min U_t/U_peak {min_share[zomb].min():.1%}–{min_share[zomb].max():.1%}"
          f" (медиана {np.median(min_share[zomb]):.1%});"
          f" U_36/U_peak {u36_share[zomb].min():.1%}–{u36_share[zomb].max():.1%}"
          f" (медиана {np.median(u36_share[zomb]):.1%})")
    for i in range(0, len(zomb), 6):
        print("   " + "  ".join(f"r={r:3d}: {min_share[r]*100:4.1f}/{u36_share[r]*100:4.1f}%"
                                for r in zomb[i:i + 6]))
    # --- §10 v1.2: квантили U_36 строго-мёртвых к пузырному пику (бегущий max на момент t*) ---
    didx = np.where(dead)[0]
    runmax = np.maximum.accumulate(B["U"], axis=1)
    bubble = runmax[didx, tstar[didx]]
    r36 = B["U"][didx, T_H] / bubble
    print(f"строго-мёртвые, U_36/пузырный_пик (бегущий max на момент t*): медиана {np.median(r36):.1%},"
          f" >50% пика: {int((r36 > 0.5).sum())}/{len(didx)}, >100%: {int((r36 > 1.0).sum())}/{len(didx)}")
    print(f"   (смерть §4 — событие пробоя, не поглощающее состояние; всё после первого пробоя,"
          f" включая U_36, — артефакт феникса, не прогноз; §11.11)")
    print("-- Коэффициент понциности payout/inflow (§3.2) --")
    print(f"A: 0.50 во все 36 месяцев (структурно = ρ; закон запрещает > 1)")
    print(f"B (медиана по прогонам, помесячно; >1 = платит больше, чем собирает):")
    for row in range(3):
        ts = range(row * 12, row * 12 + 12)
        print("   t=" + "".join(f"{t:>8d}" for t in ts))
        print("     " + "".join(f"{ponziB[t]:8.2f}" for t in ts))
    print(f"B пересекает 1.0 в месяц {cross} (замедление роста) и повторно в каждом цикле")
    print("-- Артистный слой (10 000 агентов; §6 обе контрактные колонки, direct-механизм) --")
    aggA = {c: A['D'][c][T_H] * RAIL * SPLIT[c] * A['w'][c][T_H] for c in COLS}
    row = lambda label, a, b: print(f"{label:<52s}{a:>14s}{b:>18s}")
    row("", "independent ×1,0", "signed-360 ×0,70")
    row("A агрегатный доход артистов, $/мес (t=36)", f"{aggA['ind']:,.0f}", f"{aggA['sgn']:,.0f}")
    row("A ушло артистов (выжило) из 10 000",
        f"{A['n_left']['ind']:,d} ({N_ART - A['n_left']['ind']:,d})",
        f"{A['n_left']['sgn']:,d} ({N_ART - A['n_left']['sgn']:,d})")
    row("A w_36 (коэффициент живого каталога)",
        f"{A['w']['ind'][T_H]:.3f}", f"{A['w']['sgn'][T_H]:.3f}")
    row("A казна при w соотв. колонки (справочно), $",
        f"{A['T']['ind'][T_H]:,.0f}", f"{A['T']['sgn'][T_H]:,.0f}")
    print(f"{'':52s}{'':>14s}{'дельта казны ' + format(A['T']['sgn'][T_H]/A['T']['ind'][T_H]-1, '+.2%'):>18s}")
    row("B* агрегатный доход артистов, $/мес (t=36, медиана)",
        f"{np.median(aB['ind']['agg36']):,.0f}", f"{np.median(aB['sgn']['agg36']):,.0f}")
    row("B* ушло артистов (выжило), медиана",
        f"{int(np.median(aB['ind']['n_left'])):,d} ({N_ART - int(np.median(aB['ind']['n_left'])):,d})",
        f"{int(np.median(aB['sgn']['n_left'])):,d} ({N_ART - int(np.median(aB['sgn']['n_left'])):,d})")
    row("B* w_36 (медиана)",
        f"{np.median(aB['ind']['w36']):.3f}", f"{np.median(aB['sgn']['w36']):.3f}")
    print("   * все артист-числа B — бумажная эмиссия по цене токена, не внешние деньги (§2.3, §10 v1.2)")
    print("-- Фальсификатор §8: A при i_A = 0, смерть по DAU --")
    print(f"   c, %/мес      t_death аналитика   t_death симуляция   умирает ≤ 36 мес?")
    for r in fals:
        print(f"   {r['c']*100:5.2f}%          {r['t_an']:7.1f}             {r['t_sim']:4d}"
              f"             {'да' if r['in36'] else 'нет'}")
    print(f"   порог горизонта c* = 1 − 0,04^(1/36) = {C_STAR*100:.3f}%/мес"
          f" (сеточное 8,55% — чуть ниже точного c*, смерть на t=37)")
    print(f"На бесконечном горизонте A с нулевым притоком умирает по DAU при ЛЮБОМ c > 0.")
    print(f"Обобщение (v1.2): динамика A зависит только от чистого темпа g = i_A − c, поэтому")
    print(f"смерть A по §4 ⇔ c − i_A ≥ 8,55%/мес — сетка §8 при i_A=0 покрывает все i_A через")
    print(f"чистый темп (red team: при i_A=6% смерть при c ≥ 14,6% ≈ 6% + 8,55% ✓).")
    n_loss = int((min_share <= 0.20).sum())
    zlo, zhi = min_share[zomb].min() * 100, min_share[zomb].max() * 100
    print(f"«Закон Tonify гарантирует ненулевую казну, но не бессмертие продукта: при чистом")
    print(f"темпе c − i_A ≥ 8,55%/мес продукт A умирает по хамстер-критерию внутри 36 мес —")
    print(f"разница с B в том, что смерть A требует внешней причины (продукт перестал")
    print(f"привлекать), а катастрофа B встроена в казначейскую механику: {n_loss}/200 прогонов")
    print(f"теряют ≥80% пиковой аудитории (инвариант ко всем стресс-формам red team, §11.1);")
    print(f"при базовой форме цены §3.2 медианная смерть по хамстер-критерию — месяц {med_t:.0f}")
    print(f"[IQR {q1_t:.0f}–{q3_t:.0f}]. Казна B, номинированная в собственном токене, «умирает»")
    print(f"раньше продукта (медиана — месяц {tre_med:.0f}) — но это дефект деноминации, а не расхода:")
    print(f"в $-моменте сбора она монотонно растёт, 0/200 смертей (§11.12); катастрофу продукта")
    print(f"создаёт эмиссия — это два разных дефекта режима B. Выжившие по строгому критерию")
    print(f"прогоны — не жизнь, а зомби-циклы на {zlo:.0f}–{zhi:.0f}% пика (§11.11).»")


def figures(A, B, tstar, dead, med_t, fals):
    plt.rcParams.update({"figure.facecolor":"#0D0A1A","axes.facecolor":"#0D0A1A","axes.edgecolor":"#B8C8DC",
     "axes.labelcolor":"#B8C8DC","text.color":"#B8C8DC","xtick.color":"#B8C8DC","ytick.color":"#B8C8DC","font.size":11})
    P,C,K,Y = "#6B2FFF","#00D4F5","#FF4D8D","#FFD426"
    INK = "#B8C8DC"
    OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures"))
    mo = np.arange(T_H + 1)
    medU = np.median(B["U"], axis=0)
    q25, q75 = np.percentile(B["U"], [25, 75], axis=0)
    medTB = np.median(B["TB"], axis=0)

    # ---------- fig11: рабочая, 3 панели (§9) ----------
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.9))
    a = ax[0]
    a.plot(mo, A["U"], color=P, lw=2.8, label="A «выплаты ≤ приток» — симуляция (детерминир.)")
    a.plot(mo, medU, color=K, lw=2.8, label="B «из эмиссии» — симуляция (медиана, 200 прогонов)")
    a.fill_between(mo, q25, q75, color=K, alpha=0.18, lw=0, label="B: IQR 25–75%")
    a.axhline(DEATH_FRAC * medU.max(), color=Y, lw=1.5, ls="--",
              label=f"порог смерти: 4% пика B ({DEATH_FRAC*medU.max()/1e6:.2f}M)")
    a.set_yscale("log"); a.grid(alpha=0.15); a.legend(frameon=False, fontsize=8, loc="lower left")
    a.set_xlabel("месяц"); a.set_ylabel("DAU (log)")
    a.set_title("(a) DAU: закон против эмиссии")
    b = ax[1]
    b.plot(mo, A["T"]["ind"], color=P, lw=2.8, label="казна A, $ — симуляция (детерминир.)")
    b.plot(mo, medTB, color=K, lw=2.8, label="казна B = Z·P, $ — симуляция (медиана)")
    b.text(T_H - 0.5, A["T"]["ind"][T_H] * 1.6, "казна A: растущее плато", color=INK,
           fontsize=9, ha="right", va="bottom")
    b.text(T_H - 0.5, medTB[T_H] * 2.2, "казна B: горб, обвал,\nзомби-накачка Z·P", color=INK,
           fontsize=9, ha="right", va="bottom")
    b.set_yscale("log"); b.grid(alpha=0.15); b.legend(frameon=False, fontsize=8, loc="lower right")
    b.set_xlabel("месяц"); b.set_ylabel("казна, $ (log)")
    b.set_title("(b) казна: реальные $ против токена")
    c = ax[2]
    cc = np.linspace(0.015, 0.45, 300)
    c.plot(cc * 100, np.log(DEATH_FRAC) / np.log(1 - cc), color=C, lw=2.4,
           label="аналитика: t=ln(0,04)/ln(1−c)")
    c.scatter([r["c"] * 100 for r in fals], [r["t_sim"] for r in fals], color=P, zorder=5,
              s=42, label="симуляция A (i_A=0), сетка §8")
    c.axvline(C_STAR * 100, color=Y, lw=1.5, ls=":",
              label=f"c* = {C_STAR*100:.2f}%/мес (порог 36 мес)")
    c.set_yscale("log"); c.grid(alpha=0.15); c.legend(frameon=False, fontsize=8)
    c.set_xlabel("отток c, %/мес (приток = 0)"); c.set_ylabel("t_death, мес (log)")
    c.set_title("(c) фальсификатор: аналитика vs симуляция")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig11_treasury_dau.png"), dpi=150)
    plt.close(fig)

    # ---------- fig12: распределение месяца смерти B (§9) ----------
    fig, a = plt.subplots(figsize=(9, 5.5))
    n_dead = int(dead.sum()); n_alive = R_RUNS - n_dead
    a.hist(tstar[dead], bins=np.arange(-0.5, 37.5, 1.0), weights=np.full(n_dead, 1 / R_RUNS),
           color=K, alpha=0.9, label="месяц смерти t* — симуляция (200 прогонов, критерий §4)")
    if n_alive:
        a.bar(37, n_alive / R_RUNS, width=1.0, color=C, alpha=0.9,
              label=f"«36+»: живы на горизонте ({n_alive} прогонов)")
    a.axvline(med_t, color=Y, lw=2, ls="--", label=f"медиана t* = {med_t:.0f} мес")
    a.text(0.02, 0.97, f"мертво: {n_dead}/200 при t* ≤ 36\n"
           "режим A: смертей казны 0/всех конфигураций\n(структурно, T2); по DAU при базовом\nросте — жив на горизонте",
           transform=a.transAxes, va="top", fontsize=9, color=INK)
    a.grid(alpha=0.15); a.legend(frameon=False, fontsize=9, loc="center right")
    a.set_xlabel("месяц смерти t* (критерий §4: DAU < 4% пика два месяца подряд)")
    a.set_ylabel("доля прогонов")
    a.set_title("Режим B: распределение даты смерти, 200 прогонов")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig12_death_dist.png"), dpi=150)
    plt.close(fig)

    # ---------- fig13: слайд «две кривые» (§9) ----------
    fig, a = plt.subplots(figsize=(9, 5.5))
    a.plot(mo, A["U"] / A["U"].max(), color=P, lw=4)
    a.plot(mo, medU / medU.max(), color=K, lw=4)
    a.axvline(med_t, color=Y, lw=1.8, ls="--")
    a.text(med_t + 0.6, 0.86, f"медиана смерти B:\nмесяц {med_t:.0f}", color=INK, fontsize=11)
    a.text(26.5, A["U"][27] / A["U"].max() + 0.06, "выплаты ≤ приток", color=INK,
           fontsize=15, fontweight="bold")
    a.text(8.2, 0.62, "выплаты из эмиссии", color=INK, fontsize=15, fontweight="bold")
    a.set_xlabel("месяц"); a.set_ylabel("DAU, доля пика")
    a.set_xlim(0, 36); a.set_ylim(0, 1.12)
    a.text(0.0, -0.15, "A: детерминированная симуляция; B: медиана 200 прогонов; "
           "калибровка ×25/6 мес — Hamster (Caladan, апр. 2026);\n"
           "наклон A — допущение (органика 6%/мес > churn 5%/мес, P2–P3): "
           "закон Tonify гарантирует казну ≥ 0, не рост DAU",
           transform=a.transAxes, fontsize=8, color=INK)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig13_two_curves.png"), dpi=150)
    plt.close(fig)


def main():
    t_start = time.time()
    v = build_artist_weights()
    top1 = float(np.sort(v)[-int(N_ART * 0.01):].sum())
    xi_I, xi_P, d_trig = draw_noise()

    # --- §7.1: грид гоняется каждый запуск; выбор обязан совпасть с константами базы ---
    best, grid_rows, grid_ext = calibrate(xi_I, xi_P, d_trig)
    assert (best["nu"], best["um"], best["lam"], best["kap"]) == (NU, U_MAX, LAM, KAPPA), \
        "грид §7.1 выбрал другую точку — обновить константы NU/U_MAX/LAM/KAPPA"

    # --- базовые прогоны ---
    B = simulate_B(NU, U_MAX, LAM, KAPPA, xi_I, xi_P, d_trig)
    tstar, dead = death_month(B["U"])
    n_dead = int(dead.sum())
    med_t = float(np.median(tstar[dead]))
    q1_t, q3_t = np.percentile(tstar[dead], [25, 75])
    tre_t, tre_dead = death_month(B["TB"], TRE_DEATH_FRAC)
    A = simulate_A(v)
    fals = falsifier(v)                      # T2b assert внутри
    aB = artists_B(B["payout"], v)

    # --- T3a v1.1 (§7): (i) потеря ≥80% пика у 200/200; (ii) медиана строгого t* ≤ 36 ---
    min_share = B["U"].min(axis=1) / B["U"].max(axis=1)      # min_{t≤36} U_t / U_peak
    t3a_i = bool((min_share <= 0.20).all())
    n_loss = int((min_share <= 0.20).sum())
    t3a_ii = n_dead >= 101                                    # ⇔ медиана t* ≤ 36 (спека §7)
    t3a_ok = t3a_i and t3a_ii

    # --- T3b ---
    inflow0 = FEE * U0 * S_SF * (K_PAY / 12.0) * MEAN_GIFT
    t3b_ok = abs(inflow0 - 1955.0) <= 0.01 * 1955.0
    t2b_max = max(abs(r["t_sim"] - r["t_an"]) for r in fals)

    # ================= VALIDATION (§7; печатается ДО результатов) =================
    print("==================== VALIDATION ====================")
    print(f"Мир артистов §2.3 (N={N_ART:,}, default_rng(42)): топ-1% весов держит"
          f" {top1:5.1%}   (мишень ≥ 50%) {mark(top1 >= 0.5)}")
    print(f"T1  калибровка B консистентна с Hamster ×25/6 мес (v1.2: не «воспроизводит»)"
          f" — грид §7.1: 27 точек × {R_RUNS} прогонов,"
          f" прошло {sum(r['ok'] for r in grid_rows)}, расширение по κ: {'да' if grid_ext else 'не потребовалось'}")
    print(f"    выбранная точка (медиана F ближе к 25): ν={NU}, U_max={U_MAX/1e6:.0f}M, λ={LAM},"
          f" κ={KAPPA} — зафиксирована в коде")
    print(f"    семантика (v1.2): масштаб F задаёт клип c_max (P13, тот же хамстер-якорь) —"
          f" полуциркулярность;")
    print(f"    эмерджентное — тайминг пика и эндогенный выход оттока на потолок c_max")
    print(f"    медиана F        : {best['medF']:6.2f}   (мишень [15; 35]) {mark(15 <= best['medF'] <= 35)}")
    print(f"    P10 F            : {best['p10F']:6.2f}   (мишень ≥ 10) {mark(best['p10F'] >= 10)}")
    print(f"    медиана t_peak   : {best['med_tp']:6.1f}   (мишень [4; 14]) {mark(4 <= best['med_tp'] <= 14)}")
    print(f"    исключено прогонов (t_peak > 30): {best['n_excl']}/{R_RUNS}")
    print(f"T2  закон A (hard assert каждый шаг: база, сетка §8, обе колонки):"
          f" payout ≤ inflow, T ≥ 0 — нарушений 0 ✓")
    print(f"T2b фальсификатор: |t_death сим − аналитика| ≤ 1 мес: max Δ = {t2b_max:.3f}"
          f" (c=41,5%, дискретизация) {mark(t2b_max <= 1)}")
    print(f"T3a (ред. v1.1) катастрофа B при базовых параметрах:")
    print(f"    (i)  потеря ≥80% пика, min U_t ≤ 0,20·U_peak: {n_loss}/{R_RUNS},"
          f" худшее дно {min_share.max():.1%} пика   (мишень 200/200) {mark(t3a_i)}")
    print(f"    (ii) медиана строгого t* (критерий §4) ≤ 36: строгих смертей {n_dead}/{R_RUNS} ≥ 101,"
          f" медиана t* = {med_t:.0f} мес {mark(t3a_ii)}")
    print(f"    (iii) разбивка dead/zombie — в RESULTS")
    print(f"T3b приток казны A при U=1M, w=1: ${inflow0:,.2f}/мес   (мишень $1 955 ± 1%) {mark(t3b_ok)}")
    verdict_ok = (top1 >= 0.5) and best["ok"] and t2b_max <= 1 and t3a_ok and t3b_ok
    print(f"ВЕРДИКТ §7: {'все мишени зелёные — принимается' if verdict_ok else 'есть провал мишени — симуляция по правилу §7 НЕ принимается'}")

    print()
    results_block(A, B, aB, fals, tstar, dead, med_t, q1_t, q3_t, tre_t, tre_dead)
    figures(A, B, tstar, dead, med_t, fals)
    print(f"[t] {time.time() - t_start:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
