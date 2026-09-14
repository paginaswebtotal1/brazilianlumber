# -*- coding: utf-8 -*-
"""p18 - Renombra las paginas de zona segun la demanda real.

El hallazgo, con datos de KeywordTool sobre 82 ciudades y 12 formas de nombrar
lo mismo:

    lumber yard {ciudad}      8.590 busquedas/mes en 55 ciudades
    lumber {ciudad}           7.230 en 50
    lumber yards in {ciudad}  5.380 en 27
    {ciudad} deck builder     4.020 en 18
    deck contractor {ciudad}  2.370 en 15
    decking {ciudad}            920 en 14
    ipe decking {ciudad}        140 en 13   <-- como se llaman hoy

Las paginas actuales se titulan "IPE decking Los Angeles" y similares, que es
justo el termino con menos demanda de todos. La misma pagina, titulada "Lumber
Yard in Los Angeles", apunta a 320 busquedas al mes en vez de 10.

Ademas Google Ads ya avisaba: "ipe decking los angeles" son 10 al mes. Lo que no
se veia sin esta herramienta es que "lumber yard los angeles" son 320.

Este script escribe data/zonas_renombradas.json, que consume p3_build para
titular cada pagina por su termino real.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"

MIN_VOLUMEN = 20     # por debajo de esto no justifica una URL propia

# Intenciones que NO se persiguen: Brazilian Lumber suministra material, no
# construye terrazas. Posicionar por "deck builder" traeria a quien busca un
# contratista, que es un lead que no se puede atender y una visita que rebota.
# Se descartan aunque tengan mas volumen: el volumen que no se puede convertir
# no es una oportunidad.
INTENCION_AJENA = {"{} deck builder", "deck contractor {}"}

# Como se redacta el titulo segun cual sea el termino ganador. La pagina tiene
# que llamarse como la busca la gente, no como la llamamos nosotros.
TITULO = {
    "lumber yard {}": ("Lumber Yard in {}", "lumber yard"),
    "lumber yards in {}": ("Lumber Yards in {}", "lumber yard"),
    "lumber {}": ("Lumber in {}", "lumber supplier"),
    "{} deck builder": ("Deck Builders in {}", "deck builder"),
    "deck contractor {}": ("Deck Contractors in {}", "deck contractor"),
    "decking {}": ("Decking in {}", "decking"),
    "composite decking {}": ("Composite Decking in {}", "composite decking"),
    "ipe decking {}": ("Ipe Decking in {}", "ipe decking"),
    "hardwood decking {}": ("Hardwood Decking in {}", "hardwood decking"),
    "wood decking {}": ("Wood Decking in {}", "wood decking"),
    "decking supplier {}": ("Decking Suppliers in {}", "decking supplier"),
    "hardwood supplier {}": ("Hardwood Suppliers in {}", "hardwood supplier"),
}


def main():
    kw = json.load(open(D / "keywords_zonas.json", encoding="utf-8"))["por_ciudad"]

    salida = {}
    fuera = []
    for slug, c in kw.items():
        if c["total"] < MIN_VOLUMEN:
            fuera.append((c["nombre"], c["total"]))
            continue
        propios = [t for t in c["terminos"] if t["plantilla"] not in INTENCION_AJENA]
        if not propios:
            fuera.append((c["nombre"], c["total"]))
            continue
        mejor = propios[0]
        plantilla = mejor["plantilla"]
        patron, intencion = TITULO.get(plantilla, ("Lumber Yard in {}", "lumber yard"))
        # los tres o cuatro terminos que de verdad sostienen la pagina
        soporte = [t for t in propios[:4] if t["volumen"] >= 10]
        salida[slug] = {
            "nombre": c["nombre"],
            "h1": patron.format(c["nombre"]),
            "intencion": intencion,
            "volumen_total": sum(t["volumen"] for t in propios),
            "volumen_descartado": c["total"] - sum(t["volumen"] for t in propios),
            "keyword_principal": mejor["keyword"],
            "volumen_principal": mejor["volumen"],
            "keywords": [{"k": t["keyword"], "v": t["volumen"]} for t in soporte],
        }

    json.dump(salida, open(D / "zonas_renombradas.json", "w", encoding="utf-8"),
              ensure_ascii=False)

    total = sum(v["volumen_total"] for v in salida.values())
    print("{} ciudades con {} busquedas/mes justifican pagina propia".format(
        len(salida), total))
    print("{} se quedan por debajo de {} y van al indice de zonas".format(
        len(fuera), MIN_VOLUMEN))
    print()
    print("COMO SE VAN A LLAMAR (las 20 primeras):")
    print("{:34s} {:>7s}  {}".format("TITULO NUEVO", "VOL/MES", "TERMINO QUE PERSIGUE"))
    print("-" * 78)
    for slug, v in sorted(salida.items(), key=lambda x: -x[1]["volumen_total"])[:20]:
        print("{:34s} {:>7d}  {}".format(v["h1"][:34], v["volumen_total"],
                                         v["keyword_principal"][:32]))
    print()
    import collections
    c = collections.Counter(v["intencion"] for v in salida.values())
    print("intencion dominante:", dict(c))


if __name__ == "__main__":
    main()
