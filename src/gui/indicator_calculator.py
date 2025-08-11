# Lokalizacja: C:\Users\Msi\Desktop\Analizator\src\gui\indicator_calculator.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.core.logging_config import setup_logging
import logging
import re

# Inicjalizacja logowania
setup_logging()

def calculate_indicator(parent, indicator, fields):
    try:
        calc_window = tk.Toplevel(parent)
        calc_window.title(f"Oblicz {indicator}")
        row = 0

        def clean_numeric_input(value: str) -> float:
            """Czysci dane wejściowe z przecinków i innych znaków."""
            if not value:
                raise ValueError("Pole nie może być puste!")
            cleaned = re.sub(r"[^\d.]", "", value)  # Usuń wszystko poza cyframi i kropką
            try:
                return float(cleaned)
            except ValueError:
                raise ValueError(f"Nieprawidłowa wartość: '{value}' musi być liczbą")

        if indicator == "PE Ratio":
            ttk.Label(calc_window, text="Wzór: PE Ratio = Price / EPS (TTM)").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Price").grid(row=row, column=0, padx=5, pady=5)
            price_entry = ttk.Entry(calc_window)
            price_entry.grid(row=row, column=1, padx=5, pady=5)
            price_entry.insert(0, fields["Price"].get() or "")
            row += 1
            
            ttk.Label(calc_window, text="EPS (TTM)").grid(row=row, column=0, padx=5, pady=5)
            eps_entry = ttk.Entry(calc_window)
            eps_entry.grid(row=row, column=1, padx=5, pady=5)
            eps_entry.insert(0, fields["EPS (TTM)"].get() or "")
            row += 1
            
            def calculate():
                try:
                    price = clean_numeric_input(price_entry.get())
                    eps = clean_numeric_input(eps_entry.get())
                    if eps != 0:
                        fields["PE Ratio"].delete(0, tk.END)
                        fields["PE Ratio"].insert(0, str(round(price / eps, 2)))
                    else:
                        raise ValueError("EPS nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania PE Ratio: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
            
        elif indicator == "Forward PE":
            ttk.Label(calc_window, text="Wzór: Forward PE = Price / Forward EPS").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Price").grid(row=row, column=0, padx=5, pady=5)
            price_entry = ttk.Entry(calc_window)
            price_entry.grid(row=row, column=1, padx=5, pady=5)
            price_entry.insert(0, fields["Price"].get() or "")
            row += 1
            
            ttk.Label(calc_window, text="Forward EPS").grid(row=row, column=0, padx=5, pady=5)
            forward_eps_entry = ttk.Entry(calc_window)
            forward_eps_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    price = clean_numeric_input(price_entry.get())
                    forward_eps = clean_numeric_input(forward_eps_entry.get())
                    if forward_eps != 0:
                        fields["Forward PE"].delete(0, tk.END)
                        fields["Forward PE"].insert(0, str(round(price / forward_eps, 2)))
                    else:
                        raise ValueError("Forward EPS nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Forward PE: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
            
        elif indicator == "PEG Ratio":
            ttk.Label(calc_window, text="Wzór: PEG Ratio = PE Ratio / Annual EPS Growth (%)").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="PE Ratio").grid(row=row, column=0, padx=5, pady=5)
            pe_entry = ttk.Entry(calc_window)
            pe_entry.grid(row=row, column=1, padx=5, pady=5)
            pe_entry.insert(0, fields["PE Ratio"].get() or "")
            row += 1
            
            ttk.Label(calc_window, text="Annual EPS Growth (%)").grid(row=row, column=0, padx=5, pady=5)
            growth_entry = ttk.Entry(calc_window)
            growth_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    pe = clean_numeric_input(pe_entry.get())
                    growth = clean_numeric_input(growth_entry.get())
                    if growth != 0:
                        fields["PEG Ratio"].delete(0, tk.END)
                        fields["PEG Ratio"].insert(0, str(round(pe / growth, 2)))
                    else:
                        raise ValueError("Annual EPS Growth nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania PEG Ratio: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
            
        elif indicator == "Revenue Growth (YoY)":
            ttk.Label(calc_window, text="Wzór: Revenue Growth (YoY) (%) = (Current Revenue - Previous Revenue) / Previous Revenue * 100").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Current Revenue").grid(row=row, column=0, padx=5, pady=5)
            current_rev_entry = ttk.Entry(calc_window)
            current_rev_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Previous Revenue").grid(row=row, column=0, padx=5, pady=5)
            prev_rev_entry = ttk.Entry(calc_window)
            prev_rev_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    current_rev = clean_numeric_input(current_rev_entry.get())
                    prev_rev = clean_numeric_input(prev_rev_entry.get())
                    if prev_rev != 0:
                        fields["Revenue Growth (YoY)"].delete(0, tk.END)
                        fields["Revenue Growth (YoY)"].insert(0, str(round((current_rev - prev_rev) / prev_rev * 100, 2)))
                    else:
                        raise ValueError("Previous Revenue nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Revenue Growth (YoY): {str(e)}")
                    messagebox.showerror("Błąd", str(e))
            
        elif indicator == "Gross Margin":
            ttk.Label(calc_window, text="Wzór: Gross Margin (%) = (Revenue - COGS) / Revenue * 100").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Revenue").grid(row=row, column=0, padx=5, pady=5)
            revenue_entry = ttk.Entry(calc_window)
            revenue_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="COGS").grid(row=row, column=0, padx=5, pady=5)
            cogs_entry = ttk.Entry(calc_window)
            cogs_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    revenue = clean_numeric_input(revenue_entry.get())
                    cogs = clean_numeric_input(cogs_entry.get())
                    if revenue != 0:
                        fields["Gross Margin"].delete(0, tk.END)
                        fields["Gross Margin"].insert(0, str(round((revenue - cogs) / revenue * 100, 2)))
                    else:
                        raise ValueError("Revenue nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Gross Margin: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
            
        elif indicator == "Debt / Equity Ratio":
            ttk.Label(calc_window, text="Wzór: Debt / Equity Ratio = Total Debt / Total Equity").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Total Debt").grid(row=row, column=0, padx=5, pady=5)
            debt_entry = ttk.Entry(calc_window)
            debt_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Total Equity").grid(row=row, column=0, padx=5, pady=5)
            equity_entry = ttk.Entry(calc_window)
            equity_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    debt = clean_numeric_input(debt_entry.get())
                    equity = clean_numeric_input(equity_entry.get())
                    if equity != 0:
                        fields["Debt / Equity Ratio"].delete(0, tk.END)
                        fields["Debt / Equity Ratio"].insert(0, str(round(debt / equity, 2)))
                    else:
                        raise ValueError("Total Equity nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Debt / Equity Ratio: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
            
        elif indicator == "Current Ratio":
            ttk.Label(calc_window, text="Wzór: Current Ratio = Current Assets / Current Liabilities").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Current Assets").grid(row=row, column=0, padx=5, pady=5)
            assets_entry = ttk.Entry(calc_window)
            assets_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Current Liabilities").grid(row=row, column=0, padx=5, pady=5)
            liabilities_entry = ttk.Entry(calc_window)
            liabilities_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    assets = clean_numeric_input(assets_entry.get())
                    liabilities = clean_numeric_input(liabilities_entry.get())
                    if liabilities != 0:
                        fields["Current Ratio"].delete(0, tk.END)
                        fields["Current Ratio"].insert(0, str(round(assets / liabilities, 2)))
                    else:
                        raise ValueError("Current Liabilities nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Current Ratio: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
            
        elif indicator == "ROE":
            ttk.Label(calc_window, text="Wzór: ROE (%) = Net Income / Shareholders' Equity * 100").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Net Income").grid(row=row, column=0, padx=5, pady=5)
            income_entry = ttk.Entry(calc_window)
            income_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Shareholders' Equity").grid(row=row, column=0, padx=5, pady=5)
            equity_entry = ttk.Entry(calc_window)
            equity_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    income = clean_numeric_input(income_entry.get())
                    equity = clean_numeric_input(equity_entry.get())
                    if equity != 0:
                        fields["ROE"].delete(0, tk.END)
                        fields["ROE"].insert(0, str(round(income / equity * 100, 2)))
                    else:
                        raise ValueError("Shareholders' Equity nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania ROE: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
            
        elif indicator == "Free Cash Flow Margin":
            ttk.Label(calc_window, text="Wzór: Free Cash Flow Margin (%) = Free Cash Flow / Revenue * 100").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Free Cash Flow").grid(row=row, column=0, padx=5, pady=5)
            fcf_entry = ttk.Entry(calc_window)
            fcf_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Revenue").grid(row=row, column=0, padx=5, pady=5)
            revenue_entry = ttk.Entry(calc_window)
            revenue_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    fcf = clean_numeric_input(fcf_entry.get())
                    revenue = clean_numeric_input(revenue_entry.get())
                    if revenue != 0:
                        fields["Free Cash Flow Margin"].delete(0, tk.END)
                        fields["Free Cash Flow Margin"].insert(0, str(round(fcf / revenue * 100, 2)))
                    else:
                        raise ValueError("Revenue nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Free Cash Flow Margin: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
        
        elif indicator == "PB Ratio":
            ttk.Label(calc_window, text="Wzór: PB Ratio = Price / Book Value Per Share").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Price").grid(row=row, column=0, padx=5, pady=5)
            price_entry = ttk.Entry(calc_window)
            price_entry.grid(row=row, column=1, padx=5, pady=5)
            price_entry.insert(0, fields["Price"].get() or "")
            row += 1
            
            ttk.Label(calc_window, text="Book Value Per Share").grid(row=row, column=0, padx=5, pady=5)
            book_value_entry = ttk.Entry(calc_window)
            book_value_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    price = clean_numeric_input(price_entry.get())
                    book_value = clean_numeric_input(book_value_entry.get())
                    if book_value != 0:
                        fields["PB Ratio"].delete(0, tk.END)
                        fields["PB Ratio"].insert(0, str(round(price / book_value, 2)))
                    else:
                        raise ValueError("Book Value Per Share nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania PB Ratio: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
        
        elif indicator == "PS Ratio":
            ttk.Label(calc_window, text="Wzór: PS Ratio = Price / Revenue Per Share").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Price").grid(row=row, column=0, padx=5, pady=5)
            price_entry = ttk.Entry(calc_window)
            price_entry.grid(row=row, column=1, padx=5, pady=5)
            price_entry.insert(0, fields["Price"].get() or "")
            row += 1
            
            ttk.Label(calc_window, text="Revenue Per Share").grid(row=row, column=0, padx=5, pady=5)
            revenue_per_share_entry = ttk.Entry(calc_window)
            revenue_per_share_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    price = clean_numeric_input(price_entry.get())
                    revenue_per_share = clean_numeric_input(revenue_per_share_entry.get())
                    if revenue_per_share != 0:
                        fields["PS Ratio"].delete(0, tk.END)
                        fields["PS Ratio"].insert(0, str(round(price / revenue_per_share, 2)))
                    else:
                        raise ValueError("Revenue Per Share nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania PS Ratio: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
        
        elif indicator == "Operating Margin":
            ttk.Label(calc_window, text="Wzór: Operating Margin (%) = Operating Income / Revenue * 100").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Operating Income").grid(row=row, column=0, padx=5, pady=5)
            op_income_entry = ttk.Entry(calc_window)
            op_income_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Revenue").grid(row=row, column=0, padx=5, pady=5)
            revenue_entry = ttk.Entry(calc_window)
            revenue_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    op_income = clean_numeric_input(op_income_entry.get())
                    revenue = clean_numeric_input(revenue_entry.get())
                    if revenue != 0:
                        fields["Operating Margin"].delete(0, tk.END)
                        fields["Operating Margin"].insert(0, str(round(op_income / revenue * 100, 2)))
                    else:
                        raise ValueError("Revenue nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Operating Margin: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
        
        elif indicator == "Profit Margin":
            ttk.Label(calc_window, text="Wzór: Profit Margin (%) = Net Income / Revenue * 100").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Net Income").grid(row=row, column=0, padx=5, pady=5)
            net_income_entry = ttk.Entry(calc_window)
            net_income_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Revenue").grid(row=row, column=0, padx=5, pady=5)
            revenue_entry = ttk.Entry(calc_window)
            revenue_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    net_income = clean_numeric_input(net_income_entry.get())
                    revenue = clean_numeric_input(revenue_entry.get())
                    if revenue != 0:
                        fields["Profit Margin"].delete(0, tk.END)
                        fields["Profit Margin"].insert(0, str(round(net_income / revenue * 100, 2)))
                    else:
                        raise ValueError("Revenue nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Profit Margin: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
        
        elif indicator == "Quick Ratio":
            ttk.Label(calc_window, text="Wzór: Quick Ratio = (Current Assets - Inventory) / Current Liabilities").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Current Assets").grid(row=row, column=0, padx=5, pady=5)
            assets_entry = ttk.Entry(calc_window)
            assets_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Inventory").grid(row=row, column=0, padx=5, pady=5)
            inventory_entry = ttk.Entry(calc_window)
            inventory_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Current Liabilities").grid(row=row, column=0, padx=5, pady=5)
            liabilities_entry = ttk.Entry(calc_window)
            liabilities_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    assets = clean_numeric_input(assets_entry.get())
                    inventory = clean_numeric_input(inventory_entry.get())
                    liabilities = clean_numeric_input(liabilities_entry.get())
                    if liabilities != 0:
                        fields["Quick Ratio"].delete(0, tk.END)
                        fields["Quick Ratio"].insert(0, str(round((assets - inventory) / liabilities, 2)))
                    else:
                        raise ValueError("Current Liabilities nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Quick Ratio: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
        
        elif indicator == "Cash Ratio":
            ttk.Label(calc_window, text="Wzór: Cash Ratio = (Cash + Cash Equivalents) / Current Liabilities").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Cash + Cash Equivalents").grid(row=row, column=0, padx=5, pady=5)
            cash_entry = ttk.Entry(calc_window)
            cash_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Current Liabilities").grid(row=row, column=0, padx=5, pady=5)
            liabilities_entry = ttk.Entry(calc_window)
            liabilities_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    cash = clean_numeric_input(cash_entry.get())
                    liabilities = clean_numeric_input(liabilities_entry.get())
                    if liabilities != 0:
                        fields["Cash Ratio"].delete(0, tk.END)
                        fields["Cash Ratio"].insert(0, str(round(cash / liabilities, 2)))
                    else:
                        raise ValueError("Current Liabilities nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Cash Ratio: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
        
        elif indicator == "Debt / FCF Ratio":
            ttk.Label(calc_window, text="Wzór: Debt / FCF Ratio = Total Debt / Free Cash Flow").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Total Debt").grid(row=row, column=0, padx=5, pady=5)
            debt_entry = ttk.Entry(calc_window)
            debt_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Free Cash Flow").grid(row=row, column=0, padx=5, pady=5)
            fcf_entry = ttk.Entry(calc_window)
            fcf_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    debt = clean_numeric_input(debt_entry.get())
                    fcf = clean_numeric_input(fcf_entry.get())
                    if fcf != 0:
                        fields["Debt / FCF Ratio"].delete(0, tk.END)
                        fields["Debt / FCF Ratio"].insert(0, str(round(debt / fcf, 2)))
                    else:
                        raise ValueError("Free Cash Flow nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Debt / FCF Ratio: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
        
        elif indicator == "Earnings Growth":
            ttk.Label(calc_window, text="Wzór: Earnings Growth (%) = (Current EPS - Previous EPS) / Previous EPS * 100").grid(row=row, column=0, columnspan=2, padx=5, pady=5)
            row += 1
            ttk.Label(calc_window, text="Current EPS").grid(row=row, column=0, padx=5, pady=5)
            current_eps_entry = ttk.Entry(calc_window)
            current_eps_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            ttk.Label(calc_window, text="Previous EPS").grid(row=row, column=0, padx=5, pady=5)
            prev_eps_entry = ttk.Entry(calc_window)
            prev_eps_entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
            
            def calculate():
                try:
                    current_eps = clean_numeric_input(current_eps_entry.get())
                    prev_eps = clean_numeric_input(prev_eps_entry.get())
                    if prev_eps != 0:
                        fields["Earnings Growth"].delete(0, tk.END)
                        fields["Earnings Growth"].insert(0, str(round((current_eps - prev_eps) / prev_eps * 100, 2)))
                    else:
                        raise ValueError("Previous EPS nie może być zerem!")
                    calc_window.destroy()
                except Exception as e:
                    logging.error(f"Błąd podczas obliczania Earnings Growth: {str(e)}")
                    messagebox.showerror("Błąd", str(e))
            
        ttk.Button(calc_window, text="Oblicz", command=calculate).grid(row=row, column=0, padx=5, pady=5)
        ttk.Button(calc_window, text="Anuluj", command=calc_window.destroy).grid(row=row, column=1, padx=5, pady=5)
    except Exception as e:
        logging.error(f"Błąd podczas otwierania okna obliczania {indicator}: {str(e)}")
        messagebox.showerror("Błąd", "Nie udało się otworzyć okna obliczania!")