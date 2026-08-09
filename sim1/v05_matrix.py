# -*- coding: utf-8 -*-
"""v0.5: полная матрица {правило × контракт}, перерисовка fig1/fig5, новый fig7-heatmap."""
import os
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rng=np.random.default_rng(42)
P,C,K,Y,G,TW="#6B2FFF","#00D4F5","#FF4D8D","#FFD426","#1DB954","#9146FF"; OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","figures")+"/"
plt.rcParams.update({"figure.facecolor":"#0D0A1A","axes.facecolor":"#0D0A1A","axes.edgecolor":"#B8C8DC",
 "axes.labelcolor":"#B8C8DC","text.color":"#B8C8DC","xtick.color":"#B8C8DC","ytick.color":"#B8C8DC","font.size":11})
TARGET=1200.0; PL=21.21
LABEL_PASS=0.0003/(4.43/1000)  # лейбловый проход: производная двух якорей (=6.772%, ≈CNM 6.8%), не свободный параметр
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
 "Twitch mechanics (50/50, k=12)":(tw,TW),
 "direct · 360 deal (k=4)":      (SF*4*MG*0.80*DEAL360,"#B08CFF"),
 "direct · breakeven (k=1.25)":  (d_be,P),
 "direct · k=4":                 (d4,P),
 "direct recurring · k=12, TON": (rec12,Y)}
mva={k:TARGET/v for k,(v,_) in vals.items()}
assert abs(TARGET/(pr_ind*LABEL_PASS)-TARGET/(PL*0.0003))<0.5, "v05 разошёлся с якорем $0.0003/стрим (v04/v0.2)"
# --- fig5 REDO: полная лестница-матрица (EN канон + RU в figures/ru) ---
LAD={"en":list(vals.keys()),
 "ru":["pro-rata · signed","pro-rata · independent","user-centric · signed","user-centric · independent",
       "Twitch-механика (50/50, кеф 12)","direct · 360-сделка (кеф 4)","direct · breakeven (кеф 1.25)",
       "direct · кеф 4","direct recurring · кеф 12, TON"]}
L5={"en":dict(xl="Listeners needed for $100/mo (log)",t="The full matrix: {division rule} × {contract} → MVA"),
    "ru":dict(xl="Слушателей для $100/мес (log)",t="Полная матрица: {правило дележа} × {контракт} → MVA")}
for _lang,_out in (("en",OUT),("ru",OUT+"ru/")):
    os.makedirs(_out,exist_ok=True); L=L5[_lang]
    fig,ax=plt.subplots(figsize=(11,6.5)); ypos=np.arange(len(vals))[::-1]
    for lbl,(v,c),y in zip(LAD[_lang],vals.values(),ypos):
        ax.barh(y,TARGET/v,color=c,alpha=0.92); ax.text(TARGET/v*1.12,y,f"{TARGET/v:,.0f}",va="center",fontsize=9)
    ax.set_yticks(ypos); ax.set_yticklabels(LAD[_lang],fontsize=9)
    ax.set_xscale("log"); ax.grid(alpha=0.15,axis="x")
    ax.set_xlabel(L["xl"]); ax.set_title(L["t"])
    fig.tight_layout(); fig.savefig(_out+"fig5_worlds_ladder.png",dpi=150)
# --- fig7 NEW: heatmap правило × контракт ---
L7={"en":dict(rules=["pro-rata","user-centric","direct (k=4)"],unit="/listener-yr",
      t="Orthogonal axes: division rule × contract\n(color = log MVA; darker = worse for the artist)"),
    "ru":dict(rules=["pro-rata","user-centric","direct (кеф 4)"],unit="/сл·год",
      t="Ортогональные оси: правило дележа × контракт\n(цвет = log MVA; темнее = хуже артисту)")}
contracts=["signed / 360","independent"]
M=np.array([[pr_ind*LABEL_PASS, pr_ind],
            [uc_ind*LABEL_PASS, uc_ind],
            [SF*4*MG*0.80*DEAL360, d4]])
MVAm=TARGET/M
for _lang,_out in (("en",OUT),("ru",OUT+"ru/")):
    os.makedirs(_out,exist_ok=True); L=L7[_lang]
    fig,ax=plt.subplots(figsize=(8,5.2))
    im=ax.imshow(np.log10(MVAm),cmap="magma_r",aspect="auto")
    for i in range(3):
        for j in range(2):
            ax.text(j,i,f"${M[i,j]:.4f}{L['unit']}\nMVA {MVAm[i,j]:,.0f}",ha="center",va="center",fontsize=10,
                    color="#0D0A1A" if MVAm[i,j]<20000 else "#EDEDF7")
    ax.set_xticks([0,1]); ax.set_xticklabels(contracts); ax.set_yticks([0,1,2]); ax.set_yticklabels(L["rules"])
    ax.set_title(L["t"])
    fig.colorbar(im,label="log10 MVA",fraction=0.046,pad=0.04)
    fig.tight_layout(); fig.savefig(_out+"fig7_matrix_heatmap.png",dpi=150)
# --- fig1 REDO: кривая кефа + 4 референс-линии матрицы ---
L1={"en":dict(curve="direct (superfans 1.7%, $6.9 ticket)",xl="Payments per superfan per year (k)",
      yl="Listeners needed for $100/mo (log)",t="MVA: direct vs the full World-A matrix"),
    "ru":dict(curve="direct (суперфаны 1.7%, чек $6.9)",xl="Платежей на суперфана в год (кеф)",
      yl="Слушателей для $100/мес (log)",t="MVA: direct против всей матрицы World A")}
kef=np.linspace(0.5,12,60)
for _lang,_out in (("en",OUT),("ru",OUT+"ru/")):
    os.makedirs(_out,exist_ok=True); L=L1[_lang]
    fig,ax=plt.subplots(figsize=(9.5,5.6))
    ax.plot(kef,[TARGET/(SF*k*MG*0.80) for k in kef],color=P,lw=3,label=L["curve"])
    for lbl,v,c,ls in [("pro-rata signed",pr_ind*LABEL_PASS,K,"--"),("pro-rata independent",pr_ind,G,"--"),
                       ("user-centric signed",uc_ind*LABEL_PASS,"#FF9AC1",":"),("user-centric independent",uc_ind,C,":")]:
        ax.axhline(TARGET/v,color=c,lw=2,ls=ls,label=f"{lbl}: {TARGET/v:,.0f}")
    ax.set_yscale("log"); ax.grid(alpha=0.15); ax.legend(frameon=False,fontsize=9)
    ax.set_xlabel(L["xl"]); ax.set_ylabel(L["yl"]); ax.set_title(L["t"])
    fig.tight_layout(); fig.savefig(_out+"fig1_mva.png",dpi=150)
for k,v in mva.items(): print(f"{k:38s} {v:>10,.0f}")
