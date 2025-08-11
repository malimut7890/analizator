# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\run.py
"""
Lekki punkt startowy aplikacji – alternatywa dla uruchamiania main.py bezpośrednio.
Możesz powiązać skrót/launcher z `python run.py`.
"""
from src.core.logging_config import setup_logging

def main():
    import tkinter as tk
    from src.gui.main_window import MainWindow
    setup_logging()
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
