# ŚCIEŻKA: src/gui/plot_windows.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Optional, Dict
from datetime import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def _ensure_top(title: str, prev: Optional[tk.Toplevel]) -> tk.Toplevel:
    try:
        if prev is not None and prev.winfo_exists():
            prev.destroy()
    except Exception:
        pass
    win = tk.Toplevel()
    win.title(title)
    win.geometry("900x520")
    return win

def show_price(window_owner, ticker: str, history: List[Tuple[datetime, Optional[float]]]):
    if not history:
        messagebox.showinfo("Brak danych", f"Brak historii cen dla {ticker}.")
        return None, None

    dates = [d for d, v in history if v is not None]
    prices = [float(v) for d, v in history if v is not None]

    if not dates or not prices:
        messagebox.showinfo("Brak danych", f"Brak prawidłowych punktów cenowych dla {ticker}.")
        return None, None

    top = _ensure_top(f"Cena – {ticker}", getattr(window_owner, "price_plot_window", None))

    fig = Figure(figsize=(9, 4.5), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(dates, prices, marker="o", linewidth=1.5)
    ax.set_title(f"Historia ceny: {ticker}")
    ax.set_xlabel("Data")
    ax.set_ylabel("Cena")
    ax.grid(True, alpha=0.25)

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    return top, canvas

def show_scores(window_owner, ticker: str, score_hist: List[Tuple[datetime, Optional[float]]]):
    if not score_hist:
        messagebox.showinfo("Brak danych", f"Brak historii punktacji dla {ticker}.")
        return None, None

    dates = [d for d, v in score_hist if v is not None]
    scores = [float(v) for d, v in score_hist if v is not None]
    if not dates or not scores:
        messagebox.showinfo("Brak danych", f"Brak prawidłowych punktów punktacji dla {ticker}.")
        return None, None

    top = _ensure_top(f"Punkty – {ticker}", getattr(window_owner, "score_plot_window", None))

    fig = Figure(figsize=(9, 4.5), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(dates, scores, marker="o", linewidth=1.5)
    ax.set_title(f"Historia punktów: {ticker}")
    ax.set_xlabel("Data")
    ax.set_ylabel("Punkty")
    ax.grid(True, alpha=0.25)

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    return top, canvas

def show_financials(window_owner, ticker: str, financials: Dict[str, List[Tuple[str, float]]]):
    q = financials.get("quarterly_revenue") or []
    y = financials.get("yearly_revenue") or []

    if not q and not y:
        messagebox.showinfo("Brak danych", f"Brak danych finansowych dla {ticker}.")
        return None, None

    top = _ensure_top(f"Dane finansowe – {ticker}", getattr(window_owner, "financial_window", None))

    fig = Figure(figsize=(10, 5.2), dpi=100)

    if q and y:
        ax1 = fig.add_subplot(121)
        labels_q = [l for l, v in q][-12:]  # ostatnie 12 kwartałów
        vals_q = [v for l, v in q][-12:]
        ax1.bar(labels_q, vals_q)
        ax1.set_title("Przychody kwartalne")
        ax1.tick_params(axis='x', rotation=60)
        ax1.grid(True, axis='y', alpha=0.25)

        ax2 = fig.add_subplot(122)
        labels_y = [l for l, v in y][-8:]    # ostatnie 8 lat
        vals_y = [v for l, v in y][-8:]
        ax2.bar(labels_y, vals_y)
        ax2.set_title("Przychody roczne")
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, axis='y', alpha=0.25)
    else:
        ax = fig.add_subplot(111)
        if q:
            labels = [l for l, v in q][-12:]
            vals = [v for l, v in q][-12:]
            ax.set_title("Przychody kwartalne")
            ax.tick_params(axis='x', rotation=60)
        else:
            labels = [l for l, v in y][-8:]
            vals = [v for l, v in y][-8:]
            ax.set_title("Przychody roczne")
            ax.tick_params(axis='x', rotation=45)
        ax.bar(labels, vals)
        ax.grid(True, axis='y', alpha=0.25)

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    return top, canvas
