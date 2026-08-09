# -*- coding: utf-8 -*-
"""
TONIFY SIM 2 — распространение музыки по социальному графу Telegram
BA(50k, m=3) + плантированные клики с перекрытием (чаты), complex contagion (Centola k=2),
посев в хабы против random против random-cliques. Реализация SPEC v1.1 (sim2/SPEC.md), seed=42.
Динамика — лемма 2.4: один sparse-matvec на раунд, fires-once, монетка will_share один раз.
"""
import os, sys
import numpy as np
from numpy.random import default_rng, SeedSequence
from scipy import sparse
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- Константы спеки (§1) ----------
N          = 50_000          # узлов (ТЗ)
M_BA       = 3               # BA attachment (ТЗ)
SEED       = 42              # глобальный seed (ТЗ)
MU_S       = np.log(12.0)    # лог-нормаль размеров клик: медиана 12 (допущение §1.4)
SIGMA_S    = 0.6
S_MIN, S_MAX = 5, 40         # клиппинг размеров (ТЗ)
N_CLIQUES  = 3_460           # калибровка на покрытие q=0,50 (§1.5)
N_PAR      = 2               # родителей у чата c>=2 (§1.7)
OVERLAP    = 2               # o: общих узлов с каждым родителем (§1.7)
K_COMPLEX  = 2               # порог Centola (ТЗ)
K_SIMPLE   = 1               # режим сравнения (ТЗ)
P_GRID     = np.round(np.arange(0.05, 1.0001, 0.05), 2)   # 20 точек (§1.10)
MACRO_FRAC = 0.05            # макрокаскад = охват >= 5% N; правило p* и P_macro (§1.11, §3.4)
BUDGETS    = [1, 2, 5, 10, 20, 50, 100, 200, 500]         # §1.14
RUNS_A, RUNS_B, RUNS_C = 30, 40, 40                        # §1.15
T_MAX      = 100             # §1.16
SEED_CHAT_LO, SEED_CHAT_HI = 10, 14                        # окно чата-посева (§1.17)
N_GIF, C_GIF = 4_000, 277                                  # §1.22

# ---------- Палитра sim1 (ТЗ) ----------
plt.rcParams.update({"figure.facecolor":"#0D0A1A","axes.facecolor":"#0D0A1A","axes.edgecolor":"#B8C8DC",
 "axes.labelcolor":"#B8C8DC","text.color":"#B8C8DC","xtick.color":"#B8C8DC","ytick.color":"#B8C8DC","font.size":11})
P,C,K,Y = "#6B2FFF","#00D4F5","#FF4D8D","#FFD426"
INK   = "#B8C8DC"
DIM   = "#2A2342"            # непринявшие с 0 касаний (gif, §7)
FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")


def rng_for(exp, point, run):
    """Иерархия RNG спеки §8: exp 0=посадка клик, 1=A, 2=B, 3=C, 4=gif."""
    return default_rng(SeedSequence(SEED, spawn_key=(exp, point, run)))


# ---------- Конструкция графа (§2) ----------
def sample_clique_sizes(rng, n_cliques):
    """Размеры чатов: клипнутая округлённая лог-нормаль (§2.2, шаг 1)."""
    raw = rng.lognormal(mean=MU_S, sigma=SIGMA_S, size=n_cliques)
    return np.clip(np.round(raw), S_MIN, S_MAX).astype(np.int64)


def build_graph(n, m_ba, n_cliques, nx_seed, clique_rng):
    """BA-подложка + плантированные клики с перекрытием (§2.2 v1.1).
    Наследование: чат 0 — без родителей; чат 1 — родитель чат 0; чат c>=2 — N_PAR разных
    родителей равномерно из уже посаженных; из каждого родителя OVERLAP участников без
    повторов; дубли между родительскими парами схлопываются; остаток — свежий добор.
    Возвращает (A_ba_csr, A_csr, membership, sizes). Граф простой (§2.2, шаг 4а)."""
    g_ba = nx.barabasi_albert_graph(n=n, m=m_ba, seed=nx_seed)
    ba_edges = np.array(g_ba.edges(), dtype=np.int64)          # (E, 2)

    sizes = sample_clique_sizes(clique_rng, n_cliques)
    membership = []                                            # чат -> массив узлов (§2.2, шаг 4б)
    extra_u, extra_v = [], []
    for c, s in enumerate(sizes):
        s = int(s)
        if c == 0:
            parents = []
        elif c == 1:
            parents = [0]
        else:
            parents = list(clique_rng.choice(c, size=N_PAR, replace=False))
        if len(parents):
            inherited = np.unique(np.concatenate(
                [clique_rng.choice(membership[par], size=OVERLAP, replace=False)
                 for par in parents]))                          # уникальных <= N_PAR*OVERLAP < S_MIN
        else:
            inherited = np.empty(0, dtype=np.int64)
        need = s - len(inherited)
        pool = clique_rng.choice(n, size=need + len(inherited), replace=False)
        fresh = pool[~np.isin(pool, inherited)][:need]         # свежий добор без повторов в чате
        nodes = np.concatenate([inherited, fresh])
        membership.append(nodes)
        iu, iv = np.triu_indices(s, k=1)                       # все попарные рёбра клики
        extra_u.append(nodes[iu]); extra_v.append(nodes[iv])
    cl_u = np.concatenate(extra_u); cl_v = np.concatenate(extra_v)

    def to_csr(us, vs):
        row = np.concatenate([us, vs]); col = np.concatenate([vs, us])   # симметризация
        data = np.ones(len(row), dtype=np.int32)
        a = sparse.coo_matrix((data, (row, col)), shape=(n, n)).tocsr()
        a.data[:] = 1                                          # дедуп: кратные рёбра -> простой граф
        return a

    a_ba = to_csr(ba_edges[:, 0], ba_edges[:, 1])
    a_full = to_csr(np.concatenate([ba_edges[:, 0], cl_u]),
                    np.concatenate([ba_edges[:, 1], cl_v]))
    return a_ba, a_full, membership, sizes


def degrees(a_csr):
    return np.diff(a_csr.indptr)


def top_hubs(deg, b):
    """Топ-B по степени союзного G, тай-брейк — меньший id (§2.3): stable-сорт по -deg."""
    return np.argsort(-deg, kind="stable")[:b]


# ---------- Механика заражения (§3, лемма 2.4) ----------
def run_cascade(a_csr, seed_nodes, k, p, rng, track_history=False):
    """Синхронные раунды §3.3: touches += A_csr @ indicator(sharers_t); fires-once;
    монетка will_share один раз в момент принятия; посев транслирует с p_seed=1.
    Возвращает (охват |A|, gen_sizes, hit_tmax [, history])."""
    n = a_csr.shape[0]
    adopted = np.zeros(n, dtype=bool)
    touches = np.zeros(n, dtype=np.int32)
    ind = np.zeros(n, dtype=np.int32)
    seed_nodes = np.asarray(seed_nodes)
    adopted[seed_nodes] = True
    sharers = seed_nodes                       # will_share=да для всех сеяных (p_seed=1)
    gen_sizes = [len(seed_nodes)]              # G_0 = посев
    history = []                               # (sharers_t, touches.copy(), adopted.copy()) на раунд
    t, hit_tmax = 0, False
    while len(sharers):
        if t == T_MAX:
            hit_tmax = True
            break
        t += 1
        ind[:] = 0; ind[sharers] = 1
        touches += a_csr @ ind                 # лемма 2.4: один matvec на раунд
        new = np.where(~adopted & (touches >= k))[0]
        adopted[new] = True
        coin = rng.random(len(new)) < p        # монетка один раз, навсегда
        gen_sizes.append(len(new))
        if track_history:
            history.append((sharers, touches.copy(), adopted.copy()))
        sharers = new[coin]                    # транслируют ровно один раз — в следующем раунде
    reach = int(adopted.sum())                 # охват = |A| в терминации, включая посев
    if track_history:
        return reach, gen_sizes, hit_tmax, history
    return reach, gen_sizes, hit_tmax


def r_eff(gen_sizes):
    """R_eff = (|G2|+|G3|+|G4|)/(|G1|+|G2|+|G3|); при нулевом знаменателе 0 (§3.4)."""
    g = gen_sizes + [0] * (5 - len(gen_sizes))
    denom = g[1] + g[2] + g[3]
    return (g[2] + g[3] + g[4]) / denom if denom > 0 else 0.0


# ---------- Посевы (§1.15, §1.16, §4.1) ----------
def seed_random_chat(membership, chat_pool, rng):
    """Один случайный чат размера 10–14, весь состав (Centola-соседство, §4.2)."""
    return membership[rng.choice(chat_pool)]


def seed_ba_local(a_ba, deg_ba, cand_ba, rng):
    """G_BA: узел степени >= 11 + 11 его случайных соседей, итого 12 (§1.16)."""
    u = rng.choice(cand_ba)
    neigh = a_ba.indices[a_ba.indptr[u]:a_ba.indptr[u + 1]]
    return np.concatenate([[u], rng.choice(neigh, size=11, replace=False)])


def seed_random_cliques(membership, budget, rng):
    """Чаты равномерно без повторов; сеются все участники; добор по числу НОВЫХ узлов;
    последний чат — случайный поднабор ровно до B (§4.1)."""
    order = rng.permutation(len(membership))
    seeded = np.zeros(N, dtype=bool)
    picked, total = [], 0
    for c in order:
        newcomers = membership[c][~seeded[membership[c]]]
        if total + len(newcomers) >= budget:
            need = budget - total
            picked.append(rng.choice(newcomers, size=need, replace=False))
            break
        picked.append(newcomers); seeded[newcomers] = True; total += len(newcomers)
    return np.concatenate(picked)


# ---------- Эксперимент B — фазовая диаграмма (§4.2), гонится ПЕРВЫМ ----------
def experiment_b(a_full, membership, chat_pool):
    """20 точек p x {k=1,2} x 40 прогонов. Агрегаты v1.1 (§3.4, §4.2): охват — медиана+IQR
    И mean; R_eff — среднее по прогонам с G1>=1 (условный); P_macro = P(охват >= 5% N)."""
    res = {}
    for k in (K_SIMPLE, K_COMPLEX):
        rows = []
        for pi, p in enumerate(P_GRID):
            reaches, reffs, g1s, tmax_hits = [], [], [], 0
            for run in range(RUNS_B):
                rng = rng_for(2, k * 100 + pi, run)
                seeds = seed_random_chat(membership, chat_pool, rng)
                reach, gens, hit = run_cascade(a_full, seeds, k, p, rng)
                reaches.append(reach / N); reffs.append(r_eff(gens))
                g1s.append(gens[1] if len(gens) > 1 else 0); tmax_hits += hit
            reaches = np.array(reaches); reffs = np.array(reffs); g1s = np.array(g1s)
            ignited = g1s >= 1
            rows.append({"p": p,
                         "reach_med": float(np.median(reaches)),
                         "reach_q1": float(np.percentile(reaches, 25)),
                         "reach_q3": float(np.percentile(reaches, 75)),
                         "reach_mean": float(np.mean(reaches)),
                         "p_macro": float(np.mean(reaches >= MACRO_FRAC)),
                         "reff_cond": float(np.mean(reffs[ignited])) if ignited.any() else 0.0,
                         "tmax": tmax_hits})
        res[k] = rows
    return res


def p_c_from_b(res_b, k):
    """p_c(k) = min{p из сетки: mean охват >= 5% N} (§4.2); p*(v1.1) = p_c(k=2) (§4.1).
    None если не существует."""
    for row in res_b[k]:
        if row["reach_mean"] >= MACRO_FRAC:
            return row["p"]
    return None


# ---------- Эксперимент A — посев при равном бюджете (§4.1) ----------
# strategy_id приколочен §4.1 v1.3: 0=random, 1=top-hubs, 2=random-cliques (как v1.2,
# опубликованные числа воспроизводятся байт-в-байт), 3=top-BA (КОНТРОЛЬНАЯ, v1.3).
STRATEGIES = ("random", "top-hubs", "random-cliques", "top-BA")

def experiment_a(a_full, membership, deg, deg_ba, p_star):
    """9 бюджетов x 4 стратегии x 30 прогонов, complex k=2, p=p*.
    top-BA — топ-B по степени ЧИСТОГО G_BA (контроль «каналы vs чат-хопперы», §4.1 v1.3;
    в критерий фальсификатора §6 не входит). Возвращает res[strategy][b_index]."""
    hubs_cache = {b: top_hubs(deg, b) for b in BUDGETS}
    hubs_ba_cache = {b: top_hubs(deg_ba, b) for b in BUDGETS}
    res = {}
    for sid, strat in enumerate(STRATEGIES):
        rows = []
        for bi, b in enumerate(BUDGETS):
            rps = []
            for run in range(RUNS_A):
                rng = rng_for(1, sid * 100 + bi, run)
                if strat == "random":
                    seeds = rng.choice(N, size=b, replace=False)
                elif strat == "top-hubs":
                    seeds = hubs_cache[b]      # детерминирован; стохастика — в монетках p
                elif strat == "top-BA":
                    seeds = hubs_ba_cache[b]   # детерминирован; тай-брейк меньший id
                else:
                    seeds = seed_random_cliques(membership, b, rng)
                reach, _, _ = run_cascade(a_full, seeds, K_COMPLEX, p_star, rng)
                rps.append((reach - b) / b)    # reach-per-seed = (охват - B)/B
            rps = np.array(rps)
            rows.append({"B": b, "mean": float(np.mean(rps)),
                         "sem": float(np.std(rps, ddof=1) / np.sqrt(len(rps)))})
        res[strat] = rows
    return res


def hub_decomposition(deg, deg_ba, membership):
    """Декомпозиция хабов (§4.1 v1.3): H500=топ-500 по deg_G, H500_BA=топ-500 по deg_BA.
    Возвращает (доля кликовой степени у H500, |H500 ∩ H500_BA|, медиана и max членств H500)."""
    h500 = top_hubs(deg, 500)
    h500_ba = top_hubs(deg_ba, 500)
    clique_share = float((deg[h500] - deg_ba[h500]).sum() / deg[h500].sum())
    inter = len(np.intersect1d(h500, h500_ba))
    memb_count = np.zeros(N, dtype=np.int64)
    for m in membership:
        memb_count[m] += 1
    return clique_share, inter, float(np.median(memb_count[h500])), int(memb_count[h500].max())


# ---------- Эксперимент C — контраст Centola 2x2 (§4.3) ----------
def experiment_c(a_full, a_ba, membership, chat_pool, p_c_run):
    """Ячейки (граф x механика), cell_id: 0=(G,k=1), 1=(G,k=2), 2=(G_BA,k=1), 3=(G_BA,k=2).
    Метрика мишени T3 — P_macro (v1.2, §4.3); mean-охват — справочно."""
    deg_ba = degrees(a_ba)
    cand_ba = np.where(deg_ba >= 11)[0]
    cells = {}
    for cell_id, (graph_name, k) in enumerate(
            [("G", K_SIMPLE), ("G", K_COMPLEX), ("G_BA", K_SIMPLE), ("G_BA", K_COMPLEX)]):
        a = a_full if graph_name == "G" else a_ba
        reaches = []
        for run in range(RUNS_C):
            rng = rng_for(3, cell_id, run)
            if graph_name == "G":
                seeds = seed_random_chat(membership, chat_pool, rng)
            else:
                seeds = seed_ba_local(a_ba, deg_ba, cand_ba, rng)
            reach, _, _ = run_cascade(a, seeds, k, p_c_run, rng)
            reaches.append(reach / N)
        reaches = np.array(reaches)
        cells[(graph_name, k)] = {"p_macro": float(np.mean(reaches >= MACRO_FRAC)),
                                  "mean": float(np.mean(reaches))}
    return cells


# ---------- Валидация (§5) и аналитика ----------
def newman_mle_gamma(deg, k_min=15):
    """Дискретный MLE Ньюмана: gamma = 1 + n·[sum ln(k_i/(k_min-0.5))]^{-1} (T1)."""
    tail = deg[deg >= k_min]
    return 1.0 + len(tail) / np.sum(np.log(tail / (k_min - 0.5)))


def mf_percolation_threshold(deg):
    """p_c^MF = <k>/(<k^2>-<k>) по фактическим степеням G (Newman 2002)."""
    k1, k2 = deg.mean(), (deg.astype(np.float64) ** 2).mean()
    return k1 / (k2 - k1)


def coverage(membership):
    """Доля узлов, состоящих в >= 1 чате (T2b)."""
    in_chat = np.zeros(N, dtype=bool)
    for nodes in membership:
        in_chat[nodes] = True
    return float(in_chat.mean())


def bridge_layer(membership):
    """Мостовой граф чатов B_chat (§2.2): вершины — чаты, ребро — пересечение >= OVERLAP узлами.
    Возвращает (доля чатов c>=1 с >=1 мостом, средняя степень d̄, число компонент связности)."""
    c = len(membership)
    rows = np.concatenate([np.full(len(m), i, dtype=np.int64) for i, m in enumerate(membership)])
    cols = np.concatenate(membership)
    inc = sparse.coo_matrix((np.ones(len(rows), np.int32), (rows, cols)), shape=(c, N)).tocsr()
    inter = (inc @ inc.T).tocoo()                              # число общих узлов между чатами
    mask = (inter.data >= OVERLAP) & (inter.row != inter.col)  # широкий мост
    b = sparse.coo_matrix((np.ones(mask.sum(), np.int32), (inter.row[mask], inter.col[mask])),
                          shape=(c, c)).tocsr()
    deg_b = np.diff(b.indptr)
    frac_bridged = float((deg_b[1:] >= 1).mean())              # мишень T2c(а): чаты c >= 1
    n_comp = sparse.csgraph.connected_components(b, directed=False)[0]
    return frac_bridged, float(deg_b.mean()), n_comp


def build_validation(gamma_hat, sizes, cov, bridge, p_star, cells):
    """Список мишеней: (id, описание, получено-строка, допуск-строка, ok). v1.1: +T2c, T3 на mean."""
    med, mean = float(np.median(sizes)), float(np.mean(sizes))
    p5, p40 = float(np.mean(sizes == S_MIN)), float(np.mean(sizes == S_MAX))
    frac_bridged, d_bridge, _ = bridge
    v = [
        ("T1",  "хвост степеней G_BA: MLE Ньюмана, k_min=15", f"γ̂ = {gamma_hat:.3f}",
         "γ̂ ∈ [2,60; 3,40]", 2.6 <= gamma_hat <= 3.4),
        ("T2",  "размеры клик: медиана", f"{med:.1f}", "∈ [11; 13]", 11 <= med <= 13),
        ("T2",  "размеры клик: среднее", f"{mean:.2f}", "∈ [13,30; 15,00]", 13.3 <= mean <= 15.0),
        ("T2",  "размеры клик: P(s=5)", f"{p5:.3f}", "≤ 0,12", p5 <= 0.12),
        ("T2",  "размеры клик: P(s=40)", f"{p40:.3f}", "≤ 0,04", p40 <= 0.04),
        ("T2b", "покрытие: доля узлов в ≥1 чате", f"{cov:.3f}", "∈ [0,45; 0,55]", 0.45 <= cov <= 0.55),
        ("T2c", "мостовой слой: доля чатов c≥1 с ≥1 мостом", f"{frac_bridged:.4f}", "≥ 0,99",
         frac_bridged >= 0.99),
        ("T2c", "мостовой слой: средняя степень d̄(B_chat)", f"{d_bridge:.2f}", "∈ [4,0; 5,5]",
         4.0 <= d_bridge <= 5.5),
    ]
    if p_star is None:
        v.append(("T3", "контраст Centola (§4.3)", "p* не существует", "три неравенства §5", False))
    else:                                              # v1.2: единая метрика T3 — P_macro (§5)
        a_ = cells[("G_BA", 1)]["p_macro"]
        b_ = cells[("G_BA", 2)]["p_macro"]
        c_ = cells[("G", 2)]["p_macro"]
        v += [
            ("T3", "G_BA, simple k=1: P_macro", f"{a_:.3f}", "≥ 0,75", a_ >= 0.75),
            ("T3", "G_BA, complex k=2: P_macro", f"{b_:.3f}", "≤ 0,25", b_ <= 0.25),
            ("T3", "G, complex k=2: P_macro", f"{c_:.3f}", "≥ 0,75", c_ >= 0.75),
        ]
    return v


def print_validation(v):
    print("==================== VALIDATION (мишень → получено → допуск → PASS/FAIL) ====================")
    for tid, desc, got, tol, ok in v:
        print(f"{tid:<4} {desc:<42}: {got:>18}   допуск {tol:<22} {'PASS' if ok else 'FAIL'}")
    return all(ok for *_, ok in v)


def print_b_table(res_b):
    """Фазовые числа эксперимента B (агрегаты v1.1)."""
    print("\n==================== ЭКСПЕРИМЕНТ B — фазовые числа (40 прогонов/точку) ====================")
    for k in (K_SIMPLE, K_COMPLEX):
        print(f"k={k}:   p   охват_мед %N   IQR %N              охват_ср %N   P_macro   R_eff|G₁≥1")
        for r in res_b[k]:
            print(f"     {r['p']:.2f}   {r['reach_med']*100:>10.2f}   "
                  f"[{r['reach_q1']*100:6.2f}; {r['reach_q3']*100:6.2f}]   "
                  f"{r['reach_mean']*100:>11.2f}   {r['p_macro']:>7.3f}   {r['reff_cond']:>10.3f}")
    tmax_total = sum(r["tmax"] for k in res_b for r in res_b[k])
    print(f"выходов по T_max={T_MAX}: {tmax_total}")


def falsifier_verdict(res_a):
    """Вердикт фальсификатора GTM §6 — одна из трёх формулировок, на средних.
    v1.2: B=1 структурно вырожден при k=2 (двух разных источников от одного узла нет,
    все стратегии дают 0) — исключён из критерия; сравнение на B >= 2."""
    hubs = np.array([r["mean"] for r in res_a["top-hubs"]])[1:]
    rnd  = np.array([r["mean"] for r in res_a["random"]])[1:]
    budgets = BUDGETS[1:]
    beats = hubs > rnd
    if not beats.any():
        return ("Гипотеза хабов Tonify неверна: при complex contagion посев в топ-хабы "
                "не бьёт случайный посев при равном бюджете")
    if beats.all():
        return ("гипотеза хабов подтверждена на всех бюджетах B ∈ "
                f"[{budgets[0]}; {budgets[-1]}]: mean reach-per-seed(top-hubs) > random "
                "на всей сетке (B=1 исключён как вырожденный, §6)")
    won = [str(b) for b, w in zip(budgets, beats) if w]
    return (f"гипотеза хабов подтверждена только для бюджетов из [{', '.join(won)}]; "
            "вне интервала — неверна")


# ---------- Фигуры (§7) ----------
FIG_L = {
 "en": dict(tag_ba="control §4.1; simulation", tag="simulation", sem="mean ± 1 SEM",
    y0="analytic: seeding without multiplication (y = 0)",
    b1="B=1: all strategies at 0 —\na complex track cannot be seeded by one post (§6);\nexcluded from the falsifier criterion",
    f8_xl="Seeding budget B, nodes (log)", f8_yl="Reach-per-seed = (reach − B)/B",
    f8_t="Equal-budget seeding: complex k=2, p = p* = {p:.2f}"),
 "ru": dict(tag_ba="контроль §4.1; симуляция", tag="симуляция", sem="среднее ± 1 SEM",
    y0="аналитика: посев без размножения (y = 0)",
    b1="B=1: у всех стратегий 0 —\ncomplex-трек не сеется одним постом (§6);\nиз критерия фальсификатора исключён",
    f8_xl="Бюджет посева B, узлов (log)", f8_yl="Reach-per-seed = (охват − B)/B",
    f8_t="Посев при равном бюджете: complex k=2, p = p* = {p:.2f}"),
}

def make_fig8(res_a, p_star, lang="en", outdir=None):
    """Эксперимент A: reach-per-seed vs бюджет, среднее ± 1 SEM, 30 прогонов."""
    L = FIG_L[lang]; outdir = outdir or FIGDIR; os.makedirs(outdir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    colors = {"top-hubs": P, "random": C, "random-cliques": K, "top-BA": "#00E08F"}
    for strat in ("top-hubs", "random", "random-cliques", "top-BA"):
        rows = res_a[strat]
        mean = np.array([r["mean"] for r in rows])
        sem = np.array([r["sem"] for r in rows])
        tag = L["tag_ba"] if strat == "top-BA" else L["tag"]
        ax.plot(BUDGETS, mean, color=colors[strat], lw=3, marker="o", ms=5,
                label=f"{strat} ({tag}, {L['sem']})",
                zorder=2.5 if strat == "top-hubs" else 2)   # top-hubs поверх top-BA (совпадают на B≥10)
        ax.fill_between(BUDGETS, mean - sem, mean + sem, color=colors[strat], alpha=0.18)
    ax.axhline(0, color=Y, lw=1.5, ls="--", label=L["y0"])
    ax.text(0.53, 0.56, L["b1"], transform=ax.transAxes, fontsize=8.5, color=INK)
    ax.set_xscale("log")
    ax.set_xticks(BUDGETS); ax.set_xticklabels([str(b) for b in BUDGETS])
    ax.set_xlabel(L["f8_xl"])
    ax.set_ylabel(L["f8_yl"])
    ax.set_title(L["f8_t"].format(p=p_star))
    ax.grid(alpha=0.15); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "fig8_reach_per_seed.png"), dpi=150)
    plt.close(fig)


FIG9_L = {
 "en": dict(med="median + IQR (simulation)", mean="mean (simulation)",
    mf="analytic: mean-field ⟨k⟩/(⟨k²⟩−⟨k⟩) = {v:.3f}",
    chat="analytic: bridge-layer mean-field 1/√(d̄−1) = {v:.2f}, upper bound",
    pc="(simulation)", yl="Final reach, % of N",
    t="Phase diagram: seed — one random chat (10–14 nodes); 40 runs/point",
    reff="R_eff | G₁≥1 (simulation)", pm="P_macro = P(reach ≥ 5% N) (simulation)",
    thr="analytic: criticality threshold R_eff = 1",
    sub="subcritical complex", sup="supercritical complex",
    xl="Share rate p", yl2="R_eff | G₁≥1 and P_macro (one scale)"),
 "ru": dict(med="медиана + IQR (симуляция)", mean="mean (симуляция)",
    mf="аналитика: mean-field ⟨k⟩/(⟨k²⟩−⟨k⟩) = {v:.3f}",
    chat="аналитика: mean-field мостового слоя 1/√(d̄−1) = {v:.2f}, оценка сверху",
    pc="(симуляция)", yl="Финальный охват, % N",
    t="Фазовая диаграмма: посев — один случайный чат (10–14 узлов); 40 прогонов/точку",
    reff="R_eff | G₁≥1 (симуляция)", pm="P_macro = P(охват ≥ 5% N) (симуляция)",
    thr="аналитика: порог критичности R_eff = 1",
    sub="субкритика complex", sup="сверхкритика complex",
    xl="Share rate p", yl2="R_eff | G₁≥1 и P_macro (одна шкала)"),
}

def make_fig9(res_b, p_c_mf, p_c_chat, pc1, pc2, lang="en", outdir=None):
    """Эксперимент B (v1.1): две панели, общая ось X = p. Верх — охват: медиана+IQR и mean
    тонкой линией (расхождение = подпись бимодальности); вертикали p_c^MF и p_c^chat.
    Низ — условный R_eff и P_macro точками на одной оси (dual-axis запрещён ТЗ)."""
    L = FIG9_L[lang]; outdir = outdir or FIGDIR; os.makedirs(outdir, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8.5), sharex=True)
    series = {K_COMPLEX: (P, "complex k=2"), K_SIMPLE: (C, "simple k=1")}
    for k, (col, lbl) in series.items():
        rows = res_b[k]
        med = np.array([r["reach_med"] for r in rows]) * 100
        q1 = np.array([r["reach_q1"] for r in rows]) * 100
        q3 = np.array([r["reach_q3"] for r in rows]) * 100
        mean = np.array([r["reach_mean"] for r in rows]) * 100
        ax1.plot(P_GRID, med, color=col, lw=3, label=f"{lbl}: {L['med']}")
        ax1.fill_between(P_GRID, q1, q3, color=col, alpha=0.18)
        ax1.plot(P_GRID, mean, color=col, lw=1.2, ls="-.", label=f"{lbl}: {L['mean']}")
    ax1.axvline(p_c_mf, color=Y, lw=1.5, ls="--", label=L["mf"].format(v=p_c_mf))
    ax1.axvline(p_c_chat, color=Y, lw=1.5, ls=":", ymin=0.58, label=L["chat"].format(v=p_c_chat))
    for pc, col, lbl in [(pc1, C, f"p_c(k=1) = {pc1:.2f} {L['pc']}"),
                         (pc2, P, f"p_c(k=2) = p* = {pc2:.2f} {L['pc']}")]:
        ax1.plot([pc], [-4], marker="^", ms=9, color=col, clip_on=False, ls="none", label=lbl)
    ax1.set_ylim(-8, 104)
    ax1.set_ylabel(L["yl"])
    ax1.set_title(L["t"])
    ax1.grid(alpha=0.15); ax1.legend(frameon=False, fontsize=8, loc="lower right")

    for k, (col, lbl) in series.items():
        rows = res_b[k]
        ax2.plot(P_GRID, [r["reff_cond"] for r in rows], color=col, lw=3,
                 label=f"{lbl}: {L['reff']}")
        ax2.plot(P_GRID, [r["p_macro"] for r in rows], color=col, lw=0, marker="o", ms=5,
                 alpha=0.55, label=f"{lbl}: {L['pm']}")
    ax2.axhline(1.0, color=Y, lw=1.5, ls="--", label=L["thr"])
    ax2.axvspan(P_GRID[0], pc2, color=K, alpha=0.08)
    ax2.axvspan(pc2, P_GRID[-1], color=P, alpha=0.08)
    ax2.text((P_GRID[0] + pc2) / 2, 0.06, L["sub"], ha="center", color=INK, fontsize=9)
    ax2.text((pc2 + P_GRID[-1]) / 2, 0.06, L["sup"], ha="center", color=INK, fontsize=9)
    ax2.set_xlabel(L["xl"])
    ax2.set_ylabel(L["yl2"])
    ax2.grid(alpha=0.15); ax2.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "fig9_phase_diagram.png"), dpi=150)
    plt.close(fig)


def make_gif(p_star):
    """fig10: один complex-каскад (k=2, p=p*) на мини-графе той же конструкции (§7).
    N_gif=4000, C_gif=277, spring-layout seed=42; кадр = раунд + 5 финальных статичных;
    число кадров = фактическая длина каскада + 5, ориентир 15–40 (§7 v1.3).
    RNG: посадка клик (4,0,0); посев и каскад (4,1,run) — run: первый с 25–40 кадрами
    (историческое окно v1.2, при p*=0.15 недостижимо), иначе максимальный по длине;
    выбор детерминирован и совпадает с опубликованным fig10 v1.2 (20 кадров)."""
    from PIL import Image
    from matplotlib.collections import LineCollection

    _, a_g, membership_g, sizes_g = build_graph(N_GIF, M_BA, C_GIF, SEED, rng_for(4, 0, 0))
    deg_g = degrees(a_g)
    pool_g = np.where((sizes_g >= SEED_CHAT_LO) & (sizes_g <= SEED_CHAT_HI))[0]

    chosen = None
    for run in range(40):
        rng = rng_for(4, 1, run)
        seeds = seed_random_chat(membership_g, pool_g, rng)
        reach, gens, _, hist = run_cascade(a_g, seeds, K_COMPLEX, p_star, rng, track_history=True)
        if 25 <= 1 + len(hist) + 5 <= 40:
            chosen = (run, seeds, reach, hist); break
        if chosen is None or len(hist) > len(chosen[3]):
            chosen = (run, seeds, reach, hist)
    run, seeds, reach, hist = chosen

    g_nx = nx.from_scipy_sparse_array(a_g)
    pos = nx.spring_layout(g_nx, seed=SEED)
    xy = np.array([pos[i] for i in range(N_GIF)])
    edges = np.array(g_nx.edges(), dtype=np.int64)
    node_size = 2.0 + deg_g * 0.55                     # размер узла ~ степень
    seed_mask = np.zeros(N_GIF, dtype=bool); seed_mask[seeds] = True

    GIF_L = {
     "en": dict(t="Complex cascade k=2, p = p* = {p:.2f} · round {t} · adopted {r:,}",
        key="seeds #6B2FFF · adopted #FF4D8D · at threshold (1 of 2 touches) #00D4F5 · "
            "sharing this round #FFD426 · untouched — dim #2A2342",
        note="simulation: illustrative scale N = 4,000; graph construction identical to the main run (N = 50,000)"),
     "ru": dict(t="Complex-каскад k=2, p = p* = {p:.2f} · раунд {t} · принявших {r:,}",
        key="посев #6B2FFF · принявшие #FF4D8D · на пороге (1 из 2 касаний) #00D4F5 · "
            "транслируют в раунде #FFD426 · не затронуты — тусклый #2A2342",
        note="симуляция: иллюстративный масштаб N = 4 000; конструкция графа идентична основной (N = 50 000)"),
    }

    def render(touches, adopted, sharers_now, t, cur_reach, L):
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.add_collection(LineCollection(xy[edges], colors=INK, linewidths=0.25, alpha=0.05))
        colors = np.full(N_GIF, DIM, dtype=object)     # S, 0 касаний
        colors[(touches == 1) & ~adopted] = C          # на пороге (1 из 2)
        colors[adopted] = K                            # принявшие
        colors[seed_mask] = P                          # посев
        if sharers_now is not None:
            colors[sharers_now] = Y                    # вспышка транслирующих
        order = np.argsort(np.where(colors == DIM, 0, np.where(colors == C, 1, 2)))
        ax.scatter(xy[order, 0], xy[order, 1], s=node_size[order],
                   c=list(colors[order]), linewidths=0, alpha=0.9)
        ax.set_xlim(xy[:, 0].min() * 1.05, xy[:, 0].max() * 1.05)
        ax.set_ylim(xy[:, 1].min() * 1.10, xy[:, 1].max() * 1.05)
        ax.axis("off")
        ax.set_title(L["t"].format(p=p_star, t=t, r=cur_reach), fontsize=11)
        fig.text(0.5, 0.935, L["key"], ha="center", fontsize=6.0, color=INK)
        fig.text(0.5, 0.02, L["note"], ha="center", fontsize=8.5, color=INK)
        fig.tight_layout()
        fig.canvas.draw()
        img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())).convert("RGB")
        plt.close(fig)
        return img

    for _lang, _outdir in (("en", FIGDIR), ("ru", os.path.join(FIGDIR, "ru"))):
        os.makedirs(_outdir, exist_ok=True); L = GIF_L[_lang]
        frames = [render(np.zeros(N_GIF, np.int32), seed_mask.copy(), None, 0, len(seeds), L)]
        for t, (sharers_t, touches_t, adopted_t) in enumerate(hist, start=1):
            frames.append(render(touches_t, adopted_t, sharers_t, t, int(adopted_t.sum()), L))
        frames += [frames[-1]] * 5                      # 5 финальных статичных кадров
        frames[0].save(os.path.join(_outdir, "fig10_cascade.gif"), save_all=True,
                       append_images=frames[1:], duration=250, loop=0)  # ~4 fps


def main():
    # --- Граф (§2): RNG посадки клик = spawn_key=(0,0,0) ---
    a_ba, a_full, membership, sizes = build_graph(N, M_BA, N_CLIQUES, SEED, rng_for(0, 0, 0))
    deg_ba, deg = degrees(a_ba), degrees(a_full)
    chat_pool = np.where((sizes >= SEED_CHAT_LO) & (sizes <= SEED_CHAT_HI))[0]

    gamma_hat = newman_mle_gamma(deg_ba)          # T1 — на чистом G_BA ДО клик
    cov = coverage(membership)                    # T2b
    bridge = bridge_layer(membership)             # T2c: (доля с мостом, d̄, компоненты)
    p_c_mf = mf_percolation_threshold(deg)
    p_c_chat = 1.0 / np.sqrt(bridge[1] - 1.0)     # аналитика v1.1: mean-field мостового слоя

    # --- Порядок §4.1: B первым -> p* -> A, C ---
    res_b = experiment_b(a_full, membership, chat_pool)
    pc1 = p_c_from_b(res_b, K_SIMPLE)
    p_star = p_c_from_b(res_b, K_COMPLEX)         # v1.1: p* = p_c(k=2) = min{p: mean охват >= 5% N}

    if p_star is None:                            # страховочный штатный стоп (§4.1, §5)
        v = build_validation(gamma_hat, sizes, cov, bridge, None, None)
        print_validation(v)
        print("\np* не существует; эксперимент A и фальсификатор GTM не интерпретируемы; "
              "конструкция пересматривается")
        print_b_table(res_b)
        print("\nМИШЕНЬ ПРОВАЛЕНА")
        sys.exit(1)

    p_c_run = max(p_star, 0.7)                    # §4.3 v1.1
    res_a = experiment_a(a_full, membership, deg, deg_ba, p_star)
    cells = experiment_c(a_full, a_ba, membership, chat_pool, p_c_run)

    # --- VALIDATION ПЕРЕД результатами (§5) ---
    v = build_validation(gamma_hat, sizes, cov, bridge, p_star, cells)
    if not print_validation(v):
        print("\nМИШЕНЬ ПРОВАЛЕНА")
        sys.exit(1)

    # --- Результаты ---
    p_macro_star = next(r["p_macro"] for r in res_b[K_COMPLEX] if r["p"] == p_star)
    memberships_per_node = sum(len(m) for m in membership) / N
    print(f"""
==================== ГРАФ (N={N:,}) ====================
G_BA: рёбер {a_ba.nnz // 2:,}, средняя степень {deg_ba.mean():.2f}
G = BA + {N_CLIQUES:,} клик с перекрытием (o={OVERLAP}, n_par={N_PAR}): рёбер {a_full.nnz // 2:,}, средняя степень {deg.mean():.2f}
членств на узел: {memberships_per_node:.2f}; на покрытого: {memberships_per_node / cov:.2f}
мостовой слой B_chat: d̄ = {bridge[1]:.2f}, компонент связности: {bridge[2]} (связен по построению)
чатов-кандидатов посева (размер {SEED_CHAT_LO}–{SEED_CHAT_HI}): {len(chat_pool)}

==================== КРИТИЧЕСКИЕ ТОЧКИ (эксперимент B) ====================
p*        (min p: mean охват(k=2) ≥ 5% N) : {p_star:.2f}   (= p_c(k=2))
p_c(k=1)  (min p: mean охват ≥ 5% N)      : {pc1:.2f}
P_macro на p* (k=2)                       : {p_macro_star:.3f}
p_c^chat  (аналитика 1/√(d̄_bridge−1))    : {p_c_chat:.3f}   (оценка сверху)
p_c^MF    (mean-field ⟨k⟩/(⟨k²⟩−⟨k⟩))     : {p_c_mf:.4f}

==================== ЭКСПЕРИМЕНТ C — контраст Centola 2×2 (p = {p_c_run:.2f}, {RUNS_C} прогонов/ячейку) ====================
P_macro = P(охват ≥ 5% N)     simple k=1   complex k=2      (метрика мишени T3, v1.2)
G    (BA + клики)           : {cells[('G', 1)]['p_macro']:>10.3f}   {cells[('G', 2)]['p_macro']:>11.3f}
G_BA (без клик)             : {cells[('G_BA', 1)]['p_macro']:>10.3f}   {cells[('G_BA', 2)]['p_macro']:>11.3f}
mean охват, % N (справочно)
G    (BA + клики)           : {cells[('G', 1)]['mean'] * 100:>10.1f}   {cells[('G', 2)]['mean'] * 100:>11.1f}
G_BA (без клик)             : {cells[('G_BA', 1)]['mean'] * 100:>10.1f}   {cells[('G_BA', 2)]['mean'] * 100:>11.2f}

==================== ЭКСПЕРИМЕНТ A — reach-per-seed (complex k=2, p = {p_star:.2f}, среднее ± SEM) ====================""")
    header = "B".rjust(5) + "".join(s.rjust(22) for s in STRATEGIES)
    print(header)
    for bi, b in enumerate(BUDGETS):
        cells_a = "".join(f"{res_a[s][bi]['mean']:>14.1f} ± {res_a[s][bi]['sem']:<5.1f}"
                          for s in STRATEGIES)
        print(f"{b:>5}{cells_a}")
    print("(top-BA — контроль интерпретации «каналы vs чат-хопперы», в критерий §6 не входит)")

    cs, inter, m_med, m_max = hub_decomposition(deg, deg_ba, membership)
    print(f"""
==================== ДЕКОМПОЗИЦИЯ ХАБОВ (§4.1 v1.3, справочно) ====================
доля кликовой степени у топ-500 union      : {cs * 100:.1f}%
пересечение |H₅₀₀ ∩ H₅₀₀^BA|               : {inter}/500
членства топ-500 union: медиана / максимум : {m_med:.0f} / {m_max}""")
    print(f"\nВЕРДИКТ ФАЛЬСИФИКАТОРА GTM (§6): {falsifier_verdict(res_a)}")
    print_b_table(res_b)

    # --- Фигуры ---
    for _lang in ("en", "ru"):
        _outdir = FIGDIR if _lang == "en" else os.path.join(FIGDIR, "ru")
        make_fig8(res_a, p_star, lang=_lang, outdir=_outdir)
        make_fig9(res_b, p_c_mf, p_c_chat, pc1, p_star, lang=_lang, outdir=_outdir)
    make_gif(p_star)
    print("figures saved: fig8_reach_per_seed.png, fig9_phase_diagram.png, fig10_cascade.gif")


if __name__ == "__main__":
    main()
