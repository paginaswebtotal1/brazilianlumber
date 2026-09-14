# -*- coding: utf-8 -*-
"""p17 - Demanda real por ciudad, via la API de KeywordTool.

La pregunta: ¿merece la pena tener una pagina por ciudad, y como habria que
llamarla?

Google Ads dio una primera respuesta (Miami 20, Los Angeles 10, Houston 10, el
resto sin datos), pero solo se probaron unas pocas combinaciones a mano. Aqui se
prueban TODAS las ciudades contra varias formas de nombrar el producto, que es
justo lo que decide como titular cada pagina:

    ipe decking {ciudad}      el producto estrella
    decking {ciudad}          generico de tarima
    lumber {ciudad}           generico de madera
    hardwood decking {ciudad} la categoria
    lumber yard {ciudad}      intencion de proveedor local
    {ciudad} deck builder     intencion de servicio

Con eso se sabe dos cosas: si hay demanda, y con que palabra. No es lo mismo
titular una pagina "Ipe Decking in Santa Monica" que "Lumber Yard Santa Monica"
si la segunda es la que se busca.

Salida: data/keywords_zonas.json
"""
import json, time
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"

KEY = None
for linea in (ROOT / ".env.local").read_text(encoding="utf-8").splitlines():
    if linea.startswith("KEYWORDTOOL_API_KEY"):
        KEY = linea.split("=", 1)[1].strip()
assert KEY, "falta KEYWORDTOOL_API_KEY en .env.local"

URL = "https://api.keywordtool.io/v2/search/volume/google"
LOTE = 60  # la API acepta varias keywords por peticion

PLANTILLAS = [
    "ipe decking {}",
    "decking {}",
    "lumber {}",
    "hardwood decking {}",
    "lumber yard {}",
    "lumber yards in {}",
    "{} deck builder",
    "wood decking {}",
    "composite decking {}",
    "decking supplier {}",
    "hardwood supplier {}",
    "deck contractor {}",
]


def ciudades():
    """Las del cumulo mas las que ya tienen pagina."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import ciudades as c
    nombres = {slug: info[0] for slug, info in c.CIUDADES.items()}
    # se añaden los mercados grandes, que son los que de verdad importan
    for slug, nombre in [("miami", "Miami"), ("houston", "Houston"), ("dallas", "Dallas"),
                         ("atlanta", "Atlanta"), ("tampa", "Tampa"), ("orlando", "Orlando"),
                         ("jacksonville", "Jacksonville"), ("austin", "Austin"),
                         ("san-antonio", "San Antonio"), ("charleston", "Charleston"),
                         ("savannah", "Savannah"), ("new-york", "New York"),
                         ("new-jersey", "New Jersey"), ("los-angeles", "Los Angeles"),
                         ("san-diego", "San Diego"), ("fort-lauderdale", "Fort Lauderdale"),
                         ("naples", "Naples"), ("boca-raton", "Boca Raton"),
                         ("palm-beach", "Palm Beach"), ("key-west", "Key West"),
                         ("long-island", "Long Island"), ("sacramento", "Sacramento")]:
        nombres.setdefault(slug, nombre)
    return nombres


def pide(keywords):
    p = [("apikey", KEY), ("metrics_location", 2840), ("metrics_language", "en"),
         ("metrics_network", "googlesearchnetwork"), ("output", "json")]
    # OJO: tiene que ser keyword[], no keyword. Con "keyword" la API devuelve
    # UNA sola fila por peticion aunque se manden sesenta, sin dar ningun error.
    # Cuesta verlo porque responde 200 igualmente.
    p += [("keyword[]", k) for k in keywords]
    for intento in range(4):
        try:
            r = httpx.get(URL, params=p, timeout=180)
            if r.status_code == 200:
                return r.json().get("results", {})
            print("   [{}] reintento".format(r.status_code), flush=True)
        except Exception as e:
            print("   {} reintento".format(type(e).__name__), flush=True)
        time.sleep(3 + 3 * intento)
    return {}


def main():
    nombres = ciudades()
    consultas = []
    mapa = {}
    for slug, nombre in nombres.items():
        for pl in PLANTILLAS:
            kw = pl.format(nombre).lower()
            consultas.append(kw)
            mapa[kw] = (slug, pl)
    consultas = sorted(set(consultas))
    print("{} ciudades x {} formas = {} consultas".format(
        len(nombres), len(PLANTILLAS), len(consultas)), flush=True)

    vol = {}
    for i in range(0, len(consultas), LOTE):
        lote = consultas[i:i + LOTE]
        res = pide(lote)
        for kw, info in res.items():
            v = info.get("volume")
            if v:
                vol[kw.lower()] = {"volumen": v, "cpc": info.get("cpc"),
                                   "competencia": info.get("cmp")}
        print("  {}/{}  acumulado con volumen: {}".format(
            min(i + LOTE, len(consultas)), len(consultas), len(vol)), flush=True)

    # agrupado por ciudad
    por_ciudad = {}
    for kw, d in vol.items():
        if kw not in mapa:
            continue
        slug, pl = mapa[kw]
        c = por_ciudad.setdefault(slug, {"nombre": nombres[slug], "total": 0, "terminos": []})
        c["total"] += d["volumen"]
        c["terminos"].append({"keyword": kw, "volumen": d["volumen"],
                              "plantilla": pl, "cpc": d.get("cpc")})
    for c in por_ciudad.values():
        c["terminos"].sort(key=lambda x: -x["volumen"])

    json.dump({"por_ciudad": por_ciudad, "consultas": len(consultas),
               "con_volumen": len(vol)},
              open(D / "keywords_zonas.json", "w", encoding="utf-8"), ensure_ascii=False)

    orden = sorted(por_ciudad.items(), key=lambda x: -x[1]["total"])
    print()
    print("=" * 72)
    print("  {} de {} ciudades tienen ALGUNA busqueda medible".format(
        len(por_ciudad), len(nombres)))
    print("=" * 72)
    print()
    print("{:22s} {:>7s}   mejor forma de nombrarla".format("CIUDAD", "TOTAL"))
    print("-" * 72)
    for slug, c in orden:
        mejor = c["terminos"][0]
        print("{:22s} {:>7d}   {} ({}/mes)".format(
            c["nombre"][:22], c["total"], mejor["keyword"][:34], mejor["volumen"]))
    print()
    sin = [n for s, n in nombres.items() if s not in por_ciudad]
    print("SIN NINGUNA BUSQUEDA MEDIBLE ({}):".format(len(sin)))
    print("  " + ", ".join(sorted(sin)))


if __name__ == "__main__":
    main()
