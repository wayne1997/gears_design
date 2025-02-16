import tkinter as tk
from tkinter import ttk

def crear_ventana():
    ventana = tk.Tk()
    ventana.title("Aplicación con Pestañas")
    return ventana

def crear_pestanas(ventana):
    pestanas = ttk.Notebook(ventana)
    pestanas.pack(expand=1, fill="both")
    return pestanas