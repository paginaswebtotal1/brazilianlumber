# -*- coding: utf-8 -*-
"""p25 - Enlazado interno: que ninguna pagina con demanda quede huerfana.

La auditoria contra el sitio encontro **115 paginas sin un solo enlace
entrante**, y no son paginas menores: entre ellas estan un articulo con 768
clics, la calculadora, la pagina de contacto y /ceiling-soffit/, que tiene
18.100 busquedas/mes medidas. Google solo llega a ellas por el sitemap, y la
autoridad del dominio no les llega en absoluto.

Tres arreglos, todos a partir de datos que ya estan en el dataset:

  1. ENLACE POR ENTIDAD. Cuando el texto de una pagina nombra una especie, una
     marca o una categoria que tiene pagina propia, la primera mencion pasa a
     ser un enlace. Es el enlace que mas vale: contextual y con el termino
     exacto como ancla.

  2. BLOQUE DE RELACIONADOS. Cada guia apunta a la categoria de la que habla,
     cada landing de zona a su ciudad y a su producto, y cada categoria a las
     guias que hablan de ella. La relacion no se inventa: sale de la taxonomia
     y de los temas del blog que ya estaban asignados.

  3. LAS UTILES, EN LA NAVEGACION. La calculadora, los precios de mayorista,
     las especificaciones y la rama de techos existen, tienen trafico y no
     estaban enlazadas desde ningun sitio.

Se ejecuta DESPUES de p24_geo.py y ANTES de p4_export.py.
"""
import json, re, sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p22_demanda as DEM
from kb import ESPECIES, MARCAS

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"

P = lambda t: {"t": "p", "text": t}
H2 = lambda t: {"t": "h2", "text": t}


def main():
    site = json.load(open(D / "site.json", encoding="utf-8"))
    FIN = DEM.FIN
    COLL = ("categories", "products", "posts", "postcats", "pages")
    docs = [d for c in COLL for d in site[c]]
    por_path = {d["path"]: d for d in docs}
    n = Counter()

    # ------------------------------------------------------------------
    # 1. Diccionario de entidades: termino -> pagina que lo sirve
    # ------------------------------------------------------------------
    # Solo entra lo que tiene pagina propia y nombre sin ambiguedad. 'Wood' o
    # 'Decking' se quedan fuera a proposito: enlazarlo todo no es enlazar nada.
    ENT = {}

    def registra(termino, path, peso):
        t = DEM.norm(termino)
        if len(t) < 4 or path not in por_path: return
        if t in ENT and ENT[t][1] >= peso: return
        ENT[t] = (path, peso)

    for c in site["categories"]:
        slug = c["slug"]
        if slug in ESPECIES:
            registra(ESPECIES[slug][0], c["path"], 3)
            registra(ESPECIES[slug][0] + " decking", c["path"], 4)
        if slug in MARCAS:
            registra(MARCAS[slug][0], c["path"], 3)
            registra(MARCAS[slug][0] + " decking", c["path"], 4)
        if len(c["title"].split()) >= 2:
            registra(c["title"], c["path"], 2)
    # nombres comerciales: son justo los que el cliente escribe
    for c in site["categories"] + site["pages"]:
        for alias in (c.get("alsoKnownAs") or []):
            registra(alias, c["path"], 5)

    # nada de autoenlaces ni de terminos que son el propio titulo de la pagina
    ORDEN = sorted(ENT, key=lambda t: -len(t))

    # ------------------------------------------------------------------
    # 2. Enlace por entidad dentro del texto
    # ------------------------------------------------------------------
    for doc in docs:
        propio = {DEM.norm(doc["title"]), DEM.norm(doc.get("h1") or "")}
        usados = set()
        for b in doc.get("blocks") or []:
            if b.get("t") not in ("p", "list") or b.get("refs"): continue
            texto = b.get("text") or " ".join(b.get("items") or [])
            bajo = DEM.norm(texto)
            refs = []
            for t in ORDEN:
                if len(refs) >= 3: break
                path, _ = ENT[t]
                if path == doc["path"] or t in propio or t in usados: continue
                if re.search(r"\b" + re.escape(t) + r"\b", bajo):
                    refs.append({"term": t, "path": path})
                    usados.add(t)
            if refs:
                b["refs"] = refs
                n["enlace por entidad"] += len(refs)

    # ------------------------------------------------------------------
    # 3. Bloque de relacionados, por relacion real
    # ------------------------------------------------------------------
    # guia -> categoria de la que habla, por el tema del blog ya asignado
    cat_por_nombre = {DEM.norm(c["title"]): c["path"] for c in site["categories"]}
    for c in site["categories"]:
        if c["slug"] in ESPECIES:
            cat_por_nombre[DEM.norm(ESPECIES[c["slug"]][0])] = c["path"]
        if c["slug"] in MARCAS:
            cat_por_nombre[DEM.norm(MARCAS[c["slug"]][0])] = c["path"]

    guias_de_cat = defaultdict(list)
    for post in site["posts"]:
        destinos = []
        for nombre in (post.get("catNames") or []):
            p = cat_por_nombre.get(DEM.norm(nombre))
            if p and p not in destinos: destinos.append(p)
        if not destinos:
            t = DEM.norm(post["title"])
            for nombre, p in cat_por_nombre.items():
                if re.search(r"\b" + re.escape(nombre) + r"\b", t):
                    destinos.append(p); break
        if destinos:
            post["relatedCats"] = destinos[:3]
            n["guia enlazada a su categoria"] += 1
            for p in destinos[:2]:
                guias_de_cat[p].append({"path": post["path"], "title": post["title"],
                                        "clicks": post.get("clicks") or 0})

    # categoria -> las guias que hablan de ella, las de mas trafico primero
    for c in site["categories"]:
        g = sorted(guias_de_cat.get(c["path"], []), key=lambda x: -x["clicks"])[:4]
        if g:
            c["relatedGuides"] = [{"path": x["path"], "title": x["title"]} for x in g]
            n["categoria enlazada a sus guias"] += 1

    # landing de zona -> su ciudad y su producto
    for pg in site["pages"]:
        if pg.get("sub") not in ("landing", "location"): continue
        rel = []
        slug = pg["path"].strip("/").split("/")[-1]
        for esp in ESPECIES:
            if re.search(r"\b" + esp + r"\b", slug):
                p = next((c["path"] for c in site["categories"] if c["slug"] == esp), None)
                if p: rel.append(p)
                break
        ciudad = re.sub(r"^(ipe|garapa|cumaru|composite|thermo|tropical)[-_]?(decking|hardwoods|woods|landing|deck|tiles)?[-_]?", "", slug)
        ciudad = re.sub(r"[-_](fl|ca|nj|ny|az)$", "", ciudad)
        destino = "/locations/%s/" % ciudad
        if destino in por_path and destino != pg["path"]: rel.append(destino)
        rel = [x for x in dict.fromkeys(rel) if x != pg["path"]]
        if rel:
            pg["relatedCats"] = rel[:3]
            n["landing enlazada a producto y ciudad"] += 1

    # ------------------------------------------------------------------
    # 3-bis. La direccion inversa, que es la que de verdad saca de huerfano
    # ------------------------------------------------------------------
    # Que una landing apunte a su categoria no le da un solo enlace ENTRANTE.
    # Hay que invertirlo: la categoria fuerte enlaza a sus landings de mercado,
    # y la pagina de ciudad a las landings de esa ciudad.
    landings_de = defaultdict(list)
    for pg in site["pages"]:
        for destino in (pg.get("relatedCats") or []):
            landings_de[destino].append({
                "path": pg["path"], "title": pg["title"],
                "clicks": pg.get("clicks") or 0})

    for d in docs:
        ls = sorted(landings_de.get(d["path"], []), key=lambda x: -x["clicks"])[:6]
        if not ls: continue
        ya = {x["path"] for x in (d.get("relatedGuides") or [])}
        extra = [{"path": x["path"], "title": x["title"]} for x in ls if x["path"] not in ya]
        if extra:
            d["relatedPages"] = extra
            n["pagina fuerte enlaza a sus landings"] += len(extra)

    # articulo -> articulos hermanos del mismo tema, los que mas trafico tienen.
    # Sin esto, un articulo sin categoria de catalogo no recibe ningun enlace.
    por_tema = defaultdict(list)
    for post in site["posts"]:
        for t in (post.get("cats") or []):
            por_tema[t].append(post)
    for post in site["posts"]:
        hermanos = []
        for t in (post.get("cats") or []):
            for o in por_tema[t]:
                if o["path"] != post["path"]:
                    hermanos.append(o)
        hermanos = sorted({h["path"]: h for h in hermanos}.values(),
                          key=lambda x: -(x.get("clicks") or 0))[:4]
        if hermanos:
            post["relatedPosts"] = [{"path": h["path"], "title": h["title"]} for h in hermanos]
            n["articulo enlazado a sus hermanos"] += 1

    # contacto y presupuesto: enlazados desde toda ficha de producto, que es
    # donde de verdad se pide un precio
    CTA = [p for p in ("/brazilian-lumber-contact/", "/request-a-quote/", "/request-samples/")
           if p in por_path]
    if CTA:
        for prod in site["products"]:
            prod["relatedPages"] = (prod.get("relatedPages") or []) + [
                {"path": p, "title": por_path[p]["title"]} for p in CTA]
        n["ficha enlaza a contacto y presupuesto"] = len(site["products"])

    # ------------------------------------------------------------------
    # 4. Las utiles, dentro de la navegacion
    # ------------------------------------------------------------------
    # Estaban publicadas, tienen trafico medido y no las enlazaba nadie.
    UTILES = [
        ("/ceiling-soffit/",   "Ceilings & Soffit"),
        ("/calculator/",       "Decking Calculator"),
        ("/wholesale-prices/", "Wholesale Pricing"),
        ("/tropical-hardwoods/", "Hardwood Specifications"),
        ("/sale-items/",       "Sale Items"),
        ("/request-a-quote/",  "Request a Quote"),
        ("/sitemap/",          "Site Index"),
    ]
    ya = {i["path"] for i in site["nav"].get("company", [])}
    for path, etiqueta in UTILES:
        if path in por_path and path not in ya and not por_path[path].get("noindex"):
            site["nav"]["company"].append({"path": path, "title": etiqueta})
            n["pagina util en la navegacion"] += 1

    # ------------------------------------------------------------------
    # 5. El indice HTML, que es la red de seguridad del enlazado
    # ------------------------------------------------------------------
    # /sitemap/ existia heredada de WordPress: en noindex, con un bloque de
    # base64 sin sentido y listas de texto plano sin un solo enlace. Se
    # reconstruye como lo que debe ser, un indice real de todo lo indexable.
    # Es la forma estandar de que ninguna pagina se quede sin enlace entrante,
    # y aqui resuelve las que no encajan en ninguna relacion tematica.
    idx = next((d for d in site["pages"] if d["path"] == "/sitemap/"), None)
    if idx is not None:
        SECCIONES = [
            ("Catalog", [d for d in site["categories"] if not d.get("noindex")]),
            ("Products", sorted([d for d in site["products"] if not d.get("noindex")],
                                key=lambda d: d["title"])),
            ("Guides", sorted([d for d in site["posts"] if not d.get("noindex")],
                              key=lambda d: d["title"])),
            ("Guide topics", sorted([d for d in site["postcats"] if not d.get("noindex")],
                                    key=lambda d: d["title"])),
            ("Where we deliver", sorted([d for d in site["pages"]
                                         if d.get("sub") in ("location", "landing")
                                         and not d.get("noindex")], key=lambda d: d["title"])),
            ("Company", sorted([d for d in site["pages"]
                                if d.get("sub") not in ("location", "landing")
                                and not d.get("noindex") and d["path"] != "/sitemap/"],
                               key=lambda d: d["title"])),
        ]
        bloques = [P("Every page on this site, grouped by section. If you are looking for a "
                     "species, a size or a market and cannot find it in the menu, it is here.")]
        total = 0
        for titulo, items in SECCIONES:
            if not items: continue
            bloques.append(H2("%s (%d)" % (titulo, len(items))))
            bloques.append({"t": "list",
                            "items": [d["title"] for d in items],
                            "links": [d["path"] for d in items]})
            total += len(items)
        idx["blocks"] = bloques
        idx["title"] = "Site Index"
        idx["h1"] = "Site index"
        idx["seoTitle"] = "Site Index | Brazilian Lumber"
        idx["seoDescription"] = ("Every page on brazilianlumber.com in one list: %d entries "
                                 "covering the catalog, the product records, the guides and "
                                 "every market we deliver to." % total)
        idx["noindex"] = False
        idx["words"] = total * 3
        n["indice HTML: entradas"] = total

    json.dump(site, open(D / "site.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("ENLAZADO INTERNO")
    for k, v in sorted(n.items()): print("   %-36s %d" % (k, v))
    print("   entidades en el diccionario         %d" % len(ENT))


if __name__ == "__main__":
    main()
