---
description: Direct + guaranteed discovery floor — kill the zero atom without turning Tonify back into a streaming pool.
---

# sim6 — Direct + guaranteed discovery floor

**The question.** L4 says the problem for small artists is the zero atom, not the mean and not $k$. How much does it cost to remove that lottery without turning the product back into an ordinary streaming pool?

**The gates.** World anchors T1–T3; $q_{\mathrm{eligible}}=0$ at $B>0$; floor sums to $B$; the direct term is untouched; at $\beta<1$ the floor's top share is lighter than $D$'s; MVA at $B=0$ matches pure direct.

**The headline.** The atom is an eligibility cost. A living wage is a $B$ cost. Any $B>0$ yields $q_{\mathrm{eligible}}=0$. Among artists with $A_i>0$, pure direct is 77.7% zeros; $A_{\min}=1$ kills the atom, $A_{\min}\le3$ leaves at most half. At 5% of the independent pool, $A_{\min}=10$, the mean floor is $16.38/year and hybrid MVA is 3 110 against pure direct 3 204.

**Run it.** `python3 sim6/floor.py`.

***

### sim6 — Direct + guaranteed discovery floor

Not a fourth pure mechanism and not sold as direct. L4 says the problem for
small artists is the zero atom, not the mean and not $k$. The operator that
attacks the atom keeps fan money direct and adds a platform discovery pool $B$
for artists with verified audience $A_i\ge A_{\min}$, weighted $A_i^\beta$ with
$\beta<1$.

![fig21_floor_zeros](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig21_floor_zeros.png)

*fig21 — share of artists with $Y=0$ against the eligibility threshold $A_{\min}$
($B/R=5\%$, $\beta=0.5$, sim1 world N=200,000, seed 42). Eligible artists sit
at zero; the remaining atom is whoever missed the threshold and lost the $D$
lottery.*

**Finding 13 — the atom is an eligibility cost; a living wage is a $B$ cost.**
Any $B>0$ yields $q_{\mathrm{eligible}}=0$. Among artists with $A_i>0$ (everyone
in this world) pure direct is 77.7% zeros; $A_{\min}=1$ kills that atom entirely,
$A_{\min}=3$ leaves 37.2% (≤50%), $A_{\min}=2$ leaves 27.9%. $B/R$ does not bind
the atom. At $A_{\min}=10$, $B=0.05R$ is $1,118,570$ spread over 68,271 eligible
artists — **$16.38**/year mean floor. Hybrid MVA moves 3,204 → 3,110 against
independent-pool 12,771 and signed-pool 188,590. The lottery is gone; the wage
is not. Signed hybrid MVA equals independent: $B$ and $D$ do not pass through
$\rho$ ([sim6](https://github.com/ProximaCA/tonify-sims/blob/main/sim6/SPEC.md)).

![fig22_floor_mva](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig22_floor_mva.png)

*fig22 — hybrid MVA against $B/R$ ($A_{\min}=10$, $\beta=0.5$). Yellow:
independent pool 12,771; pink: signed 188,590; cyan: pure direct 3,204. The
floor barely moves MVA because $B$ is smeared across every eligible artist.*

**Finding 14 — the floor changes the bottom, not the top; fake uniques at the
threshold are the fraud that bites.** At $\beta=0.5$ the top 0.28% take 11.4% of
the floor against 44.5% of $D$; at $\beta=1$ the floor copies $D$'s tail (44.6%).
50,000 one-contact fakes steal 2.5% of $B$; the same farm at $A_{\min}=30$
steals 14.3%. $A_{\min}$ is not an anti-fraud defense by itself: it moves the
incentive from minting many one-shot identities to producing convincing
threshold audiences. Each fake is dearer, but the honest eligible set has
shrunk.
