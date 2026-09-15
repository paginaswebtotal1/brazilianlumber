# -*- coding: utf-8 -*-
"""La categoria REAL de WooCommerce, en vez de deducirla del nombre.

De donde sale el problema: el clasificador adivinaba la categoria leyendo el
slug y el titulo. Funciona para "ipe-1x6", pero no para "Ciro Green" (cesped
artificial), "Diana Blush" (panel vegetal) ni "Origens Tauari 8x12x0.3" (teto
vinilico). Lo que no reconocia caia en el cajon de sastre /accessories/, que es
justo lo que no es: 235 URLs acabaron ahi, y con ellas archivos de color, de
largo y de etiqueta que no son accesorios de ninguna clase.

La Store API de WooCommerce publica, para cada ficha, sus categorias, sus
etiquetas y sus atributos. Es el dato de origen, no una deduccion. Con eso:

  - cada producto va a la rama que la tienda dice que es,
  - cada archivo de atributo (/color/slate-gray/, /length/12/) va a la rama
    comun de los productos que llevan ese termino,
  - cada etiqueta (/product-tag/1x4/) igual,
  - y lo que de verdad abarca ramas distintas va a /shop/, que es el catalogo
    completo con filtros, no a una categoria que no le corresponde.

Salida de datos: data/woo_cats.json (lo genera p1b_woo.py).
"""
import json
from pathlib import Path
from taxonomia import MAP, ARBOL

D = Path(__file__).resolve().parent.parent / "data"

# Categorias que no dicen nada de que ES el producto: son promocionales o el
# cajon por defecto de WordPress.
IGNORAR = {"hot-deals", "hots-deals-page", "uncategorized"}

try:
    _W = json.load(open(D / "woo_cats.json", encoding="utf-8"))
except FileNotFoundError:
    _W = {}


def _profundidad(r):
    return r.count("/")


def ruta_producto(slug):
    """La rama que la propia tienda le asigna. La mas especifica si hay varias."""
    v = _W.get(slug)
    if not v:
        return ""
    rutas = [MAP[c] for c in v["cats"] if c not in IGNORAR and c in MAP]
    rutas = [r for r in rutas if r in ARBOL]
    if not rutas:
        return ""
    return sorted(rutas, key=_profundidad, reverse=True)[0]


def _comun(rutas):
    """Rama comun a un conjunto de productos.

    Si un archivo de color solo lo llevan tarimas de AZEK, su sitio es AZEK. Si
    lo llevan tarimas y aceites a la vez, no hay una categoria honesta: se
    devuelve vacio y quien llame decide (el catalogo).
    """
    rutas = [r for r in rutas if r]
    if not rutas:
        return ""
    p = rutas[0].split("/")
    for r in rutas[1:]:
        q = r.split("/")
        n = 0
        while n < len(p) and n < len(q) and p[n] == q[n]:
            n += 1
        p = p[:n]
        if not p:
            return ""
    c = "/".join(p)
    return c if c in ARBOL else ""


def _final(slug):
    """La categoria en la que el producto acaba viviendo en el portal nuevo.

    No es lo mismo que la de la tienda vieja: alli los 66 accesorios comparten
    una sola categoria, "Decking Accessories", y aqui estan repartidos en
    tornilleria, aceites, herramientas, subestructura y mantenimiento. Para
    resolver un archivo de etiqueta interesa el reparto nuevo: si todo lo que
    lleva la etiqueta "ipe-clips" acaba en tornilleria, ahi va la etiqueta, no
    a la raiz de accesorios.
    """
    if _CAT_FINAL is None:
        _cargar_final()
    return _CAT_FINAL.get(slug) or ruta_producto(slug)


_CAT_FINAL = None


def _cargar_final():
    global _CAT_FINAL
    _CAT_FINAL = {}
    try:
        for d in json.load(open(D / "classified.json", encoding="utf-8")):
            if d.get("tipo") == "product" and d.get("cat") in ARBOL:
                _CAT_FINAL[d["slug"]] = d["cat"]
    except FileNotFoundError:
        pass


def _indices():
    term, tag = {}, {}
    for slug, v in _W.items():
        r = _final(slug)
        if not r:
            continue
        for k, ts in v.get("attrs", {}).items():
            k = k.replace("pa_", "").lower().replace(" ", "-")
            for t in ts:
                term.setdefault((k, t.lower()), []).append(r)
        for t in v.get("tags", []):
            tag.setdefault(t.lower(), []).append(r)
    return ({k: _comun(v) for k, v in term.items()},
            {k: _comun(v) for k, v in tag.items()})


TERMINO, ETIQUETA = {}, {}


def _asegura():
    """Se construye al primer uso: classified.json lo escribe p2, que importa
    este modulo, asi que no puede leerse al importarlo."""
    global TERMINO, ETIQUETA
    if not TERMINO and not ETIQUETA:
        TERMINO, ETIQUETA = _indices()

# Un mismo termino puede vivir bajo dos taxonomias (/color/ y /colors/), y los
# archivos de longitud se publican como /length/ y /board-length/ a la vez.
EQUIV = {"colors": "color", "board-length": "length", "package-size": "size",
         "color-options": "color", "quantity": "count"}


def ruta_termino(taxonomia, termino):
    """Destino de un archivo de atributo. Vacio si no hay uno honesto."""
    _asegura()
    t = (termino or "").lower()
    for k in (taxonomia, EQUIV.get(taxonomia, "")):
        if k and (k, t) in TERMINO:
            # Ojo: cadena vacia no es "no lo se", es "no hay una categoria
            # honesta". El termino existe y lo llevan productos de ramas
            # distintas. Devolverlo vacio manda la URL al catalogo, que es lo
            # que toca; buscarlo en otra taxonomia seria inventarse una rama.
            return TERMINO[(k, t)]
    # el termino no existe bajo esta taxonomia: se busca bajo las demas
    cand = [v for (k, x), v in TERMINO.items() if x == t and v]
    return _comun(cand) if cand else ""


def ruta_etiqueta(termino):
    _asegura()
    return ETIQUETA.get((termino or "").lower(), "")


# Taxonomias de atributo que WooCommerce publica como archivo propio.
ATRIBUTOS = {"color", "colors", "color-options", "length", "board-length",
             "size", "package-size", "upc", "amount", "quantity", "count",
             "width", "thickness", "grade", "finish", "profile", "hardwood",
             "wood-type", "turboclip", "voc"}


def es_atributo(tax):
    return tax in ATRIBUTOS
