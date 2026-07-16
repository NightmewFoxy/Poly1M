"""Quick check: does vol-targeting improve trend OOS? (claim from sweep: Sharpe
1.12->1.42). Reuses backtest_tsmom functions/cache; prints OOS 2024->now for the
top IS vol-target configs vs their 1x siblings. ASCII only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_tsmom as T  # noqa: E402


def main() -> None:
    data = T.load()
    print("OOS 2024-01-01..now, portfolio BTC/ETH/SOL (net):")
    for kind, n, ls, vt, label in [
        ("tsmom", 30, False, False, "tsmom30 long-flat 1x (IS pick)"),
        ("tsmom", 30, False, True,  "tsmom30 long-flat VOL-TARGET"),
        ("sma", 50, False, False,   "sma50   long-flat 1x"),
        ("sma", 50, False, True,    "sma50   long-flat VOL-TARGET"),
        ("tsmom", 120, False, True, "tsmom120 long-flat VOL-TARGET"),
    ]:
        per = [T.run(data[s], kind, n, ls, vt, T.IS_END, "2027-01-01") for s in T.SYMS]
        st = T.stats(T.combine(per))
        print(f"  {label:34s}: ann={st['ann']*100:6.1f}% Sharpe={st['sharpe']:5.2f} "
              f"maxDD={st['maxdd']*100:6.1f}% worst30={st['worst30']*100:6.1f}%")


if __name__ == "__main__":
    main()
