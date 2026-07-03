@echo off
rem Double-click to run the LP rewards MICRO-PILOT live (~$200 committed):
rem 200 shares each side of the calm Fed-September market, quotes at
rem mid+/-1c. Needs the account funded (~$210 USDC) and the home IP
rem (orders 403 from cloud/WARP IPs; check: warp-cli tunnel host list).
rem Stop: create data\STOP_LP (the ONLY stop that sticks - the watchdog
rem task resurrects the quoter within ~5 min otherwise). Closing the
rem window / Ctrl-C also cancel every resting order first (console-ctrl
rem handler), but count as a crash and get auto-restarted.
cd /d "%~dp0"
set LP_LIVE=1
set LP_MARKETS=0x876506d8b2bd7a0d3fa4fe18c024eee6e1dd81ee24c26795dadd6cfe4a7b5d0d
set LP_SHARES=200
.venv\Scripts\python.exe lp_quoter.py
pause
