# -*- coding: utf-8 -*-
"""p3 - Construye el dataset final del portal unico: contenido unico por URL,
menu, breadcrumbs, relacionados, redirecciones y metadatos SEO.
Salida: data/site.json
"""
import json, re, hashlib
from pathlib import Path
from collections import defaultdict, Counter
from taxonomia import ARBOL, MAP, ESPECIE
from kb import ESPECIES, MARCAS, MEDIDAS, COLORES
import contenido
import contenido_paginas
import ciudades as _ciu
import medidas as _med

D = Path(__file__).resolve().parent.parent / "data"
HOST = "https://brazilianlumber.com"


def path_of(u):
    p = u.replace(HOST, "")
    if not p.startswith("/"):
        p = "/" + p
    if not p.endswith("/"):
        p += "/"
    return p


def pick(seed, opts):
    """Elige de forma determinista pero distinta por pagina: evita texto calcado."""
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return opts[h % len(opts)]


def titlecase(s):
    minor = {"and", "or", "the", "of", "for", "in", "on", "a", "an", "to", "with", "by"}
    w = s.split()
    return " ".join(x if (i and x.lower() in minor) else (x[:1].upper() + x[1:]) for i, x in enumerate(w))


# Paginas legacy que duplican un nodo de la taxonomia. Tener las dos compitiendo
# por la misma consulta es canibalizacion: la categoria es la que gana, porque
# lista producto real. Estas se consolidan y quedan documentadas en el mapa.
CONSOLIDAR = {
    "trex-decking": "decking/composite/trex",
    "timbertech-composite-decking": "decking/composite/timbertech",
    "deckotech": "decking/composite/deckotech",
    "deckotech-2": "decking/composite/deckotech",
    "pvc-decking": "decking/pvc",
    "composite-decking": "decking/composite",
    "decking-accessories": "accessories",
    "tools": "accessories/tools",
    "thermally-modified-wood": "decking/thermally-modified",
    "thermally-enhanced-wood": "decking/thermally-modified",
    "lunawood": "decking/thermally-modified",
    "cumaru": "decking/tropical-hardwood/cumaru",
    "garapa": "decking/tropical-hardwood/garapa",
    "jatoba": "decking/tropical-hardwood/jatoba",
    "tigerwood": "decking/tropical-hardwood/tigerwood",
    "piquia": "decking/tropical-hardwood/piquia",
    "ipe": "decking/tropical-hardwood/ipe",
    "cladding": "cladding-siding",
    "siding-and-cladding": "cladding-siding",
    "wood-wall-panels": "cladding-siding/wood-wall-panels",
    "decktiles": "decking/deck-tiles",
    "ipe-deck-tiles": "decking/deck-tiles",
    "fences-docks": "fencing-gates",
    "menu-shop": "shop",
    "new-shop": "shop",
    "brazilian-lumber-blogs": "guides",
    "blogs": "guides",
    "brazilian-lumber-los-angeles-blogs": "guides",
}

JUNK = {"hometest", "carousel-home", "thank-you-page", "cont-form-example", "test-form-flowsly",
        "home-test-2025", "blog-example", "thank-you-review", "thank-you-ibs", "thank-you", "demo-home"}

# Campanas y formularios de eventos ya pasados. No son basura (existieron y
# tuvieron trafico), pero un formulario de sorteo de una feria del ano pasado no
# tiene por que estar en el indice de Google compitiendo con el catalogo.
CADUCADAS = {"ibs", "ibs-show-giveaway-form", "thank-you-ibs", "black-friday-2025-terms-conditions",
             "black-friday-terms-and-conditions", "covid-19-update", "trend-guide",
             "download-trend-guide", "thank-you-review", "download-or-digital-brochure"}

UTIL = {"cart", "my-cart", "checkout", "my-account", "register", "privacy-policy", "terms-conditions",
        "terms-and-conditions", "sitemap", "free-shipping-terms", "black-friday-2025-terms-conditions",
        "black-friday-terms-and-conditions", "covid-19-update", "pay-with-affirm"}

CIUDADES = {"albany", "altadena", "anaheim", "atlanta", "austin", "bahamas", "beaufort", "berkeley-lake",
            "boca-raton", "buffalo", "charleston", "coconut-grove", "columbia", "coral-gables", "corpus-christi",
            "dallas-fort-worth", "el-paso", "fort-lauderdale", "fort-myers", "fresno", "galveston", "houston",
            "jacksonville", "johns-creek", "key-west", "long-island", "los-angeles", "miami", "milton", "naples",
            "new-jersey", "new-york", "orlando", "palm-beach", "rochester-syracuse", "sacramento", "san-antonio",
            "san-diego", "san-francisco", "san-jose", "san-marcos", "santa-barbara", "savannah", "tampa",
            "wellington", "california", "florida", "georgia", "south-carolina", "texas", "islands-of-the-caribbean"}


# ---------------- contenido generado, unico por pagina ----------------
def specs_producto(a):
    rows = []
    esp = ESPECIES.get(a.get("especie") or "")
    if a.get("medida"):
        rows.append(("Nominal size", a["medida"].replace("x", " x ")))
    if a.get("real"):
        rows.append(("Actual size", a["real"]))
    if esp:
        rows.append(("Species", esp[0]))
        rows.append(("Janka hardness", "{:,} lbf".format(esp[1])))
        rows.append(("Density", "{} kg/m3 average, air dried".format(esp[2])))
        rows.append(("Color", titlecase(esp[3].split(" with ")[0])))
        rows.append(("Service life", esp[4]))
    if a.get("marca"):
        m = MARCAS[a["marca"]]
        rows.append(("Brand", m[0]))
        rows.append(("Material", titlecase(m[1])))
        rows.append(("Warranty", titlecase(m[2])))
    if a.get("coleccion"):
        rows.append(("Collection", a["coleccion"]))
    if a.get("largo"):
        rows.append(("Board length", "{} ft".format(a["largo"])))
    if a.get("grado"):
        rows.append(("Grade", a["grado"]))
    rows.append(("Moisture content", "Kiln dried to 12-16% for exterior use"))
    rows.append(("Availability", "In stock, cut to order"))
    return rows


def gen_producto(d):
    a = d.get("attr") or {}
    t = d["titulo"]
    slug = d["slug"]
    esp = ESPECIES.get(a.get("especie") or "")
    mrc = MARCAS.get(a.get("marca") or "")
    uso = a.get("uso") or "profile"
    bl = []

    if esp and a.get("real"):
        lead = pick(slug, [
            "{} is a {} {} milled from {}, a {}. At {:,} lbf on the Janka scale it is {}.".format(
                t, a["real"], uso, esp[0], esp[3], esp[1], esp[5]),
            "This {} {} is cut from {}. The wood is {}, rates {:,} lbf on the Janka hardness scale, and is {}.".format(
                a["real"], uso, esp[0], esp[3], esp[1], esp[5]),
            "{} gives you a {} {} in {}: {}, {:,} lbf Janka, and {} of service with no chemical treatment.".format(
                t, a["real"], uso, esp[0], esp[3], esp[1], esp[4]),
        ])
    elif esp:
        lead = pick(slug, [
            "{} is milled from {}, a {}. It rates {:,} lbf on the Janka scale and is {}.".format(
                t, esp[0], esp[3], esp[1], esp[5]),
            "{} is a {} product. The species is {}, rates {:,} lbf Janka, and delivers {}.".format(
                t, esp[0], esp[3], esp[1], esp[4]),
        ])
    elif mrc:
        lead = pick(slug, [
            "{} is part of the {} line of {}. It carries a {} and {}.".format(t, mrc[0], mrc[1], mrc[2], mrc[3]),
            "{} comes from {}, built as {}. The product is backed by a {}, and {}.".format(
                t, mrc[0], mrc[1], mrc[2], mrc[3]),
        ])
    else:
        lead = ("{} is part of the Brazilian Lumber catalog, stocked and shipped from our yards in "
                "Miami, Los Angeles and New Jersey.".format(t))
    bl.append({"t": "p", "text": lead})

    # El texto propio del producto es lo mas valioso que hay: es lo unico que
    # ninguna plantilla puede replicar. Se aprovecha siempre que exista y no
    # este duplicado en el origen.
    orig = [b for b in d["blocks"] if b["t"] == "p" and len(b.get("text", "")) > 80]
    if orig and not d.get("dup"):
        for b in orig[:4]:
            bl.append(b)
    elif not orig and d.get("texto") and not d.get("dup"):
        # Hay texto en WordPress pero venia dentro de una tabla o un shortcode
        # que el extractor de bloques no supo abrir. Se recupera en crudo: son
        # fichas tecnicas reales (medidas, clase, acabado, especie, longitud).
        crudo = [x.strip() for x in d["texto"].splitlines() if len(x.strip()) > 25]
        for trozo in crudo[:5]:
            bl.append({"t": "p", "text": trozo[:600]})

    # Cuando no hay especie ni marca reconocidas, el nombre del producto es la
    # unica senal propia que queda. Sin esto, todas las fichas sin atributos
    # acababan con el MISMO texto: fue exactamente lo que detecto la auditoria
    # de contenido duplicado.
    if not esp and not mrc:
        import re as _re
        tokens = [x for x in _re.split(r"[\s\-_/]+", t) if len(x) > 2 and not x.isdigit()]
        propio = " ".join(dict.fromkeys(tokens))[:80]
        dims = _re.findall(r'\d+(?:[.,]\d+)?\s*(?:mm|cm|["″]|′|x)\s*\d+(?:[.,]\d+)?[^,;.]{0,18}', t)
        linea = "{} is catalogued as {}".format(t, propio.lower())
        if dims:
            linea += ", supplied at {}".format(dims[0].strip())
        bl.append({"t": "p", "text": linea + ". Ask the sales desk for the current "
                                     "specification sheet, stock and lead time on this exact "
                                     "reference before you specify it."})

    # ---- coleccion y largo: lo que separa dos referencias de la misma marca
    if a.get("coleccion") or a.get("largo"):
        trozos = []
        if a.get("coleccion"):
            trozos.append("This is the {} range".format(a["coleccion"]))
        if a.get("largo"):
            trozos.append("supplied in {} foot lengths".format(a["largo"]))
            if a.get("medida") and a["medida"] in _med.DIM:
                _ancho = _med.DIM[a["medida"]][1]
                _cob = round((_ancho + _med.GAP) / 12 * a["largo"], 2)
                trozos.append("so each board covers about {} square feet".format(_cob))
        bl.append({"t": "p", "text": ", ".join(trozos) +
                   ". Length matters more than people expect: matching the board length to the "
                   "deck run is what removes the offcut from the order."})

    # ---- cifras propias de ESTA escuadria
    #
    # Es lo que separa de verdad una ficha de su hermana. Un Ipe 1x4 y un Ipe
    # 5/4x6 comparten todo lo que se puede decir del Ipe, pero cubren distinto,
    # pesan distinto y se piden en cantidades distintas. Esos numeros son
    # reales, utiles para pedir material, y distintos en cada ficha.
    num = _med.datos(a.get("medida"), esp[2] if esp else None)
    if num:
        frases = []
        if num["vano"]:
            frases.append("Over joists at {} inches on center".format(num["vano"]))
        frases.append("each linear foot covers {} square feet with a 3/16 inch gap"
                      .format(num["cobertura"]))
        frases.append("so 100 square feet of deck takes about {} linear feet"
                      .format(num["lineales_100"]))
        texto = ", ".join(frases)
        if num.get("lb_pie"):
            texto += (". The section is {} square inches and it weighs about {} lb per linear "
                      "foot, roughly {} lb for those 100 square feet, which is what decides "
                      "whether the delivery needs a liftgate"
                      .format(num["seccion"], num["lb_pie"], num["lb_100sqft"]))
        bl.append({"t": "p", "text": texto + "."})
        bl.append({"t": "p", "text": "This size is normally specified for {}.".format(num["uso"])})

    name = esp[0] if esp else (mrc[0] if mrc else t)
    bl.append({"t": "h2", "text": pick(slug + "w", [
        "Why builders specify {}".format(name),
        "What you get with {}".format(name),
        "Why this board is specified",
    ])})
    items = []
    if esp:
        # Solo dos lineas de especie. El desarrollo completo esta en la pagina
        # de categoria, enlazada desde aqui: repetirlo en las 21 fichas de Ipe
        # era lo que las convertia en duplicados entre si.
        items.append("Janka hardness of {:,} lbf and {} outdoors with no chemical treatment."
                     .format(esp[1], esp[4]))
        items.append(pick(slug + "s", [
            "Color: {}.".format(esp[3]),
            "{}.".format(esp[5][0].upper() + esp[5][1:]),
        ]))
    if mrc:
        items.append("{} construction: {}, {}.".format(mrc[0], mrc[1], mrc[3]))
        items.append("Backed by a {}.".format(mrc[2]))
        items.append("No sanding, sealing or staining. Washing with soap and water is the full maintenance program.")
    if a.get("medida"):
        items.append("Milled to {}, the standard {} {} dimension, so it drops into existing framing without "
                     "rework.".format(a["real"], a["medida"].replace("x", " x "), uso))
    items.append("Stocked in Miami, Los Angeles and New Jersey, with cut-to-length service and nationwide freight.")
    bl.append({"t": "list", "items": items})

    bl.append({"t": "h2", "text": "Installation notes"})
    if num and num["vano"]:
        bl.append({"t": "p", "text":
            "Frame at {} inches on center for this thickness, and allow {} linear feet per 100 "
            "square feet when you order.".format(num["vano"], num["lineales_100"])})
    if esp and esp[1] >= 1600:
        bl.append({"t": "p", "text": pick(slug + "i", [
            "Dense tropical hardwood has to be pre-drilled and counterbored before fastening; a screw driven "
            "straight into it will snap or split the board. Use stainless steel fasteners, leave a 3/16 inch gap "
            "between boards for airflow, and seal every fresh cut end with an end grain sealer the same day it is cut.",
            "Pre-drill every fastener hole. At this density the board will split before a screw bites, so a "
            "counterbore and a stainless screw are not optional. Space boards 3/16 inch apart, keep the "
            "substructure ventilated, and seal cut ends immediately to stop end checking.",
            "Plan for pre-drilling and for carbide tooling: this wood will dull standard steel blades quickly. "
            "Fasten with stainless steel only, hold a 3/16 inch gap between boards, and apply end grain sealer to "
            "every cut within the same working day.",
        ])})
    elif mrc:
        bl.append({"t": "p", "text": pick(slug + "i", [
            "{} boards install over a conventional joist layout at 16 inches on center, or 12 inches on center for "
            "a diagonal pattern. Follow the manufacturer gapping chart, which changes with the installation "
            "temperature, and use the hidden fastener system sold for this profile.".format(mrc[0]),
            "Install over joists at 16 inches on center, tightening to 12 inches for diagonal or stair "
            "applications. {} expands and contracts with temperature, so the gap at install has to be read off the "
            "manufacturer chart rather than set by eye.".format(mrc[0]),
        ])})
    else:
        bl.append({"t": "p", "text": "Install over a ventilated, level substructure. Keep the material dry and "
                                     "stickered on site, and let it acclimate to local humidity before it is "
                                     "fastened down."})

    bl.append({"t": "h2", "text": "Care and maintenance"})
    if esp and "interior" not in esp[4]:
        tone = esp[3].split(" with ")[0]
        bl.append({"t": "p", "text": pick(slug + "m", [
            "Left alone, {} fades to a soft silver patina without losing an ounce of structural strength. If you "
            "want to hold the {} tone, clean the deck and re-apply a penetrating hardwood oil once a year, twice "
            "in full southern sun.".format(esp[0], tone),
            "{} needs no sealer to survive. The only reason to oil it is color: one coat of a penetrating UV oil "
            "each spring keeps the {} tone; skip it and the surface silvers evenly instead.".format(esp[0], tone),
        ])})
    else:
        bl.append({"t": "p", "text": "Wash with warm water and a mild soap. Do not use a pressure washer above "
                                     "1,500 psi, and keep the nozzle at least twelve inches from the surface."})

    faq = []
    if esp:
        faq.append(("How long will {} last outdoors?".format(esp[0]),
                    "{} in a ventilated installation, with no chemical treatment. The limiting factor is almost "
                    "never the board, it is the substructure underneath it.".format(esp[4].capitalize())))
        faq.append(("Does {} need to be sealed?".format(esp[0]),
                    "Only the cut ends, and only to prevent checking. Surface oil is a cosmetic choice, not a "
                    "structural one."))
    if a.get("medida"):
        faq.append(("What is the actual size of a {}?".format(a["medida"].replace("x", " x ")),
                    "{}. Nominal sizes describe the rough sawn dimension before milling, so the finished board "
                    "always measures less.".format(a["real"])))
    if mrc:
        faq.append(("What warranty comes with {}?".format(mrc[0]),
                    "A {}. Registration is handled by the manufacturer and we supply the proof of "
                    "purchase.".format(mrc[2])))
    faq.append(("Can I get this cut to length?",
                "Yes. We mill to order in house and can ship cut stock, which cuts jobsite waste and freight cost "
                "on long runs."))
    # Fichas sin especie ni marca reconocida (cesped artificial, hiedra, losetas)
    # se quedaban cortas. Se les añade la guia de su familia, que es informacion
    # util de verdad y no relleno.
    if not esp and not mrc:
        import contenido as _c
        fam = _c.FAMILIA.get((d.get("cat") or "accessories").split("/")[0])
        if fam:
            bl.append({"t": "h2", "text": "What to look at before you order"})
            bl.append({"t": "list", "items": ["{}. {}".format(t, x) for t, x in fam["elegir"]]})
            bl.append({"t": "h2", "text": "Installation"})
            bl.append({"t": "p", "text": fam["instalacion"]})
            for q, a in fam["faq"]:
                faq.append((q, a))

    bl.append({"t": "h2", "text": "Frequently asked questions"})
    d["faq"] = [{"q": q, "a": aa} for q, aa in faq[:4]]
    for q, aa in faq[:4]:
        bl.append({"t": "h3", "text": q})
        bl.append({"t": "p", "text": aa})
    return bl


def gen_categoria(ruta, titulo, hijos, prods):
    n = len(prods)
    key = ruta.rsplit("/", 1)[-1]
    esp = ESPECIES.get(key)
    mrc = MARCAS.get(key)
    bl = []
    if esp:
        bl.append({"t": "p", "text": "{} covers every {} profile we stock: {}, {:,} lbf on the Janka scale, and {} "
                                     "outdoors with no chemical treatment. {}.".format(
                                         titulo, esp[0], esp[3], esp[1], esp[4], esp[5][0].upper() + esp[5][1:])})
    elif mrc:
        bl.append({"t": "p", "text": "{} brings together the {} range we carry, built as {} and backed by a {}. "
                                     "{}.".format(titulo, mrc[0], mrc[1], mrc[2], mrc[3][0].upper() + mrc[3][1:])})
    else:
        bl.append({"t": "p", "text": pick(ruta, [
            "{} groups every product in this line across the Brazilian Lumber catalog, stocked in Miami, "
            "Los Angeles and New Jersey.".format(titulo),
            "Everything we carry under {}, in one place. All of it ships from our own yards, cut to length on "
            "request.".format(titulo),
            "{}: the full range we stock, with live inventory in three yards and nationwide freight.".format(titulo),
        ])})
    if n:
        sizes = sorted({p["attr"]["medida"] for p in prods if (p.get("attr") or {}).get("medida")})
        especies = sorted({ESPECIES[p["attr"]["especie"]][0] for p in prods
                           if (p.get("attr") or {}).get("especie") in ESPECIES})
        line = "There are {} product{} in this category".format(n, "s" if n != 1 else "")
        if sizes:
            line += ", in {} milled size{} ({})".format(
                len(sizes), "s" if len(sizes) != 1 else "",
                ", ".join(s.replace("x", " x ") for s in sizes[:8]))
        if especies and not esp:
            line += ", across {}".format(", ".join(especies[:6]))
        bl.append({"t": "p", "text": line + "."})
    if hijos:
        bl.append({"t": "h2", "text": "Browse by type"})
        bl.append({"t": "list", "items": [h[1] for h in hijos]})
    if esp:
        bl.append({"t": "h2", "text": "Specifying {}".format(esp[0])})
        bl.append({"t": "list", "items": [
            "Janka hardness: {:,} lbf.".format(esp[1]),
            "Average dry density: {} kg/m3.".format(esp[2]),
            "Expected service life: {}.".format(esp[4]),
            "Pre-drilling and stainless fasteners required.",
            "End grain sealer on every cut, applied the same day.",
        ]})
    return bl


def gen_pagina(d):
    if d["blocks"]:
        return d["blocks"]
    t = d["titulo"] or titlecase(d["slug"].replace("-", " "))
    return [{"t": "p", "text": "{}. This page is part of the unified Brazilian Lumber portal. The content of the "
                               "original page is preserved in the migration map and will be moved across during "
                               "the build.".format(t)}]


# ---------------- main ----------------
def main():
    docs = json.load(open(D / "classified.json", encoding="utf-8"))
    raw = json.load(open(D / "raw.json", encoding="utf-8"))

    # Fotografias reales, descargadas y optimizadas por p6/p7. Se sirven desde
    # el propio portal: Cloudflare bloquea el hotlinking desde otro dominio.
    try:
        im = json.load(open(D / "imgmap.json", encoding="utf-8"))
        REL, IMGS = im["rel"], im["img"]
    except FileNotFoundError:
        REL, IMGS = {}, {}
    try:
        BODY = json.load(open(D / "bodyimg.json", encoding="utf-8"))
    except FileNotFoundError:
        BODY = {}
    try:
        DIMS = json.load(open(D / "imgdims.json", encoding="utf-8"))
    except FileNotFoundError:
        DIMS = {}

    def dim(src):
        d = DIMS.get(src.rsplit("/", 1)[-1].replace(".webp", ""))
        return {"w": d[0], "h": d[1]} if d else {}

    def intercalar(bloques, fotos):
        """Reparte las fotos del cuerpo entre los parrafos, como estaban en el
        original. Un articulo de 1.500 palabras sin una sola imagen se lee como
        un muro de texto, por muy bueno que sea el contenido."""
        if not fotos:
            return bloques
        out, usadas, desde = [], 0, 0
        for i, b in enumerate(bloques):
            out.append(b)
            # Despues del segundo parrafo, y luego cada cuatro bloques.
            if usadas < len(fotos) and i >= 1 and (i - desde) >= (2 if usadas == 0 else 4)                     and b["t"] in ("p", "list"):
                f = fotos[usadas]
                out.append({"t": "img", "src": f["src"], **dim(f["src"])})
                usadas += 1
                desde = i
        return out

    def foto(d):
        mid = REL.get("{}|{}|{}".format(d["portal"], d["tipo"], d["wp_id"]))
        if mid is None:
            return None
        return IMGS.get("{}|{}".format(d["portal"], mid))

    # Fotos rescatadas por p15: las fichas que no tenian foto destacada puesta
    # en WooCommerce pero si imagenes en la galeria del producto, que el
    # endpoint de core no expone.
    try:
        RESCATE = json.load(open(D / "fotos_rescatadas.json", encoding="utf-8"))
    except FileNotFoundError:
        RESCATE = {}

    for d in docs:
        f = foto(d)
        if f is None and d["slug"] in RESCATE:
            r = RESCATE[d["slug"]]
            f = {"src": r["src"], "alt": r.get("alt") or d["titulo"], "w": None, "h": None}
        d["foto"] = f
        # La foto destacada manda; las del cuerpo quedan como galeria.
        cuerpo = [BODY[u] for u in d["imagenes"] if u in BODY]
        vistos = {f["src"]} if f else set()
        d["cuerpo"] = [c for c in cuerpo if not (c["src"] in vistos or vistos.add(c["src"]))]
        d["galeria"] = ([f["src"]] if f else []) + [c["src"] for c in d["cuerpo"]]

    hc = Counter(d["hash"] for d in docs if d["hash"])
    for d in docs:
        d["dup"] = bool(d["hash"]) and hc[d["hash"]] > 1

    by_type = defaultdict(list)
    for d in docs:
        by_type[d["tipo"]].append(d)

    real_cat = {path_of(d["url_destino"]).strip("/"): d for d in by_type["product_cat"]}
    prods_por_cat = defaultdict(list)
    for p in by_type["product"]:
        prods_por_cat[p["cat"]].append(p)

    cats = []
    for ruta, (titulo, padre) in ARBOL.items():
        src = real_cat.get(ruta)
        hijos = [(r, v[0]) for r, v in ARBOL.items() if v[1] == ruta]
        desc_rutas = [r for r in ARBOL if r == ruta or r.startswith(ruta + "/")]
        todos = [p for r in desc_rutas for p in prods_por_cat.get(r, [])]
        for r in desc_rutas:
            todos += [p for p in by_type["product"]
                      if r in (p.get("cats_extra") or []) and p not in todos]
        _bl, _faq = contenido.gen_categoria(ruta, titulo, hijos, todos,
                                            ARBOL[padre][0] if padre else None)
        cats.append({
            "faq": _faq,
            "kind": "category", "path": "/" + ruta + "/", "slug": ruta.rsplit("/", 1)[-1],
            "route": ruta, "parent": ("/" + padre + "/") if padre else None,
            "title": titulo, "h1": titulo,
            "blocks": _bl,
            "children": ["/" + h[0] + "/" for h in hijos],
            "productCount": len(todos), "directCount": len(prods_por_cat.get(ruta, [])),
            "description": "{}: {} products in stock at Brazilian Lumber. Specs, sizes and pricing from our "
                           "Miami, Los Angeles and New Jersey yards.".format(titulo, len(todos)),
            # Solo vale una imagen ya descargada al propio portal. Las URLs
            # antiguas de los 3 dominios no resuelven desde aqui (Cloudflare),
            # asi que dejarlas puestas es garantizar una tarjeta rota.
            "image": next((BODY[u]["src"] for u in (src["imagenes"] if src else []) if u in BODY), None),
            "color": COLORES.get(ruta.rsplit("/", 1)[-1]) or COLORES.get(ruta.split("/")[0], "#6b4f3a"),
            "origins": [src["url_origen"]] if src else [],
            "modified": src["modificado"] if src else "2026-09-13",
        })

    products = []
    for d in by_type["product"]:
        a = d.get("attr") or {}
        blocks_gen = gen_producto(d)
        esp = ESPECIES.get(a.get("especie") or "")
        mrc = MARCAS.get(a.get("marca") or "")
        desc = re.sub(r"\s+", " ", d["excerpt"] or "").strip()
        if len(desc) < 60 or d["dup"]:
            if esp and a.get("medida"):
                desc = "{} in {}, {} actual. {:,} lbf Janka, {}. In stock in Miami, Los Angeles and New " \
                       "Jersey.".format(d["titulo"], esp[0], a["real"], esp[1], esp[4])
            elif esp:
                desc = "{} in {}. {:,} lbf Janka hardness, {} outdoors. Cut to order and shipped " \
                       "nationwide.".format(d["titulo"], esp[0], esp[1], esp[4])
            elif mrc:
                desc = "{} by {}, {} with a {}. In stock and shipped nationwide from three US " \
                       "yards.".format(d["titulo"], mrc[0], mrc[1], mrc[2])
            else:
                desc = "{} from Brazilian Lumber. In stock in Miami, Los Angeles and New Jersey, cut to order, " \
                       "shipped nationwide.".format(d["titulo"])
        products.append({
            "kind": "product", "path": path_of(d["url_destino"]), "slug": d["slug"],
            "title": d["titulo"], "h1": d["titulo"],
            "category": "/" + d["cat"] + "/", "categoryTitle": ARBOL[d["cat"]][0],
            # Categorias adicionales. No crean URL: el producto sigue viviendo
            # solo en /product/{slug}/, que es la regla de oro del estudio.
            "alsoIn": ["/" + c + "/" for c in d.get("cats_extra", []) if c in ARBOL],
            "attrs": a, "specs": specs_producto(a),
            "blocks": blocks_gen, "faq": d.get("faq", []),
            "description": desc[:280],
            "image": (d.get("foto") or {}).get("src"),
            "imageW": (d.get("foto") or {}).get("w"),
            "imageH": (d.get("foto") or {}).get("h"),
            "imageAlt": (d.get("foto") or {}).get("alt") or d["titulo"],
            "gallery": d.get("galeria", [])[:6],
            "color": COLORES.get(a.get("especie") or "", COLORES.get(d["cat"].split("/")[0], "#6b4f3a")),
            "clicks": d["clics"], "impressions": d["impresiones"],
            "modified": d["modificado"], "origins": [d["url_origen"]],
            "rewritten": bool(d["dup"]) or d["accion"] == "CONSERVAR-REESCRIBIR",
        })

    catid_by_wp = {}
    for c in by_type["categories"]:
        catid_by_wp.setdefault((c["portal"], c["wp_id"]), c)
    posts = []
    for d in by_type["posts"]:
        desc = re.sub(r"\s+", " ", d["excerpt"] or d["texto"])[:200].strip()
        cs = [catid_by_wp.get((d["portal"], i)) for i in (d.get("cat_ids") or [])]
        cs = [c for c in cs if c]
        posts.append({
            "kind": "post", "path": path_of(d["url_destino"]), "slug": d["slug"],
            "title": d["titulo"], "h1": d["titulo"],
            "blocks": intercalar(d["blocks"] or [{"t": "p", "text": d["texto"][:2000]}],
                                 d.get("cuerpo", [])[:6]),
            "description": (desc or d["titulo"]),
            "image": (d.get("foto") or {}).get("src"),
            "imageW": (d.get("foto") or {}).get("w"),
            "imageH": (d.get("foto") or {}).get("h"),
            "imageAlt": (d.get("foto") or {}).get("alt") or d["titulo"],
            "gallery": d.get("galeria", [])[:6],
            "cats": [path_of(c["url_destino"]) for c in cs],
            "catNames": [c["titulo"] for c in cs],
            "date": d["fecha"] or d["modificado"], "modified": d["modificado"],
            "words": d["palabras"], "clicks": d["clics"], "impressions": d["impresiones"],
            "origins": [d["url_origen"]], "color": "#5a4632",
            # Un articulo de 35 palabras no es un articulo. Sigue publicado para
            # no perder la URL, pero no entra en el indice ni en el sitemap.
            "noindex": (d["palabras"] or 0) < 120,
        })

    postcats = []
    for d in by_type["categories"]:
        p = path_of(d["url_destino"])
        mine = [x for x in posts if p in x["cats"]]
        postcats.append({
            "kind": "postcat", "path": p, "slug": d["slug"], "title": d["titulo"], "h1": d["titulo"],
            "blocks": contenido.gen_postcat(d["titulo"], mine),
            "description": "Guides and technical articles on {} from the Brazilian Lumber "
                           "team.".format(d["titulo"].lower()),
            "postCount": len(mine), "origins": [d["url_origen"]],
            # Un tema con uno o dos articulos es contenido pobre y canibaliza a
            # esos mismos articulos. Sigue navegable, pero fuera del indice.
            "noindex": len(mine) < 3,
            "modified": d["modificado"], "color": "#5a4632",
        })

    pages = []
    for d in by_type["pages"]:
        slug = d["slug"]
        if slug in JUNK:
            sub = "junk"
        elif slug in UTIL:
            sub = "utility"
        elif slug in CIUDADES or re.search(r"^ipe-decking-|-la$|-fl$|-az$|-ca$|-nj$", slug):
            sub = "location"
        elif re.search(r"landing|wholesale|hot-deals|sale-items|download|brochure|trend-guide|request|estimate|"
                       r"calculator|samples|quote", slug):
            sub = "landing"
        else:
            sub = "company"
        desc = re.sub(r"\s+", " ", d["excerpt"] or d["texto"])[:200].strip()
        title = d["titulo"] or titlecase(slug.replace("-", " "))
        if len(desc) < 60:
            # Algunas paginas llegaron sin nada de texto. Una meta description
            # vacia es peor que una generada: se genera con lo que sabemos.
            desc = pick(slug, [
                "{} at Brazilian Lumber. Tropical hardwood, composite decking, cladding and lumber, "
                "in stock in Miami, Los Angeles and New Jersey.".format(title),
                "{} - Brazilian Lumber. One catalog across three yards, cut to order and shipped "
                "nationwide.".format(title),
                "{} from Brazilian Lumber, supplier of tropical hardwood decking and composite "
                "decking since 2006.".format(title),
            ])
        if sub == "location":
            bloques = contenido_paginas.gen_ubicacion(
                title, [ESPECIES[e][0] for e in ("ipe", "cumaru", "garapa") if e in ESPECIES])
            bloques = gen_pagina(d) + bloques if d["blocks"] else bloques
        elif sub in ("junk", "utility"):
            bloques = gen_pagina(d)
        else:
            bloques = contenido_paginas.gen_pagina(slug, sub, gen_pagina(d) if d["blocks"] else [])
        pages.append({
            "kind": "page", "sub": sub, "path": path_of(d["url_destino"]), "slug": slug,
            "title": title, "h1": title,
            "blocks": intercalar(bloques, d.get("cuerpo", [])[:5]),
            "description": (desc or "{} - Brazilian Lumber.".format(title)),
            "image": (d.get("foto") or {}).get("src"),
            "imageW": (d.get("foto") or {}).get("w"),
            "imageH": (d.get("foto") or {}).get("h"),
            "imageAlt": (d.get("foto") or {}).get("alt") or title,
            "gallery": d.get("galeria", [])[:6],
            "words": d["palabras"], "clicks": d["clics"], "impressions": d["impresiones"],
            "modified": d["modificado"], "origins": [d["url_origen"]],
            "noindex": sub in ("junk", "utility") or slug in CADUCADAS, "color": "#4c5a66",
        })

    # ---- portada de las categorias y de los temas del blog
    #
    # WordPress no guarda imagen para estas taxonomias, asi que hay que elegirla.
    # Y no vale cualquiera: un recorte de tablon sobre fondo blanco, estirado a
    # sangre en una tarjeta, se ve como un error. Se prefiere una foto de
    # ambiente, medida por p9 (poco blanco y con color), y solo si no hay
    # ninguna se cae al recorte de producto.
    try:
        ST = json.load(open(D / "imgstats.json", encoding="utf-8"))
    except FileNotFoundError:
        ST = {}

    def ambiente(src):
        v = ST.get((src or "").rsplit("/", 1)[-1].replace(".webp", ""))
        if not v:
            return 0.0
        # Puntua: penaliza el blanco, premia el color y el formato apaisado.
        horizontal = 1.0 if v["w"] >= v["h"] else 0.55
        return (1 - v["white"]) * min(v["sat"] / 30, 1.4) * horizontal

    def portada(candidatas, titulo):
        """candidatas: lista de (src, clics)."""
        vistas, pool = set(), []
        for src, clics in candidatas:
            if src and src not in vistas:
                vistas.add(src)
                pool.append((src, clics))
        if not pool:
            return None
        mejor = max(pool, key=lambda x: (ambiente(x[0]), x[1]))
        return mejor[0] if ambiente(mejor[0]) > 0.30 else pool[0][0]

    # Palabra clave de cada rama, para poder tirar tambien de las fotos de los
    # articulos: los reportajes de Ipe o de Cumaru tienen las mejores imagenes.
    for c in cats:
        clave = c["route"].rsplit("/", 1)[-1].replace("-", " ").lower()
        dentro = [p for p in products
                  if p["category"] == c["path"] or p["category"].startswith(c["path"])]
        cand = [(p["image"], p["clicks"] or 0) for p in dentro if p["image"]]
        cand += [(g, (p["clicks"] or 0) * 0.5) for p in dentro for g in p.get("gallery", [])[:3]]
        # fotos de articulos que hablan de esta rama
        for po in posts:
            if clave and clave in po["title"].lower():
                if po["image"]:
                    cand.append((po["image"], (po["clicks"] or 0) + 5))
                for b in po["blocks"]:
                    if b["t"] == "img":
                        cand.append((b["src"], (po["clicks"] or 0) + 3))
        elegida = portada(cand, c["title"])
        if elegida:
            c["image"] = elegida
            c["imageAlt"] = c["title"]

    for pc in postcats:
        dentro = [p for p in posts if pc["path"] in p["cats"]]
        cand = [(p["image"], p["clicks"] or 0) for p in dentro if p["image"]]
        cand += [(b["src"], (p["clicks"] or 0) * 0.5) for p in dentro for b in p["blocks"] if b["t"] == "img"]
        elegida = portada(cand, pc["title"])
        if elegida:
            pc["image"] = elegida
            pc["imageAlt"] = pc["title"]

    absorbed_home = []

    # ---- las portadas
    #
    # La raiz de cada dominio va a la raiz del portal unificado. Ni la portada
    # de Miami se convierte en subpagina, ni una pagina de pruebas se convierte
    # en portada.
    RAICES = {"https://brazilianlumber.com/", "https://brazilianlumber.com",
              "https://brazilianlumberlosangeles.com/", "https://brazilianlumberlosangeles.com",
              "https://brazilianlumbernewyork.com/", "https://brazilianlumbernewyork.com"}

    portada_real = None
    for pg in pages:
        if any(o in RAICES for o in (pg.get("origins") or [])):
            if pg["portal_origen"] == "MIA" if "portal_origen" in pg else True:
                if portada_real is None or (pg.get("clicks") or 0) > (portada_real.get("clicks") or 0):
                    portada_real = pg

    # Nada que no sea la portada puede ocupar la raiz.
    for pg in pages:
        if pg["path"] == "/" and pg is not portada_real:
            pg["path"] = "/" + pg["slug"] + "/"
            pg["noindex"] = True
            pg["sub"] = "junk"

    if portada_real is not None:
        # Su contenido es el de la portada, asi que se absorbe en la raiz: no
        # debe existir ademas bajo su slug, seria la misma pagina dos veces.
        absorbed_home.append({"path": portada_real["path"], "from": portada_real["origins"],
                              "into": "/"})
        pages = [x for x in pages if x is not portada_real]
        print("portada: {} absorbida en la raiz ({} clics)".format(
            portada_real["path"], int(portada_real.get("clicks") or 0)))

    # ---- fichas practicamente identicas: se consolidan, no se reescriben
    #
    # La auditoria de contenido duplicado destapo dos cosas distintas con la
    # misma solucion. Por un lado, productos duplicados en WordPress
    # (armadillo-pvc-decking y armadillo-pvc-decking-2). Por otro, variantes de
    # color del mismo articulo (Origens Okan, Tauari, Carvalho, Teca Bege), que
    # son un producto con opciones, no cuatro productos.
    #
    # Inventarles textos distintos seria maquillar el problema. Lo correcto es
    # que una pieza de contenido tenga una URL, que es la regla del estudio.
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as _np
        import re as _re

        def _plano(d):
            out = []
            for b in d["blocks"]:
                if b["t"] == "list":
                    out.append(" ".join(b["items"]))
                elif b["t"] == "table":
                    out.append(" ".join(str(c) for r in b["rows"] for c in r))
                elif b["t"] != "img":
                    out.append(b.get("text", ""))
            t = " ".join(out).lower()
            return _re.sub(r"[^a-z0-9 ]", " ", t)

        # Se consolidan productos Y paginas: la auditoria encontro la misma
        # pagina de ciudad publicada en dos rutas distintas.
        # Las paginas con destino explicito en CONSOLIDAR no entran: su destino
        # ya esta decidido por la taxonomia y no lo decide un parecido de texto.
        fusionables = products + [x for x in pages
                                  if x.get('sub') != 'junk' and x['slug'] not in CONSOLIDAR]
        textos = [_plano(x) for x in fusionables]
        vec = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        X = vec.fit_transform(textos)
        sim = (X @ X.T).toarray()
        _np.fill_diagonal(sim, 0)

        UMBRAL = 0.97
        padre_de = {}

        # Antes del umbral: dos fichas con el MISMO titulo y la misma medida no
        # son parecidas, son la misma. Se fusionan aunque el texto difiera algo.
        _por_titulo = {}
        for x in fusionables:
            if x["kind"] != "product":
                continue
            clave = (x["title"].strip().lower(),
                     (x.get("attrs") or {}).get("medida"),
                     (x.get("attrs") or {}).get("coleccion"),
                     (x.get("attrs") or {}).get("largo"))
            _por_titulo.setdefault(clave, []).append(x)
        for clave, grupo in _por_titulo.items():
            if len(grupo) < 2:
                continue
            grupo.sort(key=lambda x: (-(x["clicks"] or 0), len(x["slug"])))
            raiz = grupo[0]["path"]
            for x in grupo[1:]:
                padre_de.setdefault(x["path"], raiz)
        for i in range(len(fusionables)):
            for j in _np.where(sim[i] >= UMBRAL)[0]:
                if j <= i:
                    continue
                a, b = fusionables[i], fusionables[j]
                if a['kind'] != b['kind']:
                    continue
                # gana el que tiene mas demanda medida; a igualdad, el slug mas corto
                ganador, perdedor = ((a, b) if (a["clicks"] or 0, -len(a["slug"])) >=
                                     (b["clicks"] or 0, -len(b["slug"])) else (b, a))
                raiz = padre_de.get(ganador["path"], ganador["path"])
                if perdedor["path"] != raiz:
                    padre_de.setdefault(perdedor["path"], raiz)

        fusionadas = []
        if padre_de:
            vivos, vivas_pag = [], []
            por_path = {x['path']: x for x in fusionables}
            for x in fusionables:
                destino = padre_de.get(x["path"])
                if destino and destino in por_path and destino != x["path"]:
                    fusionadas.append({"path": x["path"], "from": x["origins"], "into": destino})
                    g = por_path[destino]
                    g["clicks"] = (g["clicks"] or 0) + (x["clicks"] or 0)
                    if not g["image"] and x["image"]:
                        g["image"] = x["image"]
                        g["imageAlt"] = g["title"]
                else:
                    (vivos if x['kind'] == 'product' else vivas_pag).append(x)
            products = vivos
            # Se filtra la lista ORIGINAL en vez de reconstruirla: las paginas
            # que quedaron fuera de la fusion (las de prueba y las que tienen
            # destino explicito en CONSOLIDAR) tienen que seguir estando, o
            # desaparecen sin dejar redireccion y su URL antigua muere en 404.
            _fusionadas = {f["path"] for f in fusionadas}
            pages = [x for x in pages if x["path"] not in _fusionadas]
            absorbed_prod = fusionadas
            print("fichas consolidadas por contenido identico: {}".format(len(fusionadas)))
        else:
            absorbed_prod = []
    except Exception as _e:
        print("aviso: no se pudo consolidar por contenido ({})".format(type(_e).__name__))
        absorbed_prod = []

    # Colisiones: una pagina legacy que ocupa la misma URL que un nodo de la taxonomia.
    # La categoria es la duena de la URL, asi que la pagina se absorbe dentro de ella.
    cat_by_path = {c["path"]: c for c in cats}
    absorbed = list(absorbed_prod) + list(absorbed_home)
    keep = []
    for pg in pages:
        destino = CONSOLIDAR.get(pg["slug"])
        if destino:
            # Duplica una categoria o una seccion: se consolida y se documenta.
            absorbed.append({"path": pg["path"], "from": pg["origins"],
                             "into": "/" + destino + "/"})
            c = cat_by_path.get("/" + destino + "/")
            if c and not c["image"] and pg["image"]:
                c["image"] = pg["image"]
            continue
        c = cat_by_path.get(pg["path"])
        if c is None:
            keep.append(pg)
            continue
        extra = [b for b in pg["blocks"] if b["t"] == "p" and len(b.get("text", "")) > 90][:3]
        c["blocks"] = c["blocks"][:1] + extra + c["blocks"][1:]
        c["origins"] = c["origins"] + pg["origins"]
        if not c["image"] and pg["image"]:
            c["image"] = pg["image"]
        absorbed.append({"path": pg["path"], "from": pg["origins"], "into": c["path"]})
    pages = keep

    redirects = [{"from": r["url_origen"], "to": path_of(r["url_destino"]),
                  "portal": r["portal"], "type": r["tipo"]}
                 for r in raw if r["accion"] == "CONSOLIDAR-301" and r["url_destino"]]

    # Resolucion de cadenas. Una consolidacion puede apuntar a algo que a su vez
    # se consolido despues; sin esto queda un 301 hacia un 404, que es peor que
    # no redirigir. Se recorre hasta el destino final.
    vivos = {d["path"] for d in (cats + products + posts + postcats + pages)}
    vivos |= {"/", "/shop/", "/guides/", "/search/", "/redirect-map/"}
    salto = {a["path"]: a["into"] for a in absorbed if a["path"] != a["into"]}

    def final(p):
        visto = set()
        while p in salto and p not in visto:
            visto.add(p)
            p = salto[p]
        return p

    for a in absorbed:
        a["into"] = final(a["into"])
    for r in redirects:
        r["to"] = final(r["to"])

    huerfanas = [r for r in redirects if r["to"] not in vivos]
    if huerfanas:
        print("AVISO: {} redirecciones sin destino vivo, se reapuntan".format(len(huerfanas)))
        for r in huerfanas:
            # Ultimo recurso: la rama padre de la ruta, y si no, el catalogo.
            partes = [x for x in r["to"].strip("/").split("/") if x]
            destino = "/shop/"
            for n in range(len(partes) - 1, 0, -1):
                cand = "/" + "/".join(partes[:n]) + "/"
                if cand in vivos:
                    destino = cand
                    break
            r["to"] = destino

    # Regla 14: dos paginas con el mismo titulo son la misma pagina. Se
    # consolidan igual que se hizo con los productos. Gana la que mas clics
    # tiene, y a igualdad, la de slug mas corto.
    from collections import defaultdict as _dd
    _t = _dd(list)
    for pg in pages:
        if pg.get("sub") == "junk" or pg.get("noindex"):
            continue
        _t[pg["title"].strip().lower()].append(pg)
    _fus = []
    for titulo, grupo in _t.items():
        if len(grupo) < 2:
            continue
        grupo.sort(key=lambda x: (-(x.get("clicks") or 0), len(x["slug"])))
        raiz = grupo[0]
        for x in grupo[1:]:
            _fus.append({"path": x["path"], "from": x["origins"], "into": raiz["path"]})
            raiz["clicks"] = (raiz.get("clicks") or 0) + (x.get("clicks") or 0)
            if not raiz.get("image") and x.get("image"):
                raiz["image"] = x["image"]
    if _fus:
        _ids = {f["path"] for f in _fus}
        pages = [x for x in pages if x["path"] not in _ids]
        absorbed.extend(_fus)
        print("paginas con el mismo titulo, consolidadas: {}".format(len(_fus)))

    # Los temas del blog con menos de 3 articulos quedan en noindex. Mandar su
    # URL antigua ahi es tirar el enlace: el usuario llega a algo que Google no
    # va a mostrar. Su trafico va al indice de guias, que si se indexa.
    _pc_noindex = {c["path"] for c in postcats if c.get("noindex")}
    _ya = {r["from"].rstrip("/") for r in redirects}
    _añadidas = 0
    for c in postcats:
        if not c.get("noindex"):
            continue
        for origen in (c.get("origins") or []):
            if origen.rstrip("/") not in _ya:
                redirects.append({"from": origen, "to": "/guides/",
                                  "portal": "MIA", "type": "categories"})
                _añadidas += 1
    if _añadidas:
        print("temas del blog en noindex, su URL antigua va a /guides/: {}".format(_añadidas))

    # Regla 5: nada redirige a una pagina en noindex. Si el destino no se va a
    # indexar, se sube a la seccion que si lo esta.
    _noindex = {d["path"] for d in (posts + postcats + pages)
                if d.get("noindex") or d.get("sub") == "junk"}
    _vivos_idx = {d["path"] for d in (cats + products + posts + postcats + pages)
                  if not (d.get("noindex") or d.get("sub") == "junk")}
    _vivos_idx |= {"/", "/shop/", "/guides/"}

    def _subir(ruta):
        partes = [x for x in ruta.strip("/").split("/") if x]
        for n in range(len(partes) - 1, 0, -1):
            cand = "/" + "/".join(partes[:n]) + "/"
            if cand in _vivos_idx:
                return cand
        return "/shop/" if ruta.startswith("/product") else "/"

    # Las paginas de prueba y de "gracias" no son destino de nada: quien llegue
    # ahi desde una URL antigua acaba en una pagina vacia. Van a la portada.
    _basura = {d["path"] for d in pages if d.get("sub") == "junk"}
    for r in redirects:
        if r["to"] in _basura:
            r["to"] = "/"
    # Y las que no estan en el mapa porque el estudio las daba por conservadas,
    # pero su destino resulto ser una de esas paginas de prueba.
    _ya2 = {r["from"].rstrip("/") for r in redirects}
    for rr in raw:
        dest = path_of(rr["url_destino"]) if rr["url_destino"] else None
        if dest in _basura and rr["url_origen"].rstrip("/") not in _ya2:
            redirects.append({"from": rr["url_origen"], "to": "/",
                              "portal": rr["portal"], "type": rr["tipo"]})
    for a in absorbed:
        if a["into"] in _basura:
            a["into"] = "/"

    _subidas = 0
    for r in redirects:
        if r["to"] in _noindex:
            r["to"] = _subir(r["to"])
            _subidas += 1
    for a in absorbed:
        if a["into"] in _noindex:
            a["into"] = _subir(a["into"])
    if _subidas:
        print("redirecciones que apuntaban a noindex, reapuntadas: {}".format(_subidas))

    # ---- titulos de zona segun la demanda real
    #
    # Investigacion con KeywordTool sobre 82 ciudades y 12 formas de nombrar lo
    # mismo. El resultado, sumando todas las ciudades:
    #     lumber yard {ciudad}   8.590 busquedas/mes
    #     lumber {ciudad}        7.230
    #     ipe decking {ciudad}     140   <-- como se llamaban hasta ahora
    # Se excluyen "deck builder" y "deck contractor" pese a tener volumen: son
    # intencion de servicio y Brazilian Lumber suministra material.
    try:
        ZONAS_KW = json.load(open(D / "zonas_renombradas.json", encoding="utf-8"))
    except FileNotFoundError:
        ZONAS_KW = {}

    # ---- paginas de zona que faltaban
    #
    # Cada ciudad con demanda medida tiene su URL bajo /locations/. Sin esto su
    # trafico caia en el indice generico y se perdia la intencion local, que es
    # justo lo que busca quien escribe "ipe decking santa monica".
    _ya_loc = {pg["slug"] for pg in pages}
    _gsc_por_slug = {}
    try:
        _g = json.load(open(D / "gsc.json", encoding="utf-8"))
        for _p, _d in _g["portales"].items():
            for _u, _m in _d["paginas"].items():
                _sl = _u.rstrip("/").split("/")[-1]
                _acc = _gsc_por_slug.setdefault(_sl, {"c": 0, "i": 0})
                _acc["c"] += _m.get("clicks", 0)
                _acc["i"] += _m.get("impressions", 0)
    except FileNotFoundError:
        pass

    _nuevas = 0
    for _slug, _info in _ciu.CIUDADES.items():
        if _slug in _ya_loc:
            continue
        _m = _gsc_por_slug.get(_slug, {"c": 0, "i": 0})
        # Se crea si la investigacion de palabras clave la justifica. Las
        # impresiones de Search Console no bastan: vienen de consultas genericas
        # donde la pagina sale de refilon, no de busquedas de esa ciudad.
        if _slug not in ZONAS_KW:
            continue
        _nombre, _estado, _area, _terreno, _almacen = _info
        _clave, _texto, _especies = _ciu.contexto(_terreno)
        _kw = ZONAS_KW.get(_slug)
        _h1 = _kw["h1"] if _kw else "Lumber Yard Serving {}".format(_nombre)
        _intencion = _kw["intencion"] if _kw else "lumber yard"
        _bl = [
            {"t": "p", "text":
                "Brazilian Lumber is the {} serving {}, {}. Hardwood and composite decking, "
                "cladding, fencing and dimensional lumber, held in stock and cut to length "
                "before it ships from our {} yard.".format(
                    _intencion, _nombre, _area, _almacen)},
            {"t": "h2", "text": "What {} does to a deck".format(_clave)},
            {"t": "p", "text": _texto},
            {"t": "h2", "text": "What gets specified in {}".format(_nombre)},
            {"t": "p", "text":
                "The three materials that come up most in {} are {}. If you are choosing "
                "between them, ask for samples first: screen color is not wood color, and grain "
                "reads completely differently at full size.".format(
                    _nombre, contenido.unir(_especies))},
            {"t": "h2", "text": "Delivery to {}".format(_nombre)},
            {"t": "list", "items": [
                "Shipped from the {} yard, the closest of our three.".format(_almacen),
                "Cut to length in our own mill, so you are not paying freight on offcuts.",
                "Lead time and freight quoted together with the material, never added later.",
                "{} sits in {}; tell us the delivery access and we size the truck to "
                "it.".format(_nombre, _area),
            ]},
        ]
        pages.append({
            "kind": "page", "sub": "location", "path": "/locations/{}/".format(_slug),
            "slug": _slug,
            "title": "{} | {}".format(_h1, _estado),
            "h1": _h1,
            "blocks": _bl,
            "description": ("{} serving {}, {}. Tropical hardwood and composite decking, "
                            "cladding and dimensional lumber in stock, cut to length and "
                            "shipped from our {} yard.".format(
                                _h1.split(" in ")[0], _nombre, _area, _almacen)),
            "image": None, "gallery": [], "words": 0,
            "clicks": _m["c"], "impressions": _m["i"],
            "modified": "2026-09-14", "origins": [], "noindex": False, "color": "#4c5a66",
        })
        _nuevas += 1
    if _nuevas:
        print("paginas de zona creadas con contenido local propio: {}".format(_nuevas))

    # Las paginas de zona que ya existian tambien se renombran: se llamaban
    # "IPE decking Los Angeles", que es el termino con menos demanda de todos.
    _renombradas = 0
    for pg in pages:
        if pg.get("sub") != "location":
            continue
        _kw = ZONAS_KW.get(pg["slug"])
        if not _kw or pg["h1"] == _kw["h1"]:
            continue
        pg["h1"] = _kw["h1"]
        pg["title"] = _kw["h1"]
        _renombradas += 1
    if _renombradas:
        print("paginas de zona renombradas por su termino real: {}".format(_renombradas))

    # Paginas de ciudad: ninguna redirige a otra ciudad.
    #
    # El mapa heredado mandaba 134 paginas de ciudad a /altadena/, que tiene
    # cero clics. Quien busca tarima en Santa Monica no quiere Altadena.
    _por_slug = {}
    for pg in pages:
        # Si hay varias con el mismo slug, gana la de /locations/, que es la
        # ruta canonica de una pagina de zona.
        if pg["slug"] not in _por_slug or pg["path"].startswith("/locations/"):
            _por_slug[pg["slug"]] = pg["path"]
    _indice_zonas = _por_slug.get("areas-we-serve", "/")

    _ciudades = 0
    for r in redirects:
        destino = r["to"].strip("/").split("/")[-1]
        origen_slug = r["from"].rstrip("/").split("/")[-1]
        # Solo actua cuando el destino es una pagina de ciudad distinta del origen.
        if destino and destino != origen_slug and r["to"] in {v for v in _por_slug.values()}:
            pg_destino = next((x for x in pages if x["path"] == r["to"]), None)
            if pg_destino is not None and pg_destino.get("sub") == "location":
                propia = _por_slug.get(origen_slug)
                nuevo = propia if propia else _indice_zonas
                if nuevo != r["to"]:
                    r["to"] = nuevo
                    _ciudades += 1
    if _ciudades:
        print("paginas de ciudad reapuntadas (ya no van todas a una sola): {}".format(_ciudades))

    # La raiz de cada dominio, a la raiz. Esto va despues de construir la lista
    # y antes del encadenado, para que no lo pise ningun salto posterior.
    for r in redirects:
        if r["from"].rstrip("/") + "/" in RAICES:
            r["to"] = "/"
    for dom in ("https://brazilianlumber.com/", "https://brazilianlumberlosangeles.com/",
                "https://brazilianlumbernewyork.com/"):
        if not any(x["from"].rstrip("/") == dom.rstrip("/") for x in redirects):
            redirects.append({"from": dom, "to": "/", "portal": "MIA", "type": "pages"})

    # Encadenado de redirecciones. Si una pagina se ha consolidado dentro de una
    # categoria, todo lo que apuntaba a ella tiene que apuntar ahora al destino
    # final. Una redireccion a una URL que ya no existe es un 301 hacia un 404,
    # que es peor que no redirigir: el control de calidad del estudio ya detecto
    # 234 casos asi en Los Angeles y New Jersey.
    salto = {a["path"]: a["into"] for a in absorbed if a["path"] != a["into"]}
    for r in redirects:
        visto = set()
        while r["to"] in salto and r["to"] not in visto:
            visto.add(r["to"])
            r["to"] = salto[r["to"]]

    # Las propias paginas consolidadas entran en el mapa: su URL antigua tiene
    # que llevar a la categoria que se quedo con el contenido.
    existentes = {r["from"].rstrip("/") for r in redirects}
    for a in absorbed:
        if a["path"] == a["into"]:
            continue
        for origen in a["from"]:
            if origen.rstrip("/") not in existentes:
                redirects.append({"from": origen, "to": a["into"],
                                  "portal": "MIA", "type": "pages"})
    noindex = [{"url": r["url_origen"], "type": r["tipo"], "reason": r["motivo"]}
               for r in raw if r["accion"] == "NOINDEX"]

    # ---- menu unificado
    by_path = {c["path"]: c for c in cats}

    def rama(p):
        c = by_path[p]
        return {"path": p, "title": c["title"], "count": c["productCount"],
                "children": [rama(h) for h in c["children"]]}

    shop = [rama(c["path"]) for c in cats if c["parent"] is None]
    page_by_slug = {p["slug"]: p for p in pages}

    def link(slug, label=None):
        p = page_by_slug.get(slug)
        return {"path": p["path"], "title": label or p["title"]} if p else None

    company = [x for x in [link("brazilian-lumber", "About Us"), link("contact", "Contact"),
                           link("hardwood-decking-faqs", "FAQ"), link("sustainability", "Sustainability"),
                           link("in-house-custom-milling", "Custom Milling"),
                           link("estimate-take-off-design-services", "Estimating and Take-Offs"),
                           link("projects", "Projects"), link("press-media", "Press and Media"),
                           link("wholesale", "Wholesale"), link("request-samples", "Request Samples")] if x]
    locs = sorted([p for p in pages if p["sub"] == "location"],
                  key=lambda p: (-(p["clicks"] or 0), p["title"]))
    nav = {
        "shop": shop,
        "guides": {"path": "/guides/", "title": "Guides",
                   "cats": sorted([{"path": c["path"], "title": c["title"], "count": c["postCount"]}
                                   for c in postcats if c["postCount"] > 0],
                                  key=lambda c: -c["count"])},
        "locations": {"path": "/areas-we-serve/", "title": "Areas We Serve",
                      "items": [{"path": p["path"], "title": p["title"]} for p in locs[:40]]},
        "company": company,
    }

    site = {
        "generated": "2026-09-13",
        "host": HOST,
        "nav": nav, "absorbed": absorbed,
        "categories": cats, "products": products, "posts": posts,
        "postcats": postcats, "pages": pages,
        "redirects": redirects, "noindex": noindex,
        "stats": {
            "crawled": len(raw), "final": len(docs),
            "categories": len(cats), "products": len(products), "posts": len(posts),
            "postcats": len(postcats), "pages": len(pages),
            "redirects": len(redirects), "noindexed": len(noindex),
            "rewritten": sum(1 for p in products if p["rewritten"]),
        },
    }
    json.dump(site, open(D / "site.json", "w", encoding="utf-8"), ensure_ascii=False)
    total = len(cats) + len(products) + len(posts) + len(postcats) + len(pages)
    print(json.dumps(site["stats"], indent=1))
    print("URLs publicas del portal:", total)
    paths = [x["path"] for k in ("categories", "products", "posts", "postcats", "pages") for x in site[k]]
    dup = [k for k, v in Counter(paths).items() if v > 1]
    print("paths duplicados:", len(dup), dup[:5])


if __name__ == "__main__":
    main()
