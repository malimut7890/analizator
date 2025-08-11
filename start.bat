REM ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\start.bat
@echo off
chcp 65001 >nul
ECHO Uruchamianie aplikacji Analizator...

cd /d %~dp0

IF NOT EXIST "venv\Scripts\activate.bat" (
    ECHO Błąd: Środowisko wirtualne nie istnieje w folderze 'venv'.
    ECHO Utwórz środowisko za pomocą: python -m venv venv
    ECHO Następnie zainstaluj zależności: pip install -r requirements.txt
    python -c "import logging; logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()]); logging.error('Środowisko wirtualne nie istnieje')"
    pause
    exit /b 1
)

CALL venv\Scripts\activate.bat
IF %ERRORLEVEL% NEQ 0 (
    ECHO Błąd: Nie udało się aktywować środowiska wirtualnego.
    ECHO Sprawdź, czy folder 'venv' jest poprawny i zawiera activate.bat.
    python -c "import logging; logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()]); logging.error('Nie udało się aktywować środowiska wirtualnego')"
    pause
    exit /b 1
)

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO Błąd: Python nie jest dostępny w środowisku wirtualnym.
    ECHO Sprawdź instalację Pythona w środowisku wirtualnym.
    python -c "import logging; logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()]); logging.error('Python nie jest dostępny')"
    pause
    exit /b 1
)

FOR %%F IN (error.log errors_only.log) DO (
    echo. > %%F 2>nul
    IF %ERRORLEVEL% NEQ 0 (
        ECHO Błąd: Brak uprawnień do zapisu pliku %%F.
        ECHO Uruchom skrypt jako administrator lub sprawdź uprawnienia do folderu.
        python -c "import logging; logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(), logging.FileHandler('errors_only.log', encoding='utf-8')]); logging.error('Brak uprawnień do zapisu pliku %%F')"
        pause
        exit /b 1
    )
)

ECHO Uruchamiam main.py...
python main.py >> error.log 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO Błąd: Nie udało się uruchomić aplikacji.
    ECHO Szczegóły błędu w error.log i errors_only.log.
    python -c "import logging; logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(), logging.FileHandler('errors_only.log', encoding='utf-8')]); logging.error('Nie udało się uruchomić aplikacji')"
    pause
    exit /b 1
)

ECHO Aplikacja zakończyła działanie.
pause