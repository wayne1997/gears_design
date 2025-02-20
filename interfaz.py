import tkinter as tk
from tkinter import ttk

import sv_ttk


def crear_ventana():
    ventana = tk.Tk()
    ventana.title("Aplicación con Pestañas")
    sv_ttk.set_theme("dark")
    return ventana

def crear_pestanas(ventana):
    pestanas = ttk.Notebook(ventana)
    pestanas.pack(expand=1, fill="both")
    return pestanas