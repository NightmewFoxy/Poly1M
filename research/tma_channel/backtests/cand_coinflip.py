"""Coinflip baseline: random-direction, random-time entries on BTCUSDT.

Purpose: establish the NULL strategy's performance under the exact same
execution engine, fee model, and 2R exit mechanics used by every real
candidate. Any strategy whose numbers sit inside the coinflip distribution
has no edge — it's just riding fees + trend drift.

Signal: at randomly chosen bars, flip a fair coin for direction, SL at
1.5*ATR(14), TP at 2R (the bot's standard). Deterministic seeds; 20 seeds
per cell so we report the distribution (mean, min, max of total_net).
"""
import random
import statistics
from engine import load, atr, Sim

SEEDS = list(range(20))
N_SIGNALS = 400          # ~ matches the real strategies' trade frequency
ATR_MULT = 1.5
TP_R = 2.0

CELLS = [
    ("5m",  "taker"), ("5m",  "maker"),
    ("15m", "taker"), ("15m", "maker"),
    ("1h",  "taker"), ("1h",  "maker"),
]


def coinflip_signals(d, seed, n):
    rng = random.Random(seed)
    a = atr(d["h"], d["l"], d["c"], 14)
    lo = 20
    hi = len(d["c"]) - 10
    bars = sorted(rng.sample(range(lo, hi), n))
    sigs = []
    for i in bars:
        if a[i] is None:
            continue
        dr = rng.choice((+1, -1))
        sl = d["c"][i] - dr * ATR_MULT * a[i]
        sigs.append({"bar": i, "dir": dr, "sl": sl, "tp_r": TP_R})
    return sigs


def main():
    for iv, ex in CELLS:
        d = load("BTCUSDT", iv)
        totals, wins, ns = [], [], []
        for seed in SEEDS:
            trades = Sim(d, exec_model=ex).run(
                coinflip_signals(d, seed, N_SIGNALS))
            if not trades:
                continue
            nets = [t["net"] for t in trades]
            totals.append(sum(nets) * 100)
            wins.append(sum(1 for x in nets if x > 0) / len(nets))
            ns.append(len(trades))
        mean_t = statistics.mean(totals)
        sd_t = statistics.stdev(totals)
        pos = sum(1 for t in totals if t > 0)
        print(f"{iv:>3s} {ex:5s}  n_avg={statistics.mean(ns):5.0f}  "
              f"win={statistics.mean(wins):5.1%}  "
              f"total_net mean={mean_t:+7.1f}%  sd={sd_t:6.1f}  "
              f"min={min(totals):+7.1f}%  max={max(totals):+7.1f}%  "
              f"seeds>0: {pos}/{len(totals)}")


if __name__ == "__main__":
    main()
