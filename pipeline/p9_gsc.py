# -*- coding: utf-8 -*-
"""p9 - Datos reales de Google Search Console para los 3 portales.

Es lo que convierte la unificacion en una decision con datos detras en vez de
una opinion: cuantos clics, impresiones y CTR tiene HOY cada URL de cada
portal, y por tanto que se gana y que se arriesga al consolidar.

Ventana: 16 meses completos. Dimension: pagina, y ademas los totales por
propiedad y las consultas principales.

Salida: data/gsc.json
"""
import json, time, sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

D = Path(__file__).resolve().parent.parent / "data"
KEY = r"C:\Users\USER\6 - brazilian lumber\GSC API\brazilian-lumber-502317-0052a9d15c7c.json"

INI, FIN = "2025-05-01", "2026-08-31"

# Propiedad que se usa para cada portal. En Los Angeles se usa la propiedad de
# dominio porque recoge tambien www y subdominios, asi que no infravalora.
PORTALES = {
    "MIA": "https://brazilianlumber.com/",
    "LA": "sc-domain:brazilianlumberlosangeles.com",
    "NJ": "https://brazilianlumbernewyork.com/",
}

creds = service_account.Credentials.from_service_account_file(
    KEY, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def consultar(site, dims, tope=None):
    """Pagina hasta agotar. La API devuelve 25.000 filas como maximo por peticion."""
    filas, start = [], 0
    while True:
        body = {"startDate": INI, "endDate": FIN, "dimensions": dims,
                "rowLimit": 25000, "startRow": start}
        for intento in range(4):
            try:
                r = svc.searchanalytics().query(siteUrl=site, body=body).execute().get("rows", [])
                break
            except Exception as e:
                if intento == 3:
                    print(f"    fallo en {site} {dims}: {e}", flush=True)
                    return filas
                time.sleep(3 * (intento + 1))
        filas += r
        if len(r) < 25000 or (tope and len(filas) >= tope):
            break
        start += 25000
    return filas


def main():
    out = {"ventana": {"desde": INI, "hasta": FIN}, "portales": {}}

    for portal, site in PORTALES.items():
        print(f"{portal}  {site}", flush=True)

        # totales de la propiedad
        tot = consultar(site, [])
        t = tot[0] if tot else {}
        totales = {
            "clicks": t.get("clicks", 0),
            "impressions": t.get("impressions", 0),
            "ctr": round(t.get("ctr", 0) * 100, 2),
            "position": round(t.get("position", 0), 1),
        }

        # por pagina
        paginas = {}
        for r in consultar(site, ["page"]):
            url = r["keys"][0]
            paginas[url] = {
                "clicks": int(r["clicks"]),
                "impressions": int(r["impressions"]),
                "ctr": round(r["ctr"] * 100, 2),
                "position": round(r["position"], 1),
            }

        # consultas principales
        consultas = []
        for r in consultar(site, ["query"], tope=25000)[:500]:
            consultas.append({
                "query": r["keys"][0],
                "clicks": int(r["clicks"]),
                "impressions": int(r["impressions"]),
                "ctr": round(r["ctr"] * 100, 2),
                "position": round(r["position"], 1),
            })
        consultas.sort(key=lambda x: -x["clicks"])

        out["portales"][portal] = {
            "site": site, "totales": totales,
            "paginas": paginas, "consultas": consultas[:500],
        }
        print(f"    {totales['clicks']:,} clics | {totales['impressions']:,} impresiones | "
              f"CTR {totales['ctr']}% | posicion media {totales['position']}", flush=True)
        print(f"    {len(paginas):,} paginas con datos | {len(consultas):,} consultas", flush=True)

    json.dump(out, open(D / "gsc.json", "w", encoding="utf-8"), ensure_ascii=False)

    g = sum(p["totales"]["clicks"] for p in out["portales"].values())
    i = sum(p["totales"]["impressions"] for p in out["portales"].values())
    print(f"\nTOTAL 3 PORTALES: {g:,} clics, {i:,} impresiones, "
          f"CTR conjunto {round(g / i * 100, 2) if i else 0}%")


if __name__ == "__main__":
    main()
