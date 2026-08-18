#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SIM4-S — насыщенный user-centric: двухпараметрическое семейство F^(λ,h).

Правило сохраняет нормативный принцип user-centric — деньги слушателя идут
только тем, кого он слушал, — но отказывается от скрытого допущения, что
сотый стрим одного артиста весит столько же, сколько первый:

    F_i^(λ,h) = λ·R·P_i/T + (1−λ)·Σ_u W_u · ψ_h(p_iu) / Σ_j ψ_h(p_ju),
    ψ_h(p)    = 1 − exp(−p/h)  — вогнутая, возрастающая, ψ(0) = 0.

Пределы (проверяются воротами, а не декларируются):
    λ=1                → pro-rata
    λ=0, h→∞           → user-centric (ψ ≈ p/h, множитель сокращается)
    λ=0, h→0⁺          → artist-centric: кошелёк поровну между слушанными
    λ=0, 0<h<∞         → насыщенный user-centric

Ворота печатаются ДО выводов; FAIL = exit(1). seed=42. MIT.
"""
import sys, os
import numpy as np
from scipy import sparse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FAILS = []

def gate(name, val, lo, hi, fmt="{:.6g}"):
    ok = lo <= val <= hi
    print(f"  {'PASS' if ok else 'FAIL'}  {name} = {fmt.format(val)} (допуск [{lo}; {hi}])")
    if not ok:
        FAILS.append(name)
    return ok

def gini(x):
    x = np.sort(np.asarray(x, dtype=np.float64)); n = x.size; s = x.sum()
    return 0.0 if s <= 0 else (2.0 * np.arange(1, n + 1) - n - 1).dot(x) / (n * s)

def saturated(M, lam, h, W=None):
    """F^(λ,h) на разреженной матрице M (пользователи × артисты).

    h = np.inf даёт чистый user-centric, h → 0⁺ — равный делёж кошелька.
    Используется -expm1(-p/h): при большом h разность 1 − exp(−p/h) теряет
    значащие разряды, expm1 считает её точно.
    """
    U_, N_ = M.shape
    P_u = np.asarray(M.sum(axis=1)).ravel().astype(np.float64)
    P_i = np.asarray(M.sum(axis=0)).ravel().astype(np.float64)
    T = P_u.sum()
    active = P_u > 0
    W = np.where(active, 1.0, 0.0) if W is None else np.asarray(W, dtype=np.float64) * active
    R = W.sum()

    PR_part = R * P_i / T                                    # pro-rata-компонент
    if lam >= 1.0:
        return PR_part

    S = M.tocsr(copy=True).astype(np.float64)
    if np.isinf(h):
        psi = S.data                                         # ψ ∝ p, множитель 1/h сокращается
    elif h <= 0:
        psi = np.ones_like(S.data)                           # предел h→0⁺: индикатор p>0
    else:
        psi = -np.expm1(-S.data / h)
    S.data = psi
    den = np.asarray(S.sum(axis=1)).ravel()
    scale = np.divide(W, den, out=np.zeros_like(den), where=den > 0)
    UC_part = np.asarray(S.multiply(scale[:, None]).sum(axis=0)).ravel()
    return lam * PR_part + (1 - lam) * UC_part


# ворота и отчёт выполняются только при прямом запуске: saturated() и gini()
# переиспользуются другими модулями импортом
if __name__ == "__main__":
    # ---------- вход ----------
    path = os.path.join(DATA, "matrix_b_seed42.npz")
    if not os.path.exists(path):
        sys.exit("нет data/matrix_b_seed42.npz — сначала: python3 sim4/bipartite_gen.py")
    M = sparse.load_npz(path).tocsr()
    U, N = M.shape
    P_u = np.asarray(M.sum(axis=1)).ravel().astype(np.float64)
    P_i = np.asarray(M.sum(axis=0)).ravel().astype(np.float64)
    T = P_u.sum(); Ueff = int((P_u > 0).sum())
    A = np.asarray((M > 0).sum(axis=0)).ravel().astype(np.int64)

    PR = Ueff * P_i / T
    inv = np.divide(1.0, P_u, out=np.zeros_like(P_u), where=P_u > 0)
    UC = np.asarray(M.multiply(inv[:, None]).sum(axis=0)).ravel()
    K_u = np.asarray((M > 0).sum(axis=1)).ravel().astype(np.float64)   # артистов в кошельке
    invK = np.divide(1.0, K_u, out=np.zeros_like(K_u), where=K_u > 0)
    AC = np.asarray((M > 0).multiply(invK[:, None]).sum(axis=0)).ravel()  # equal-split предел

    print("=" * 74)
    print("SIM4-S · ворота (ДО выводов; FAIL блокирует прогон)")
    print(f"мир: N={N:,}, U={U:,}, активных слушателей {Ueff:,}, пул R = {Ueff:,.0f}")
    print("-" * 74)

    # B1 — бюджетный баланс на сетке (λ, h): правило не создаёт и не уничтожает денег
    worst_bud = 0.0
    for lam in (0.0, 0.25, 0.5, 1.0):
        for h in (0.0, 1.0, 5.0, 50.0, np.inf):
            F = saturated(M, lam, h)
            worst_bud = max(worst_bud, abs(F.sum() - Ueff) / Ueff)
    gate("B1  max|ΣF − R|/R по сетке (λ,h)", worst_bud, 0, 1e-12, "{:.3e}")

    # B2 — предел λ=1 равен pro-rata точно
    gate("B2  max|F(1,·) − PR|/PR", np.max(np.abs(saturated(M, 1.0, 5.0) - PR) / np.maximum(PR, 1e-300)),
         0, 1e-12, "{:.3e}")

    # B3 — предел h→∞ равен user-centric
    gate("B3  max|F(0,∞) − UC|/UC", np.max(np.abs(saturated(M, 0.0, np.inf) - UC) / np.maximum(UC, 1e-300)),
         0, 1e-12, "{:.3e}")

    # B4 — предел h→0⁺ равен равному делёжу кошелька между слушанными артистами
    gate("B4  max|F(0,0⁺) − AC|/AC", np.max(np.abs(saturated(M, 0.0, 0.0) - AC) / np.maximum(AC, 1e-300)),
         0, 1e-12, "{:.3e}")

    # B5 — сходимость к пределу монотонна по h. Норма — доля пула, размещённая
    # иначе (½‖F−UC‖₁ / R): максимум ОТНОСИТЕЛЬНОЙ ошибки для этого не годится,
    # он берётся по артистам с исчезающе малым UC и немонотонен на малых h,
    # хотя сходимость есть. Экономически осмысленная мера — деньги, а не разы.
    tv_prev, mono = np.inf, True
    for h in (1, 10, 100, 1000, 10_000):
        tv = np.abs(saturated(M, 0.0, float(h)) - UC).sum() / (2 * Ueff)
        mono &= tv < tv_prev
        tv_prev = tv
    gate("B5.1 доля пула, размещённая иначе, убывает по h", 1.0 if mono else 0.0, 1, 1, "{:.0f}")
    gate("B5.2 остаточное расхождение при h=10⁴", tv_prev, 0, 1e-3, "{:.2e}")

    # B6 — неотрицательность и локальность кошелька: p_iu=0 ⟹ артист не получает
    F5 = saturated(M, 0.0, 5.0)
    no_aud = A == 0
    gate("B6.1 min F(0,5)", float(F5.min()), 0, np.inf, "{:.3e}")
    gate("B6.2 доход артистов без аудитории", float(np.abs(F5[no_aud]).max()) if no_aud.any() else 0.0,
         0, 1e-12, "{:.3e}")

    print("-" * 74)
    if FAILS:
        print(f"FAIL ворот: {FAILS} — выводы заблокированы.")
        sys.exit(1)
    print("ВСЕ ВОРОТА PASS. Поверхность по (λ, h):")
    print()

    top = int(np.ceil(0.0028 * N))
    mA = A > 0
    def top_share(x, frac):
        k = int(np.ceil(frac * N))
        return np.sort(x)[::-1][:k].sum() / x.sum() * 100

    print("  Чистое насыщение (λ=0): что делает шкала h")
    print(f"  {'h':>8} {'Джини':>8} {'топ0.28%':>9} {'топ1%':>8} {'топ10%':>8} "
          f"{'медиана+':>9} {'выигр.у PR':>11} {'выигр.топ':>10}")
    for h in (1, 2, 5, 10, 20, 50, np.inf):
        F = saturated(M, 0.0, float(h))
        win = (F[mA] > PR[mA]).mean() * 100
        big = np.argsort(P_i)[::-1][:top]
        win_top = (F[big] > PR[big]).mean() * 100
        med = np.median(F[F > 0]) / F.mean()
        hl = "∞" if np.isinf(h) else f"{h:g}"
        print(f"  {hl:>8} {gini(F):8.4f} {top_share(F,0.0028):8.1f}% {top_share(F,0.01):7.1f}% "
              f"{top_share(F,0.10):7.1f}% {med:9.4f} {win:10.1f}% {win_top:9.1f}%")
    print(f"  {'pro-rata':>8} {gini(PR):8.4f} {top_share(PR,0.0028):8.1f}% {top_share(PR,0.01):7.1f}% "
          f"{top_share(PR,0.10):7.1f}% {np.median(PR[PR>0])/PR.mean():9.4f} {'—':>10} {'—':>9}")
    print()

    print("  Гибрид: доля pro-rata в смеси (h = 5)")
    print(f"  {'λ':>8} {'Джини':>8} {'топ0.28%':>9} {'выигр.у PR':>11}")
    for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
        F = saturated(M, lam, 5.0)
        print(f"  {lam:>8.2f} {gini(F):8.4f} {top_share(F,0.0028):8.1f}% "
              f"{(F[mA] > PR[mA]).mean()*100:10.1f}%")

    # ---------- кто выигрывает: по децилям размера ----------
    print()
    print("  Медиана F/PR по децилям размера артиста (d1 — мельчайшие, d10 — крупнейшие)")
    order = np.argsort(P_i[mA])
    for h in (1.0, 5.0, 20.0, np.inf):
        r = saturated(M, 0.0, h)[mA] / PR[mA]
        dec = np.array_split(order, 10)
        hl = "∞" if np.isinf(h) else f"{h:g}"
        print(f"  h={hl:>3}  " + " ".join(f"{np.median(r[d]):5.2f}" for d in dec))

    # ---------- давление манипуляции ----------
    # Бюджет: m дополнительных стримов, множество аккаунтов ФИКСИРОВАНО (иначе
    # сравнение нечестно: новый аккаунт приносит в пул настоящий кошелёк).
    # Сравниваются три способа потратить один и тот же бюджет.
    print()
    print("  Давление манипуляции: прирост дохода на m = 500 добавленных стримов")
    print(f"  {'способ':<38}" + "".join(f"{('h='+('∞' if np.isinf(h) else f'{h:g}')):>10}"
                                        for h in (1.0, 5.0, 20.0, np.inf)))

    def gain(tgt, plan, h):
        """Прирост дохода артиста tgt при добавлении стримов plan={u: +p}."""
        rows = sorted(plan)
        S = M[rows].tocsr().astype(np.float64)
        base_num = np.zeros(len(rows)); base_den = np.zeros(len(rows))
        new_num = np.zeros(len(rows));  new_den = np.zeros(len(rows))
        for k, u in enumerate(rows):
            d = S.data[S.indptr[k]:S.indptr[k+1]].copy()
            cols = S.indices[S.indptr[k]:S.indptr[k+1]]
            psi = d.copy() if np.isinf(h) else -np.expm1(-d / h)
            base_den[k] = psi.sum()
            hit = cols == tgt
            base_num[k] = psi[hit].sum() if hit.any() else 0.0
            d2 = d.copy()
            if hit.any():
                d2[hit] += plan[u]
                psi2 = d2.copy() if np.isinf(h) else -np.expm1(-d2 / h)
                new_num[k] = psi2[hit].sum()
            else:
                psi2 = np.append(psi, plan[u] if np.isinf(h) else -np.expm1(-plan[u] / h))
                new_num[k] = psi2[-1]
            new_den[k] = psi2.sum()
        b = np.divide(base_num, base_den, out=np.zeros_like(base_den), where=base_den > 0)
        n = np.divide(new_num, new_den, out=np.zeros_like(new_den), where=new_den > 0)
        return (n - b).sum()

    m_budget = 500
    tgt = int(np.argsort(P_i)[len(P_i) // 2])           # артист медианного размера
    col = M[:, tgt].tocoo()
    fans = col.row[np.argsort(-col.data)]                # его слушатели, по убыванию
    non_fans = np.setdiff1d(np.arange(U)[np.asarray(M.sum(axis=1)).ravel() > 0][:200_000],
                            col.row, assume_unique=False)
    plans = [
        ("весь бюджет одному фанату (repeat)",    {int(fans[0]): m_budget}),
        ("по 50 стримов 10 фанатам",              {int(u): m_budget // 10 for u in fans[:10]}),
        ("по 5 стримов 100 фанатам",              {int(u): m_budget // 100 for u in fans[:100]}),
        ("по 1 стриму 500 НЕ-слушателям (breadth)", {int(u): 1 for u in non_fans[:m_budget]}),
    ]
    for label, plan in plans:
        cells = "".join(f"{gain(tgt, plan, h):10.4f}" for h in (1.0, 5.0, 20.0, np.inf))
        print(f"  {label:<38}{cells}")
    print()
    print("  Читается по строкам: чем меньше h, тем слабее окупается повтор одним")
    print("  аккаунтом и тем сильнее — охват новых слушателей. Правило давит")
    print("  repeat-farming; identity-farming (создание аккаунтов) оно не решает —")
    print("  новый аккаунт приносит настоящий кошелёк и потому всегда выгоден.")
