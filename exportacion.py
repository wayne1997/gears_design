import ezdxf
import numpy as np

def exportarDXF(xe,ye, nombre_archivo):
    doc = ezdxf.new()
    msp = doc.modelspace()

    puntos = [(x, y) for x, y in zip(xe, ye)]
    msp.add_spline(fit_points=puntos)
    #msp.add_lwpolyline(points=list(zip(xe, ye)))

    doc.saveas(nombre_archivo)