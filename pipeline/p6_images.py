# -*- coding: utf-8 -*-
"""p6 - Trae las fotografias REALES de los 3 portales.

El volcado original (rest_full.jsonl) no pidio el campo featured_media, que es
donde WooCommerce guarda la foto del producto. Por eso 285 de 295 fichas
salieron sin imagen: no es que no existan, es que no se pidieron.

Aqui se pide: primero la relacion contenido -> featured_media, despues la URL
real de cada fichero en la biblioteca de medios, y ademas la galeria de
WooCommerce cuando existe.

Cloudflare bloquea el HTML de los 3 dominios, pero la API REST responde si la
peticion parece un navegador. Salida: data/images.json
"""
import json, time, sys
from pathlib import Path
import httpx

D = Path(__file__).resolve().parent.parent / "data"
OUT = D / "images.json"

DOMS = {
    "MIA": "https://brazilianlumber.com",
    "LA": "https://brazilianlumberlosangeles.com",
    "NJ": "https://brazilianlumbernewyork.com",
}
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
H = {"User-Agent": UA, "Accept": "application/json", "Accept-Encoding": "gzip, deflate",
     "Accept-Language": "en-US,en;q=0.9"}

ENDPOINTS = ["product", "posts", "pages"]


def fetch(c, url, tries=4):
    for i in range(tries):
        try:
            r = c.get(url, headers=H, timeout=90)
            if r.status_code == 200:
                return r
            if r.status_code in (400, 404):
                return None
            time.sleep(2 + 2 * i)
        except Exception:
            time.sleep(2 + 2 * i)
    return None


def paginate(c, base, fields):
    """Recorre todas las paginas de un endpoint."""
    out, page = [], 1
    while True:
        r = fetch(c, f"{base}?per_page=100&page={page}&_fields={fields}")
        if r is None:
            break
        try:
            data = r.json()
        except Exception:
            break
        if not data:
            break
        out.extend(data)
        total = int(r.headers.get("X-WP-TotalPages", 1) or 1)
        if page >= total:
            break
        page += 1
    return out


def main():
    rel = {}      # (portal, endpoint, id) -> featured_media id
    media_ids = {}  # portal -> set de ids
    with httpx.Client(follow_redirects=True, http2=False) as c:
        for portal, dom in DOMS.items():
            media_ids[portal] = set()
            for ep in ENDPOINTS:
                url = f"{dom}/wp-json/wp/v2/{ep}"
                rows = paginate(c, url, "id,slug,featured_media,link")
                got = 0
                for r in rows:
                    fm = r.get("featured_media") or 0
                    if fm:
                        rel[f"{portal}|{ep}|{r['id']}"] = fm
                        media_ids[portal].add(fm)
                        got += 1
                print(f"  {portal} {ep:8s}: {len(rows):4d} entidades, {got:4d} con foto", flush=True)

        # ---- URLs reales de la biblioteca de medios
        media = {}
        for portal, dom in DOMS.items():
            ids = sorted(media_ids[portal])
            if not ids:
                continue
            done = 0
            for i in range(0, len(ids), 60):
                lote = ids[i:i + 60]
                url = (f"{dom}/wp-json/wp/v2/media?per_page=100&include={','.join(map(str, lote))}"
                       "&_fields=id,source_url,alt_text,media_details")
                r = fetch(c, url)
                if r is None:
                    continue
                try:
                    for m in r.json():
                        sizes = (m.get("media_details") or {}).get("sizes") or {}
                        # Se prefiere un tamano intermedio: el original suele
                        # pesar 2-4 MB y arruinaria el LCP.
                        pick = None
                        for k in ("large", "woocommerce_single", "medium_large", "shop_single", "full"):
                            if k in sizes and sizes[k].get("source_url"):
                                pick = sizes[k]
                                break
                        media[f"{portal}|{m['id']}"] = {
                            "url": (pick or {}).get("source_url") or m.get("source_url"),
                            "w": (pick or {}).get("width"),
                            "h": (pick or {}).get("height"),
                            "alt": (m.get("alt_text") or "").strip(),
                            "full": m.get("source_url"),
                        }
                        done += 1
                except Exception:
                    pass
            print(f"  {portal} medios   : {done:4d} ficheros resueltos", flush=True)

    json.dump({"rel": rel, "media": media},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"\nrelaciones: {len(rel)} | medios: {len(media)} -> {OUT.name}")


if __name__ == "__main__":
    main()
