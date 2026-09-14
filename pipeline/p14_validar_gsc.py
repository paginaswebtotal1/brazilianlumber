# -*- coding: utf-8 -*-
"""p14 - Validacion definitiva contra Google Search Console.

La pregunta que responde es una sola, y no admite matices:

    De todo lo que Google conoce hoy de los 3 portales, ¿queda algo sin
    respuesta el dia que se apaguen Los Angeles y New Jersey?

Para cada URL que Search Console reporta con datos:
  - ¿Esta en el mapa?
  - ¿Tiene un destino, o un motivo documentado para no necesitarlo?
  - ¿Ese destino responde 200 en el portal nuevo?
  - ¿Cuantos clics dependen de que la respuesta sea correcta?

Todo contra el servidor LOCAL. Cero peticiones al sitio publicado.

Salida: data/validacion_gsc.json
"""
import json, sys, pathlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
AQUI = pathlib.Path(__file__).resolve().parent
ROOT = AQUI.parent
D = ROOT / "data"
HOST = "https://brazilianlumber.com"

# Se reutiliza el universo del Excel, para validar exactamente lo que se entrega.
src = (AQUI / "p10_excel.py").read_text(encoding="utf-8").split("wb = Workbook()")[0]
src = src.replace("Path(__file__).resolve().parent.parent", "pathlib.Path(r'{}')".format(ROOT))
src = src.replace("Path(__file__).resolve().parent", "pathlib.Path(r'{}')".format(AQUI))
ns = {"pathlib": pathlib}
exec(src, ns)
universo = ns["universo"]
metricas = ns["metricas"]
GSC = json.load(open(D / "gsc.json", encoding="utf-8"))

# Acciones que NO necesitan destino, con su motivo.
SIN_DESTINO_OK = {
    "FICHERO": "se migra el fichero tal cual, conservando su ruta",
    "NO-PUBLICO": "no es una pagina publica",
    "NOINDEX": "deja de indexarse, sin destino necesario",
    "ELIMINAR": "se elimina por decision del estudio",
}


def ruta(u):
    if not u:
        return None
    r = u.replace(HOST, "")
    return r if r.startswith("/") else None


def comprueba(path):
    try:
        req = Request(BASE + path, headers={"User-Agent": "bl-validacion"})
        with urlopen(req, timeout=40) as r:
            return r.status
    except HTTPError as e:
        return e.code
    except URLError:
        return 0


def main():
    # ---------- 1. todas las URLs que Google conoce
    gsc_urls = {}
    for portal, datos in GSC["portales"].items():
        for url, m in datos["paginas"].items():
            gsc_urls[url] = (portal, m)

    print("Search Console reporta {:,} URLs con datos en los 3 portales".format(len(gsc_urls)),
          flush=True)

    # ---------- 2. cada una, en el mapa
    def en_mapa(u):
        for k in (u, u.rstrip("/"), u.rstrip("/") + "/"):
            if k in universo:
                return universo[k]
        return None

    fuera, sin_dest, con_dest = [], [], {}
    for url, (portal, m) in gsc_urls.items():
        fila = en_mapa(url)
        if fila is None:
            fuera.append((url, m.get("clicks", 0)))
            continue
        d = ruta(fila.get("destino"))
        if not d:
            if fila["accion"] not in SIN_DESTINO_OK:
                sin_dest.append((url, fila["accion"], m.get("clicks", 0)))
            continue
        con_dest.setdefault(d, []).append((url, m.get("clicks", 0)))

    print("  en el mapa          : {:,}".format(len(gsc_urls) - len(fuera)), flush=True)
    print("  fuera del mapa      : {:,}".format(len(fuera)), flush=True)
    print("  sin destino indebido: {:,}".format(len(sin_dest)), flush=True)
    print("  destinos distintos  : {:,}".format(len(con_dest)), flush=True)

    # ---------- 3. cada destino, que responda
    print("\ncomprobando destinos contra {} ...".format(BASE), flush=True)
    with ThreadPoolExecutor(max_workers=10) as ex:
        estados = dict(zip(con_dest, ex.map(comprueba, con_dest)))

    rotos = {d: c for d, c in estados.items() if c != 200}
    clics_rotos = sum(c for d in rotos for _, c in con_dest[d])
    clics_fuera = sum(c for _, c in fuera)
    clics_sin = sum(c for _, _, c in sin_dest)
    clics_total = sum(m.get("clicks", 0) for _, m in gsc_urls.values())
    ok = clics_total - clics_rotos - clics_fuera - clics_sin

    salida = {
        "gsc_urls": len(gsc_urls),
        "fuera_del_mapa": len(fuera),
        "sin_destino_indebido": len(sin_dest),
        "destinos": len(con_dest),
        "destinos_rotos": len(rotos),
        "clics_total": clics_total,
        "clics_cubiertos": ok,
        "clics_en_riesgo": clics_total - ok,
        "detalle_rotos": {d: {"codigo": estados[d], "urls": len(con_dest[d]),
                              "clics": sum(c for _, c in con_dest[d])}
                          for d in sorted(rotos)},
        "detalle_fuera": sorted(fuera, key=lambda x: -x[1])[:60],
        "detalle_sin_destino": sorted(sin_dest, key=lambda x: -x[2])[:60],
    }
    json.dump(salida, open(D / "validacion_gsc.json", "w", encoding="utf-8"), ensure_ascii=False)

    print()
    print("=" * 62)
    print("  URLs que Google conoce      : {:,}".format(len(gsc_urls)))
    print("  fuera del mapa              : {:,}".format(len(fuera)))
    print("  sin destino sin motivo      : {:,}".format(len(sin_dest)))
    print("  destinos que no responden   : {:,}".format(len(rotos)))
    print()
    print("  clics totales               : {:,}".format(clics_total))
    print("  clics con destino correcto  : {:,}  ({:.2f}%)".format(
        ok, ok / clics_total * 100 if clics_total else 0))
    print("  clics en riesgo             : {:,}  ({:.2f}%)".format(
        clics_total - ok, (clics_total - ok) / clics_total * 100 if clics_total else 0))
    print("=" * 62)

    if rotos:
        print("\nDESTINOS QUE NO RESPONDEN:")
        for d in sorted(rotos, key=lambda x: -sum(c for _, c in con_dest[x]))[:20]:
            print("  [{}] {:52s} {} clics".format(
                estados[d], d[:52], sum(c for _, c in con_dest[d])))
    if fuera:
        print("\nFUERA DEL MAPA (top por clics):")
        for u, c in sorted(fuera, key=lambda x: -x[1])[:20]:
            print("  {:5d} clics  {}".format(c, u[:88]))
    if sin_dest:
        print("\nSIN DESTINO Y DEBERIAN TENERLO:")
        for u, a, c in sorted(sin_dest, key=lambda x: -x[2])[:20]:
            print("  {:5d} clics  [{}] {}".format(c, a, u[:76]))


if __name__ == "__main__":
    main()
