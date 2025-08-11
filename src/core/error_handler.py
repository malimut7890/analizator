import logging
from typing import Any, Optional
from src.core.logging_config import setup_logging

# Inicjalizacja logowania
setup_logging()

class ErrorHandler:
    """
    Centralizuje obsługę błędów i logowanie wyjątków w aplikacji Analizator.
    """
    @staticmethod
    def handle_exception(exception: Exception, context: str, critical: bool = False) -> None:
        """
        Obsługuje wyjątek, logując go i wyświetlając odpowiedni komunikat.
        
        Args:
            exception: Wyjątek do obsłużenia.
            context: Kontekst błędu (np. nazwa funkcji lub modułu).
            critical: Jeśli True, przerywa działanie programu po błędzie.
        """
        error_message = f"Błąd w {context}: {str(exception)}"
        if critical:
            logging.critical(error_message)
            raise exception
        else:
            logging.error(error_message)

    @staticmethod
    def validate_data(data: Any, required_fields: list[str], context: str) -> Optional[str]:
        """
        Sprawdza, czy dane zawierają wszystkie wymagane pola i zwraca komunikat błędu, jeśli nie.
        
        Args:
            data: Słownik lub obiekt do walidacji.
            required_fields: Lista wymaganych pól.
            context: Kontekst walidacji (np. nazwa funkcji).
        
        Returns:
            Komunikat błędu lub None, jeśli dane są poprawne.
        """
        if not isinstance(data, dict):
            error_message = f"Nieprawidłowy typ danych w {context}: oczekiwano słownika, otrzymano {type(data)}"
            logging.error(error_message)
            return error_message
        
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            error_message = f"Brakujące pola w {context}: {', '.join(missing_fields)}"
            logging.warning(error_message)
            return error_message
        return None

    @staticmethod
    def log_and_return_default(context: str, default: Any, error: Exception) -> Any:
        """
        Loguje błąd i zwraca wartość domyślną.
        
        Args:
            context: Kontekst błędu.
            default: Wartość domyślna do zwrócenia.
            error: Wyjątek do zalogowania.
        
        Returns:
            Wartość domyślna.
        """
        logging.error(f"Błąd w {context}: {str(error)}")
        return default