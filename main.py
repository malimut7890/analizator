# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\main.py
import tkinter as tk
from src.gui.main_window import MainWindow
from src.core.logging_config import setup_logging
import logging

# Inicjalizacja logowania
setup_logging()

def main():
    """
    Uruchamia główną aplikację Analizator.
    
    Inicjalizuje główne okno Tkinter, tworzy instancję klasy MainWindow i rozpoczyna
    główną pętlę aplikacji. Obsługuje globalne wyjątki, logując błędy do pliku error.log.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        Exception: W przypadku błędów podczas uruchamiania aplikacji, loguje błąd i rzuca wyjątek.
    
    Example:
        >>> main()
        # Uruchamia aplikację, tworząc okno GUI i zapisując logi do error.log
    """
    try:
        root = tk.Tk()
        app = MainWindow(root)
        logging.info("Uruchomiono aplikację Analizator")
        root.mainloop()
    except Exception as e:
        logging.error(f"Błąd uruchamiania aplikacji: {str(e)}")
        raise

if __name__ == "__main__":
    main()