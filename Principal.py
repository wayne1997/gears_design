import tkinter as tk
from tkinter import ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas import DataFrame
from global_functions import add_logs
import global_values
import global_widgets
from graficas import grafica_w, curv_prim_anim,dientes_anim
from interfaz import crear_ventana, crear_pestanas
from tabla import crear_tabla
from opcions_box import recuadro1
import matplotlib.pyplot as plt


x_intp = [0]
y_intp = [0]



#_________________FUNCIONES______________________________________________________
#________________________________________________________________________________

# Función para cerrar la aplicación
def cerrar_aplicacion():
    ventana.quit()


# Función para graficar la curva interpolada w2/w1
def imprimir_datos():

    plt.close('all')
    
    global x_intp, y_intp

#_________________GRAFICAR CURVA INTERPOLADA____________________________________    
    #TODO: Modificar esta función para que trabaje con datos ingresados por teclado y con los datos del archivo CSV
    
    add_logs("Graficando curva interpolada w2/w1...\n")


    # Frame para colocar la grafica w2/w1
    graf_frame = ttk.LabelFrame(pestana_curva, text="Grafica θ vs ω2/ω1")
    graf_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")
    
    #Frame para colocar la relación de transmisión TOTAL
    rel_frame = ttk.LabelFrame(pestana_curva, text="Relación de transmisión TOTAL")
    rel_frame.grid(row=3, column=1, rowspan=1, padx=10, pady=5, sticky="nsew")
    

    if global_values.global_dataframe is not None:
        #TODO: Agregar la validacion de errores.
        print("Dataframe global: ", global_values.global_dataframe)
        data_csv = global_values.global_dataframe
        x = data_csv["theta"].values
        y = data_csv["w2/w1"].values
        x_intp, y_intp, rel = grafica_w(graf_frame,x,y)
    else:
        x, y = obtener_datos()
        x_intp, y_intp, rel = grafica_w(graf_frame,x,y)
        global_values.global_dataframe = None
    
    # Label tap one
    tk.Label(rel_frame, text=f"media(ω2/ω1) = {rel}").grid(row=0, column=0)
#_________________________________________________________________________________________________________________


    # Graficar las curvas primitivas
    graf_frame2 = ttk.LabelFrame(pestana_parametros, text="Grafica curvas primitivas")
    graf_frame2.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="nsew")
   
    datos_frame = ttk.LabelFrame(pestana_parametros, text="Datos")
    datos_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")
     
    curv_prim_anim(graf_frame2,datos_frame,x_intp,y_intp)
    
    # Graficar cutter y dientes
    cutter_frame = ttk.LabelFrame(pestana_dientes, text="Grafica cutter")
    cutter_frame.grid(row=0, column=2, rowspan=7, padx=10, pady=10, sticky="nsew")
   
    datos_frame2 = ttk.LabelFrame(pestana_dientes, text="Datos")
    datos_frame2.grid(row=0, column=1, rowspan=6, padx=10, pady=10, sticky="nsew")
    
    datos_frame3 = ttk.LabelFrame(pestana_dientes, text="Grafica cutter")
    datos_frame3.grid(row=6, column=1, rowspan=1, padx=10, pady=10, sticky="nsew")
    
    
    # Graficar Dientes, Animación, Exportar DXF
      
    dientesgraf_frame = ttk.LabelFrame(pestana_dientes2, text="Engranajes")
    dientesgraf_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="nsew")
   
    export_frame = ttk.LabelFrame(pestana_dientes2, text="Ajustes finales y exportación")
    export_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")
    
     
    dientes_anim(cutter_frame,datos_frame2,datos_frame3,dientesgraf_frame,export_frame,pestanas)




#_________________CONFIGURACIONES________________________________________________
#________________________________________________________________________________
# Crear ventana principal
ventana = crear_ventana()
pestanas = crear_pestanas(ventana)

# Configurar función de cierre
ventana.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)

#________________________________FRAME DE ERRORES______________________________________
#_______________________________________________________________________________________

frame_inferior = tk.Frame(ventana, width=200, height=300)
frame_inferior.pack(fill="both", expand=True, pady=10)

if "textarea" not in global_widgets.widgets:
    text_area = tk.Text(frame_inferior, wrap="word", fg="white", height=35, width=200, font=("Arial", 12))
    # Crear una Scrollbar y vincularla al TextArea
    scrollbar = ttk.Scrollbar(frame_inferior, command=text_area.yview)
    scrollbar.pack(side="right", fill="y")
    text_area.pack();
    # Configurar la scrollbar para que funcione con el TextArea
    global_widgets.widgets["textarea"] = text_area
    text_area.config(yscrollcommand=scrollbar.set)


#_________________CREAR PESTAÑAS_________________________________________________
#________________________________________________________________________________
# Pestaña 1: Definir curva w2/w1
pestana_curva = ttk.Frame(pestanas)
pestanas.add(pestana_curva, text="Relacion de velocidades")

# Pestaña 2: Definir parámetros para las curvas primitivas
pestana_parametros = crear_pestanas(ventana)
pestanas.add(pestana_parametros, text="Curvas Primitivas")

# Pestaña 3: Parámetros para los dientes de los engranajes
pestana_dientes = crear_pestanas(ventana)
pestanas.add(pestana_dientes, text="Cutter")

# Pestaña 4: Parámetros para los dientes de los engranajes
pestana_dientes2 = crear_pestanas(ventana)
pestanas.add(pestana_dientes2, text="Dientes")


# Tab 5: Analisis
tab_analysis = crear_pestanas(ventana)
pestanas.add(tab_analysis, text="Análisis")


# ________________Contenido: Relacion de velocidades_____________________________
#________________________________________________________________________________


# Frame para el recuadro de opciones
recuadro_frame = ttk.LabelFrame(pestana_curva, text="Opciones")
recuadro_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
# Frame para la tabla
tabla_frame = ttk.LabelFrame(pestana_curva, text="Tabla")

tabla_frame.grid(row=1, column=0, rowspan=2,padx=10, pady=0, sticky="nsew")
tabla_frame.grid_rowconfigure(0, weight=1)

# Colocar el recuadro de opciones dentro del marco
recuadro = recuadro1(recuadro_frame)
recuadro.grid(row=0,rowspan=1, column=0, padx=10, pady=10)

#Creates ui's table
obtener_datos = crear_tabla(tabla_frame)

boton_graficar = ttk.Button(pestana_curva, text="Graficar",command=imprimir_datos)
boton_graficar.grid(row=3, column=0, pady=10)

# __________________Contenido: Curvas Primitivas_________________________________
#________________________________________________________________________________






# __________________________Contenido: Dientes___________________________________
#________________________________________________________________________________


# __________________________Contenido: Analisis___________________________________
#________________________________________________________________________________

# Frame para el recuadro de opciones
analysis_tab = ttk.LabelFrame(tab_analysis, text="Opciones")
analysis_tab.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")




ventana.mainloop()
