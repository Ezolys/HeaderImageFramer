@echo off

rem === ���S�t�@�C�� ===
set LOGO=""
rem === ���S�t�@�C�� ===

if %LOGO% == "" (
	set LOGO_ARG=
) else (
	set LOGO_ARG=-l %LOGO%
)

%~dp0.venv\Scripts\python.exe "%~dp0main.py" "%1" %LOGO_ARG%

pause
