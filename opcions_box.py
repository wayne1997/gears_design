import tkinter as tk
from tkinter import ttk

def recuadro1(pestana_curva):
    recuadro = ttk.Frame(pestana_curva)
    recuadro.grid(row=0, column=0, columnspan=4,rowspan=1, pady=10)

    seleccion_theta = tk.StringVar()
    seleccion_theta.set("Grados")  # Predeterminado
    ttk.Radiobutton(recuadro, text="Grados", value="Grados", variable=seleccion_theta).grid(row=0, column=0, padx=10)
    ttk.Radiobutton(recuadro, text="Radianes", value="Radianes", variable=seleccion_theta).grid(row=1, column=0, padx=10)

    seleccion_geometria = tk.StringVar()
    seleccion_geometria.set("Geometría Cerrada")  # Predeterminado
    ttk.Radiobutton(recuadro, text="Geometría Cerrada", value="Cerrada", variable=seleccion_geometria).grid(row=0, column=2, padx=10)
    ttk.Radiobutton(recuadro, text="Geometría Abierta", value="Abierta", variable=seleccion_geometria).grid(row=1, column=2, padx=10)
    
    return recuadro

