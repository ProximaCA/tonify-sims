# -*- coding: utf-8 -*-
"""TONIFY-SIMS · run_all.py — полный прогон трёх симуляций одной командой.
sim1 (касса): мир+валидация (v0.2) -> красная команда fixes (v0.3) -> карта миров (v0.4) -> матрица (v0.5).
sim2 (граф): BA+клики, complex contagion, фальсификатор хабов. sim3 (анти-кладбище): казна A vs B.
Все фигуры fig1-fig13 в ./figures, ключевые числа в stdout. seed=42, MIT.
"""
import subprocess, sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
os.environ.setdefault("MPLBACKEND","Agg")
steps=[(os.path.join("sim1","tonify_cash_sim.py"),"sim1: мир, валидация T1-T3, MVA, фрод, логистика, кеш-слой v0.3"),
       (os.path.join("sim1","v04_full.py"),"sim1: user-centric MC, лестница миров, MRR-solver"),
       (os.path.join("sim1","v05_matrix.py"),"sim1: полная матрица {правило × контракт}, heatmap"),
       (os.path.join("sim1","v06_uc_crossover.py"),"sim1: UC-кроссовер u* (external review §2), fig14"),
       (os.path.join("sim2","tonify_graph_sim.py"),"sim2: граф Telegram, complex contagion, фальсификатор хабов (~1 мин)"),
       (os.path.join("sim3","sim3_anti_graveyard.py"),"sim3: анти-кладбище, казна A vs B, 200 прогонов")]
for f,desc in steps:
    print(f"\n{'='*70}\n>> {f} — {desc}\n{'='*70}")
    r=subprocess.run([sys.executable,f],capture_output=True,text=True)
    print(r.stdout if len(r.stdout)<20000 else r.stdout[-20000:])
    if r.returncode!=0: print(r.stderr[-2000:]); sys.exit(1)
print("\nDONE. Фигуры fig1-fig13 в ./figures (EN) и ./figures/ru (RU), числа выше.")
print("Документы: README.md (сводка), paper/PAPER.md, paper/RESULTS.md, paper/CRITIC.md (sim1), sim2/README.md, sim3/README.md")
