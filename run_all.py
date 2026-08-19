# -*- coding: utf-8 -*-
"""TONIFY-SIMS · run_all.py — sim1–sim5 + emp2-слот одной командой.
sim1 касса (включая v07 сетку прохода) → sim2 граф → sim3 казна → emp2 кеф
→ sim5 склейка → sim4 двудольная матрица. Фигуры fig1–fig20. seed=42, MIT.
"""
import subprocess, sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
os.environ.setdefault("MPLBACKEND","Agg")
steps=[(os.path.join("sim1","tonify_cash_sim.py"),"sim1: мир, валидация T1-T3, MVA, фрод, логистика, кеш-слой v0.3"),
       (os.path.join("sim1","v04_full.py"),"sim1: user-centric MC, лестница миров, MRR-solver"),
       (os.path.join("sim1","v05_matrix.py"),"sim1: полная матрица {правило × контракт}, heatmap"),
       (os.path.join("sim1","v06_uc_crossover.py"),"sim1: UC-кроссовер u* (external review §2), fig14"),
       (os.path.join("sim1","v07_passthrough.py"),"sim1: сетка прохода 6.772/10.6/20%, fig19"),
       (os.path.join("sim2","tonify_graph_sim.py"),"sim2: граф Telegram, complex contagion, фальсификатор хабов (~1 мин)"),
       (os.path.join("sim3","sim3_anti_graveyard.py"),"sim3: анти-кладбище, казна A vs B, 200 прогонов"),
       (os.path.join("emp2","cadence_measure.py"),"emp2: кеф Telegram-пилота (fail-closed, UNMEASURED без CSV)"),
       (os.path.join("sim5","glue.py"),"sim5: склейка каскад → σ → k/чек → казна, fig20"),
       (os.path.join("sim4","bipartite_gen.py"),"sim4: двудольная матрица user×artist, ворота G1-G3, выгрузка data/, fig15-fig16 (~6 мин)"),
       (os.path.join("sim4","group_gamma.py"),"sim4-G: гетерогенный γ по группам слушателей, ворота H1-H4, fig18 (~8 мин)"),
       (os.path.join("sim4","downside.py"),"sim4-D: метрики нижнего края — экстенсивная маржа, пороги, ES, ворота G1-G5 (~1 мин)"),
       (os.path.join("sim4","saturated.py"),"sim4-S: насыщенный user-centric F^(λ,h), пределы как ворота B1-B6 (~2 мин)")]
# emp1 требует внешних данных (emp1/raw/, ~4 ГБ, в гит не входят) — гоняется
# отдельно: python3 emp1/gamma_measure.py и python3 emp1/moreau_check.py.
# Источники и контрольные суммы — emp1/README.md §Датасеты.
for f,desc in steps:
    print(f"\n{'='*70}\n>> {f} — {desc}\n{'='*70}")
    r=subprocess.run([sys.executable,f],capture_output=True,text=True)
    print(r.stdout if len(r.stdout)<20000 else r.stdout[-20000:])
    if r.returncode!=0: print(r.stderr[-2000:]); sys.exit(1)
print("\nDONE. Фигуры fig1-fig20 в ./figures (EN) и ./figures/ru (RU), числа выше.")
print("Документы: README.md, paper/, sim5/SPEC.md, emp2/README.md")
