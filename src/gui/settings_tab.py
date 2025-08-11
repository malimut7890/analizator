# Lokalizacja: C:\Users\Msi\Desktop\Analizator\src\gui\settings_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
from dotenv import load_dotenv, find_dotenv
from dotenv import set_key
from src.core.logging_config import setup_logging
import logging

class SettingsTab:
    def __init__(self, parent):
        self.parent = parent
        
        # Pole do edycji kluczy API
        self.api_key_entry = ttk.Entry(self.parent, width=50)
        self.api_key_entry.pack(pady=10)
        self.api_key_entry.insert(0, "Przykład: ALPHA_VANTAGE_API_KEY=nowy_klucz")
        
        # Przycisk Zapisz
        self.save_button = ttk.Button(self.parent, text="Zapisz klucz API", command=self.save_api_key)
        self.save_button.pack(pady=5)
        
        # Opcje logów
        self.log_level_var = tk.StringVar(value="ERROR")
        self.log_level_combo = ttk.Combobox(self.parent, values=["DEBUG", "INFO", "ERROR"], state="readonly", textvariable=self.log_level_var)
        self.log_level_combo.pack(pady=5)
        self.log_level_combo.bind("<<ComboboxSelected>>", self.update_log_level)
        
        # Limity requestów
        self.request_limit_entry = ttk.Entry(self.parent, width=50)
        self.request_limit_entry.pack(pady=10)
        self.request_limit_entry.insert(0, "Przykład: LIMIT_REQUESTS=5")
        self.save_limit_button = ttk.Button(self.parent, text="Zapisz limit requestów", command=self.save_request_limit)
        self.save_limit_button.pack(pady=5)
        
    def save_api_key(self):
        try:
            input_str = self.api_key_entry.get()
            key, value = input_str.split("=", 1)
            dotenv_path = find_dotenv(usecwd=True)
            set_key(dotenv_path, key.strip(), value.strip())
            load_dotenv(dotenv_path, override=True)
            messagebox.showinfo("Sukces", "Klucz API zapisany w .env!")
        except Exception as e:
            logging.error(f"Błąd zapisywania klucza API: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się zapisać klucza!")
    
    def update_log_level(self, event):
        try:
            level = self.log_level_var.get()
            setup_logging(level)
            messagebox.showinfo("Sukces", f"Poziom logowania zmieniony na {level}!")
        except Exception as e:
            logging.error(f"Błąd zmiany poziomu logowania: {str(e)}")
            messagebox.showerror("Błąd", f"Nie udało się zmienić poziomu logowania: {str(e)}")
    
    def save_request_limit(self):
        try:
            input_str = self.request_limit_entry.get()
            key, value = input_str.split("=", 1)
            dotenv_path = find_dotenv(usecwd=True)
            set_key(dotenv_path, key.strip(), value.strip())
            load_dotenv(dotenv_path, override=True)
            messagebox.showinfo("Sukces", "Limit requestów zapisany w .env!")
        except Exception as e:
            logging.error(f"Błąd zapisywania limitu: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się zapisać limitu!")