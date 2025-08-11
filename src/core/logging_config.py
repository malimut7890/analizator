# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\src\core\logging_config.py
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_IS_CONFIGURED = False

def _resolve_paths():
    """
    Ustal ścieżki plików logów.
    Priorytet:
      1) ERROR_LOG_PATH / ERRORS_ONLY_LOG_PATH (pełne ścieżki)
      2) LOG_DIR + nazwy plików
      3) katalog roboczy + nazwy domyślne
    """
    log_dir_env = os.getenv("LOG_DIR", "")
    error_path = os.getenv("ERROR_LOG_PATH", "")
    errors_only_path = os.getenv("ERRORS_ONLY_LOG_PATH", "")
    if error_path and errors_only_path:
        return Path(error_path), Path(errors_only_path)
    if log_dir_env:
        d = Path(log_dir_env)
        d.mkdir(parents=True, exist_ok=True)
        return d / "error.log", d / "errors_only.log"
    # domyślnie – bieżący katalog roboczy
    cwd = Path(os.getcwd())
    return cwd / "error.log", cwd / "errors_only.log"


def setup_logging(level: int = logging.DEBUG):
    """Konfiguracja logowania (wywołuj wielokrotnie bez efektu ubocznego)."""
    global _IS_CONFIGURED
    if _IS_CONFIGURED:
        logging.getLogger(__name__).debug("Logger już skonfigurowany, pomijam konfigurację")
        return

    logger = logging.getLogger()
    logger.setLevel(level)

    error_log, errors_only_log = _resolve_paths()

    # Upewnij się, że katalog istnieje
    error_log.parent.mkdir(parents=True, exist_ok=True)
    errors_only_log.parent.mkdir(parents=True, exist_ok=True)

    # Handlery plikowe
    file_handler_all = RotatingFileHandler(error_log, maxBytes=2_000_000, backupCount=2, encoding="utf-8")
    file_handler_all.setLevel(logging.DEBUG)

    file_handler_errors = RotatingFileHandler(errors_only_log, maxBytes=1_000_000, backupCount=1, encoding="utf-8")
    file_handler_errors.setLevel(logging.ERROR)

    # Konsola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    for h in (file_handler_all, file_handler_errors, console_handler):
        h.setFormatter(formatter)
        logger.addHandler(h)

    # Weryfikacja (tworzy pliki natychmiast)
    try:
        with open(error_log, "a", encoding="utf-8") as f:
            f.write("")
        print(f"Zweryfikowano uprawnienia do zapisu dla {error_log.name}")
    except Exception:
        pass
    try:
        with open(errors_only_log, "a", encoding="utf-8") as f:
            f.write("")
        print(f"Zweryfikowano uprawnienia do zapisu dla {errors_only_log.name}")
    except Exception:
        pass

    # Krótkie wpisy testowe – pozwalają testom sprawdzić obecność rekordów
    logging.getLogger(__name__).debug(
        "Test debug: Konfiguracja handlerów zakończona: %s (DEBUG, INFO), %s (ERROR, CRITICAL), konsola (DEBUG)",
        error_log.name, errors_only_log.name
    )
    logging.getLogger(__name__).error("Test error: Weryfikacja zapisu do errors_only.log")

    _IS_CONFIGURED = True
