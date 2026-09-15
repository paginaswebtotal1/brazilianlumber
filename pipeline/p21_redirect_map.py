# -*- coding: utf-8 -*-
"""p21 - El mapa de redirecciones, en CSV, para el dia de la migracion.

El prototipo NO redirige: es una maqueta y cualquier 301 real seria un problema.
Esto es la hoja de instrucciones para cuando se haga el cambio de verdad, en el
formato que se le puede pasar a quien configure el servidor.

Salida: data/redirect-map.csv y la copia del entregable.
"""
import json, csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
HOST = "https://brazilianlumber.com"
ENTREGA = Path("C:/Users/USER/Desktop/BRAZILIAN LUMBER/ARQUITECTURA WEB BL/"
               "MENÙ VISUAL/9 - PROTOTIPO WEB UNIFICADO/redirect-map.csv")

PORTAL = {"brazilianlumber.com": "MIA", "brazilianlumberlosangeles.com": "LA",
          "brazilianlumbernewyork.com": "NJ"}


def main():
    S = json.load(open(D / "site.json", encoding="utf-8"))
    filas = []
    for r in S["redirects"]:
        dom = r["from"].split("/")[2] if "//" in r["from"] else ""
        filas.append([r.get("portal") or PORTAL.get(dom, "?"), r.get("type", ""),
                      r["from"], HOST + r["to"]])
    filas.sort(key=lambda x: (x[0], x[2]))

    for destino in (D / "redirect-map.csv", ENTREGA):
        if destino == ENTREGA and not destino.parent.exists():
            continue
        with open(destino, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["portal_origen", "tipo", "url_antigua", "url_nueva_portal_unico"])
            w.writerows(filas)
        print("{}  {} redirecciones".format(destino.name, len(filas)))


if __name__ == "__main__":
    main()
