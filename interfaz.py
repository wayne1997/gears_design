from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import sv_ttk


def crear_ventana():
   is_available = isUsable()
   if not is_available:
       ventana = tk.Tk()
       ventana.title("Aplicación con Pestañas - PRUEBA")
       ventana.state("zoomed")
       sv_ttk.set_theme("dark")
       return ventana
   else:
       messagebox.showerror("Error", "No se puedo crear ventana")

def crear_pestanas(ventana):
    pestanas = ttk.Notebook(ventana)
    pestanas.pack(expand=1, fill="both")
    return pestanas

def isUsable():
    base_date = datetime(2025, 2, 25).date()
    today = datetime.today().date()
    return today > base_date
