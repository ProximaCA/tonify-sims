# -*- coding: utf-8 -*-
"""TONIFY-SIM · run_all.py — полный прогон одной командой.
Порядок: мир+валидация (v0.2) -> красная команда fixes (v0.3) -> карта миров (v0.4) -> матрица (v0.5).
Все фигуры fig1-fig7 в ./figures, ключевые числа в stdout. seed=42, MIT.
"""
import subprocess, sys, os, shutil
HERE=os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
os.environ.setdefault("MPLBACKEND","Agg")
steps=[("tonify_cash_sim.py","мир, валидация T1-T3, MVA, фрод, логистика, кеш-слой v0.3"),
       ("v04_full.py","user-centric MC, лестница миров, MRR-solver"),
       ("v05_matrix.py","полная матрица {правило × контракт}, heatmap")]
for f,desc in steps:
    print(f"\n{'='*70}\n>> {f} — {desc}\n{'='*70}")
    r=subprocess.run([sys.executable,f],capture_output=True,text=True)
    print(r.stdout[-3000:])
    if r.returncode!=0: print(r.stderr[-2000:]); sys.exit(1)
os.makedirs("figures",exist_ok=True)
for p in [x for x in os.listdir(".") if x.endswith(".png")]:
    shutil.copy(p,os.path.join("figures",p))
print("\nDONE. Фигуры в ./figures, числа выше, документы: PAPER.md, RESULTS.md, CRITIC.md")
