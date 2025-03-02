from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import sv_ttk


def crear_ventana():
    ventana = tk.Tk()
    ventana.title("Aplicación con Pestañas - PRUEBA")
    ventana.state("zoomed")
    sv_ttk.set_theme("dark")
    return ventana

def crear_pestanas(ventana):
    pestanas = ttk.Notebook(ventana)
    pestanas.pack(expand=1, fill="both")
    return pestanas
