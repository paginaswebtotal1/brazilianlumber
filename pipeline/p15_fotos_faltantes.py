# -*- coding: utf-8 -*-
"""p15 - Recupera las fotos de las fichas que se quedaron sin ninguna.

Por que faltaban: p6 pidio featured_media, que es la foto destacada. Estas 24
fichas no la tienen puesta en WooCommerce, pero muchas si tienen imagenes en la
GALERIA del producto, que el endpoint de core no expone.

La Store API de WooCommerce (/wp-json/wc/store/v1/products) si la expone, es
publica y no necesita credenciales. Se prueba tambien en Los Angeles y New
Jersey: el mismo producto puede tener foto en un portal y no en otro, y a
efectos del catalogo unificado sirve igual.

Ultimo recurso si la galeria tambien viene vacia: leer la pagina del producto
con curl_cffi y quedarse con la imagen principal.

Salida: web/public/img/ + data/fotos_rescatadas.json
"""
import json, re, io, hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import httpx
from curl_cffi import requests as cr
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
IMG = ROOT / "web" / "public" / "img"
IMG.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
H = {"User-Agent": UA, "Accept": "application/json"}

DOMS = {
    "MIA": "https://brazilianlumber.com",
    "LA": "https://brazilianlumberlosangeles.com",
    "NJ": "https://brazilianlumbernewyork.com",
}

MAX_W, Q, MIN_PX = 880, 72, 150
MALAS = ("placeholder", "woocommerce-placeholder", "logo", "icon", "spinner")


def busca_store_api(slug):
    """Galeria del producto por la Store API, en los 3 portales."""
    urls = []
    with httpx.Client(follow_redirects=True) as c:
        for portal, dom in DOMS.items():
            try:
                r = c.get("{}/wp-json/wc/store/v1/products?slug={}&per_page=1".format(dom, slug),
                          headers=H, timeout=60)
                if r.status_code != 200:
                    continue
                for prod in r.json():
                    for im in prod.get("images") or []:
                        src = im.get("src") or ""
                        if src and not any(m in src.lower() for m in MALAS):
                            urls.append((src, portal, im.get("alt") or ""))
            except Exception:
                continue
    return urls


IMG_RE = re.compile(r'<img[^>]+(?:data-src|src)=["\']([^"\']+)["\']', re.I)


def busca_en_html(slug):
    """Ultimo recurso: la pagina del producto, leida con huella de navegador."""
    for portal, dom in DOMS.items():
        try:
            r = cr.get("{}/product/{}/".format(dom, slug), impersonate="chrome", timeout=60)
            if r.status_code != 200:
                continue
            html = r.text
            # la zona de la galeria, para no traerse el logotipo ni banners
            zona = html
            m = re.search(r'class="[^"]*woocommerce-product-gallery.*', html, re.S)
            if m:
                zona = m.group(0)[:20000]
            for u in IMG_RE.findall(zona):
                if u.startswith("http") and "/wp-content/uploads/" in u \
                        and not any(x in u.lower() for x in MALAS) \
                        and not u.lower().endswith(".svg"):
                    u = re.sub(r"-\d{2,4}x\d{2,4}(\.(jpe?g|png|webp))$", r"\1", u, flags=re.I)
                    return [(u, portal, "")]
        except Exception:
            continue
    return []


def descarga(url):
    k = hashlib.md5(url.encode()).hexdigest()[:16]
    dest = IMG / "{}.webp".format(k)
    if dest.exists() and dest.stat().st_size > 0:
        return "/img/{}.webp".format(k)
    try:
        r = cr.get(url, impersonate="chrome", timeout=90)
        if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image"):
            return None
        im = Image.open(io.BytesIO(r.content))
        im = ImageOps.exif_transpose(im)
        if im.width < MIN_PX or im.height < MIN_PX:
            return None
        if im.mode in ("RGBA", "LA", "P"):
            fondo = Image.new("RGB", im.size, (255, 255, 255))
            im = im.convert("RGBA")
            fondo.paste(im, mask=im.split()[-1])
            im = fondo
        else:
            im = im.convert("RGB")
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        im.save(dest, "WEBP", quality=Q, method=5)
        return "/img/{}.webp".format(k)
    except Exception:
        return None


def una(slug):
    fuentes = busca_store_api(slug)
    via = "galeria de WooCommerce"
    if not fuentes:
        fuentes = busca_en_html(slug)
        via = "pagina del producto"
    for url, portal, alt in fuentes:
        ruta = descarga(url)
        if ruta:
            return slug, {"src": ruta, "origen": url, "portal": portal,
                          "alt": alt, "via": via}
    return slug, None


def main():
    site = json.load(open(D / "site.json", encoding="utf-8"))
    faltan = [p["slug"] for p in site["products"] if not p.get("image")]
    print("{} fichas sin foto".format(len(faltan)), flush=True)

    out = {}
    with ThreadPoolExecutor(max_workers=5) as ex:
        for slug, info in ex.map(una, faltan):
            out[slug] = info
            estado = info["via"] if info else "no encontrada"
            print("  {:54s} {}".format(slug[:54], estado), flush=True)

    ok = {k: v for k, v in out.items() if v}
    json.dump(ok, open(D / "fotos_rescatadas.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("\nrecuperadas {} de {}".format(len(ok), len(faltan)))
    if len(ok) < len(faltan):
        print("sin foto en ninguno de los 3 portales:")
        for k, v in out.items():
            if not v:
                print("  ", k)


if __name__ == "__main__":
    main()
