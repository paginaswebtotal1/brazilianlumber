# -*- coding: utf-8 -*-
"""p11 - Trae los ficheros de la biblioteca de medios al portal nuevo.

Un PDF no se redirige: se migra. Y para que la URL antigua siga funcionando sin
redireccion ninguna, el fichero tiene que quedar en la MISMA ruta.

Por eso se descargan a web/public/wp-content/uploads/..., que es exactamente la
ruta que tenian en WordPress. Asi
  /wp-content/uploads/2021/12/Hardwoods_Spec_sheets_Brazilian-1.pdf
responde igual en el portal nuevo que en el viejo, sin tocar nada.

Ese PDF concreto tiene 426 clics y 82.459 impresiones en 16 meses: es una de
las piezas con mas trafico de todo el sitio.

Salida: web/public/wp-content/... + data/ficheros.json
"""
import json, re
from pathlib import Path
from urllib.parse import urlparse, unquote
from concurrent.futures import ThreadPoolExecutor
from curl_cffi import requests as cr

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
PUB = ROOT / "web" / "public"

GSC = json.load(open(D / "gsc.json", encoding="utf-8"))

# Extensiones que se migran como fichero. Las imagenes del contenido ya las
# trajeron p7 y p8; aqui interesan sobre todo los documentos, que son los que
# reciben trafico de busqueda directo.
DOCS = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".csv")
IMGS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg")


def limpia(url):
    """Quita parametros, anclas y la basura que a veces mete Search Console."""
    u = url.split("#")[0].split("?")[0]
    return u.rstrip(").,;'\"")


def ruta_local(url):
    """Misma ruta que tenia en WordPress, bajo public/."""
    p = unquote(urlparse(limpia(url)).path).lstrip("/")
    p = re.sub(r"[^A-Za-z0-9/._-]", "_", p)
    return PUB / p


def candidatos():
    vistos, out = set(), []
    for portal, datos in GSC["portales"].items():
        for url, m in datos["paginas"].items():
            u = limpia(url)
            low = u.lower()
            if "/wp-content/" not in low and "/wp-includes/" not in low:
                continue
            if not low.endswith(DOCS + IMGS):
                continue
            if u in vistos:
                continue
            vistos.add(u)
            out.append((u, m.get("clicks", 0), m.get("impressions", 0)))
    return out


def baja(item):
    url, clics, impr = item
    dest = ruta_local(url)
    if dest.exists() and dest.stat().st_size > 0:
        return url, {"ruta": "/" + str(dest.relative_to(PUB)).replace("\\", "/"),
                     "bytes": dest.stat().st_size, "clics": clics, "estado": "ya estaba"}
    try:
        r = cr.get(url, impersonate="chrome", timeout=90)
        if r.status_code != 200 or not r.content:
            return url, {"estado": "no responde ({})".format(r.status_code),
                         "clics": clics}
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        return url, {"ruta": "/" + str(dest.relative_to(PUB)).replace("\\", "/"),
                     "bytes": len(r.content), "clics": clics, "estado": "descargado"}
    except Exception as e:
        return url, {"estado": "error: {}".format(type(e).__name__), "clics": clics}


def main():
    items = candidatos()
    docs = [x for x in items if x[0].lower().endswith(DOCS)]
    imgs = [x for x in items if x[0].lower().endswith(IMGS)]
    print("{} ficheros en Search Console: {} documentos, {} imagenes".format(
        len(items), len(docs), len(imgs)), flush=True)
    print("clics en documentos: {} | en imagenes: {}".format(
        sum(x[1] for x in docs), sum(x[1] for x in imgs)), flush=True)

    # Los documentos, todos. Las imagenes, solo las que reciben visitas: bajar
    # 548 imagenes sueltas que nadie abre solo engorda el repositorio.
    objetivo = docs + [x for x in imgs if x[1] > 0]
    print("se descargan {} ({} documentos + {} imagenes con trafico)".format(
        len(objetivo), len(docs), len(objetivo) - len(docs)), flush=True)

    out = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for url, info in ex.map(baja, objetivo):
            out[url] = info

    ok = [v for v in out.values() if v.get("ruta")]
    mal = {k: v for k, v in out.items() if not v.get("ruta")}
    peso = sum(v["bytes"] for v in ok)
    json.dump(out, open(D / "ficheros.json", "w", encoding="utf-8"), ensure_ascii=False)

    print("\n{} de {} disponibles en el portal nuevo, {:.1f} MB".format(
        len(ok), len(objetivo), peso / 1024 / 1024))
    if mal:
        print("\nNO se pudieron traer ({}):".format(len(mal)))
        for k, v in sorted(mal.items(), key=lambda x: -x[1].get("clics", 0))[:15]:
            print("  {:4d} clics  {}  [{}]".format(v.get("clics", 0), k.split("/")[-1][:58],
                                                   v["estado"]))


if __name__ == "__main__":
    main()
