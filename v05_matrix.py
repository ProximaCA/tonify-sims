# -*- coding: utf-8 -*-
"""v0.5: полная матрица {правило × контракт}, перерисовка fig1/fig5, новый fig7-heatmap."""
import os
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rng=np.random.default_rng(42)
P,C,K,Y,G,TW="#6B2FFF","#00D4F5","#FF4D8D","#FFD426","#1DB954","#9146FF"; OUT=os.path.dirname(os.path.abspath(__file__))+"/"
plt.rcParams.update({"figure.facecolor":"#0D0A1A","axes.facecolor":"#0D0A1A","axes.edgecolor":"#B8C8DC",
 "axes.labelcolor":"#B8C8DC","text.color":"#B8C8DC","xtick.color":"#B8C8DC","ytick.color":"#B8C8DC","font.size":11})
TARGET=1200.0; PL=21.21
LABEL_PASS=0.068           # доля, доходящая до подписанного артиста (0.0003/0.00443; ~CNM 6.8%)
DEAL360=0.70               # direct под 360-сделкой: лейбл забирает ~30%
# --- per-listener-year value by rule ---
pr_ind=PL*4.43/1000                                  # pro-rata independent
uc_ind_tbl={}
for u in [5_000,10_000,20_000]:
    p=rng.lognormal(np.log(5.16),1.676,200_000); o=rng.lognormal(np.log(u),1.0,200_000)
    uc_ind_tbl[u]=0.40*(11.99*12*0.70)*float((p/(p+o)).mean())
uc_ind=uc_ind_tbl[10_000]
SF=0.017; MG=float(np.exp(np.log(5.0)+0.8**2/2))
d_be=SF*1.25*MG*0.80; d4=SF*4*MG*0.80; rec12=SF*12*MG*(0.95*0.999)
tw=0.017*12*5.0*0.50
vals={ # (label, per-listener-yr, color)
 "pro-rata · signed":            (pr_ind*LABEL_PASS,K),
 "pro-rata · independent":       (pr_ind,G),
 "user-centric · signed":        (uc_ind*LABEL_PASS,"#FF9AC1"),
 "user-centric · independent":   (uc_ind,C),
 "Twitch-механика (50/50, кеф 12)":(tw,TW),
 "direct · 360-сделка (кеф 4)":  (SF*4*MG*0.80*DEAL360,"#B08CFF"),
 "direct · breakeven (кеф 1.25)":(d_be,P),
 "direct · кеф 4":               (d4,P),
 "direct recurring · кеф 12, TON":(rec12,Y)}
mva={k:TARGET/v for k,(v,_) in vals.items()}
# --- fig5 REDO: полная лестница-матрица ---
fig,ax=plt.subplots(figsize=(11,6.5)); ypos=np.arange(len(vals))[::-1]
for (lbl,(v,c)),y in zip(vals.items(),ypos):
    ax.barh(y,TARGET/v,color=c,alpha=0.92); ax.text(TARGET/v*1.12,y,f"{TARGET/v:,.0f}",va="center",fontsize=9)
ax.set_yticks(ypos); ax.set_yticklabels(list(vals.keys()),fontsize=9)
ax.set_xscale("log"); ax.grid(alpha=0.15,axis="x")
ax.set_xlabel("Слушателей для $100/мес (log)"); ax.set_title("Полная матрица: {правило дележа} × {контракт} → MVA")
fig.tight_layout(); fig.savefig(OUT+"fig5_worlds_ladder.png",dpi=150)
# --- fig7 NEW: heatmap правило × контракт ---
rules=["pro-rata","user-centric","direct (кеф 4)"]; contracts=["signed / 360","independent"]
M=np.array([[pr_ind*LABEL_PASS, pr_ind],
            [uc_ind*LABEL_PASS, uc_ind],
            [SF*4*MG*0.80*DEAL360, d4]])
MVAm=TARGET/M
fig,ax=plt.subplots(figsize=(8.6,5))
im=ax.imshow(np.log10(MVAm),cmap="magma_r")
for i in range(3):
    for j in range(2):
        ax.text(j,i,f"${M[i,j]:.3f}/сл·год\nMVA {MVAm[i,j]:,.0f}",ha="center",va="center",fontsize=10,
                color="#0D0A1A" if MVAm[i,j]<20000 else "#EDEDF7")
ax.set_xticks([0,1]); ax.set_xticklabels(contracts); ax.set_yticks([0,1,2]); ax.set_yticklabels(rules)
ax.set_title("Ортогональные оси: правило дележа × контракт\n(цвет = log MVA; светлее = хуже артисту)")
fig.colorbar(im,label="log10 MVA")
fig.tight_layout(); fig.savefig(OUT+"fig7_matrix_heatmap.png",dpi=150)
# --- fig1 REDO: кривая кефа + 4 референс-линии матрицы ---
kef=np.linspace(0.5,12,60)
fig,ax=plt.subplots(figsize=(9.5,5.6))
ax.plot(kef,[TARGET/(SF*k*MG*0.80) for k in kef],color=P,lw=3,label="direct (суперфаны 1.7%, чек $6.9)")
for lbl,v,c,ls in [("pro-rata signed",pr_ind*LABEL_PASS,K,"--"),("pro-rata independent",pr_ind,G,"--"),
                   ("user-centric signed",uc_ind*LABEL_PASS,"#FF9AC1",":"),("user-centric independent",uc_ind,C,":")]:
    ax.axhline(TARGET/v,color=c,lw=2,ls=ls,label=f"{lbl}: {TARGET/v:,.0f}")
ax.set_yscale("log"); ax.grid(alpha=0.15); ax.legend(frameon=False,fontsize=9)
ax.set_xlabel("Платежей на суперфана в год (кеф)"); ax.set_ylabel("Слушателей для $100/мес (log)")
ax.set_title("MVA: direct против всей матрицы World A")
fig.tight_layout(); fig.savefig(OUT+"fig1_mva.png",dpi=150)
for k,v in mva.items(): print(f"{k:38s} {v:>10,.0f}")
