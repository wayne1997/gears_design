import numpy as np
import shapely.geometry as shp
from shapely.ops import unary_union
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from global_functions import add_logs
from modelos_math import longitudes_lados,offset_abierto,angulos,generar_offset

def ajustar_puntos(x, y, nuevos_puntos):
    interpolacion = interp1d(np.arange(len(x)), np.column_stack((x, y)), kind='linear', axis=0)
    nuevos_indices = np.linspace(0, len(x) - 1, nuevos_puntos, dtype=int)
    nueva_curva = interpolacion(nuevos_indices)

    xx,yy = reorder_points(nueva_curva[:, 0], nueva_curva[:, 1])
    xx,yy = nueva_curva[:, 0], nueva_curva[:, 1]
    
    return xx,yy


def reorder_points2(x, y):
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
    
    x_r = np.concatenate((x_r, [x_r[0]]))
    y_r = np.concatenate((y_r, [y_r[0]]))
    
    return x_r,y_r


def reorder_points(x, y):
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
    
    return x_r,y_r


def geom(m, alpha, radio_cutter, z):
    t = np.linspace(0, 2 * np.pi, 1000)
    xp = radio_cutter * np.cos(t)
    yp = radio_cutter * np.sin(t)
    
    # Dimensiones rack
    addendum = 1.25 * m
    dedendum = 1.25 * m
    h = addendum + dedendum
    d = (2 * np.pi * radio_cutter) / z
    b = h * np.tan(alpha)
    a = d / 2 - b
    
    xrack = np.array([0, a/2, (a/2 + b), (1.5*a + b), (1.5*a + 2*b), (2*a + 2*b)])
    yrack = np.array([0, 0, h, h, 0, 0])
    
    radioesquinas = 0.2*m
    xrack,yrack = offset_abierto(xrack,yrack,radioesquinas)
    xrack,yrack = offset_abierto(xrack,yrack,-2*radioesquinas)
    xrack,yrack = offset_abierto(xrack,yrack,radioesquinas)

    yrack = yrack - radio_cutter - dedendum
    
    
    xrack = np.concatenate([xrack + i * (xrack[-1]) for i in range(z+1)])
    yrack = np.concatenate([yrack]*(z+1))
    
    xrack = np.concatenate((xrack, [xrack[-1]]))
    xrack = np.concatenate((xrack, [xrack[0]]))
    xrack = np.concatenate((xrack, [xrack[0]]))
    yrack = yrack = np.concatenate((yrack, [yrack[-1]-5]))
    yrack = yrack = np.concatenate((yrack, [yrack[-1]]))
    yrack = yrack = np.concatenate((yrack, [yrack[0]]))
    
    xc = (radio_cutter + dedendum) * np.cos(t)
    yc = (radio_cutter + dedendum) * np.sin(t)
    
    return xc, yc, xrack, yrack


#TODO: REVIEW THE COREALATION BETWEEN THIS FUNCITONS
def intersecar(xcurva,ycurva,xrack,yrack):
    print(f"x: {xcurva}, y: {ycurva}, XR:{xrack}, YR:{yrack}")
    curva = shp.Polygon(np.column_stack((xcurva, ycurva)))
    cutter = shp.Polygon(np.column_stack((xrack, yrack)))
    # Encontrar la geometría resultante después de la intersección
    resultado_interseccion = curva.difference(cutter)
    if resultado_interseccion.is_empty:
        add_logs("La intersección es vacía")
        return [], []
    elif resultado_interseccion.geom_type == 'Polygon':
        X, y = np.array(resultado_interseccion.exterior.xy)
        return X, y
    elif resultado_interseccion.geom_type == 'MultiPolygon':
        add_logs("El resultado es un MultiPolygon")
        first_polygon = list(resultado_interseccion.geoms)[0]
        X, y = np.array(first_polygon.exterior.xy)
    elif resultado_interseccion.geom_type == 'GeometryCollection':
        for geom in resultado_interseccion.geoms:
            if geom.geom_type == "Polygon":
                x, y = np.array(geom.exterior.xy)
                return x, y
        add_logs("La GeometryCollection no tiene polígonos válidos")
        return [], []
    else:
        add_logs("No se ha podido extraer los datos de la interseccion")
        return [], []

def rotate(x_, y_, angle):
    # Matriz de rotación
    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                                [np.sin(angle), np.cos(angle)]])

    # Aplicar la rotación (en el origen)
    rotated_coordinates_at_origin = np.dot(rotation_matrix, np.vstack((x_, y_)))

    x_rotated, y_rotated = rotated_coordinates_at_origin

    return x_rotated, y_rotated


def ajustar_puntos_angular(x, y, nuevos_puntos):
    # Calcular ángulos a lo largo de la curva
    angulos = np.arctan2(y - y.mean(), x - x.mean())
    angulos[angulos < 0] += 2 * np.pi  # Asegurar que los ángulos estén en el rango [0, 2*pi)

    # Asegurar que haya al menos un punto cercano a 0
    if not (0 in angulos):
        angulos = np.concatenate([[0], angulos])
        x = np.concatenate([[x[0]], x])
        y = np.concatenate([[y[0]], y])

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
    x += 1e-8

    # Ajustar la curva interpolando angularmente
    interpolacion_angular = interp1d(angulos, np.column_stack((x, y)), kind='linear', axis=0, fill_value='extrapolate')

    # Crear nuevos ángulos igualmente espaciados, asegurando que comiencen en 0
    nuevos_angulos = np.linspace(0, 2 * np.pi, nuevos_puntos, endpoint=False)

    # Evaluar la interpolación en los nuevos ángulos
    nueva_curva = interpolacion_angular(nuevos_angulos)

    xx, yy = nueva_curva[:, 0], nueva_curva[:, 1]
    xx, yy = reorder_points2(xx, yy)

    return xx, yy


def cutter(m, alpha, r, z, pasos):
    xc, yc, xrack, yrack = geom(m, alpha, r, z)
    
    girototal = 2.5*np.pi
    giro = girototal/pasos
    d = giro*r
    
    for i in range(1, pasos+1):
        #print(i)
        xc,yc = intersecar(xc,yc,xrack,yrack)
        xc,yc = rotate(xc, yc,-giro)
        xrack,yrack = xrack-d, yrack
    
    xc,yc = rotate(xc, yc,giro*pasos)
    
   
    
    radioesquinas = 0.08*m

    xc,yc = offset_abierto(xc,yc,radioesquinas)
    engranaje_xy = shp.LineString(zip(xc,yc))
    poligono_cerrado = shp.Polygon(engranaje_xy)
    xc, yc = poligono_cerrado.exterior.xy
    xc,yc = offset_abierto(xc,yc,-radioesquinas)
    engranaje_xy = shp.LineString(zip(xc,yc))
    poligono_cerrado = shp.Polygon(engranaje_xy)
    xc, yc = poligono_cerrado.exterior.xy

    return xc,yc


def cutter2(long,xc,yc,xg,yg,xR,yR,ang_c):          
    for i in range(0, long):
        print(i)
        xc1,yc1 = rotate(xc, yc,ang_c[i])
        xc1,yc1 = xc1+xg[i], yc1+yg[i]
        xR,yR = intersecar(xR,yR,xc1,yc1)
    return xR,yR


def cutter3(xc, yc, xg, yg, ang_c,m):
    print('TEST CUTTER3')
    poligonos = []
    long = len(ang_c)
    for i in range(0, long):
        xc1, yc1 = rotate(xc, yc, ang_c[i])
        xc1, yc1 = xc1 + xg[i], yc1 + yg[i]
        lista = shp.LineString(np.column_stack((xc1, yc1)))
        poligonos.append(shp.Polygon(lista))

    print('union poligonos')
    try:
        result_union = unary_union(poligonos)
        print('fin union')
        # Coordenadas interiores
        interiores = [interior.xy for interior in result_union.interiors]
        xinterior, yinterior = interiores[0]  # Tomamos la primera isla
        return np.array(xinterior), np.array(yinterior)
    except Exception as ex:
        print('Error en union')
        add_logs(f'Error log: {ex}')
        return None


def parametros(xg,yg,r):       
    perimetros,dx = longitudes_lados(xg,yg)

    ang_c = perimetros/(r)
	
    print('PARAMETROS ang_c \n')
    add_logs('PARAMETROS ang_c \n')
    print(ang_c[0])
    add_logs(str(ang_c[0]))
    print(ang_c[-1])
    add_logs(str(ang_c[-1]))
    print(len(ang_c))
    add_logs(str(len(ang_c)))
    
    
    return ang_c#,long


def cortar_puntas_dientes(xengranaje, yengranaje, xprimitiva, yprimitiva, distancia_corte, modulo):
    offset = modulo - distancia_corte
    xcorte,ycorte = generar_offset(xprimitiva, yprimitiva, offset)
    
    engranaje = shp.Polygon(np.column_stack((xengranaje, yengranaje)))
    cortador = shp.Polygon(np.column_stack((xcorte, ycorte)))
    
    interseccion = engranaje.intersection(cortador)
    
    xengranaje, yengranaje = np.array(interseccion.exterior.xy)
    
    return xengranaje,yengranaje


def redondear_puntas_dientes(xengranaje, yengranaje, radio_redondeo):
    xengranaje,yengranaje = generar_offset(xengranaje,yengranaje,-radio_redondeo)
    xredondeado,yredondeado = generar_offset(xengranaje,yengranaje,radio_redondeo)
    return xredondeado,yredondeado
    


#m = 2
#alpha = np.radians(20)
#r = 10

#z = round(2*r/(m))
#m = 2*r/(z)
#r = (z*m)/2
#pasos = 500

#x,y = cutter(m, alpha, r, z, pasos)

#fig, ax = plt.subplots()
#ax.scatter(0, 0, color='black')
#ax.plot(x, y, label='Engranaje redondeado')
#ax.axis('equal')
#ax.grid(True)
#ax.legend()
#plt.show()