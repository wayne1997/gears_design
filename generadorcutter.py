import numpy as np
import shapely.geometry as shp
from shapely.ops import unary_union
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from rack import cutter,ajustar_puntos
from modelos_math import generar_offset,perimetro


def rotate(x_, y_, angle):
    # Matriz de rotación
    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                                [np.sin(angle), np.cos(angle)]])

    # Aplicar la rotación (en el origen)
    rotated_coordinates_at_origin = np.dot(rotation_matrix, np.vstack((x_, y_)))

    x_rotated, y_rotated = rotated_coordinates_at_origin

    return x_rotated, y_rotated


def intersecar(xc,yc,xrack,yrack):
    curva = shp.Polygon(np.column_stack((xc, yc)))
    cutter = shp.Polygon(np.column_stack((xrack, yrack)))

    # Encontrar la geometría resultante después de la intersección
    resultado_interseccion = curva.difference(cutter)
    x, y = np.array(resultado_interseccion.exterior.xy)
    return x,y


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
    xx, yy = reorder_points(xx, yy)

    return xx, yy


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
    
    x_r = np.concatenate((x_r, [x_r[0]]))
    y_r = np.concatenate((y_r, [y_r[0]]))
    
    return x_r,y_r


def longitudes_lados(x, y):
    longitudes = []
    for i in range(len(x) - 1):
        distancia = ((x[i+1] - x[i])**2 + (y[i+1] - y[i])**2)**0.5
        longitudes.append(distancia)
    acumulativas = np.cumsum(longitudes)
    acumulativas = np.insert(acumulativas, 0, 0)
    return acumulativas,longitudes


def cutter2(long,xc,yc,xg,yg,xR,yR,ang_c):          
    for i in range(0, long):
        print(i)
        xc1,yc1 = rotate(xc, yc,ang_c[i])
        xc1,yc1 = xc1+xg[i], yc1+yg[i]
        xR,yR = intersecar(xR,yR,xc1,yc1)
    return xR,yR

def cutter3(long, xc, yc, xg, yg, ang_c):
    print('TEST CUTTER3')
    poligonos = []

    for i in range(0, long):
        xc1, yc1 = rotate(xc, yc, ang_c[i])
        xc1, yc1 = xc1 + xg[i], yc1 + yg[i]
        lista = shp.LineString(np.column_stack((xc1, yc1)))
        poligonos.append(shp.Polygon(lista))

    print('union poligonos')
    result_union = unary_union(poligonos)

    print('fin union')
    # Coordenadas interiores
    interiores = [interior.xy for interior in result_union.interiors]

    xinterior, yinterior = interiores[0]  # Tomamos la primera isla

    return np.array(xinterior), np.array(yinterior)



def parametros(xg,yg,r):
    print('PARAMETROS')
    perimetros,dx = longitudes_lados(xg,yg)
    print(len(perimetros))
    ang_c = perimetros/(r)
    return ang_c,long

def parametros2(xg,yg,r):
    print('PARAMETROS2')
 
    ang_g = np.arctan2(yg, xg)
    ang_g[ang_g < 0] += 2*np.pi
    ang_g[-1] = 2*np.pi
    long = len(ang_g)
    
    perimetros,dx = longitudes_lados(xg,yg)

    #ang_c = angulos(rp,dx)
    #ang_c = np.insert(ang_c, 0, 0)
    #ang_c = np.cumsum(ang_c)
    #ang_c = ang_c*factor_correct
    dx = np.insert(dx, 0, 0)
    ang_c = dx/(r)
    ang_c = np.cumsum(ang_c)
    print(ang_c[-1])
    return ang_c,long


def angulos(r, s):
    angulos_resultantes = []
    
    # Calcular ángulos para cada par de puntos consecutivos
    for i in range(len(s)):
        # Calcular ángulo usando la ley de los cosenos
        cos_theta = (r[i]**2 + r[i + 1]**2 - s[i]**2) / (2 * r[i] * r[i + 1])

        # Manejar posibles errores de redondeo que podrían llevar a un valor fuera del rango [-1, 1]
        cos_theta = max(min(cos_theta, 1), -1)
        angulo_rad = np.arccos(cos_theta)

        # Agregar ángulo a la lista de resultados
        angulos_resultantes.append(angulo_rad)
    return angulos_resultantes
    

#__________________________________________________________________________________
# PRUEBA __________________________________________________________________________
#__________________________________________________________________________________



# CURVA PRIMITIVA
t = np.linspace(0, 2 * np.pi, 5000)
xp = 60 * np.cos(t)
yp = 20 * np.sin(t)

#xp = 60 * (2*np.cos(t) - np.cos(2*t))
#yp = 60 * (2*np.sin(t) - np.sin(2*t))

perimetro1 = perimetro(xp,yp)

print(perimetro1)
# Generar cutter
m = 2
alpha = np.radians(20)
r = 20

z = round(perimetro1/(np.pi*m))
m = perimetro1/(np.pi*z)
zc = round((2*r)/m)
r = (zc*m)/2




pasos = 500

xc,yc = cutter(m, alpha, r, zc, pasos)
xc,yc = ajustar_puntos(xc, yc, pasos*3)


print('1')

xg,yg = generar_offset(xp, yp, r)
xR,yR = generar_offset(xp, yp, m)

xp,yp = ajustar_puntos(xp, yp, 10000)
xg,yg = ajustar_puntos(xg, yg, 10000)
xR,yR = ajustar_puntos(xR, yR, 10000)

xp,yp = ajustar_puntos_angular(xp, yp, 2000)
xg,yg = ajustar_puntos_angular(xg, yg, 2000)
xR,yR = ajustar_puntos_angular(xR, yR, 2000)
print('________XP')
print(len(xp))

# Corte
print('2')
ang_c,long = parametros(xg,yg,r)

print('3')

#xR,yR = cutter2(long,xc,yc,xg,yg,xR,yR,ang_c)
xin, yin = cutter3(long,xc,yc,xg,yg,ang_c)

xin2,yin2 = ajustar_puntos(xin, yin, 10000)



tt = np.linspace(0, 2 * np.pi, 2001)
xpp = 90 * np.cos(tt)
ypp = 90 * np.sin(tt)
perimm,dx = longitudes_lados(xp,yp)
rrr = np.sqrt(xp**2 + yp**2)
phi = angulos(rrr, dx)
# = np.tile(rrr, 2)
ang_c2,long2 = parametros2(xpp,ypp,rrr)
xpp = -90 * np.cos(tt)+90
ypp = 90 * np.sin(tt)

print('Angulo final 2')
print(ang_c2[-1])
#tt2 = np.linspace(0, 4 * np.pi, 500)

xin3, yin3 = cutter3(long2,xin2,yin2,xpp,ypp,-ang_c2)

xin3,yin3 = ajustar_puntos(xin3, yin3, 10000)


# Configurar el gráfico
fig, ax = plt.subplots()
ax.scatter(0, 0, color='black')
ax.scatter(xg[0], yg[0], color='red')
ax.scatter(xg[-1], yg[-1], color='red')
ax.plot(xp, yp, label='rprimitiva')
ax.plot(xg, yg, label='rguia')
ax.plot(xin, yin, label='interior')
ax.plot(xin2, yin2, label='interior ajustado')
ax.plot(xin3, yin3, label='interior ajustado 2')



ax.axis('equal')
ax.grid(True)
ax.legend()
plt.show()