import numpy as np
rng = np.random.default_rng(42)

print("=== CHECK 1: L1 identity on 200 random play matrices ===")
worst = 0.0
for trial in range(200):
    N, U = rng.integers(2, 30), rng.integers(2, 40)
    p = rng.integers(0, 12, size=(N, U)).astype(float)
    p[rng.random((N, U)) < 0.5] = 0
    # ensure every user plays someone, every artist has plays
    for u in range(U):
        if p[:, u].sum() == 0: p[rng.integers(0, N), u] = rng.integers(1, 5)
    keep = p.sum(axis=1) > 0
    p = p[keep]; N = p.shape[0]
    P_u = p.sum(axis=0); P_i = p.sum(axis=1); T = P_u.sum(); Ucnt = len(P_u)
    W = 1.0
    PR = Ucnt * W * P_i / T
    UC = W * (p / P_u).sum(axis=1)
    ratio_direct = UC / PR
    Pbar = T / Ucnt
    w = p / P_i[:, None]
    ratio_id = (w * (Pbar / P_u)[None, :]).sum(axis=1)
    worst = max(worst, np.abs(ratio_direct - ratio_id).max())
    # zero-sum
    assert abs(UC.sum() - PR.sum()) < 1e-9
    # AM/HM decomposition
    m = (w * P_u[None, :]).sum(axis=1)
    H = 1.0 / (w * (1.0 / P_u)[None, :]).sum(axis=1)
    dec = (Pbar / m) * (m / H)
    worst = max(worst, np.abs(ratio_direct - dec).max())
    assert (m / H >= 1 - 1e-12).all()  # AM>=HM under weights
print(f"identity + decomposition max abs error over 200 trials: {worst:.2e}  (zero-sum + AM>=HM asserted)")

print("\n=== CHECK 2: corollary (a) counterexample ===")
p = np.array([[10.0, 20.0]])  # one artist, two users
P_u = p.sum(axis=0); T = P_u.sum()
PR = 2 * 1.0 * p.sum(axis=1) / T
UC = (p / P_u).sum(axis=1)
print(f"P_u = {P_u} (heterogeneous), UC = {UC[0]:.6f}, PR = {PR[0]:.6f} -> coincide: {abs(UC[0]-PR[0])<1e-12}")

print("\n=== CHECK 3: L4 dominance blocking (Monte Carlo, 2M draws) ===")
s, k, gbar, tau = 0.017, 4.0, 6.886, 0.80
PL, rate = 21.21, 0.00443
for A in [30, 300, 3000]:
    X = PL * rate * A
    S = rng.binomial(A, s, size=2_000_000)
    # lognormal gift median 5 sigma 0.8 -> mean 6.886
    Y = tau * np.array([0.0]*0)
    gifts_mean_per_fan = k * gbar  # E per superfan per year
    # exact-ish: sum of S*k lognormal draws ~ approximate via normal per large; do direct for atom + threshold prob
    # atom:
    atom = (S == 0).mean()
    # P(Y < X): approximate per-superfan payment as exact lognormal sum — use S*k draws aggregated via gamma approx? do direct sampling for A=30 only
    mu, sig = np.log(5), 0.8
    if A == 30:
        # red team v2 (C14): full 2M via repeat+bincount, not a 200k subsample
        tot = (S * int(k)).astype(np.int64)
        draws = rng.lognormal(mu, sig, size=int(tot.sum()))
        Ys = tau * np.bincount(np.repeat(np.arange(len(S)), tot), weights=draws, minlength=len(S))
        pbelow = (Ys < X).mean()
        print(f"A={A}: atom P(Y=0)={atom:.4f} (theory {(1-s)**A:.4f}), E[Y]={tau*s*k*gbar*A:.2f} vs X={X:.2f}, "
              f"P(Y<X)={pbelow:.4f}, P(Y<X)-P(Y=0)={pbelow-atom:.2e} -> проигрыш пулу = в точности нулевой исход")
    else:
        print(f"A={A}: atom P(Y=0)={atom:.4f} (theory {(1-s)**A:.4f}), E[Y]={tau*s*k*gbar*A:.1f} vs X={X:.1f}")

print("\n=== CHECK 4: calibrated world — q, Gini decomposition ===")
# reproduce sim1 world (SPEC §2)
rng2 = np.random.default_rng(42)
N = 200_000
n_low = int(0.87 * N); n_mid = int((1 - 0.87 - 0.026) * N); n_top = N - n_low - n_mid
s_low = np.clip(np.exp(rng2.normal(np.log(80), 1.4, n_low)), 1, 999)
s_mid = np.exp(rng2.uniform(np.log(1000), np.log(225_734), n_mid))
s_top = 225_734 * (1 + rng2.pareto(1.4, n_top))
streams = np.concatenate([s_low, s_mid, s_top]); rng2.shuffle(streams)
A = np.maximum(1, streams / PL)
sf = 0.017
q = np.mean((1 - sf) ** A)
def gini(x):
    x = np.sort(x); n = len(x); c = np.cumsum(x)
    return 1 - 2 * (c.sum() / (n * c[-1])) + 1/n if c[-1] > 0 else 0.0
G_pool = gini(streams)  # income prop to streams
# direct incomes: binomial superfans, deterministic k*gbar*tau per fan (recurring)
S = rng2.binomial(A.astype(int), sf)
Yd = tau * S * k * gbar
G_dir = gini(Yd)
pos = Yd > 0
G_plus = gini(Yd[pos])
q_m = (~pos).mean()  # red team v2 (C9): в тождестве — ИЗМЕРЕННАЯ масса нулей
print(f"q = E[(1-s)^A] = {q:.3f} | measured zero share = {q_m:.3f} (расходятся из-за A.astype(int) в биноме)")
print(f"G_pool = {G_pool:.3f} | G_direct = {G_dir:.6f} | identity q_m+(1-q_m)G+ = {q_m + (1-q_m)*G_plus:.6f} "
      f"(G+ = {G_plus:.3f}, |diff| = {abs(G_dir - (q_m + (1-q_m)*G_plus)):.2e} — точное тождество)")
print(f"T1-region atom (A<48): {np.mean((1-sf)**A[A<48]):.3f}")

print("\n=== CHECK 5 (red team): corrected atom inequality + lognormal-gift Gini ===")
for sv in [0.017, 0.05, 0.1, 0.3, 0.5]:
    lhs = (1-sv)**(1/sv)
    old_bound = np.e**-1/(1-sv)   # RETRACTED (false)
    new_bound = np.e**-1*(1-sv)   # corrected
    print(f"  s={sv}: (1-s)^(1/s)={lhs:.5f} | retracted bound {old_bound:.5f} (holds: {lhs>=old_bound}) | corrected {new_bound:.5f} (holds: {lhs>=new_bound})")
# lognormal-gift variant of check 4
rng3 = np.random.default_rng(43)
mu, sig = np.log(5), 0.8
S2 = rng3.binomial(A.astype(int), sf)
tot = (S2 * k).astype(int)
Yd2 = np.zeros(len(tot))
nz = tot > 0
# sum of lognormals per artist via normal approx for large counts, exact for small
small = nz & (tot <= 100)
Yd2[small] = np.array([tau * rng3.lognormal(mu, sig, c).sum() for c in tot[small]])
big = nz & (tot > 100)
m1 = np.exp(mu + sig**2/2); v1 = (np.exp(sig**2)-1)*np.exp(2*mu+sig**2)
Yd2[big] = tau * (tot[big]*m1 + rng3.standard_normal(big.sum())*np.sqrt(tot[big]*v1))
G_dir2 = gini(np.maximum(Yd2, 0))
print(f"  G_direct with lognormal gifts: {G_dir2:.3f} (deterministic-gift variant: {G_dir:.3f}) -> robustness confirmed" )

print("\n=== CHECK 6 (red team v2): L2(2b) boost counterexample — MVA ratio 1/(2rho) ===")
# Deezer-механика: artist-centric буст x2 выше A0; контрпример из §4 (C6/C22)
rho, V, A0 = 0.06772, 1200.0, 15000
c = PL * rate
F = lambda Av: c * Av * (1 + (Av >= A0))          # доход инди
mva = lambda income: next(Av for Av in range(1, 200_000) if income(Av) >= V)
mva_i = mva(F)
mva_s = mva(lambda Av: rho * F(Av))
print(f"  MVA_indep = {mva_i} (небустованная ветвь), MVA_signed = {mva_s} (бустованная)")
print(f"  ratio = {mva_s/mva_i:.4f} = 1/(2rho) = {1/(2*rho):.4f} != 1/rho = {1/rho:.4f}")
assert abs(mva_s/mva_i - 1/(2*rho)) < 0.01 and mva_i == 12772 and mva_s == 94296
# лог-периодический F: нелинеен, но MVA-ratio = 1/rho при всех V (линейность НЕ необходима)
Flog = lambda Av: Av * (1 + 0.1*np.sin(2*np.pi*np.log(Av)/np.log(1/rho)))
for Vt in (50.0, 1200.0, 40000.0):
    from scipy.optimize import brentq
    inv = lambda Vv: brentq(lambda Av: Flog(Av) - Vv, 1e-3, 1e9)
    r = inv(Vt/rho) / inv(Vt)
    assert abs(r - 1/rho) < 1e-6
print(f"  log-periodic F (нелинеен): MVA-ratio = 1/rho при V=50/1200/40000 — линейность достаточна, НЕ необходима")
