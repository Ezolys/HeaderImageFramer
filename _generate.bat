@echo off

rem === ロゴファイル ===
set LOGO=""
rem === ロゴファイル ===

if %LOGO% == "" (
	set LOGO_ARG=
) else (
	set LOGO_ARG=-l %LOGO%
)

%~dp0.venv\Scripts\python.exe "%~dp0main.py" "%1" %LOGO_ARG%

pause
