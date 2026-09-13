# -*- coding: utf-8 -*-
"""p7 - Descarga y optimiza las fotografias reales.

Por que descargarlas en vez de enlazarlas: Cloudflare deja pasar al navegador
pero bloquea todo lo que no tenga huella TLS de navegador, y su proteccion de
hotlinking puede activarse en cualquier momento para peticiones que vengan de
otro dominio. Si eso pasa un dia de demo, el sitio se queda sin fotos.

Sirviendolas desde el propio portal: cargan siempre, cargan rapido y ademas se
recomprimen a WebP, que es lo que pide Core Web Vitals.

Salida: web/public/img/<hash>.webp  +  data/imgmap.json
"""
import json, hashlib, io, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from curl_cffi import requests as cr
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
IMG = ROOT / "web" / "public" / "img"
IMG.mkdir(parents=True, exist_ok=True)

MAX_W = 1000        # suficiente para la ficha a pantalla completa
QUALITY = 78

data = json.load(open(D / "images.json", encoding="utf-8"))
media = data["media"]


def key(url):
    return hashlib.md5(url.encode()).hexdigest()[:16]


def one(item):
    mid, m = item
    url = m.get("url")
    if not url:
        return mid, None
    k = key(url)
    dest = IMG / f"{k}.webp"
    if dest.exists() and dest.stat().st_size > 0:
        try:
            with Image.open(dest) as im:
                return mid, {"src": f"/img/{k}.webp", "w": im.width, "h": im.height,
                             "alt": m.get("alt") or ""}
        except Exception:
            dest.unlink(missing_ok=True)
    try:
        r = cr.get(url, impersonate="chrome", timeout=60)
        if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image"):
            return mid, None
        im = Image.open(io.BytesIO(r.content))
        im = ImageOps.exif_transpose(im)
        if im.mode in ("RGBA", "LA", "P"):
            fondo = Image.new("RGB", im.size, (255, 255, 255))
            im = im.convert("RGBA")
            fondo.paste(im, mask=im.split()[-1])
            im = fondo
        else:
            im = im.convert("RGB")
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        im.save(dest, "WEBP", quality=QUALITY, method=5)
        return mid, {"src": f"/img/{k}.webp", "w": im.width, "h": im.height,
                     "alt": m.get("alt") or ""}
    except Exception:
        return mid, None


def main():
    items = list(media.items())
    out = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, (mid, info) in enumerate(ex.map(one, items), 1):
            if info:
                out[mid] = info
            if i % 100 == 0:
                print(f"  {i}/{len(items)}", flush=True)

    json.dump({"rel": data["rel"], "img": out},
              open(D / "imgmap.json", "w", encoding="utf-8"), ensure_ascii=False)

    total = sum(f.stat().st_size for f in IMG.glob("*.webp"))
    print(f"\n{len(out)} de {len(items)} imagenes descargadas y optimizadas")
    print(f"peso total: {total / 1024 / 1024:.1f} MB  |  media: {total / max(len(out),1) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
