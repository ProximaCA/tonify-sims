---
description: Direct + guaranteed discovery floor — kill the zero atom without turning Tonify back into a streaming pool.
---

# sim6 — Direct + guaranteed discovery floor

**The question.** L4 says the problem for small artists is the zero atom, not the mean and not $k$. How much does it cost to remove that lottery without turning the product back into an ordinary streaming pool?

**The gates.** World anchors T1–T3; $q_{\mathrm{eligible}}=0$ at $B>0$; floor sums to $B$; the direct term is untouched; at $\beta<1$ the floor's top share is lighter than $D$'s; MVA at $B=0$ matches pure direct.

**The headline.** The atom is an eligibility cost. A living wage is a $B$ cost. Any $B>0$ yields $q_{\mathrm{eligible}}=0$. Among artists with $A_i>0$, pure direct is {{s6.q_dir}}% zeros; $A_{\min}=1$ kills the atom, $A_{\min}\le{{s6.amin50}}$ leaves at most half. At 5% of the independent pool, $A_{\min}=10$, the mean floor is ${{s6.mean_floor}}/year and hybrid MVA is {{s6.mva_hyb05}} against pure direct {{s6.mva_dir}}.

**Run it.** `python3 sim6/floor.py`.

***

{{INCLUDE:README.md|## sim6 — Direct + guaranteed discovery floor|## Reproducibility}}
