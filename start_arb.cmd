@echo off
rem Double-click to run the arb executor in its own window (LIVE trading,
rem tiny rails: $3 max exposure unless ARB_MAX_EXPOSURE says otherwise).
rem Must run on the home PC - Polymarket geoblocks cloud IPs for orders.
rem Stop: close this window, Ctrl-C, or create data\STOP_ARB.
cd /d "%~dp0"
.venv\Scripts\python.exe arb_executor.py
pause
