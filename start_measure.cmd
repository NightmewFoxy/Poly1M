@echo off
rem Double-click to start the 24h arb-flow measurement in its own window.
rem Survives closing Claude Code; stops if you close this window, shut
rem down, or the PC sleeps. Log: data\arb_log_v2.jsonl (append-only, so
rem interrupted runs still count -- the report just sees a smaller window).
cd /d "%~dp0"
.venv\Scripts\python.exe measure_arb.py
pause
