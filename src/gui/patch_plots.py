# ŚCIEŻKA: src/gui/patch_plots.py
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from src.gui.plot_windows import show_price, show_scores, show_financials
from src.core.company_data import CompanyData

def patch_mainwindow_plots() -> None:
    """
    Dokleja do klasy MainWindow kompletne metody:
      - show_price_plot_window / hide_price_plot_window
      - show_score_plot_window / hide_score_plot_window
      - show_financial_plots   / hide_financial_plots

    Dzięki temu przyciski/akcje w istniejącym GUI zaczną działać bez większych zmian.
    """
    from src.gui.main_window import MainWindow

    def _get_selected_ticker(self) -> Optional[str]:
        # priorytet: aktualnie wybrany wiersz w tabeli
        try:
            sel = self.tree.selection()
            if sel:
                item = self.tree.item(sel[0])
                vals = item.get("values") or []
                if vals:
                    return str(vals[0]).strip()
        except Exception:
            pass
        # fallback: ostatnio ustawiony ticker
        return getattr(self, "current_ticker", None)

    def show_price_plot_window(self):
        ticker = _get_selected_ticker(self)
        if not ticker:
            messagebox.showwarning("Brak wyboru", "Zaznacz spółkę w tabeli.")
            return
        hist = self.company_data.load_company_history(ticker)
        top, canvas = show_price(self.root, ticker, hist)
        if top is not None:
            self.price_plot_window = top
            self.price_plot_canvas = canvas

    def hide_price_plot_window(self):
        w = getattr(self, "price_plot_window", None)
        try:
            if w is not None and w.winfo_exists():
                w.destroy()
        except Exception:
            pass
        finally:
            if hasattr(self, "price_plot_window"): delattr(self, "price_plot_window")
            if hasattr(self, "price_plot_canvas"): delattr(self, "price_plot_canvas")

    def show_score_plot_window(self):
        ticker = _get_selected_ticker(self)
        if not ticker:
            messagebox.showwarning("Brak wyboru", "Zaznacz spółkę w tabeli.")
            return
        hist = self.company_data.load_score_history(ticker)
        top, canvas = show_scores(self.root, ticker, hist)
        if top is not None:
            self.score_plot_window = top
            self.score_plot_canvas = canvas

    def hide_score_plot_window(self):
        w = getattr(self, "score_plot_window", None)
        try:
            if w is not None and w.winfo_exists():
                w.destroy()
        except Exception:
            pass
        finally:
            if hasattr(self, "score_plot_window"): delattr(self, "score_plot_window")
            if hasattr(self, "score_plot_canvas"): delattr(self, "score_plot_canvas")

    def show_financial_plots(self):
        ticker = _get_selected_ticker(self)
        if not ticker:
            messagebox.showwarning("Brak wyboru", "Zaznacz spółkę w tabeli.")
            return
        fin = self.company_data.load_financials(ticker)
        top, canvas = show_financials(self.root, ticker, fin)
        if top is not None:
            self.financial_window = top
            self.financial_canvas = canvas

    def hide_financial_plots(self):
        w = getattr(self, "financial_window", None)
        try:
            if w is not None and w.winfo_exists():
                w.destroy()
        except Exception:
            pass
        finally:
            if hasattr(self, "financial_window"): delattr(self, "financial_window")
            if hasattr(self, "financial_canvas"): delattr(self, "financial_canvas")

    # patchujemy metody
    for name, fn in {
        'show_price_plot_window': show_price_plot_window,
        'hide_price_plot_window': hide_price_plot_window,
        'show_score_plot_window': show_score_plot_window,
        'hide_score_plot_window': hide_score_plot_window,
        'show_financial_plots': show_financial_plots,
        'hide_financial_plots': hide_financial_plots,
    }.items():
        setattr(MainWindow, name, fn)
