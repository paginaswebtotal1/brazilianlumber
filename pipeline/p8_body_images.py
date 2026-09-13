# -*- coding: utf-8 -*-
"""p8 - Descarga TODAS las imagenes del cuerpo de las 838 paginas.

p6/p7 trajeron la foto destacada de cada contenido (724 ficheros). Aqui se
completan las galerias: cada imagen que aparece dentro del texto de un
articulo, una ficha o una pagina.

Mismo metodo: curl_cffi con huella TLS de Chrome, que es lo unico que deja
pasar Cloudflare, en 12 hilos. Salida: web/public/img/ + data/bodyimg.json
"""
import json, hashlib, io
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from curl_cffi import requests as cr
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = 200_000_000

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
IMG = ROOT / "web" / "public" / "img"
IMG.mkdir(parents=True, exist_ok=True)

MAX_W = 1000
QUALITY = 78
MIN_PX = 120  # descarta iconos, pixeles de seguimiento y separadores


def key(url):
    return hashlib.md5(url.encode()).hexdigest()[:16]


def one(url):
    k = key(url)
    dest = IMG / f"{k}.webp"
    if dest.exists() and dest.stat().st_size > 0:
        try:
            with Image.open(dest) as im:
                return url, {"src": f"/img/{k}.webp", "w": im.width, "h": im.height}
        except Exception:
            dest.unlink(missing_ok=True)
    try:
        r = cr.get(url, impersonate="chrome", timeout=60)
        if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image"):
            return url, None
        im = Image.open(io.BytesIO(r.content))
        im = ImageOps.exif_transpose(im)
        if im.width < MIN_PX or im.height < MIN_PX:
            return url, None
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
        return url, {"src": f"/img/{k}.webp", "w": im.width, "h": im.height}
    except Exception:
        return url, None


def main():
    raw = json.load(open(D / "raw.json", encoding="utf-8"))
    surv = [d for d in raw if d["accion"] in ("CONSERVAR", "CONSERVAR-REESCRIBIR")]
    urls = sorted({u for d in surv for u in d["imagenes"]})
    print(f"{len(urls)} imagenes de cuerpo por descargar", flush=True)

    out = {}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for i, (u, info) in enumerate(ex.map(one, urls), 1):
            if info:
                out[u] = info
            if i % 200 == 0:
                print(f"  {i}/{len(urls)}  ({len(out)} ok)", flush=True)

    json.dump(out, open(D / "bodyimg.json", "w", encoding="utf-8"), ensure_ascii=False)
    total = sum(f.stat().st_size for f in IMG.glob("*.webp"))
    print(f"\n{len(out)} de {len(urls)} descargadas")
    print(f"biblioteca completa: {len(list(IMG.glob('*.webp')))} ficheros, {total / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
