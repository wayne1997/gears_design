import tkinter as tk
from tkinter import ttk

def crear_tabla(pestana_curva):
    def agregar_fila(i):
        nueva_fila = [""] * len(matriz[0])
        matriz.insert(i + 1, nueva_fila)
        celdas.insert(i + 1, [tk.StringVar() for _ in nueva_fila])
        for widget in frame_tabla.winfo_children():
            widget.destroy()

        refrescar_tabla()

    def eliminar_fila(fila):
        if len(matriz) > 2 and 0 < fila < len(matriz):
            matriz.pop(fila)
            celdas.pop(fila)
            for widget in frame_tabla.winfo_children():
                widget.destroy()
            refrescar_tabla()

    def refrescar_tabla():
        
        for widget in frame_tabla.winfo_children():
            widget.grid_forget()

        tk.Label(frame_tabla, text="Puntos").grid(row=0, column=0)
        tk.Label(frame_tabla, text="θ").grid(row=0, column=1)
        tk.Label(frame_tabla, text="ω2/ω1").grid(row=0, column=2)

        for i, fila in enumerate(matriz):
            tk.Label(frame_tabla, text=f"Punto {i + 1}").grid(row=i + 1, column=0)
            for j, valor in enumerate(fila):
                celda = tk.Entry(frame_tabla, textvariable=celdas[i][j])
                celda.insert(0, valor)
                celda.grid(row=i + 1, column=j + 1)

            if i < len(matriz) - 1:
                btn_agregar = tk.Button(frame_tabla, text="+", command=lambda i=i: agregar_fila(i))
                btn_agregar.grid(row=i + 1, column=len(fila) + 1)

            if i > 0 and i < len(matriz) - 1:
                btn_eliminar = tk.Button(frame_tabla, text="-", command=lambda i=i: eliminar_fila(i))
                btn_eliminar.grid(row=i + 1, column=len(fila) + 2)

        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        if len(matriz) <= 9:
            scrollbar.pack_forget()
        else:
            scrollbar.pack(side=tk.RIGHT, fill='y')

    def on_canvas_configure(event):
        canvas.itemconfig(window, width=canvas.winfo_width())

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas = tk.Canvas(pestana_curva)
    canvas.pack(side=tk.LEFT, fill='both', expand=True)

    scrollbar = ttk.Scrollbar(pestana_curva, orient='vertical', command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    frame_tabla = tk.Frame(canvas)
    window = canvas.create_window((0, 0), window=frame_tabla, anchor='nw')

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', on_canvas_configure)
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    matriz = [
        ["", ""],
        ["", ""]
    ]

    celdas = [[tk.StringVar() for _ in fila] for fila in matriz]

    
    
    refrescar_tabla()

    def obtener_datos():
        x = [float(fila[0].get()) if fila[0].get() != '' else 0 for fila in celdas]
        y = [float(fila[1].get()) if fila[1].get() != '' else 0 for fila in celdas]
        return x, y

    return obtener_datos
