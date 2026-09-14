# -*- coding: utf-8 -*-
"""p12 - Auditoria de destinos: que TODO lo que el mapa promete, exista.

Comprueba, una por una, las 6.169 URLs del mapa:

  - Si tiene destino, que ese destino responda 200 en el portal nuevo.
  - Si es un fichero, que el fichero este disponible en su ruta original.
  - Que ninguna redireccion apunte a otra redireccion (cadenas).
  - Que ninguna apunte a si misma (bucle).

Todo contra el servidor LOCAL. Cero peticiones al sitio publicado, para no
volver a disparar la mitigacion automatica de Vercel.

Salida: data/auditoria.json + AUDITORIA DE DESTINOS.md
"""
import json, sys, pathlib
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
AQUI = pathlib.Path(__file__).resolve().parent
ROOT = AQUI.parent
D = ROOT / "data"

# Se reutiliza el universo que construye p10, para auditar exactamente lo que
# sale en el Excel y no una version paralela que podria divergir.
src = (AQUI / "p10_excel.py").read_text(encoding="utf-8").split("wb = Workbook()")[0]
src = src.replace("Path(__file__).resolve().parent.parent", "pathlib.Path(r'{}')".format(ROOT))
src = src.replace("Path(__file__).resolve().parent", "pathlib.Path(r'{}')".format(AQUI))
ns = {"pathlib": pathlib}
exec(src, ns)
universo = ns["universo"]
metricas = ns["metricas"]

HOST = "https://brazilianlumber.com"


def ruta(u):
    """Destino -> ruta local comprobable."""
    if not u:
        return None
    r = u.replace(HOST, "")
    if r.startswith("http"):
        return None
    return r if r.startswith("/") else "/" + r


def comprueba(path):
    try:
        req = Request(BASE + path, headers={"User-Agent": "bl-auditoria"}, method="GET")
        with urlopen(req, timeout=40) as r:
            return r.status, r.headers.get("Content-Type", "")
    except HTTPError as e:
        return e.code, ""
    except URLError as e:
        return 0, str(e)


def main():
    # ---- todos los destinos distintos que promete el mapa
    destinos = {}
    for u in universo.values():
        r = ruta(u.get("destino"))
        if r:
            destinos.setdefault(r, []).append(u)

    print("{:,} URLs en el mapa -> {:,} destinos distintos que comprobar".format(
        len(universo), len(destinos)), flush=True)

    with ThreadPoolExecutor(max_workers=10) as ex:
        res = dict(zip(destinos, ex.map(comprueba, destinos)))

    rotos = {d: v for d, v in res.items() if v[0] != 200}

    # ---- ficheros: que existan en su ruta original
    ficheros = [u for u in universo.values() if u["accion"] == "FICHERO"]
    fich_res = {}
    for u in ficheros:
        p = ruta(u["url"].split("?")[0].split("#")[0].rstrip(").,;'\""))
        if p:
            fich_res[p] = u
    with ThreadPoolExecutor(max_workers=10) as ex:
        fres = dict(zip(fich_res, ex.map(comprueba, fich_res)))
    fich_ok = {p: v for p, v in fres.items() if v[0] == 200}
    fich_no = {p: v for p, v in fres.items() if v[0] != 200}

    # ---- cadenas y bucles
    destino_de = {}
    for u in universo.values():
        r = ruta(u.get("destino"))
        o = ruta(u["url"])
        if r and o:
            destino_de[o] = r
    # Una pagina que se conserva mantiene su URL: destino == origen NO es un
    # bucle, es lo normal. Solo cuenta como bucle si la fila dice que redirige.
    redirige = {ruta(u["url"]) for u in universo.values()
                if u["accion"] in ("CONSOLIDAR-301", "ANCLA", "PARAMETRO", "ATRIBUTO",
                                   "DESCATALOGADO", "REVISAR")}
    cadenas = [(o, d, destino_de[d]) for o, d in destino_de.items()
               if d in destino_de and destino_de[d] != d and o in redirige]
    bucles = [o for o, d in destino_de.items() if o == d and o in redirige]

    # ---- clics en juego
    clics_rotos = sum(metricas(x["url"]).get("clicks", 0)
                      for d in rotos for x in destinos[d])
    clics_fich_no = sum(metricas(fich_res[p]["url"]).get("clicks", 0) for p in fich_no)

    salida = {
        "destinos": len(destinos), "rotos": len(rotos),
        "ficheros": len(fich_res), "ficheros_ok": len(fich_ok), "ficheros_no": len(fich_no),
        "cadenas": len(cadenas), "bucles": len(bucles),
        "clics_en_riesgo": clics_rotos + clics_fich_no,
        "detalle_rotos": {d: {"codigo": v[0], "urls_que_apuntan": len(destinos[d])}
                          for d, v in sorted(rotos.items())},
        "detalle_ficheros": {p: metricas(fich_res[p]["url"]).get("clicks", 0)
                             for p in sorted(fich_no)},
    }
    json.dump(salida, open(D / "auditoria.json", "w", encoding="utf-8"), ensure_ascii=False)

    print()
    print("DESTINOS")
    print("  distintos comprobados : {:,}".format(len(destinos)))
    print("  que no responden 200  : {}".format(len(rotos)))
    print("  redirecciones en cadena: {}".format(len(cadenas)))
    print("  bucles (a si misma)   : {}".format(len(bucles)))
    print()
    print("FICHEROS")
    print("  referenciados         : {}".format(len(fich_res)))
    print("  disponibles en su ruta: {}".format(len(fich_ok)))
    print("  no disponibles        : {}".format(len(fich_no)))
    print()
    print("clics en riesgo: {}".format(clics_rotos + clics_fich_no))

    if rotos:
        print("\nDESTINOS ROTOS:")
        for d, v in sorted(rotos.items(), key=lambda x: -len(destinos[x[0]]))[:25]:
            print("  [{}] {}  <- {} URLs".format(v[0], d[:78], len(destinos[d])))
    if fich_no:
        print("\nFICHEROS NO DISPONIBLES (top por clics):")
        for p in sorted(fich_no, key=lambda x: -metricas(fich_res[x]["url"]).get("clicks", 0))[:20]:
            print("  {:4d} clics  {}".format(metricas(fich_res[p]["url"]).get("clicks", 0), p[:78]))


if __name__ == "__main__":
    main()
