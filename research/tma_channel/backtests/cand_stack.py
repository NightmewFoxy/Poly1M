"""Canonical TMA 5m scalp (wbfXaqjIrJ0, 2.7M views) + variants.
Long: SMMA21>SMMA50>SMMA200, close>SMMA21, RSI(14)>50, entry candle = bullish
engulfing (or 3LS 4th candle). SL = close - 2*candle_range. TP = 2R.
Variants: day filter Tue/Wed/Thu (10SNAXJkgbg), ATR stop 2x, session 07-21.
"""
import sys
from engine import *
from cand_misc import taker_signals_run, show

def sig_stack(d, use_3ls=False):
    o,h,l,c = d["o"],d["h"],d["l"],d["c"]
    m21,m50,m200 = smma(c,21), smma(c,50), smma(c,200)
    r = rsi(c)
    out=[]
    for i in range(210,len(c)):
        if None in (m21[i],m50[i],m200[i],r[i]): continue
        rng = h[i]-l[i]
        if rng<=0: continue
        eng_b = c[i]>o[i] and c[i-1]<o[i-1] and c[i]>o[i-1]
        eng_s = c[i]<o[i] and c[i-1]>o[i-1] and c[i]<o[i-1]
        if use_3ls:
            eng_b = eng_b and all(c[k]<o[k] for k in (i-3,i-2,i-1))
            eng_s = eng_s and all(c[k]>o[k] for k in (i-3,i-2,i-1))
        if m21[i]>m50[i]>m200[i] and c[i]>m21[i] and r[i]>50 and eng_b:
            out.append((i, 1, c[i]-2*rng))
        if m21[i]<m50[i]<m200[i] and c[i]<m21[i] and r[i]<50 and eng_s:
            out.append((i, -1, c[i]+2*rng))
    return out

def sig_hiddiv_trend(d):
    """Hidden divergence WITH trend filter (YqHTDBJlkb0): long = price higher
    low, RSI lower low, in uptrend (21>50>200). Entry close, SL under signal
    candle, TP 2R (his 1:3 also tested)."""
    h,l,c = d["h"],d["l"],d["c"]
    r = rsi(c)
    m21,m50,m200 = smma(c,21), smma(c,50), smma(c,200)
    ph,pl = pivots(h,l,3)
    phs,pls = set(ph),set(pl)
    out=[]; last_ph=[]; last_pl=[]
    for i in range(210,len(c)):
        j=i-3
        if j in phs:
            for p in [p for p in last_ph if j-p<=60]:
                if h[j]<h[p] and r[j] is not None and r[p] is not None and r[j]>r[p]:
                    if m21[i]<m50[i]<m200[i]:
                        out.append((i,-1,h[j]))
                    break
            last_ph.append(j); last_ph=last_ph[-8:]
        if j in pls:
            for p in [p for p in last_pl if j-p<=60]:
                if l[j]>l[p] and r[j] is not None and r[p] is not None and r[j]<r[p]:
                    if m21[i]>m50[i]>m200[i]:
                        out.append((i,1,l[j]))
                    break
            last_pl.append(j); last_pl=last_pl[-8:]
    return out

def dayfilt(d, sigs, days):
    t=d["t"]
    return [s for s in sigs if ((t[s[0]]//86400000+4)%7) in days]

if __name__=="__main__":
    sym = sys.argv[1] if len(sys.argv)>1 else "BTCUSDT"
    for iv in ("5m","15m","30m","1h"):
        d = load(sym,iv)
        print(f"=== {sym} {iv} ===")
        s = sig_stack(d)
        show(taker_signals_run(d,s), "stack engulf 2R")
        show(taker_signals_run(d,dayfilt(d,s,{1,2,3})), "stack engulf TueWedThu")
        show(taker_signals_run(d,sig_stack(d,use_3ls=True)), "stack 3LS 2R")
        show(taker_signals_run(d,sig_hiddiv_trend(d)), "hidden-div trend 2R")
        show(taker_signals_run(d,sig_hiddiv_trend(d),tp_r=3.0), "hidden-div trend 3R")
