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


JUNK = {"hometest", "carousel-home", "thank-you-page", "cont-form-example", "test-form-flowsly",
        "home-test-2025", "blog-example", "thank-you-review", "thank-you-ibs", "thank-you", "demo-home"}

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

    orig = [b for b in d["blocks"] if b["t"] == "p" and len(b.get("text", "")) > 80]
    if orig and not d.get("dup"):
        for b in orig[:3]:
            bl.append(b)

    name = esp[0] if esp else (mrc[0] if mrc else t)
    bl.append({"t": "h2", "text": pick(slug + "w", [
        "Why builders specify {}".format(name),
        "What you get with {}".format(name),
        "Why this board is specified",
    ])})
    items = []
    if esp:
        items.append("Janka hardness of {:,} lbf, which is what keeps furniture legs and heel marks from "
                     "denting the surface.".format(esp[1]))
        items.append("Natural durability rated at {}, with no pressure treatment and no chemicals added.".format(esp[4]))
        items.append("Color: {}. Left unfinished it weathers to a silver gray; oiled once a year it holds its "
                     "original tone.".format(esp[3]))
        items.append(esp[5][0].upper() + esp[5][1:] + ".")
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
        cats.append({
            "kind": "category", "path": "/" + ruta + "/", "slug": ruta.rsplit("/", 1)[-1],
            "route": ruta, "parent": ("/" + padre + "/") if padre else None,
            "title": titulo, "h1": titulo,
            "blocks": gen_categoria(ruta, titulo, hijos, todos),
            "children": ["/" + h[0] + "/" for h in hijos],
            "productCount": len(todos), "directCount": len(prods_por_cat.get(ruta, [])),
            "description": "{}: {} products in stock at Brazilian Lumber. Specs, sizes and pricing from our "
                           "Miami, Los Angeles and New Jersey yards.".format(titulo, len(todos)),
            "image": (src["imagenes"][0] if src and src["imagenes"] else None),
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
            "attrs": a, "specs": specs_producto(a),
            "blocks": blocks_gen, "faq": d.get("faq", []),
            "description": desc[:280],
            "image": d["imagenes"][0] if d["imagenes"] else None,
            "gallery": d["imagenes"][:6],
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
            "blocks": d["blocks"] or [{"t": "p", "text": d["texto"][:2000]}],
            "description": (desc or d["titulo"]),
            "image": d["imagenes"][0] if d["imagenes"] else None,
            "gallery": d["imagenes"][:6],
            "cats": [path_of(c["url_destino"]) for c in cs],
            "catNames": [c["titulo"] for c in cs],
            "date": d["fecha"] or d["modificado"], "modified": d["modificado"],
            "words": d["palabras"], "clicks": d["clics"], "impressions": d["impresiones"],
            "origins": [d["url_origen"]], "color": "#5a4632",
        })

    postcats = []
    for d in by_type["categories"]:
        p = path_of(d["url_destino"])
        mine = [x for x in posts if p in x["cats"]]
        postcats.append({
            "kind": "postcat", "path": p, "slug": d["slug"], "title": d["titulo"], "h1": d["titulo"],
            "blocks": [{"t": "p", "text": "Every guide we have published on {}. {} article{} written by the "
                                          "Brazilian Lumber team from what we see in the yard and on "
                                          "jobsites.".format(d["titulo"].lower(), len(mine),
                                                             "s" if len(mine) != 1 else "")}],
            "description": "Guides and technical articles on {} from the Brazilian Lumber "
                           "team.".format(d["titulo"].lower()),
            "postCount": len(mine), "origins": [d["url_origen"]],
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
        pages.append({
            "kind": "page", "sub": sub, "path": path_of(d["url_destino"]), "slug": slug,
            "title": title, "h1": title,
            "blocks": gen_pagina(d),
            "description": (desc or "{} - Brazilian Lumber.".format(title)),
            "image": d["imagenes"][0] if d["imagenes"] else None,
            "gallery": d["imagenes"][:6],
            "words": d["palabras"], "clicks": d["clics"], "impressions": d["impresiones"],
            "modified": d["modificado"], "origins": [d["url_origen"]],
            "noindex": sub in ("junk", "utility"), "color": "#4c5a66",
        })

    # Colisiones: una pagina legacy que ocupa la misma URL que un nodo de la taxonomia.
    # La categoria es la duena de la URL, asi que la pagina se absorbe dentro de ella.
    cat_by_path = {c["path"]: c for c in cats}
    absorbed = []
    keep = []
    for pg in pages:
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
