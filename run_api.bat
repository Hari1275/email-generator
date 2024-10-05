@echo off
cd /d %~dp0
set PYTHONPATH=%PYTHONPATH%;%CD%
python api\main.py