# -*- coding: utf-8 -*-
"""v0.4 FULL MAP: pro-rata / user-centric / direct(attention) + Twitch benchmark + MRR solver."""
import os
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rng=np.random.default_rng(42)
P,C,K,Y,G="#6B2FFF","#00D4F5","#FF4D8D","#FFD426","#1DB954"; OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","figures")+"/"
plt.rcParams.update({"figure.facecolor":"#0D0A1A","axes.facecolor":"#0D0A1A","axes.edgecolor":"#B8C8DC",
 "axes.labelcolor":"#B8C8DC","text.color":"#B8C8DC","xtick.color":"#B8C8DC","ytick.color":"#B8C8DC","font.size":11})

TARGET=1200.0; PL=21.21
# --- WORLD A ---
PR_INDEP=4.43/1000                      # pro-rata, независимый правообладатель (Duetti US 2026)
PR_SIGNED=0.0003                        # pro-rata, подписанный артист (карман после лейбла)
mva_pr_ind=TARGET/(PL*PR_INDEP); mva_pr_sgn=TARGET/(PL*PR_SIGNED)

# user-centric (SoundCloud FPR): Monte-Carlo доли кошелька слушателя
SUB_NET_YR=11.99*12*0.70                # $/год в пул прав (≈70% выручки, arXiv 2310.11861)
PAID_SHARE=0.40                          # доля платящих слушателей (freemium-бленд)
def uc_per_listener(user_total_med, n=200_000):
    p=rng.lognormal(np.log(5.16),1.676,n)                 # плэи этого артиста у слушателя
    other=rng.lognormal(np.log(user_total_med),1.0,n)     # остальное прослушивание юзера
    share=p/(p+other)
    return PAID_SHARE*SUB_NET_YR*float(share.mean())
uc_vals={u:uc_per_listener(u) for u in [5_000,10_000,20_000]}
mva_uc={u:TARGET/v for u,v in uc_vals.items()}

# Twitch-механика (рекуррентная подписка на канал): 1.7% платящих, 12 платежей, $5, сплит 50/50
tw_per_listener=0.017*12*5.0*0.50; mva_twitch=TARGET/tw_per_listener

# --- WORLD B: Tonify attention economy ---
SF=0.017; MG=float(np.exp(np.log(5.0)+0.8**2/2)); TAKE_TON=0.95*0.999
def mva_direct(kef,take=0.80): return TARGET/(SF*kef*MG*take)
mva_d_be=mva_direct(1.25); mva_d4=mva_direct(4); mva_rec12=TARGET/(SF*12*MG*TAKE_TON)

# --- fig5: лестница World A -> World B ---
ROWS={"en":["WORLD A  pro-rata · signed (Spotify, post-label pocket)",
      "WORLD A  pro-rata · independent (Spotify, $4.43/1K)",
      "WORLD A  user-centric (SoundCloud FPR, 10k-play wallet)",
      "WORLD A  Twitch mechanics (50/50 sub split, k=12)",
      "WORLD B  Tonify direct · breakeven (k=1.25)",
      "WORLD B  Tonify direct · k=4",
      "WORLD B  Tonify recurring · k=12, TON rail"],
 "ru":["WORLD A  pro-rata · signed (Spotify, карман после лейбла)",
      "WORLD A  pro-rata · independent (Spotify, $4.43/1K)",
      "WORLD A  user-centric (SoundCloud FPR, кошелёк 10k плэев)",
      "WORLD A  Twitch-механика (подписка 50/50, кеф 12)",
      "WORLD B  Tonify direct · breakeven (кеф 1.25)",
      "WORLD B  Tonify direct · кеф 4",
      "WORLD B  Tonify recurring · кеф 12, TON-рельса"]}
L5={"en":dict(xl="Listeners needed for $100/mo (log)",t="Minimum viable audience: World A → World B"),
    "ru":dict(xl="Слушателей нужно для $100/мес (log)",t="Минимальная жизнеспособная аудитория: World A → World B")}
vals5=[mva_pr_sgn,mva_pr_ind,mva_uc[10_000],mva_twitch,mva_d_be,mva_d4,mva_rec12]
cols5=[K,G,C,"#9146FF",P,P,Y]
for _lang,_out in (("en",OUT),("ru",OUT+"ru/")):
    os.makedirs(_out,exist_ok=True); L=L5[_lang]
    fig,ax=plt.subplots(figsize=(11,6))
    ypos=np.arange(len(vals5))[::-1]
    for lbl,v,c,y in zip(ROWS[_lang],vals5,cols5,ypos):
        ax.barh(y,v,color=c,alpha=0.9); ax.text(v*1.15,y,f"{v:,.0f}",va="center",color="#B8C8DC")
    ax.set_yticks(ypos); ax.set_yticklabels(ROWS[_lang],fontsize=9)
    ax.set_xscale("log"); ax.grid(alpha=0.15,axis="x")
    ax.set_xlabel(L["xl"]); ax.set_title(L["t"])
    fig.tight_layout(); fig.savefig(_out+"fig5_worlds_ladder.png",dpi=150)

# --- fig6: MRR solver ---
mau=np.logspace(5,7.7,60)
def mrr(mau,paying,kef,check,take): return mau*paying*kef*check*take/12
CFG_L={"en":["5% donation fee alone (superfans 1.7%, k=4, $6.9)",
       "+ artist subscriptions: 5% paying, k=12, $5, take 5%",
       "blended: 5% paying, k=12, $6, take 20% (drops/premium)"],
 "ru":["Только 5% на донатах (суперфаны 1.7%, кеф 4, $6.9)",
       "+ подписки на артиста: платящих 5%, кеф 12, $5, take 5%",
       "blended: платящих 5%, кеф 12, $6, take 20% (дропы/premium)"]}
L6={"en":dict(ms="Milestone $300K MRR",xl="MAU (log)",yl="Tonify MRR, $ (log)",
      t="MRR solver: which mechanics reach $300K"),
    "ru":dict(ms="Milestone $300K MRR",xl="MAU (log)",yl="Tonify MRR, $ (log)",
      t="MRR-solver: какие механики довозят до $300K")}
cfgs=[(0.017,4,6.9,0.05,K),(0.05,12,5,0.05,C),(0.05,12,6,0.20,P)]
for _lang,_out in (("en",OUT),("ru",OUT+"ru/")):
    os.makedirs(_out,exist_ok=True); L=L6[_lang]
    fig,ax=plt.subplots(figsize=(10,5.8))
    for lbl,(pr,k,ch,t,c) in zip(CFG_L[_lang],cfgs): ax.plot(mau,mrr(mau,pr,k,ch,t),lw=3,color=c,label=lbl)
    ax.axhline(300_000,color=Y,ls="--",lw=2,label=L["ms"])
    ax.set_xscale("log"); ax.set_yscale("log"); ax.grid(alpha=0.15); ax.legend(frameon=False,fontsize=9)
    ax.set_xlabel(L["xl"]); ax.set_ylabel(L["yl"]); ax.set_title(L["t"])
    fig.tight_layout(); fig.savefig(_out+"fig6_mrr_solver.png",dpi=150)

print("user-centric $/слушатель-год:",{k:round(v,3) for k,v in uc_vals.items()})
print("MVA: pr_signed %.0f | pr_indep %.0f | UC(10k) %.0f | twitch %.0f | direct_be %.0f | direct4 %.0f | rec12 %.0f"%(
 mva_pr_sgn,mva_pr_ind,mva_uc[10_000],mva_twitch,mva_d_be,mva_d4,mva_rec12))
