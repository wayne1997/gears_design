from matplotlib.axes import Axes
from file_handler import FileHandler
from global_functions import add_logs, text_validation
import global_values
from modelos_math import primitivas ,correcciones,primitivas_generico
import tkinter as tk
from tkinter import Frame, StringVar, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import pchip
import numpy as np 
from rack import cutter,ajustar_puntos,parametros,rotate,cutter3,cortar_puntas_dientes,redondear_puntas_dientes
from exportacion import exportarDXF
import pandas as pd

pi = np.pi
slider_long =  2000
axx = None




def destruir_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


#TODO: Refactoring on this function
def grafica_w(pestana_grafica: Frame, x: np.array, y: np.array):
    cs_limit_sup = 0.500
    cs_init_value= 0.0
    cs_limit_inf = -0.500

    #TODO: Don't know how this works
    if len(x) == 0 or len(y) == 0:
        add_logs("No hay datos para graficar")
        return [], [], 0
    
    interp = pchip(x, y)
    rel_trans = sum(y)/len(y)
    
    puntos = 20000
    
    #This point is in charge to create the graph
    x_interp = np.linspace(0, 360, puntos)


    y_interp = interp(x_interp) 
    
    rel_trans = sum(y_interp)/len(y_interp)
    
    rel = np.ones(puntos)*rel_trans
    fig1, axe = plt.subplots()
    
    refresh_graphic_w(axe, x, y, x_interp, y_interp, rel)
    

    # Muestra la grafica en el Frame de tkinter
    canvas = FigureCanvasTkAgg(fig1, master=pestana_grafica)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    canvas_widget.grid_propagate(False)
    canvas_widget.config(width=700, height=500)

    #Slicer precision range
    def update_range_funct(value):
        precision = 10 ** int(precision_slider.get())
        values_slider.config(from_=-precision, to=precision)
        #Ajustar los valores de los slicer para modificarlos al valor de la curva en azul x_intercp, y_interp
        add_logs(f"Precision ajustada desde:{-precision} hasta: {precision}")

    #Implementation sliders
    #TODO: Modificar el resto del slider para que trabaje con los datos finales en las otras pestañas.
    def update_range_values(value):
        global_values.cs_value_one = float(value)
        y_interp_updated = y_interp + global_values.cs_value_one
        rel_trans_updated = sum(y_interp_updated) / len(y_interp_updated)
        rel_updated = np.ones(puntos) * rel_trans_updated
        refresh_graphic_w(axe, x, y, x_interp, y_interp_updated, rel_updated)
        canvas.draw()

        add_logs(f"Valor del slider: {value}\n")

    #Sliders
    precision_panel = ttk.LabelFrame(pestana_grafica, text="Ajuste de Curva")
    precision_panel.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    #Value Sliders
    add_logs(f"Slider de modificación inicializado en {cs_init_value}")
    values_slider = ttk.Scale(precision_panel, value=cs_init_value, from_=cs_limit_sup, to=cs_limit_inf, orient="vertical", length=520,command=update_range_values)
    values_slider.grid(row=0, column=1, padx=15, pady=5, sticky="nsew")

    #Precision slider
    precision_slider = ttk.Scale(precision_panel, from_=-16, to=0, orient="vertical", length=520, command=update_range_funct)
    precision_slider.grid(row=0, column=2, padx=15, pady=5, sticky="nsew")


    def reset_curve():
        values_slider.set(0)
        precision_slider.set(0)
        cs_limit_inf = -0.500
        cs_limit_sup = 0.500
        values_slider.config(from_=cs_limit_inf, to=cs_limit_sup)
        refresh_graphic_w(axe, x, y, x_interp, y_interp, rel)
        canvas.draw()
        add_logs("Reiniciado")

    #Restablecer button
    reset_btn = ttk.Button(precision_panel, text="Restablecer", command=reset_curve)
    reset_btn.grid(row=1, column=1, padx=15, pady=5)

    return x_interp, y_interp.astype(np.float64) + global_values.cs_value_one, rel_trans


def refresh_graphic_w(axe: Axes, x: np.array, y: np.array, x_interp: np.array, y_interp: np.array, rel: np.array):
    add_logs(f"Actualizando gráfica: y: {y}")
    axe.clear()
    axe.scatter(x, y, color='red', label='Curva 1') # datos originales
    axe.plot(x_interp, y_interp, color='purple', label='Curva 2')
    axe.plot(x_interp, rel, label= f'media(ω2/ω1) {rel[0]}', color="orange")
    axe.set_xlabel('θ')
    axe.set_ylabel('ω2/ω1')
    axe.set_title('Función relación de velocidades')
    plt.xticks([0, 30, 45,60, 90, 120, 135,150, 180, 210, 225,240, 270,300,315,330,360])
    plt.xticks(rotation=45, va='top')
    plt.grid(True)
    axe.legend(bbox_to_anchor=(0, 1), loc='upper left')


def curv_prim_anim(frame1, frame2, x, y):
    add_logs("Me ejecuto a pesar de estar de ser ejecutado en otra pestaña")
    def actualizar_anim(ax, canvas, celda_texto, rotation_slider, x, y):            
        global c
        f = np.array(y)
        theta = np.array(x)

        if celda_texto.get() == '':
            c = 0
        else:
            c = float(celda_texto.get())

        ang = rotation_slider.get()

        x1, y1, x2, y2, perimetro_r1, perimetro_r2, th, ph = primitivas(theta, f, c, ang)

        # Perimetros    
        p_r1 = ttk.Label(per_frame, text=f"P1: {perimetro_r1:.4f} mm", justify="left")
        p_r1.grid(row=0, column=0, padx=5, pady=5)
        p_r2 = ttk.Label(per_frame, text=f"P2: {perimetro_r2:.4f} mm", justify="left")
        p_r2.grid(row=1, column=0, padx=5, pady=5)

        # Desplazamientos
        des_r1 = ttk.Label(des_frame, text=f"θ: {th:.4f} °", justify="left")
        des_r1.grid(row=0, column=0, padx=5, pady=5)
        des_r2 = ttk.Label(des_frame, text=f"Φ: {ph:.4f} °", justify="left")
        des_r2.grid(row=1, column=0, padx=5, pady=5)

        add_logs("Actualizando curvas primitivas...\n")

        if c > 0:
            ax.clear()
            ax.scatter(0, 0, color='red')
            ax.scatter(c, 0, color='red')
            ax.plot(x1, y1, label='r1(θ)')
            ax.plot(x2, y2, label='r2(Φ)')
            ax.axis('equal')
            ax.set_xticks([0, c])
            ax.set_yticks([0])
            ax.grid(True)
            ax.set_ylim(-c, c)
            ax.set_xlim(-c, c*2)
            ax.set_title(f'Curvas Primitivas (c = {c})')
            ax.legend()
        else:
            pass

        canvas.draw()

    fig, ax = plt.subplots()

    canvas = FigureCanvasTkAgg(fig, master=frame1)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid_propagate(False)

    canvas_widget.config(width=700, height=500)
    canvas_widget.pack(fill=tk.BOTH, expand=True)

    # Crea una ventana para el contenido
    contenido = ttk.Frame(frame1)
    contenido.pack(fill=tk.BOTH, expand=True)

    datos = ttk.Frame(frame2)
    datos.pack(fill=tk.BOTH, expand=True)

    celdas_frame = ttk.LabelFrame(datos, text="Distancia entre centros")
    celdas_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    per_frame = ttk.LabelFrame(datos, text="Perímetros")
    per_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    des_frame = ttk.LabelFrame(datos, text="Desplazamiento")
    des_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    etiqueta = ttk.Label(celdas_frame, text="c [mm]:")
    etiqueta.grid(row=0, column=0, padx=5, pady=5)

    def validar_texto(*args):
        try:
            converted_number = float(celda_texto.get())
            return converted_number
        except ValueError as error:
            add_logs(f"El número debe ser un entero o un flotante: {error}")

    celda_texto = tk.StringVar()
    celda_texto.trace_add('write', validar_texto)
    celda = ttk.Entry(celdas_frame, textvariable=celda_texto)
    celda.grid(row=0, column=1, padx=5, pady=5)

    slider_frame = ttk.LabelFrame(contenido, text="Rotar curvas")
    slider_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    long = len(x) - 1

    rotation_slider = ttk.Scale(slider_frame, from_=0, to=long, orient="horizontal", length=620, command=lambda val: actualizar_anim(ax, canvas, celda_texto, rotation_slider, x, y))
    rotation_slider.pack()

    celda_texto.trace_add('write', lambda *args: actualizar_anim(ax, canvas, celda_texto, rotation_slider, x, y))
    actualizar_anim(ax, canvas, celda_texto, rotation_slider, x, y)
    




def dientes_anim(frame1, frame2, frame3,frame4,frame5,notebook):
    global axx
    def actualizar_b(canvas, celda_m, celda_a, celda_c,rot_slider):
        global xc,yc,xg1,yg1,x1,y1,xR1,yR1,axx,angg,giro1,zc,x2,y2,ang1,ang2,mod
        if celda_c.get()=='' or celda_m.get()=='' or celda_a.get()=='':
            xc=yc=xg1=yg1 = 0 
              
        else:        
            angg = np.int_(rot_slider.get())
            
            axx.clear()
            axx.scatter(0, 0, color='red')
            axx.scatter(c, 0, color='red')
            axx.plot(x1, y1, label='primitiva 1', linestyle='dashed')
            axx.plot(x2, y2, label='primitiva 2', linestyle='dashed')
            axx.plot(xR1,yR1,label='Radio externo 1')
            axx.plot(xg1,yg1)
            xc1,yc1 = rotate(xc, yc,giro1[angg])
            xc1,yc1 = xc1+xg1[angg], yc1+yg1[angg]
            axx.plot(xc1,yc1, label='c1(θ)')
            axx.axis('equal')
            axx.set_xticks([0, c])
            axx.set_yticks([0])
            axx.grid(True)
            axx.set_ylim(-c, c)
            axx.set_xlim(-c, c*2)
            axx.set_title('Correción de curvas primitivas')
            axx.legend()  
        canvas.draw()
    
    def actualizar_a(canvas,canvas_dientes, celda_m, celda_a, celda_c,rot_slider,ax_dientes):
        add_logs("Ejecutando funcion para generar cutter")
        global xc,yc,xg1,yg1,x1,y1,xR1,yR1,axx,angg,giro1,zc,x2,y2,ang1,ang2,mod

        if celda_c.get()=='' or celda_m.get()=='' or celda_a.get()=='' or c == 0:
            a = 0
            m = 0
            cut = 0

            xc=yc=x1=y1=xg1=yg1=mod=rcut=zc=z=perim1=perim2=ang1=ang2 = 0                  
        else:
            a = np.radians(float(celda_a.get()))
            m = float(celda_m.get())
            cut = float(celda_c.get())

            #TODO: Review the variable f_correg - Requisito
            x1,y1,x2,y2,xg1,yg1,xR1,yR1,mod,rcut,zc,z,perim1,perim2,ang1,ang2,f_correg = correcciones(m,cut,slider_long)
            
            xc,yc = cutter(mod, a, rcut, zc, 1000)         
            xc,yc = ajustar_puntos(xc, yc, 10000)
            giro1 = parametros(xg1,yg1,rcut)
            giro2 = parametros(xg1,yg1,c)

             
        

        # Módulo corregido  
        p_r1 = ttk.Label(cutter_frame, text=f"módulo: {mod:.4f}   ", justify="left")
        p_r1.grid(row=0, column=0, padx=5, pady=5)
        
        # Radio cutter corregido
        p_r2 = ttk.Label(cutter_frame, text=f"radio: {rcut:.4f} mm", justify="left")
        p_r2.grid(row=1, column=0, padx=5, pady=5)

        # Perímetros corregidos
        p_r3 = ttk.Label(perimetros_frame, text=f"Perímetro 1: {perim1:.4f} mm", justify="left")
        p_r3.grid(row=0, column=0, padx=5, pady=5)
        # Perímetros corregidos
        p_r4 = ttk.Label(perimetros_frame, text=f"Perímetro 2: {perim2:.4f} mm", justify="left")
        p_r4.grid(row=1, column=0, padx=5, pady=5)

        # Num dientes 
        des_r1 = ttk.Label(num_frame, text=f"Z: {z:.4f}", justify="left")
        des_r1.grid(row=0, column=0, padx=5, pady=5)
        
        #Export to CSV
        ang_theta = ang1 * (180/np.pi)

        #Button to export csv
        file_handler = FileHandler()
        correg_data = pd.DataFrame({"Theta": ang_theta,"f_correg": f_correg})
        global_values.correg_data_global = correg_data
        exp_csv_btn = ttk.Button(cor_frame, text="Función w2/w1 corregida CSV", command= lambda: file_handler.process_export_csv(correg_data))
        exp_csv_btn.grid(row=2, column=0, padx=5, pady=10, columnspan=2, sticky="ew")

        if a > 0 and m > 0 and cut > 0:
            angg = np.int_(rot_slider.get())
            axx.clear()
            axx.scatter(0, 0, color='red')
            axx.scatter(c, 0, color='red')
            axx.plot(x1, y1, label='primitiva 1', linestyle='dashed')
            axx.plot(x2, y2, label='primitiva 2', linestyle='dashed')
            axx.plot(xR1,yR1,label='Radio externo 1')
            axx.plot(xc+xg1[angg], yc+yg1[angg], label='c1(θ)')
            axx.plot(xg1,yg1)
            axx.axis('equal')
            axx.set_xticks([0, c])
            axx.set_yticks([0])
            axx.grid(True)
            axx.set_ylim(-c, c)
            axx.set_xlim(-c, c*2)
            axx.set_title('Correción de curvas primitivas')
            axx.legend()
            
            destruir_frame(generate)
            destruir_frame(corte_dientes_frame)
            destruir_frame(export)
            destruir_frame(slider_frame2)
            
            boton_generar_cut = ttk.Button(generate, text="Generar Engranajes", command=lambda: generar_dientes(canvas_dientes,ax_dientes))
            boton_generar_cut.pack(pady=10)
            
        canvas.draw()



    def graficar_engranajes(canvas_dientes,ax_dientes,xprimitiva1,yprimitiva1,xprimitiva2,yprimitiva2,xengranaje1,yengranaje1,xengranaje2,yengranaje2,rot_slider2,ang1,ang2):
        
        if len(ang1) < 2:
            angulo_rotacion = 0
            angulo1 = 0
            angulo2 = 0
        else:
            angulo_rotacion = np.int_(rot_slider2.get())   
            angulo1 = ang1[angulo_rotacion]   
            angulo2 = ang2[angulo_rotacion] 
        
        xengranaje1,yengranaje1 = rotate(xengranaje1,yengranaje1,-angulo1)
        xprimitiva1,yprimitiva1 = rotate(xprimitiva1,yprimitiva1,-angulo1)
        
        xengranaje2 = xengranaje2 - c
        xprimitiva2 = xprimitiva2 - c
        xengranaje2,yengranaje2 = rotate(xengranaje2,yengranaje2,angulo2)
        xprimitiva2,yprimitiva2 = rotate(xprimitiva2,yprimitiva2,angulo2)
        xengranaje2 = xengranaje2 + c
        xprimitiva2 = xprimitiva2 + c
        
        ax_dientes.clear()
        ax_dientes.scatter(0, 0, color='red')
        ax_dientes.scatter(c, 0, color='red')
        ax_dientes.plot(xprimitiva1, yprimitiva1, label='primitiva 1', linestyle='dashed')
        ax_dientes.plot(xprimitiva2, yprimitiva2, label='primitiva 2', linestyle='dashed')
        ax_dientes.plot(xengranaje1, yengranaje1, label='Engranaje 1')
        ax_dientes.plot(xengranaje2, yengranaje2, label='Engranaje 2')
        ax_dientes.axis('equal')
        ax_dientes.set_xticks([0, c])
        ax_dientes.set_yticks([0])
        ax_dientes.grid(True)
        ax_dientes.set_ylim(-c, c)
        ax_dientes.set_xlim(-c, c * 2)
        ax_dientes.set_title('Engranajes no circulares')
        #ax_dientes.legend()
        
        canvas_dientes.draw()
    
 
    
    def generar_dientes(canvas_dientes,ax_dientes):
        global giro1, xe1, ye1, xe2, ye2, xxe1, yye1, xxe2, yye2,xxxe1,yyye1,xxxe2,yyye2
        
        destruir_frame(generate)
        
        def exportar(xe1,ye1,xe2,ye2,xc,yc):
            xe11, ye11 = ajustar_puntos(xe1, ye1, 8000)
            xe22, ye22 = ajustar_puntos(xe2, ye2, 8000)
            xc_, yc_ = ajustar_puntos(xc, yc, 8000)
            exportarDXF(xe11,ye11,"piñon.dxf")
            exportarDXF(xe22,ye22,"corona.dxf")
            exportarDXF(xc_,yc_,"cutter.dxf")
        
        def actualizar_celda_puntas(*args):
            global xe1, ye1, xe2, ye2, xxe1, yye1, xxe2, yye2, xxxe1,yyye1,xxxe2,yyye2
            
            valor_celda = celda_puntas.get()
            
            if valor_celda == '':
                distancia_corte = 0
            else:
                distancia_corte = float(valor_celda)
                
                xxe1, yye1 = cortar_puntas_dientes(xe1, ye1, x1, y1, distancia_corte, 1.25*mod)
                xxe2, yye2 = cortar_puntas_dientes(xe2, ye2, x2, y2, distancia_corte, 1.25*mod)
                
                xxxe1 = xxe1
                yyye1 = yye1
                xxxe2 = xxe2
                yyye2 = yye2
                
                actualizar_celda_redondeo
                
                graficar_engranajes(canvas_dientes,ax_dientes,x1,y1,x2,y2,xxxe1,yyye1,xxxe2,yyye2,rot_slider2,ang1,ang2)
        
        def actualizar_celda_redondeo(*args):
            global xxe1, yye1, xxe2, yye2, xxxe1,yyye1,xxxe2,yyye2
            
            valor_celda = celda_redondeo.get()
            
            if valor_celda == '':
                radio_redondeo = 0
            else:
                radio_redondeo = float(valor_celda)
                
                xxxe1, yyye1 = redondear_puntas_dientes(xxe1, yye1, radio_redondeo)
                xxxe2, yyye2 = redondear_puntas_dientes(xxe2, yye2, radio_redondeo)
                
                graficar_engranajes(canvas_dientes,ax_dientes,x1,y1,x2,y2,xxxe1,yyye1,xxxe2,yyye2,rot_slider2,ang1,ang2)

   
        notebook.select(3)  # Cambiar a la pestaña 3

        xe1, ye1 = cutter3(xc, yc, xg1, yg1, giro1,mod)

        # CURVA GUIA PARA GENERAR ENGRANAJE 2
        xp = c * np.cos(ang2)
        yp = c * np.sin(ang2)
        
        xp = -c * np.cos(ang2) + c
        yp = c * np.sin(ang2)
        
        angulot = ang2 + ang1
        
        print('ANGULOS')
        add_logs('ANGULOS')
        print(angulot[0])
        add_logs(str(angulot[0]))       
        print(angulot[250])
        add_logs(str(angulot[250]))
        print(angulot[500])
        add_logs(str(angulot[500]))
        print(angulot[750])
        add_logs(str(angulot[750]))
        print(angulot[-1])
        add_logs(str(angulot[-1]))
        print(len(angulot))
        add_logs(str(len(angulot)))

        
        xe2, ye2 = cutter3(xe1, ye1, xp, yp, -angulot,mod)  

        # Graficar en la nueva figura y ejes

        xxxe1 = xxe1 = xe1
        yyye1 = yye1 = ye1 
        xxxe2 = xxe2 = xe2
        yyye2 = yye2 = ye2
        
        graficar_engranajes(canvas_dientes,ax_dientes,x1,y1,x2,y2,xxxe1,yyye1,xxxe2,yyye2,0,[],[])
        
        slider_longitud = len(ang1)-1
        
        rot_slider2 = ttk.Scale(slider_frame2, from_=0, to=slider_longitud, orient="horizontal", length=620, command=lambda val: graficar_engranajes(canvas_dientes,ax_dientes,x1,y1,x2,y2,xxxe1,yyye1,xxxe2,yyye2,rot_slider2,ang1,ang2))
        rot_slider2.pack()
        
        #Crea la celda para ingresar el valor de corte en los dientes
        etiqueta_puntas = ttk.Label(corte_dientes_frame, text="reducir altura [mm]:")
        etiqueta_puntas.grid(row=0, column=0, padx=5, pady=5)

        celda_puntas = tk.StringVar()
        
        celdapuntascorte = ttk.Entry(corte_dientes_frame, textvariable=celda_puntas, validate='key')
        celdapuntascorte.grid(row=0, column=1, padx=5, pady=5)
        
        celda_puntas.trace_add('write', actualizar_celda_puntas)
        
        #Crea la celda para ingresar el valor de redondeo las puntas de los dientes
        etiqueta_redondeo = ttk.Label(corte_dientes_frame, text="redondear puntas [mm]:")
        etiqueta_redondeo.grid(row=1, column=0, padx=5, pady=5)

        celda_redondeo = tk.StringVar()
        celdapuntasredondeo = ttk.Entry(corte_dientes_frame, textvariable=celda_redondeo, validate='key')
        celdapuntasredondeo.grid(row=1, column=1, padx=5, pady=5)
        
        celda_redondeo.trace_add('write', actualizar_celda_redondeo)
        
        
        # Crear botón para exportar el DXF
        boton_generar_cut = ttk.Button(export, text="DXF", command=lambda: exportar(xxxe1,yyye1,xxxe2,yyye2,xc,yc))
        boton_generar_cut.grid(row=0, column=0, padx=5, pady=5)
        


    
    
    fig, axx = plt.subplots()

    canvas = FigureCanvasTkAgg(fig, master=frame1)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    
    fig_dientes, ax_dientes = plt.subplots()
    
    canvas_dientes = FigureCanvasTkAgg(fig_dientes, master=frame4)
    canvas_widget_dientes = canvas_dientes.get_tk_widget()
    canvas_widget_dientes.pack(fill=tk.BOTH, expand=True)

    
    # Ventana para el contenido
    contenido = ttk.Frame(frame1)
    contenido.pack(fill=tk.BOTH, expand=True)

    datos = ttk.Frame(frame2)
    datos.pack(fill=tk.BOTH, expand=True)
    
    generate = ttk.Frame(frame3)
    generate.pack(fill=tk.BOTH, expand=True)
    
    configuracion_pestana_dientes = ttk.Frame(frame5)
    configuracion_pestana_dientes.pack(fill=tk.BOTH, expand=True)

    # Frame datos de entrada
    celdas_frame = ttk.LabelFrame(datos, text="Parámetros cutter")
    celdas_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    # Frame entrada angulo de presión
    ang_frame = ttk.LabelFrame(datos, text="Águlo de presión del cutter")
    ang_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

#__________________ Frame realted to export csv file

    # Frame resultados corregidos
    cor_frame = ttk.LabelFrame(datos, text="Correciones")
    cor_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
    
    # Frame datos cutter corrregidos
    cutter_frame = ttk.LabelFrame(cor_frame, text="Parámetros cutter")
    cutter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    # Frame perímetros corregidos
    perimetros_frame = ttk.LabelFrame(cor_frame, text="Perímetros")
    perimetros_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    #Button action
    def export_primitives_csv(*args):
        add_logs("Exportando primitivas a formato csv")

    #Export button
    exp_to_csv_btn = ttk.Button(cor_frame, text="Exportar w2/w1 corregida CSV", command=export_primitives_csv)
    exp_to_csv_btn.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

#______________

    # Frame num dientes
    num_frame = ttk.LabelFrame(datos, text="Dientes ruedas no circulares")
    num_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    # Dato de entrada 1
    etiqueta = ttk.Label(celdas_frame, text="módulo :")
    etiqueta.grid(row=0, column=0, padx=5, pady=5)

    def validar_celdam(*args):
        texto = celda_m.get()
        if texto == '':
            return
        if not texto.isdigit():
            add_logs(f"Solo se permiten números enteros positivos. '{texto}' no es permitido.")
            celda_m.set(texto[:-1])

    celda_m = tk.StringVar()
    celda_m.trace_add('write', validar_celdam)
    celda1 = ttk.Entry(celdas_frame, textvariable=celda_m, validate='key')
    celda1.grid(row=0, column=1, padx=5, pady=5)
    
    # Dato de entrada 2
    etiqueta = ttk.Label(celdas_frame, text="radio [mm]:")
    etiqueta.grid(row=1, column=0, padx=5, pady=5)

    def validar_celdac(*args):
        texto = celda_c.get()
        if texto == '':
            return
        if not texto.isdigit():
            add_logs(f"Solo se permiten números enteros positivos. '{texto}' no es permitido.")
            celda_c.set(texto[:-1])

    celda_c = tk.StringVar()
    celda_c.trace_add('write', validar_celdac)
    celda3 = ttk.Entry(celdas_frame, textvariable=celda_c, validate='key')
    celda3.grid(row=1, column=1, padx=5, pady=5)
     
    # Dato de entrada 3
    etiqueta = ttk.Label(ang_frame, text="α [°]:")
    etiqueta.grid(row=2, column=0, padx=5, pady=5)

    def validar_celda_a(*args):
        texto = celda_a.get()
        if texto == '':
            return
        if not texto.isdigit():
            add_logs(f"Solo se permiten números enteros positivos. '{texto}' no es permitido.")
            celda_a.set(texto[:-1])
    celda_a = tk.StringVar()
    celda_a.trace_add('write', validar_celda_a)
    celda2 = ttk.Entry(ang_frame, textvariable=celda_a, validate='key')
    celda2.grid(row=2, column=1, padx=5, pady=5)
    
    
    # Frame para ingresar el corte de puntas en los dientes
    corte_dientes_frame = ttk.LabelFrame(configuracion_pestana_dientes, text="Ajustar dientes")
    corte_dientes_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    # Frame para exportar
    export = ttk.LabelFrame(configuracion_pestana_dientes, text="Exportar")
    export.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
    
    # Frame para slider de la pestaña dientes
    slider_dientes = ttk.Frame(frame4)
    slider_dientes.pack(fill=tk.BOTH, expand=True)
    
    slider_frame2 = ttk.LabelFrame(slider_dientes, text="Rotar engranajes")
    slider_frame2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
    
    boton_generar_cut = ttk.Button(ang_frame, text="Generar cutter", command=lambda: actualizar_a(canvas,canvas_dientes, celda_m, celda_a, celda_c, rot_slider,ax_dientes))
    boton_generar_cut.grid(row=2, column=2, pady=2)
    
    
    slider_frame = ttk.LabelFrame(contenido, text="Rotar cutter")
    slider_frame.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")


    rot_slider = ttk.Scale(slider_frame, from_=0, to=slider_long, orient="horizontal", length=620, command=lambda val: actualizar_b(canvas,celda_m, celda_a, celda_c,rot_slider))
    rot_slider.pack()
 
    actualizar_a(canvas,canvas_dientes, celda_m, celda_a, celda_c, rot_slider,ax_dientes)
