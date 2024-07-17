@echo off
python -m pip install virtualenv
python -m venv .venv
%~dp0.venv\Scripts\python.exe -m pip install -r "%~dp0requirements.txt"
pause
