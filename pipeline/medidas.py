# -*- coding: utf-8 -*-
"""Datos numericos por medida, para que cada ficha tenga cifras propias.

El problema que resuelve: 21 fichas de Ipe compartian el mismo texto sobre el
Ipe y solo cambiaba la medida en el titulo. Para Google y para un motor
generativo eso son 21 duplicados.

La solucion no es escribir 21 ensayos distintos sobre la misma madera: es que
cada ficha lleve los numeros de SU medida, que son reales, distintos y ademas
lo que el comprador necesita para pedir cantidad.

grosor y ancho reales en pulgadas, mas el uso tipico de esa escuadria.
"""
DIM = {
    "1x4":    (0.75, 3.5,  "decking", 16),
    "1x6":    (0.75, 5.5,  "decking", 16),
    "1x8":    (0.75, 7.25, "decking and cladding", 16),
    "1x12":   (0.75, 11.25, "stair risers, fascia and wide trim", 16),
    "5/4x4":  (1.0,  3.5,  "heavy decking", 24),
    "5/4x6":  (1.0,  5.5,  "heavy decking", 24),
    "5/4x8":  (1.0,  7.25, "wide heavy decking", 24),
    "5/4x12": (1.0,  11.25, "stair treads and fascia", 24),
    "2x2":    (1.5,  1.5,  "balusters, battens and sleepers", 0),
    "2x4":    (1.5,  3.5,  "framing and rails", 0),
    "2x6":    (1.5,  5.5,  "framing, stair treads and benches", 0),
    "2x8":    (1.5,  7.25, "joists and beams", 0),
    "2x10":   (1.5,  9.25, "joists and stringers", 0),
    "2x12":   (1.5,  11.25, "joists, stringers and heavy beams", 0),
    "4x4":    (3.5,  3.5,  "posts", 0),
    "6x6":    (3.5,  5.5,  "heavy posts and beams", 0),
    "8x8":    (7.5,  7.5,  "timber columns", 0),
    "1x2":    (0.75, 1.5,  "trim, battens and edging", 0),
    "1x10":   (0.75, 9.25, "wide fascia and riser stock", 16),
    "4x6":    (3.5,  5.5,  "beams and heavy posts", 0),
    "4x8":    (3.5,  7.25, "beams", 0),
    "4x10":   (3.5,  9.25, "heavy beams", 0),
    "4x12":   (3.5,  11.25, "heavy beams and headers", 0),
    "5/4x10": (1.0,  9.25, "wide heavy board for treads and fascia", 24),
    "6x8":    (5.5,  7.25, "timber beams", 0),
    "8x12":   (7.5,  11.25, "timber columns and beams", 0),
}

GAP = 0.1875  # separacion habitual entre tablas, en pulgadas


def datos(medida, densidad_kg_m3=None):
    """Cifras propias de esa escuadria. Devuelve None si no se conoce."""
    d = DIM.get(medida)
    if not d:
        return None
    grosor, ancho, uso, vano = d
    # cobertura: cada pie lineal cubre (ancho + separacion) / 12 pies cuadrados
    cobertura = (ancho + GAP) / 12
    # pies lineales necesarios para cubrir 100 pies cuadrados
    lineales_100 = 100 / cobertura
    out = {
        "grosor": grosor, "ancho": ancho, "uso": uso, "vano": vano,
        "cobertura": round(cobertura, 3),
        "lineales_100": int(round(lineales_100)),
        "seccion": round(grosor * ancho, 2),
    }
    if densidad_kg_m3:
        # peso por pie lineal: seccion en pulgadas cuadradas -> m2 -> kg/m -> lb/ft
        m2 = grosor * ancho * 0.00064516
        kg_por_m = m2 * densidad_kg_m3
        out["lb_pie"] = round(kg_por_m * 0.3048 * 2.20462, 2)
        out["lb_100sqft"] = int(round(out["lb_pie"] * lineales_100))
    return out
