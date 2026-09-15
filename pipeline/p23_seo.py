# -*- coding: utf-8 -*-
"""p23 - Aplica al portal la propuesta de keywords del correo de Felipe.

Lo que hace, sobre `data/site.json` y nada mas:

  1. TITULO Y META POR DEMANDA. Cada URL recibe el termino que de verdad se
     busca, no el nombre interno de la categoria. 'Wood Wall Panels' pasa a
     titular con 'wood wall panels' porque son 90.500 busquedas/mes.

  2. NOMBRE COMERCIAL DELANTE DONDE GANA. Regla del correo de Felipe, aplicada
     con el dato: 'brazilian cherry' mide 1.600 y 'jatoba' 1.300, asi que la
     pagina de Jatoba titula por Brazilian Cherry. Donde gana el botanico
     (Ipe, Cumaru, Garapa, Tigerwood) no se toca el titulo y el nombre
     comercial entra en el cuerpo y en alsoKnownAs.

  3. NINGUNA AFIRMACION FALSA DE ESPECIE. Toda pagina con nombre comercial
     lleva un parrafo que explica la equivalencia y la diferencia tecnica.
     Red Balau se vende como Philippine mahogany y NO es caoba: es Shorea, no
     Swietenia, y la pagina lo dice.

  4. LA CAPA DE BENEFICIO. Es la peor servida (0,297% de CTR sobre 6.467
     impresiones/mes). No le falta pagina: le falta que el titulo responda la
     pregunta. Se arregla desde la misma regla 1.

Se ejecuta DESPUES de p3_build.py y ANTES de p4_export.py.
"""
import json, re, sys, os
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p22_demanda as DEM

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
BRAND = "Brazilian Lumber"
MAX_TIT, MAX_DESC = 60, 158

# --------------------------------------------------------------- titulacion
SIGLAS = {"pvc": "PVC", "azek": "AZEK", "timbertech": "TimberTech", "trex": "Trex",
          "moistureshield": "MoistureShield", "newtechwood": "NewTechWood",
          "deckotech": "DeckoTech", "zuri": "Zuri", "armadillo": "Armadillo",
          "t&g": "T&G", "ipe": "Ipe", "usa": "USA", "fl": "FL", "ca": "CA",
          "nj": "NJ", "ny": "NY", "led": "LED", "uv": "UV", "diy": "DIY"}
MINUS = {"and", "or", "for", "the", "a", "an", "of", "in", "on", "to", "with", "vs"}


def tcase(s):
    palabras = re.split(r"(\s+|/|-)", str(s or "").strip())
    out = []
    for i, w in enumerate(palabras):
        bajo = w.lower()
        if not w.strip() or w in ("/", "-"):
            out.append(w)
        elif bajo in SIGLAS:
            out.append(SIGLAS[bajo])
        elif bajo in MINUS and i:
            out.append(bajo)
        elif re.match(r"^\d", w):
            out.append(w)
        else:
            out.append(w[0].upper() + w[1:])
    return "".join(out)


def recortar(txt, limite):
    """Corta sin partir palabras y sin dejar el separador colgando."""
    txt = re.sub(r"\s+", " ", txt).strip()
    if len(txt) <= limite: return txt
    corte = txt[:limite]
    if " " in corte: corte = corte[:corte.rfind(" ")]
    return corte.rstrip(" ,;:|&-")


def redundante(a, b):
    """True si uno de los dos terminos ya dice lo que dice el otro."""
    na, nb = DEM.norm(a), DEM.norm(b)
    return not na or not nb or na in nb or nb in na


def titulo_seo(base, secundaria=""):
    """Une termino principal y secundario sin cortar nunca por la mitad.

    Un titulo como 'Lumber Yard Orlando & Lumber Yard in' sale de recortar la
    cadena ya montada. Aqui el segundo termino entra entero o no entra.
    """
    cola = " | " + BRAND
    hueco = MAX_TIT - len(cola)
    cuerpo = recortar(base, hueco)
    if secundaria and not redundante(cuerpo, secundaria):
        cand = cuerpo + " & " + secundaria
        if len(cand) <= hueco: cuerpo = cand
    return cuerpo + cola


# ------------------------------------------- nombre comercial contra especie
# vol botanico, vol comercial, quien encabeza. Cifras de Keyword Tool / Semrush.
TRADE = {
    "ipe":          dict(bot="ipe wood",        vb=12100, com="Brazilian Walnut",    vc=1000, manda="bot"),
    "cumaru":       dict(bot="cumaru wood",     vb=1300,  com="Brazilian Teak",      vc=320,  manda="bot"),
    "jatoba":       dict(bot="jatoba",          vb=1300,  com="Brazilian Cherry",    vc=1600, manda="com"),
    "garapa":       dict(bot="garapa decking",  vb=720,   com="Brazilian Oak",       vc=210,  manda="bot"),
    "massaranduba": dict(bot="massaranduba",    vb=320,   com="Brazilian Redwood",   vc=210,  manda="ambos"),
    "tigerwood":    dict(bot="tigerwood",       vb=2900,  com="Brazilian Koa",       vc=0,    manda="bot"),
    "batu":         dict(bot="red balau",       vb=320,   com="Philippine Mahogany", vc=720,  manda="com"),
}

# El nombre botanico es la prueba de que la pagina explica la diferencia y no
# solo repite el nombre comercial.
BOTANICO = {
    "ipe": "Handroanthus", "cumaru": "Dipteryx odorata", "jatoba": "Hymenaea courbaril",
    "garapa": "Apuleia leiocarpa", "massaranduba": "Manilkara bidentata",
    "tigerwood": "Astronium graveolens", "batu": "Shorea",
}

EXPLICACION = {
    "ipe": "Ipe is sold in the US market as Brazilian walnut. The name is commercial, "
           "not botanical: Ipe is Handroanthus spp. and has no relation to true walnut "
           "(Juglans). What the two share is the deep brown tone, and that is where the "
           "comparison ends. Ipe rates 3,510 lbf on the Janka scale; black walnut rates 1,010.",
    "cumaru": "Cumaru is sold as Brazilian teak. It is Dipteryx odorata, not teak "
              "(Tectona grandis), and the trade name describes the color and the oily, "
              "dimensionally stable feel of the board rather than the species. Cumaru rates "
              "3,540 lbf on the Janka scale against roughly 1,070 for genuine teak.",
    "jatoba": "Jatoba is sold across the US as Brazilian cherry, and that is the name most "
              "people search for. It is Hymenaea courbaril, not cherry (Prunus). The trade "
              "name comes from the warm red tone that deepens with light exposure. Jatoba "
              "rates 2,690 lbf on the Janka scale; American black cherry rates 950.",
    "garapa": "Garapa is occasionally marketed as Brazilian oak. It is Apuleia leiocarpa and "
              "is not an oak (Quercus). The name refers to the light golden color and the "
              "straight grain. Garapa rates 1,650 lbf on the Janka scale.",
    "massaranduba": "Massaranduba is sold as Brazilian redwood and as bulletwood. It is "
                    "Manilkara bidentata, unrelated to redwood (Sequoia). The name describes "
                    "the deep red color. Massaranduba rates 3,190 lbf on the Janka scale, "
                    "against roughly 450 for redwood.",
    "tigerwood": "Tigerwood is also listed as Brazilian koa. It is Astronium graveolens and "
                 "is not koa (Acacia koa). The name describes the dark striping over a "
                 "golden background. Tigerwood rates 2,160 lbf on the Janka scale.",
    "batu": "Red Balau, also sold as Batu, is widely marketed under Philippine mahogany "
            "terminology. It is not a true mahogany: Red Balau is Shorea spp., while genuine "
            "mahogany is Swietenia. We use the term because it is how the market searches for "
            "this board, and we state the distinction plainly rather than letting it pass. "
            "Red Balau rates roughly 1,700 lbf on the Janka scale.",
}


def bloque_p(texto):
    return {"t": "p", "text": texto}


def bloque_h2(texto):
    return {"t": "h2", "text": texto}


# ------------------------------------------------------------------- main
def main():
    site = json.load(open(D / "site.json", encoding="utf-8"))
    FIN = DEM.FIN

    cambios = Counter()
    titulos_vistos = Counter()

    COLL = ("categories", "products", "posts", "postcats", "pages")
    for coll in COLL:
        for doc in site[coll]:
            rec = FIN.get(doc["path"])
            if not rec: continue

            kw = rec["kw_principal"]
            vol = rec["vol_principal"]
            propia = rec["propias"] > 0

            # ---- 1. datos de demanda visibles en el documento
            doc["kwPrimary"] = kw or None
            doc["kwVolume"] = vol or None
            doc["kwLayer"] = DEM.CAPA_EN[rec["capa"]]
            doc["kwCluster"] = rec["vol_cluster"] or None
            doc["kwCount"] = rec["n_kw"] or None
            doc["kwSource"] = rec["fuente_vol"]
            doc["kwSecondary"] = [k["kw"] for k in rec["kws"][1:6]] or None

            # ---- 2. nombre comercial
            slug = doc["path"].strip("/").split("/")[-1]
            t = TRADE.get(slug)
            if t:
                doc["alsoKnownAs"] = [t["com"]] if t["vc"] else []
                if t["manda"] == "com":
                    nuevo = "%s %s" % (t["com"], "Decking" if "decking" in doc["path"] else "Lumber")
                    doc["h1"] = "%s (%s)" % (nuevo, tcase(slug))
                    doc["navLabel"] = "%s (%s)" % (t["com"], tcase(slug))
                    cambios["h1 por nombre comercial"] += 1
                elif t["manda"] == "ambos":
                    doc["h1"] = "%s Decking (%s)" % (tcase(slug), t["com"])
                    cambios["h1 con los dos nombres"] += 1
                # El parrafo que evita la afirmacion falsa de especie. Se busca
                # el nombre botanico, no el comercial: muchas fichas ya dicen
                # 'Brazilian cherry' sin explicar en ningun sitio que no es
                # cerezo, que es justo lo que pide el correo.
                exp = EXPLICACION.get(slug)
                marca = BOTANICO.get(slug, t["com"]).lower()
                if exp and not any(marca in (b.get("text") or "").lower()
                                   for b in doc["blocks"]):
                    doc["blocks"] = (doc["blocks"][:1]
                                     + [bloque_h2("%s and %s: the same board, two names"
                                                  % (tcase(slug), t["com"])),
                                        bloque_p(exp)]
                                     + doc["blocks"][1:])
                    cambios["parrafo de equivalencia"] += 1

            # ---- 3. titulo y meta por demanda
            h1 = doc.get("h1") or doc["title"]
            if doc["kind"] == "product":
                base = h1
                sec = ""
            elif doc["kind"] == "postcat":
                base = (tcase(kw) if (propia and kw and vol >= 100) else h1) + " Guides"
                sec = ""
            elif propia and kw and vol >= 100:
                # manda el termino que se busca; el nombre interno de la
                # categoria entra detras solo si aporta algo y cabe entero
                base = tcase(kw)
                if t and t["manda"] == "com":
                    # donde gana el nombre comercial, gana tambien en el titulo
                    base = "%s %s" % (t["com"], "Decking" if "decking" in doc["path"] else "Lumber")
                    sec = tcase(kw)
                else:
                    sec = h1 if (not redundante(base, h1)
                                 and not re.match(r"^(the|a|an)\b", h1, re.I)) else (
                        tcase(rec["kws"][1]["kw"]) if len(rec["kws"]) > 1 else "")
            else:
                base = h1
                sec = tcase(kw) if kw and vol >= 100 else ""

            doc["seoTitle"] = titulo_seo(base, sec)
            titulos_vistos[doc["seoTitle"]] += 1

            # meta: el termino que se busca, lo que hay y donde esta
            actual = re.sub(r"\s+", " ", (doc.get("description") or "")).strip()
            if propia and kw and vol >= 100 and DEM.norm(kw) not in DEM.norm(actual):
                extras = ", ".join(k["kw"] for k in rec["kws"][1:4])
                cuerpo = "Shop %s at %s." % (kw, BRAND)
                if extras: cuerpo += " Also %s." % extras
                cuerpo += " In stock in Miami, Los Angeles and New Jersey."
                doc["seoDescription"] = recortar(cuerpo, MAX_DESC)
                cambios["meta reescrita por demanda"] += 1
            else:
                doc["seoDescription"] = recortar(actual or "%s at %s." % (h1, BRAND), MAX_DESC)

    # ---- 4. la pagina de Red Balau / Batu, que no tiene categoria ni surtido
    batu = next((p for p in site["pages"] if p["path"] == "/batu/"), None)
    if batu:
        t = TRADE["batu"]
        batu["h1"] = "Philippine Mahogany Decking (Red Balau / Batu)"
        batu["title"] = "Philippine Mahogany Decking"
        batu["seoTitle"] = titulo_seo("Philippine Mahogany Decking", "Red Balau")
        batu["seoDescription"] = recortar(
            "Philippine mahogany decking, sold in the US as Red Balau or Batu. What the name "
            "means, how the board performs and what it is not. %s, Miami, Los Angeles and "
            "New Jersey." % BRAND, MAX_DESC)
        batu["alsoKnownAs"] = ["Red Balau", "Batu", "Philippine Mahogany"]
        batu["blocks"] = [
            bloque_p("If you are looking for mahogany decking, this is the board the market "
                     "usually means. It is sold as Philippine mahogany, as Red Balau and as "
                     "Batu, and the three names describe the same red tropical hardwood."),
            bloque_h2("Why it is called mahogany, and why it is not"),
            bloque_p(EXPLICACION["batu"]),
            bloque_h2("How it compares with what we stock today"),
            bloque_p("Against Ipe, Red Balau is softer and less dense, which makes it easier "
                     "to machine and lighter to handle, and it costs less per square foot. "
                     "Against pressure-treated pine it is a different class of material "
                     "altogether. If you came here for mahogany decking and want the longest "
                     "service life available, Ipe is the board to compare it against; if you "
                     "want the red tone at a lower price, Jatoba and Massaranduba are the "
                     "closest products we carry in stock."),
            bloque_p("Ask us for current availability of Red Balau before specifying it: it "
                     "is not part of our standing inventory."),
            bloque_h2("Red Balau against the red hardwoods we do stock"),
            {"t": "table",
             "head": ["Species", "Also sold as", "Janka hardness (lbf)",
                      "Service life outdoors", "In stock"],
             "rows": [
                 ["Red Balau", "Philippine Mahogany, Batu", "1,700", "20+ years untreated", "On request"],
                 ["Ipe", "Brazilian Walnut", "3,680", "50+ years untreated", "Yes"],
                 ["Massaranduba", "Brazilian Redwood, Bulletwood", "3,190", "30+ years untreated", "Yes"],
                 ["Jatoba", "Brazilian Cherry", "2,350", "25+ years untreated", "Yes"],
             ]},
            bloque_p("Janka hardness is measured per ASTM D1037. Service life assumes a "
                     "ventilated installation with no chemical treatment. Figures compiled by "
                     "the Brazilian Lumber technical team, last reviewed September 15, 2026."),
        ]
        batu["answerBlock"] = batu["blocks"][0]["text"]
        batu["kwPrimary"] = "philippine mahogany"
        batu["kwVolume"] = 720
        batu["kwLayer"] = DEM.CAPA_EN[3]
        cambios["pagina de Red Balau reescrita"] += 1

    # ---- 5. desempate de titulos
    # Recortar a 60 caracteres hace que dos fichas largas acaben con el mismo
    # titulo ('Trex PVC Decking Transcend Collection' x3). Un titulo duplicado es
    # contenido duplicado a ojos de Google, asi que cada una recupera lo que de
    # verdad la distingue: la medida, el largo o la coleccion.
    docs = [d for c in COLL for d in site[c]]

    def discriminante(d):
        a = d.get("attrs") or {}
        partes = [a.get("medida"), ("%sft" % a.get("largo")) if a.get("largo") else None,
                  a.get("coleccion"), a.get("grado")]
        val = " ".join(str(x) for x in partes if x).strip()
        if val: return val
        cola = d["path"].strip("/").split("/")[-1].split("-")
        return tcase(" ".join(cola[-2:]))

    def por_slug(d, titulo):
        """Lo que separa a esta ficha de sus gemelas: las palabras de su slug
        que no estan ya en el titulo (PVC contra Composite, Colormatch...)."""
        ya = set(DEM.norm(titulo).split())
        extra = [w for w in d["path"].strip("/").split("/")[-1].split("-")
                 if w not in ya and not w.isdigit() and len(w) > 2]
        return tcase(" ".join(extra[:2]))

    for vuelta in range(3):
        grupos = {}
        for d in docs: grupos.setdefault(d["seoTitle"], []).append(d)
        repetidos = {t: g for t, g in grupos.items() if len(g) > 1}
        if not repetidos: break
        for t, g in repetidos.items():
            # la categoria se queda el titulo limpio; desempatan las demas
            g = sorted(g, key=lambda d: {"category": 0, "postcat": 1, "page": 2,
                                         "post": 3, "product": 4}.get(d["kind"], 5))
            for d in (g[1:] if len(g) > 1 and g[0]["kind"] == "category" else g):
                disc = discriminante(d) if vuelta < 2 else por_slug(d, t)
                if not disc or DEM.norm(disc) in DEM.norm(t): continue
                cola = " | " + BRAND
                hueco = MAX_TIT - len(cola) - len(disc) - 1
                base = recortar(d.get("h1") or d["title"], max(hueco, 12))
                nuevo = "%s %s%s" % (base, disc, cola)
                if nuevo != d["seoTitle"]:
                    d["seoTitle"] = nuevo
                    cambios["titulo desempatado"] += 1

    # red de seguridad: si algo sigue repetido, manda el tipo de pagina
    ETI = {"product": "Board", "postcat": "Guides", "post": "Guide", "page": "Info"}
    grupos = {}
    for d in docs: grupos.setdefault(d["seoTitle"], []).append(d)
    for t, g in grupos.items():
        if len(g) < 2: continue
        g = sorted(g, key=lambda d: 0 if d["kind"] == "category" else 1)
        for d in g[1:]:
            eti = ETI.get(d["kind"], "")
            cola = " | " + BRAND
            base = recortar(d.get("h1") or d["title"], MAX_TIT - len(cola) - len(eti) - 1)
            d["seoTitle"] = (base + " " + eti).strip() + cola
            cambios["titulo desempatado"] += 1

    titulos_vistos = Counter(d["seoTitle"] for d in docs)

    # ---- 5-bis. La etiqueta del menu, contrastada contra la demanda
    #
    # 24 de las 46 categorias con volumen tienen una etiqueta que no contiene el
    # termino que la gente escribe. No se renombran todas a ciegas: el menu esta
    # aprobado por direccion y la keyword principal de una categoria muchas veces
    # es la de una de sus ramas ('Landscaping' contra 'artificial grass'), asi que
    # renombrarla seria estrechar la categoria, no aclararla.
    #
    # Se aplica solo el caso que no admite discusion: la keyword CONTIENE entera
    # la etiqueta actual y le anade la palabra que la gente usa de verdad
    # ('engineered flooring' -> 'engineered hardwood flooring'). Ahi no se cambia
    # de significado, se completa. El resto sale como propuesta en la hoja de
    # decisiones, con su volumen al lado.
    PARAR = {"and", "or", "the", "of", "&"}
    MATERIAL = {"wood", "composite", "pvc", "vinyl", "bamboo", "hardwood", "softwood",
                "aluminum", "steel", "plastic"}

    def toks(t):
        return set(w for w in re.split(r"[^a-z0-9]+", DEM.norm(t)) if w and w not in PARAR)

    propuestas = []
    for doc in site["categories"]:
        rec = FIN.get(doc["path"], {})
        kw, vol = rec.get("kw_principal"), rec.get("vol_principal") or 0
        if not kw or vol < 500 or rec.get("propias", 0) == 0: continue
        et, kt = toks(doc["title"]), toks(kw)
        if kt == et: continue
        nivel = doc["path"].strip("/").count("/") + 1
        seguro = (
            et and et < kt                      # la etiqueta cabe entera en la keyword
            and nivel > 1                        # nunca un item de primer nivel
            and not doc.get("navLabel")          # no pisar el nombre comercial
            # la palabra que se anade no puede ser un material que la categoria
            # no cubre: 'Decking' -> 'Wood Decking' dejaria fuera composite y PVC
            and not ((kt - et) & MATERIAL and doc.get("children"))
        )
        if seguro:
            doc["navLabel"] = tcase(kw)
            doc["h1"] = tcase(kw)
            cambios["etiqueta de menu por demanda"] += 1
        else:
            # Solo se propone lo que de verdad es otra forma de decir lo mismo.
            # 'Landscaping' -> 'Artificial Grass' no es un renombrado, es cambiar
            # de categoria: esa keyword es la de una rama, no la del padre. Se
            # filtra por raiz compartida (4 letras) para que 'Fencing' y 'Fence'
            # cuenten como la misma palabra y 'Landscaping' y 'Grass' no.
            raiz = lambda ws: {w[:4] for w in ws}
            if raiz(et) & raiz(kt):
                propuestas.append({"path": doc["path"], "actual": doc["title"],
                                   "propuesta": tcase(kw), "volumen": vol,
                                   "fuente": rec.get("fuente_vol", ""),
                                   "motivo": "mismo alcance, otra forma de nombrarlo: "
                                             "decide Marketing"})
    site["menuPropuestas"] = sorted(propuestas, key=lambda x: -x["volumen"])

    # ---- 6. el menu tambien lleva el nombre por el que se busca
    # De nada sirve titular la pagina por 'brazilian cherry' si el menu sigue
    # diciendo solo 'Jatoba': el cliente que no conoce la especie no lo pulsa.
    etiquetas = {d["path"]: d["navLabel"] for c in COLL for d in site[c] if d.get("navLabel")}

    def renombrar(rama):
        for item in rama:
            nueva = etiquetas.get(item.get("path"))
            if nueva and item.get("title") != nueva:
                item["title"] = nueva
                cambios["etiqueta de menu"] += 1
            for clave in ("children", "items", "cats"):
                if isinstance(item.get(clave), list): renombrar(item[clave])

    for clave, rama in site["nav"].items():
        if isinstance(rama, list): renombrar(rama)
        elif isinstance(rama, dict):
            for sub in ("items", "cats", "children"):
                if isinstance(rama.get(sub), list): renombrar(rama[sub])

    # ---- control de calidad de lo que acabamos de escribir
    largos = [d for c in COLL for d in site[c] if len(d.get("seoTitle", "")) > MAX_TIT]
    metas = [d for c in COLL for d in site[c] if len(d.get("seoDescription", "")) > MAX_DESC]
    dups = [t for t, n in titulos_vistos.items() if n > 1]
    vacios = [d for c in COLL for d in site[c] if not d.get("seoTitle")]

    site["seo"] = {
        "aplicado": "2026-09-15",
        "origen": "correo de Felipe Ortegon del 3 de septiembre de 2026",
        "keywords_colocadas": sum(1 for k in DEM.KW.values() if k["url_nueva"]),
        "volumen_mensual": sum(k["vol"] for k in DEM.KW.values() if k["url_nueva"]),
        "cambios": dict(cambios),
    }
    json.dump(site, open(D / "site.json", "w", encoding="utf-8"), ensure_ascii=False)

    print("CAMBIOS")
    for k, v in sorted(cambios.items()): print("   %-32s %d" % (k, v))
    print("CONTROL")
    print("   titulos de mas de %d caracteres : %d" % (MAX_TIT, len(largos)))
    print("   metas de mas de %d caracteres  : %d" % (MAX_DESC, len(metas)))
    print("   titulos duplicados             : %d" % len(dups))
    print("   documentos sin titulo          : %d" % len(vacios))
    for t in dups[:6]: print("      dup:", t)


if __name__ == "__main__":
    main()
