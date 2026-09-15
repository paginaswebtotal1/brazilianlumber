# -*- coding: utf-8 -*-
"""p1b - Categorias, etiquetas y atributos reales de cada ficha.

La Store API de WooCommerce (/wp-json/wc/store/v1/products) es publica y no la
filtra Cloudflare, igual que la REST de WordPress. Devuelve, por ficha, a que
categorias pertenece, que etiquetas lleva y que terminos de atributo tiene.

Ese dato evita adivinar. Sin el, un producto llamado "Ciro Green" no se parece
a nada conocido y acaba en el cajon de sastre; con el, la tienda dice que es
cesped artificial y se acabo la discusion.

Salida: data/woo_cats.json
"""
import json, time
from pathlib import Path
from curl_cffi import requests

D = Path(__file__).resolve().parent.parent / "data"
DOMINIOS = ["brazilianlumber.com", "brazilianlumberlosangeles.com",
            "brazilianlumbernewyork.com"]


def main():
    out = {}
    for dom in DOMINIOS:
        n = 0
        for pg in range(1, 12):
            u = "https://{}/wp-json/wc/store/v1/products?per_page=100&page={}".format(dom, pg)
            try:
                d = requests.get(u, impersonate="chrome", timeout=60).json()
            except Exception as e:
                print("  {} pagina {}: {}".format(dom, pg, type(e).__name__))
                break
            if not isinstance(d, list) or not d:
                break
            for p in d:
                e = out.setdefault(p["slug"], {"cats": [], "tags": [], "attrs": {}})
                for c in p.get("categories", []):
                    if c["slug"] not in e["cats"]:
                        e["cats"].append(c["slug"])
                for t in p.get("tags", []):
                    if t["slug"] not in e["tags"]:
                        e["tags"].append(t["slug"])
                for a in p.get("attributes", []):
                    k = a.get("taxonomy") or a.get("name", "")
                    for t in a.get("terms", []):
                        e["attrs"].setdefault(k, [])
                        if t["slug"] not in e["attrs"][k]:
                            e["attrs"][k].append(t["slug"])
            n += len(d)
            if len(d) < 100:
                break
            time.sleep(1)
        print("{:34s} {:4d} fichas".format(dom, n))
    json.dump(out, open(D / "woo_cats.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("{} slugs, {} con etiquetas".format(
        len(out), sum(1 for v in out.values() if v["tags"])))


if __name__ == "__main__":
    main()
