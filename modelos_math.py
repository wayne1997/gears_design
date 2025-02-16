import numpy as np
import shapely.geometry as shp 
from scipy.interpolate import interp1d

pi = np.pi


def primitivas(theta,f,c,ang):
    global thet,phi,r1,r2,c1
    c1 = c
    ang = int(ang)
    longitud = len(theta)
    rel_trans = sum(f)/len(f)
    f = f - (rel_trans - 1) 
    paso = theta[2]-theta[1]
    
    r1 = c*(f)/(1+f)
    r2 = c - r1     

    phi = np.zeros(longitud)
    
    for i in range(1, longitud):    
        phi[i] = paso*f[i] + phi[i-1]
     
    #phi = phi/(rel_trans)
   
    #perimetro_r2 = 0
    #perimetro_r1 = 0
   
    theta = theta*pi/180 
    thet = theta  
    phi = phi*pi/180
    paso = paso*pi/180
    
    #x = r1 * np.cos(theta)
    #y = r1 * np.sin(theta)
    
    #per_acumulado, per_pasos = longitudes_lados(x,y) 
    #ang_2 = angulos(r2,per_pasos)
    #ang_2 = np.cumsum(ang_2)
    #ang_2 = np.insert(ang_2, 0, 0)
    #factor_correct = theta[-1]/ang_2[-1]
    #ang_2 = ang_2*factor_correct
    
    x1 = r1 * np.cos(theta-theta[ang])
    y1 = r1 * np.sin(theta-theta[ang])
    
    # Hago un espejo respecto al eje y para r2
    x3 = r2 * np.cos(phi-phi[ang])
    x2 = -x3 + c
    y2 = r2 * np.sin(phi-phi[ang])
    
    x1 = np.delete(x1, -1)
    y1 = np.delete(y1, -1)
    x2 = np.delete(x2, -1)
    y2 = np.delete(y2, -1)
    
    coordinates1 = list(zip(x1, y1))
    coordinates2 = list(zip(x2, y2))
    polygon1 = shp.Polygon(coordinates1)
    polygon2 = shp.Polygon(coordinates2)
    perimeter1 = polygon1.length
    perimeter2 = polygon2.length
    
    return x1,y1,x2,y2,perimeter1,perimeter2,theta[ang]*(180/pi),phi[ang]*(180/pi)


def primitivas_generico(x_,y_,c):
    x = np.array(x_)
    y = np.array(y_)
    r_1 = np.sqrt(x**2 + y**2)  
    r_2 = c - r_1

    ang_1 = np.arctan2(y, x)
    ang_1[ang_1 < 0] += 2*np.pi
    ang_1[0] = 0
    ang_1[-1] = 2*np.pi

    # calculo del angulo de r2  
    per_acumulado, per_pasos = longitudes_lados(x,y) 

    ang_2 = angulos(r_2,per_pasos)    
    ang_2 = np.cumsum(ang_2)

    factor_correct = ang_1[-1]/ang_2[-1]
    ang_2 = ang_2*factor_correct

     
    x1 = r_1 * np.cos(ang_1)
    y1 = r_1 * np.sin(ang_1)
    
    # Espejo respecto al eje Y para r2
    x2 = -r_2 * np.cos(ang_2) + c
    y2 = r_2 * np.sin(ang_2)
    
    return x2,y2,ang_1,ang_2
    

def angulos(r, s):
    angulos_resultantes = []

    # Calcular ángulos para cada par de puntos consecutivos
    for i in range(len(s)-1):
        # Calcular ángulo usando la ley de los cosenos
        cos_theta = (r[i]**2 + r[i + 1]**2 - s[i+1]**2) / (2 * r[i] * r[i + 1])

        # Manejar posibles errores de redondeo que podrían llevar a un valor fuera del rango [-1, 1]
        cos_theta = max(min(cos_theta, 1), -1)
        angulo_rad = np.arccos(cos_theta)

        # Agregar ángulo a la lista de resultados
        angulos_resultantes.append(angulo_rad)
    angulos_resultantes = np.insert(angulos_resultantes, 0, 0)
    return angulos_resultantes


def longitudes_lados(x, y):
    longitudes = []
    for i in range(len(x) - 1):
        distancia = ((x[i+1] - x[i])**2 + (y[i+1] - y[i])**2)**0.5
        longitudes.append(distancia)
    
    longitudes = np.insert(longitudes, 0, 0)
    acumulativas = np.cumsum(longitudes)
    
    return acumulativas,longitudes


def perimetro(x,y):
    coordinates = list(zip(x, y))
    polygon = shp.Polygon(coordinates)
    perimeter = polygon.length
    return perimeter


def ajustar_puntos_angular(x, y, nuevos_puntos):
    
    # Calcular ángulos a lo largo de la curva
    angulos = np.arctan2(y - y.mean(), x - x.mean())
    angulos[angulos < 0] += 2 * np.pi  # Asegurar que los ángulos estén en el rango [0, 2*pi)

    # Manejo de duplicados
    _, unique_indices = np.unique(angulos, return_index=True)
    angulos = angulos[unique_indices]
    x = x[unique_indices]
    y = y[unique_indices]

    # Manejo de infinitos y NaN
    mask = np.isfinite(angulos) & np.isfinite(x) & np.isfinite(y)
    angulos = angulos[mask]
    x = x[mask]
    y = y[mask]

    # Agregar un pequeño desplazamiento a las coordenadas x
    x += 1e-9

    # Ajustar la curva interpolando angularmente
    interpolacion_angular = interp1d(angulos, np.column_stack((x, y)), kind='linear', axis=0, fill_value='extrapolate')

    # Crear nuevos ángulos igualmente espaciados, asegurando que comiencen en 0
    nuevos_angulos = np.linspace(0, 2 * np.pi, nuevos_puntos, endpoint=False)

    # Evaluar la interpolación en los nuevos ángulos
    nueva_curva = interpolacion_angular(nuevos_angulos)

    xx, yy = nueva_curva[:, 0], nueva_curva[:, 1]
    xx, yy = reorder_points(xx, yy,nuevos_puntos)
      
    return xx, yy


def reorder_points(x, y,nuevos_puntos):
    # Calcular ángulos polares
    angles = np.arctan2(y, x)
    angles[angles < 0] += 2*np.pi

    # Obtener índices que ordenan los ángulos en orden ascendente
    order = np.argsort(angles)

    # Encontrar el índice del ángulo más cercano o igual a cero
    start_index = np.argmin(np.abs(angles[order]))
    
    # Reorganizar los puntos comenzando desde el índice encontrado
    x_r = np.roll(x[order], -start_index)
    y_r = np.roll(y[order], -start_index)
    print('REORDER POINTS')
    print(len(y_r))  
    if y_r[0] != 0:
        print('111________')
        x_r = np.concatenate(([x_r[0]], x_r))
        y_r = np.concatenate(([0], y_r))
        print(len(y_r))  
   
    if y_r[-1] != 0:
        if len(y_r) > nuevos_puntos:
            print('222________')
            x_r[-1] = x_r[0]
            y_r[-1] = y_r[0]
            print(len(y_r))  
        else:
            print('333________')
            x_r = np.concatenate((x_r, [x_r[0]]))
            y_r = np.concatenate((y_r, [y_r[0]]))
            print(len(y_r))  
            
        print('concatena el ultimo valor')
        
    
    return x_r,y_r


def generar_offset(x, y, distancia_desfase):
    # Verificar si los puntos son cercanos, en lugar de exactamente iguales    
    if np.linalg.norm(np.array([x[-1], y[-1]]) - np.array([x[0], y[0]])) > 1e-9:
        x, y = np.concatenate((x, [x[0]])), np.concatenate((y, [y[0]]))

    original_curve = shp.LineString(np.column_stack((x, y)))

    original_curve = shp.Polygon(original_curve)

    offset_polygon = original_curve.buffer(distancia_desfase)
        
    # Convertir a LineString para evitar polígonos multipartes con buffer negativo
    offset_line = shp.LineString(offset_polygon.exterior.coords)

    x_offset, y_offset = offset_line.xy
    
    return np.array(x_offset), np.array(y_offset)


def offset_abierto(x,y,distancia_offset):
    linea_original = shp.LineString(np.column_stack((x, y)))
    linea_offset = linea_original.parallel_offset(distancia_offset, side='right')
    x, y = linea_offset.xy
    return np.array(x),np.array(y)


def corregir_curvatura(x, y,radio_cut,ajuste_angular):
    print("CORRECCION CURVATURA")
    x,y = generar_offset(x, y,radio_cut)  
    x,y = generar_offset(x, y,-2*radio_cut)
    x,y = generar_offset(x, y,radio_cut)
     
    x,y = ajustar_puntos_angular(x, y, ajuste_angular)
    
    return x,y
    
    
def correcciones(m,radio_cutter,paso):
    global r1,r2,thet,phi,c1

    x1 = r1 * np.cos(thet)
    y1 = r1 * np.sin(thet)
    x2 = r2 * np.cos(phi)
    y2 = r2 * np.sin(phi)   
     
    perim = perimetro(x1,y1)
 
    z = round(perim/(pi*m))
    m = perim/(pi*z)
    zc = round((2*radio_cutter)/m)
    radio_cut1 = (zc*m)/2
      
    x1,y1 = corregir_curvatura(x1, y1,radio_cut1,1000)   
    
    perim = perimetro(x1,y1) 
    z = round(perim/(pi*m))
    m = perim/(pi*z)
    zc = round((2*radio_cut1)/m)
    radio_cut2 = (zc*m)/2
        

    if radio_cut2 > radio_cut1:
        radio_cut2 = ((zc-1)*m)/2
    

    xg1,yg1 = generar_offset(x1, y1,radio_cut2)  
    xR1,yR1 = generar_offset(x1, y1, m)

    xg1,yg1 = ajustar_puntos_angular(xg1, yg1, paso)


    x2,y2,ang1,ang2 = primitivas_generico(x1,y1,c1)


    coordinates1 = list(zip(x1, y1))
    polygon1 = shp.Polygon(coordinates1)
    perimeter1 = polygon1.length
    coordinates2 = list(zip(x2, y2))
    polygon2 = shp.Polygon(coordinates2)
    perimeter2 = polygon2.length

    
    return x1,y1,x2,y2,xg1,yg1,xR1,yR1,m,radio_cut2,zc,z,perimeter1,perimeter2,ang1,ang2