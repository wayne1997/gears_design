import tkinter as tk
from tkinter import ttk

from file_handler import FileHandler
from global_functions import add_logs
import global_values

def recuadro1(pestana_curva):
    recuadro = ttk.Frame(pestana_curva)
    recuadro.grid(row=0, column=0, columnspan=4,rowspan=1, pady=10)

    # seleccion_theta = tk.StringVar()
    # seleccion_theta.set("Grados")  # Predeterminado
    # ttk.Radiobutton(recuadro, text="Grados", value="Grados", variable=seleccion_theta).grid(row=0, column=0, padx=10, pady=5)
    # ttk.Radiobutton(recuadro, text="Radianes", value="Radianes", variable=seleccion_theta).grid(row=0, column=1, padx=10, pady=5)

    #ComboBox
    options = ["Importar CSV", "Diseñar Curva"]

    
    def on_select(event):
        if combo.get() == "Importar CSV":
            add_logs("Seleccionó: Importar CSV")
            global_values.global_values["proceso"] = "CSV"
            file_handler = FileHandler()
            file_name = file_handler.show_get_file_path()
            add_logs(f"Archivo seleccionado: {file_name}")
            if file_name:
                csv_file =file_handler.process_csv_file(file_name)
                global_values.global_dataframe = csv_file
        elif combo.get() == "Diseñar Curva":
            add_logs("Seleccionó: Diseñar Curva")
            global_values.global_values["proceso"] = "DC"
            #TODO: Modificar esta funcion para adaptarla al contenido de la tabla
            #show_frame_table()
    
    combo = ttk.Combobox(recuadro, values=options, state="readonly")
    combo.grid(row=1, column=0, padx=3, pady=5)
    combo.set("Seleccionar proceso")
    combo.bind("<<ComboboxSelected>>", on_select)

    # seleccion_geometria = tk.StringVar()
    # seleccion_geometria.set("Geometría Cerrada")  # Predeterminado
    # ttk.Radiobutton(recuadro, text="Geometría Cerrada", value="Cerrada", variable=seleccion_geometria).grid(row=1, column=0, padx=10, pady=5)
    # ttk.Radiobutton(recuadro, text="Geometría Abierta", value="Abierta", variable=seleccion_geometria).grid(row=1, column=1, padx=10, pady=5)    
    return recuadro
