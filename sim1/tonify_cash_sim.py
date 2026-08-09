# -*- coding: utf-8 -*-
"""
TONIFY CASH SIMULATOR v0.2 — «касса против котла»
Мир строится от трёх измеренных якорей и валидируется на них; потом снимаются новые кривые.
Источники параметров: tonify-research vault (см. README).
"""
import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
N = 200_000  # артистов (масштаб ~Spotify: у 10M+ загружавших форма та же, масштаб-инвариантно)

# ---------- Мир: кусочная конструкция от измеренных якорей ----------
# Якоря: T1 87% <1000 стримов/год (Luminate); T2 2.6% > $1000/год => >225,734 стримов при $4.43/1K
#        T3 топ 0.28% артистов ~ 50% всех стримов (CMA/Last.fm, vault)
X_HI = 1000.0 / 0.00443 * (1000/1000)  # порог $1000/год в стримах: 225,734
share_low, share_mid, share_top = 0.87, 1 - 0.87 - 0.026, 0.026
n_low, n_mid, n_top = int(N*share_low), int(N*share_mid), N - int(N*share_low) - int(N*(1-0.87-0.026))
n_top = N - n_low - n_mid

low = np.exp(rng.normal(np.log(80), 1.4, n_low));  low = np.clip(low, 1, 999)          # тело <1000
mid = np.exp(rng.uniform(np.log(1000), np.log(225_734), n_mid))                        # лог-мост
ALPHA_TAIL = 1.4                                                                        # даёт топ-0.28% ~50%
top = 225_734 * (1 + rng.pareto(ALPHA_TAIL, n_top))
streams = np.concatenate([low, mid, top]); rng.shuffle(streams)
total = streams.sum()

def gini(x):
    x = np.sort(x); n = len(x)
    return float((2*np.arange(1, n+1) - n - 1).dot(x) / (n * x.sum()))

srt = np.sort(streams)
t1 = float((streams < 1000).mean())
t2 = float((streams > 225_734).mean())
top028 = float(srt[-int(N*0.0028):].sum() / total)
bottom90 = float(srt[: int(N*0.90)].sum() / total)

# ---------- Слушатели и режимы кассы ----------
PLAYS_PER_LISTENER = 21.21                    # LFM-1b среднее
listeners = np.maximum(1, streams / PLAYS_PER_LISTENER)

POOL_INDIE, POOL_SIGNED = 4.43/1000, 0.0003   # Duetti / карман подписанного
income_pool_indie, income_pool_signed = streams*POOL_INDIE, streams*POOL_SIGNED

SUPERFAN_SHARE, DONATE_MEDIAN, DONATE_SIGMA, ARTIST_TAKE = 0.017, 5.0, 0.8, 0.80
MEAN_GIFT = float(np.exp(np.log(DONATE_MEDIAN) + DONATE_SIGMA**2/2))   # ~$6.9

def direct_income(d_per_sf_year):
    return listeners * SUPERFAN_SHARE * d_per_sf_year * MEAN_GIFT * ARTIST_TAKE

# P6-инверсия: сколько донатов/суперфан/год воспроизводит измеренные 29% суперфан-доли (SoundCloud FPR)
target_share = 0.29
implied = None
for d in np.linspace(0.05, 4, 400):
    di = direct_income(d).sum()
    if di / (di + income_pool_indie.sum()) >= target_share:
        implied = d; break

# ---------- Кривая 1: минимальная жизнеспособная аудитория ($100/мес) ----------
TARGET = 1200.0
mva_pool_indie  = TARGET / (PLAYS_PER_LISTENER * POOL_INDIE)
mva_pool_signed = TARGET / (PLAYS_PER_LISTENER * POOL_SIGNED)
def mva_direct(d): return TARGET / (SUPERFAN_SHARE * d * MEAN_GIFT * ARTIST_TAKE)
dons = np.linspace(0.5, 12, 60)

# ---------- Кривая 2: фрод ----------
F = np.linspace(0, 0.30, 31)
pool_loss = F/(1+F)

# ---------- Кривая 3: логистика порога ----------
monthly_signed = income_pool_signed/12
months_to_13 = 13.0/np.maximum(monthly_signed, 1e-9)
w1 = float((months_to_13 > 12).mean()); w10 = float((months_to_13 > 120).mean())
monthly_indie = income_pool_indie/12
w1i = float((13.0/np.maximum(monthly_indie,1e-9) > 12).mean())

print(f"""
==================== ВАЛИДАЦИЯ МИРА (N={N:,} артистов) ====================
T1  <1000 стримов/год          : {t1:6.1%}   (мишень 87%, Luminate)
T2  >$1000/год (инди-карман)   : {t2:6.1%}   (мишень 2.6%, Spotify)
T3  топ-0.28% держат стримов   : {top028:6.1%}   (мишень ~50%, CMA/Last.fm)
    нижние 90% держат          : {bottom90:6.1%}   (Jensen: нижние категории ~2%)
    Gini стримов               : {gini(streams):.2f}
P6  инверсия 29% FPR [ОТОЗВАНА КРИТИКОМ, категориальная ошибка]: {implied:.2f}
    => измеренный сегодня мир = {implied:.1f} доната в год; всё сверх — то, что добывает продукт.

==================== МИНИМАЛЬНАЯ ЖИЗНЕСПОСОБНАЯ АУДИТОРИЯ ($100/мес) ====================
pro-rata · independent ($4.43/1K)         : {mva_pool_indie:>10,.0f} слушателей
pro-rata · signed ($0.0003)     : {mva_pool_signed:>10,.0f} слушателей
direct, {implied:.1f}/год [ОТОЗВАНО, CRITIC §1]: {mva_direct(implied):>10,.0f} слушателей
direct, кеф 2                       : {mva_direct(2):>10,.0f}
direct, кеф 4                       : {mva_direct(4):>10,.0f}
direct, кеф 8                      : {mva_direct(8):>10,.0f}

==================== ЛОГИСТИКА ПОРОГА ($13, холд 21 день) ====================
pro-rata signed:    ждут выплату >1 года: {w1:5.1%};  >10 лет: {w10:5.1%}
pro-rata independent: ждут выплату >1 года: {w1i:5.1%}
""")

# ---------- Графики ----------
plt.rcParams.update({"figure.facecolor":"#0D0A1A","axes.facecolor":"#0D0A1A","axes.edgecolor":"#B8C8DC",
 "axes.labelcolor":"#B8C8DC","text.color":"#B8C8DC","xtick.color":"#B8C8DC","ytick.color":"#B8C8DC","font.size":11})
P,C,K,Y = "#6B2FFF","#00D4F5","#FF4D8D","#FFD426"
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","figures")+"/"

fig,ax=plt.subplots(figsize=(9,5.5))
ax.plot(dons,[mva_direct(d) for d in dons],color=P,lw=3,label="Tonify direct till (superfans 1.7%)")
ax.axhline(mva_pool_indie,color=C,lw=2,ls="--",label=f"Pool, independent: {mva_pool_indie:,.0f}")
ax.axhline(mva_pool_signed,color=K,lw=2,ls="--",label=f"Pool, signed: {mva_pool_signed:,.0f}")
ax.set_yscale("log"); ax.grid(alpha=0.15); ax.legend(frameon=False)
ax.set_xlabel("Donations per superfan per year — the axis of the unmeasured parameter")
ax.set_ylabel("Listeners needed for $100/mo (log)")
ax.set_title("Minimum viable audience: the pool vs the direct till")
fig.tight_layout(); fig.savefig(OUT+"fig1_mva.png",dpi=150)

fig,ax=plt.subplots(figsize=(9,5.5))
bins=np.logspace(-2,6,70)
d4=direct_income(4)
for data,c,lbl in [(np.maximum(income_pool_signed,1e-2),K,"Pool: signed pocket"),
                   (np.maximum(income_pool_indie,1e-2),C,"Pool: independent pocket"),
                   (np.maximum(income_pool_indie+d4,1e-2),P,"Hybrid: pool + direct (4 donations/yr)")]:
    ax.hist(data,bins=bins,histtype="step",lw=2.2,color=c,label=lbl)
ax.axvline(1000,color=Y,lw=1.5,ls=":",ymax=0.70)
ax.text(1000,1.2,"$1,000/yr ",color=Y,rotation=90,ha="right",va="bottom",fontsize=9)
ax.set_xscale("log"); ax.set_yscale("log"); ax.grid(alpha=0.15); ax.legend(frameon=False,loc="upper right")
ax.set_xlabel("Artist income, $/yr (log)"); ax.set_ylabel("Artists (log)")
ax.set_title(f"Annual income distribution over {N:,} artists")
fig.tight_layout(); fig.savefig(OUT+"fig2_income_dist.png",dpi=150)

fig,ax=plt.subplots(figsize=(9,5.5))
ax.plot(F*100,pool_loss*100,color=K,lw=3,label="Pool: share of money leaked to bots")
ax.plot(F*100,np.zeros_like(F),color=P,lw=3,label="Direct till: honest artists' losses")
ax.fill_between(F*100,pool_loss*100,0,color=K,alpha=0.12)
ax.set_xlabel("Bot-stream injection, % of volume"); ax.set_ylabel("Losses, %")
ax.set_title("Who pays for fraud: the pool smears it on everyone, the direct rail does not")
ax.grid(alpha=0.15); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(OUT+"fig3_fraud.png",dpi=150)
print("PNG saved.")
# -*- coding: utf-8 -*-
"""v0.3: биномиальные суперфаны, кеш-слой 5% (Stars vs TON), sensitivity, milestone-solver."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rng = np.random.default_rng(42)
N=200_000
X_HI=225_734
n_low=int(N*0.87); n_mid=int(N*(1-0.87-0.026)); n_top=N-n_low-n_mid
low=np.clip(np.exp(rng.normal(np.log(80),1.4,n_low)),1,999)
mid=np.exp(rng.uniform(np.log(1000),np.log(X_HI),n_mid))
top=X_HI*(1+rng.pareto(1.4,n_top))
streams=np.concatenate([low,mid,top]); rng.shuffle(streams)

PL=21.21; listeners=np.maximum(1,streams/PL).astype(np.int64)
POOL_INDIE=4.43/1000; POOL_SIGNED=0.0003
inc_indie=streams*POOL_INDIE; inc_signed=streams*POOL_SIGNED
SF=0.017; GIFT_MED=5.0; SIG=0.8; TAKE=0.80
MG=float(np.exp(np.log(GIFT_MED)+SIG**2/2))

# --- fig2 fix: биномиальные суперфаны, честный рваный хвост ---
sf_counts=rng.binomial(listeners,SF)
d4=sf_counts*4*MG*TAKE
plt.rcParams.update({"figure.facecolor":"#0D0A1A","axes.facecolor":"#0D0A1A","axes.edgecolor":"#B8C8DC",
 "axes.labelcolor":"#B8C8DC","text.color":"#B8C8DC","xtick.color":"#B8C8DC","ytick.color":"#B8C8DC","font.size":11})
P,C,K,Y="#6B2FFF","#00D4F5","#FF4D8D","#FFD426"; OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","figures")+"/"
fig,ax=plt.subplots(figsize=(9,5.5)); bins=np.logspace(-2,6,70)
for data,c,lbl in [(np.maximum(inc_signed,1e-2),K,"Pool: signed pocket"),
                   (np.maximum(inc_indie,1e-2),C,"Pool: independent pocket"),
                   (np.maximum(inc_indie+d4,1e-2),P,"Hybrid: pool + direct (4/yr, binomial)")]:
    ax.hist(data,bins=bins,histtype="step",lw=2.2,color=c,label=lbl)
ax.axvline(1000,color=Y,lw=1.5,ls=":",ymax=0.70)
ax.text(1000,1.2,"$1,000/yr ",color=Y,rotation=90,ha="right",va="bottom",fontsize=9)
ax.set_xscale("log"); ax.set_yscale("log"); ax.grid(alpha=0.15); ax.legend(frameon=False,loc="upper right")
ax.set_xlabel("Artist income, $/yr (log)"); ax.set_ylabel("Artists (log)")
ax.set_title("Income distribution, 200,000 artists (v0.3, binomial superfans)")
fig.tight_layout(); fig.savefig(OUT+"fig2_income_dist.png",dpi=150)

# --- Кеш-слой: $1 доната по рельсам, комиссия Tonify 5% от суммы на ledger ---
rails={"TON (fee ~$0.0005)":0.999,"Stars desktop (96.5%)":0.965,"Stars mobile (67.5%)":0.675}
COMM=0.05
fig,ax=plt.subplots(figsize=(9,4.9)); ylab=[];
for i,(name,r) in enumerate(rails.items()):
    artist=r*(1-COMM); tonify=r*COMM; rail=1-r
    ax.barh(i,artist,color=P,label="To the artist" if i==0 else None)
    ax.barh(i,tonify,left=artist,color=Y,label="Tonify 5%" if i==0 else None)
    ax.barh(i,rail,left=artist+tonify,color=K,label="Rail / app stores" if i==0 else None)
    ax.text(artist/2,i,f"{artist*100:.1f}¢",ha="center",va="center",color="#0D0A1A",fontweight="bold")
    ylab.append(name)
ax.set_yticks(range(len(rails))); ax.set_yticklabels(ylab); ax.set_xlim(0,1)
ax.set_xlabel("Out of $1 donated"); ax.set_title("Where the dollar goes: two rails + the 5% Tonify fee",pad=28)
ax.legend(frameon=False,loc="lower center",bbox_to_anchor=(0.5,1.0),ncol=3)
ax.grid(alpha=0.1,axis="x")
fig.tight_layout(); fig.savefig(OUT+"fig4_rails.png",dpi=150)

# --- Sensitivity breakeven d* (против инди-котла) ---
res=[]
for pl in [8.0,21.21]:
    for g in [3.10,5.0,6.9]:
        gm=g if g==3.10 else float(np.exp(np.log(g)+SIG**2/2)) if g==5.0 else 6.9
        for s in [0.006,0.01,0.017]:
            d=(pl*POOL_INDIE)/(s*gm*TAKE); res.append((pl,g,s,d))
ds=[r[3] for r in res]
print("Breakeven донатов/суперфан/год против инди-котла: min %.2f | медиана %.2f | max %.2f"%(min(ds),float(np.median(ds)),max(ds)))

# --- Milestone solver: конфигурации, дающие $300K MRR при комиссии 5-20% ---
print("\n$300K MRR: MAU × платящих% × платежей/год × $чек × take% /12")
for mau,pr,k,chk,take in [(1e6,0.017,4,6.9,0.05),(1e6,0.05,12,5,0.05),(5e6,0.05,12,6,0.20),(10e6,0.04,12,5,0.15),(30e6,0.02,12,5,0.05)]:
    mrr=mau*pr*k*chk*take/12
    print(f"  MAU {mau/1e6:>4.0f}M × {pr*100:>4.1f}% × {k:>2} × ${chk} × take {take*100:>4.1f}%  => MRR ${mrr:>10,.0f}")
