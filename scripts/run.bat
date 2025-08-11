:: ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\scripts\run.bat
@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

REM Ustal katalog projektu na folder nadrzędny względem /scripts
set "SCRIPT_DIR=%~dp0"
set "PROJ_DIR=%SCRIPT_DIR%\.."
cd /d "%PROJ_DIR%"

REM Tworzenie środowiska, jeśli brak
if not exist ".venv\Scripts\python.exe" (
  echo [run.bat] Tworzenie srodowiska .venv...
  py -3 -m venv .venv
)

REM Aktywacja
call ".venv\Scripts\activate.bat"

REM Instalacja zaleznosci (idempotentnie)
if exist "requirements.txt" (
  echo [run.bat] Sprawdzam zaleznosci...
  python -m pip install --upgrade pip >nul 2>nul
  pip install -r requirements.txt
)

echo [run.bat] Start aplikacji...
python main.py
endlocal
