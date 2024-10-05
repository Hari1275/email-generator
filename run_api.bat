@echo off
cd /d %~dp0
set PYTHONPATH=%PYTHONPATH%;%CD%
streamlit run api\main.py