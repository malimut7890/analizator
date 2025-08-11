# main.py
import tkinter as tk
from src.gui.main_window import MainWindow
from src.core.logging_config import setup_logging

def main():
    setup_logging()
    root = tk.Tk()
    app = MainWindow(root)   # <-- MUSI dostać root
    root.mainloop()

if __name__ == "__main__":
    main()
