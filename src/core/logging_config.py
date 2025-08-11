# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\src\core\logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Literal

class ErrorsOnlyFilter(logging.Filter):
    """
    Filtr dla handlera errors_only.log, przepuszcza tylko logi ERROR i CRITICAL.
    """
    def filter(self, record):
        return record.levelno >= logging.ERROR

def setup_logging(log_level: Literal["DEBUG", "INFO", "ERROR"] = "DEBUG") -> None:
    """
    Konfiguruje system logowania dla aplikacji Analizator jako singleton.
    Logi zapisywane są do pliku 'error.log' (DEBUG, INFO) oraz 'errors_only.log' (ERROR i CRITICAL)
    z maksymalnym rozmiarem 10MB i 5 kopiami zapasowymi.

    Args:
        log_level: Poziom logowania ("DEBUG", "INFO", "ERROR"). Domyślnie "DEBUG".
    Returns:
        None
    """
    logger = logging.getLogger()
    if logger.handlers:
        logger.debug("Logger już skonfigurowany, pomijam konfigurację")
        return

    error_log_file = "error.log"
    errors_only_log_file = "errors_only.log"
    max_bytes = 10 * 1024 * 1024  # 10MB
    backup_count = 5

    log_dir = os.path.dirname(error_log_file)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
            print(f"Utworzono katalog logów: {log_dir}")
        except Exception as e:
            print(f"Błąd tworzenia katalogu logów: {str(e)}")
            return

    for log_file in [error_log_file, errors_only_log_file]:
        try:
            if os.path.exists(log_file):
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write("")
            else:
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write("")
            print(f"Zweryfikowano uprawnienia do zapisu dla {log_file}")
        except PermissionError as e:
            logging.basicConfig(
                level=log_level,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[logging.StreamHandler()]
            )
            logging.error(f"Brak uprawnień do zapisu pliku logów {log_file}: {str(e)}. Logi będą zapisywane tylko do konsoli.")
            return
        except Exception as e:
            logging.basicConfig(
                level=log_level,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[logging.StreamHandler()]
            )
            logging.error(f"Błąd podczas konfiguracji logowania dla pliku {log_file}: {str(e)}. Logi będą zapisywane tylko do konsoli.")
            return

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    error_handler = RotatingFileHandler(error_log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    error_handler.setLevel(logging.DEBUG)
    error_handler.setFormatter(formatter)

    errors_only_handler = RotatingFileHandler(errors_only_log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    errors_only_handler.setLevel(logging.ERROR)
    errors_only_handler.setFormatter(formatter)
    errors_only_handler.addFilter(ErrorsOnlyFilter())
    errors_only_handler.flush = lambda: errors_only_handler.stream.flush()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.setLevel(log_level)
    logger.addHandler(error_handler)
    logger.addHandler(errors_only_handler)
    logger.addHandler(console_handler)
    logger.propagate = True

    logging.debug("Test debug: Konfiguracja handlerów zakończona: error.log (DEBUG, INFO), errors_only.log (ERROR, CRITICAL), konsola (DEBUG)")
    logging.error("Test error: Weryfikacja zapisu do errors_only.log")
    errors_only_handler.flush()
    logging.info("Inicjalizacja logowania zakończona, logi zapisywane do error.log (DEBUG, INFO) i errors_only.log (ERROR, CRITICAL) z poziomem %s", log_level)
    errors_only_handler.flush()