# -*- coding: utf-8 -*-
"""p24 - Capa GEO/AEO: hacer que el portal sea CITABLE por los motores generativos.

El SEO clasico busca posicion. Esto busca que ChatGPT, Perplexity, Gemini, Claude
y AI Overviews nos usen como fuente cuando alguien pregunta por madera. No son lo
mismo: un motor generativo no cita paginas, cita PASAJES, y solo puede citar lo
que puede extraer sin contexto alrededor.

Lo que hace, sobre `data/site.json`:

  1. COHERENCIA DE CIFRAS. Un solo origen para la dureza Janka, la densidad y la
     vida util: `kb.ESPECIES`. Si una pagina dice 3.680 lbf y otra 3.510 para el
     mismo Ipe, un motor que las lea las dos nos descarta a las dos.

  2. AFIRMACIONES CON RESPALDO. Felipe lo pidio por escrito: nada de 'Class A' sin
     el ensayo del producto concreto. Se reescriben las menciones de fuego para que
     digan de donde sale el dato y a que se aplica.

  3. BLOQUE DE RESPUESTA. Un parrafo de 40 a 60 palabras al principio de cada
     pagina que contesta la consulta principal entero y por si solo, con cifras.
     Es el formato que los motores extraen.

  4. ENCABEZADOS EN FORMA DE PREGUNTA, sacados de consultas reales medidas, no
     inventadas. 'How long does wood decking last' son 720 busquedas/mes.

  5. TABLA COMPARATIVA por especie. El contenido comparativo es ~33% de todo lo
     que citan los motores, mas que ningun otro formato.

  6. FRESCURA Y AUTORIA visibles. Un motor pondera la fecha y quien firma.

  7. ENTIDADES. `alternateName` con los nombres comerciales, para que el motor
     sepa que 'Brazilian cherry' y 'Jatoba' son la misma cosa.

  8. llms.txt, el mapa del sitio para sistemas de IA.

Se ejecuta DESPUES de p23_seo.py y ANTES de p4_export.py.
"""
import json, re, sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p22_demanda as DEM
from kb import ESPECIES, MARCAS

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
PUB = ROOT / "web" / "public"
BRAND = "Brazilian Lumber"
HOY = "2026-09-15"
AUTOR = "the Brazilian Lumber technical team"

SALTO = chr(10)
P = lambda t: {"t": "p", "text": t}
H2 = lambda t: {"t": "h2", "text": t}
TABLA = lambda head, rows: {"t": "table", "head": head, "rows": rows}

TRADE = {
    "ipe": "Brazilian Walnut", "cumaru": "Brazilian Teak", "jatoba": "Brazilian Cherry",
    "garapa": "Brazilian Oak", "massaranduba": "Brazilian Redwood / Bulletwood",
    "tigerwood": "Brazilian Koa", "piquia": "White Ironwood", "batu": "Philippine Mahogany",
    "ayous": "Thermo Ayous",
}

# ---------------------------------------------------------------------------
# 1. Coherencia de cifras
# ---------------------------------------------------------------------------
def cifras(slug):
    e = ESPECIES.get(slug)
    if not e: return None
    nombre, janka, dens, color, vida, nota = e
    return dict(nombre=nombre, janka=janka, dens=dens, color=color, vida=vida, nota=nota)


def arregla_janka(texto):
    """Cualquier cifra Janka escrita a mano se sustituye por la de kb.ESPECIES."""
    def rep(m):
        esp = m.group(1).lower()
        for slug, e in ESPECIES.items():
            if DEM.norm(e[0]) == DEM.norm(esp):
                return "%s rates %s lbf" % (m.group(1), format(e[1], ","))
        return m.group(0)
    return re.sub(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)?) rates [\d,]+ lbf", rep, texto)


# ---------------------------------------------------------------------------
# 2. Afirmaciones con respaldo
# ---------------------------------------------------------------------------
FUEGO_NUEVO = (
    "On fire performance: Ipe is published in the ASTM E84 literature with a Class A "
    "flame spread result, the same class as concrete and steel. That figure describes "
    "the species as tested, not a certification of any particular board. If your project "
    "is in a wildfire or high-rise jurisdiction, ask us for the test report covering the "
    "exact profile and thickness you are specifying before it goes on the drawings."
)

RX_FUEGO = re.compile(r"Class A fire rating[^.]*\.|Ipe carries a Class A flame spread rating[^.]*\.", re.I)


def corrige_fuego(texto):
    if not RX_FUEGO.search(texto): return texto, False
    return RX_FUEGO.sub("Ipe is published with a Class A flame spread result under ASTM E84, "
                        "which describes the species as tested rather than certifying a "
                        "specific board.", texto), True


# ---------------------------------------------------------------------------
# 3. Bloque de respuesta
# ---------------------------------------------------------------------------
def respuesta_categoria(doc, rec):
    slug = doc["slug"]
    n = doc.get("productCount") or 0
    c = cifras(slug)
    if c:
        alias = TRADE.get(slug)
        alias_txt = " It is also sold as %s." % alias if alias else ""
        return ("%s is a tropical hardwood used for exterior decking, cladding and "
                "dimensional lumber. It rates %s lbf on the Janka hardness scale, weighs "
                "about %s kg/m3 air dried, and lasts %s outdoors with no chemical treatment."
                "%s %s stocks %d %s items in Miami, Los Angeles and New Jersey."
                % (c["nombre"], format(c["janka"], ","), format(c["dens"], ","),
                   c["vida"], alias_txt, BRAND, n, c["nombre"]))
    m = MARCAS.get(slug)
    if m:
        nombre, material, garantia, nota = m
        return ("%s is a %s decking and cladding line carrying a %s. %s. %s stocks %d %s "
                "items across its Miami, Los Angeles and New Jersey yards."
                % (nombre, material, garantia, nota[0].upper() + nota[1:], BRAND, n, nombre))
    kw = rec.get("kw_principal") or DEM.norm(doc["title"])
    vol = rec.get("vol_principal") or 0
    if not n and vol:
        # Categoria del menu acordado que todavia no tiene surtido. No se puede
        # decir que hay stock, pero callarse tampoco sirve: la demanda esta
        # medida y el visitante que llega merece saber a que atenerse.
        return ("%s is part of the %s catalog structure and is not stocked yet. Measured US "
                "search demand for %s is about %s queries a month, which is why the category "
                "exists in the menu. Tell us what you need and we will quote it from the "
                "Miami, Los Angeles or New Jersey yard, or point you at the closest product "
                "we do carry."
                % (doc["title"], BRAND, kw, format(vol, ",")))
    if n:
        return ("%s covers %d products in stock at %s, with published species, nominal and "
                "actual dimensions, coverage per square foot and installation notes on every "
                "item. Orders ship from the Miami, Los Angeles and New Jersey yards. Search "
                "demand for %s is about %s queries a month in the United States."
                % (doc["title"], n, BRAND, kw, format(vol, ",") if vol else "under 100"))
    return None


def respuesta_producto(doc):
    a = doc.get("attrs") or {}
    esp = a.get("especie")
    c = cifras(esp) if esp else None
    partes = []
    if a.get("medida"): partes.append("nominal %s" % a["medida"])
    if a.get("real"): partes.append("%s actual" % a["real"])
    if a.get("largo"): partes.append("%s ft lengths" % a["largo"])
    med = ", ".join(partes)
    if c:
        return ("%s is a %s board%s. %s rates %s lbf on the Janka scale at about %s kg/m3, "
                "and lasts %s outdoors untreated. In stock at %s in Miami, Los Angeles and "
                "New Jersey."
                % (doc["title"], c["nombre"], (" measuring " + med) if med else "",
                   c["nombre"], format(c["janka"], ","), format(c["dens"], ","), c["vida"], BRAND))
    marca = a.get("marca")
    m = MARCAS.get(marca) if marca else None
    if m:
        return ("%s is part of the %s line, a %s with a %s.%s In stock at %s in Miami, Los "
                "Angeles and New Jersey."
                % (doc["title"], m[0], m[1], m[2], (" Supplied " + med + ".") if med else "", BRAND))
    return ("%s is stocked at %s in Miami, Los Angeles and New Jersey.%s Specifications, "
            "coverage and installation notes are published on this page."
            % (doc["title"], BRAND, (" Supplied " + med + ".") if med else ""))


def respuesta_zona(doc, rec):
    kw = rec.get("kw_principal") or ""
    vol = rec.get("vol_principal") or 0
    ciudad = doc["title"].replace("Lumber Yard in ", "").replace("Lumber in ", "") \
                          .replace("Lumber Yards in ", "").replace("Lumber Yard Serving ", "")
    return ("%s supplies %s with tropical hardwood decking, composite and PVC decking, "
            "cladding and dimensional lumber, delivered from the nearest of its three yards "
            "in Miami, Los Angeles and New Jersey. Local search demand for %s is about %s "
            "queries a month."
            % (BRAND, ciudad, kw or ("lumber in " + ciudad),
               format(vol, ",") if vol else "under 100"))


# ---------------------------------------------------------------------------
# 4. Encabezados en forma de pregunta
# ---------------------------------------------------------------------------
RX_PREGUNTA = re.compile(r"^(how|what|why|which|when|where|is|are|does|do|can|should)\b")

def preguntas_de(rec, limite=3):
    out = []
    for k in rec.get("kws", []):
        kw = k["kw"]
        if RX_PREGUNTA.search(kw) or " vs " in kw:
            out.append((kw, k["vol"]))
    out.sort(key=lambda x: -x[1])
    return out[:limite]


def titula_pregunta(kw):
    t = kw[0].upper() + kw[1:]
    if " vs " in kw: return t.replace(" vs ", " vs ")
    return t + "?"


# ---------------------------------------------------------------------------
# 5. Tabla comparativa
# ---------------------------------------------------------------------------
DECKING = ["ipe", "cumaru", "massaranduba", "jatoba", "tigerwood", "garapa", "piquia",
           "teak", "cedar", "redwood", "ayous", "bamboo"]

def tabla_comparativa(slug):
    c = cifras(slug)
    if not c or slug not in DECKING: return None
    otros = sorted([s for s in DECKING if s != slug and s in ESPECIES],
                   key=lambda s: abs(ESPECIES[s][1] - c["janka"]))[:3]
    filas = []
    for s in [slug] + otros:
        e = ESPECIES[s]
        filas.append([e[0], TRADE.get(s, "—"), format(e[1], ","), format(e[2], ","), e[4]])
    return TABLA(["Species", "Also sold as", "Janka hardness (lbf)",
                  "Density (kg/m3, air dried)", "Service life outdoors"], filas)


# ---------------------------------------------------------------------------
def main():
    site = json.load(open(D / "site.json", encoding="utf-8"))
    FIN = DEM.FIN
    n = Counter()
    COLL = ("categories", "products", "posts", "postcats", "pages")

    for coll in COLL:
        for doc in site[coll]:
            rec = FIN.get(doc["path"], {})
            bloques = doc.get("blocks") or []

            # --- 1 y 2: cifras coherentes y afirmaciones con respaldo
            for b in bloques:
                if b.get("t") in ("p", "h2", "h3", "h4") and b.get("text"):
                    t0 = b["text"]
                    t1 = arregla_janka(t0)
                    t1, tocado = corrige_fuego(t1)
                    if tocado: n["afirmacion de fuego matizada"] += 1
                    if t1 != t0:
                        b["text"] = t1
                        n["cifra o afirmacion corregida"] += 1
            for spec in (doc.get("specs") or []):
                if len(spec) == 2 and isinstance(spec[1], str):
                    spec[1] = arregla_janka(spec[1])
            for f in (doc.get("faq") or []):
                f["a"] = arregla_janka(f["a"])
                f["a"], tocado = corrige_fuego(f["a"])
                if tocado: n["afirmacion de fuego matizada"] += 1

            # --- 3: bloque de respuesta, primero del todo
            if doc["kind"] == "category":
                resp = respuesta_categoria(doc, rec)
            elif doc["kind"] == "product":
                resp = respuesta_producto(doc)
            elif doc.get("sub") in ("location", "landing") and rec.get("mercado"):
                resp = respuesta_zona(doc, rec)
            else:
                resp = None
            # Un pasaje de 20 palabras no se cita: no contesta nada entero. Los
            # que se quedan cortos reciben el contexto de su categoria, que es
            # dato que ya tenemos, hasta entrar en el rango extraible.
            if resp and len(resp.split()) < 35:
                cat = doc.get("categoryTitle") or doc.get("title")
                extra = (" It is listed under %s, with nominal and actual dimensions, "
                         "coverage per square foot and installation notes published on this "
                         "page. Quotes are per piece and stock is checked at the yard before "
                         "it is confirmed." % cat)
                resp = resp + extra
            if resp and not doc.get("answerBlock"):
                doc["answerBlock"] = resp
                bloques.insert(0, P(resp))
                n["bloque de respuesta"] += 1

            # --- 4: encabezados en forma de pregunta
            preg = preguntas_de(rec)
            if preg and doc["kind"] in ("category", "post", "page"):
                ya = " ".join(DEM.norm(b.get("text", "")) for b in bloques if b.get("t") == "h2")
                nuevas = [(k, v) for k, v in preg if DEM.norm(k) not in ya]
                if nuevas:
                    doc["queryHeadings"] = [k for k, _ in nuevas]
                    n["encabezado desde consulta real"] += len(nuevas)

            # --- 4-bis: preguntas medidas que SI podemos contestar con el dato
            # que ya tenemos. No se inventa ninguna respuesta: salen de kb.ESPECIES.
            if doc["kind"] == "category" and cifras(doc["slug"]):
                c = cifras(doc["slug"])
                faq = doc.get("faq") or []
                ya = " ".join(DEM.norm(f["q"]) for f in faq)
                nuevas = []
                alias = TRADE.get(doc["slug"])
                if alias and "also called" not in ya and "also known" not in ya:
                    nuevas.append({
                        "q": "What is %s also called?" % c["nombre"],
                        "a": "%s is sold in the US market as %s. The trade name describes the "
                             "color, not the botany: it is not the species the name borrows "
                             "from. We publish both names on every %s page so the board you "
                             "receive is the board you specified."
                             % (c["nombre"], alias, c["nombre"])})
                if "how long" not in ya:
                    nuevas.append({
                        "q": "How long does %s last outdoors?" % c["nombre"],
                        "a": "%s in a ventilated installation, with no chemical treatment and "
                             "no preservative. Life drops if the boards sit in standing water "
                             "or trap moisture against a solid substrate, which is why we "
                             "publish the joist spacing and gap for every profile."
                             % c["vida"].capitalize()})
                if "janka" not in ya and "hard" not in ya:
                    nuevas.append({
                        "q": "How hard is %s?" % c["nombre"],
                        "a": "%s lbf on the Janka scale, measured per ASTM D1037, at an air "
                             "dried density of about %s kg/m3. For reference, red oak rates "
                             "1,290 lbf and western red cedar 350 lbf."
                             % (format(c["janka"], ","), format(c["dens"], ","))})
                if nuevas:
                    doc["faq"] = faq + nuevas
                    n["pregunta contestada con dato propio"] += len(nuevas)

            # --- 5: tabla comparativa
            if doc["kind"] == "category":
                tab = tabla_comparativa(doc["slug"])
                ya_comparada = any(b.get("t") == "table" and "Also sold as" in (b.get("head") or [])
                                   for b in bloques)
                if tab and not ya_comparada:
                    bloques.append(H2("%s compared with the closest species we stock" % doc["title"]))
                    bloques.append(tab)
                    bloques.append(P(
                        "Janka hardness is measured per ASTM D1037. Density is an air dried "
                        "average and varies by board. Service life assumes a ventilated "
                        "installation with no chemical treatment. Figures compiled by %s, "
                        "last reviewed %s." % (AUTOR, HOY)))
                    n["tabla comparativa"] += 1

            # --- 6 y 7: frescura, autoria y entidades
            doc["reviewed"] = HOY
            doc["reviewedBy"] = AUTOR
            alias = []
            if doc["kind"] == "category" and doc["slug"] in TRADE:
                alias = [x.strip() for x in TRADE[doc["slug"]].split("/")]
            if doc.get("alsoKnownAs"): alias = list(dict.fromkeys(doc["alsoKnownAs"] + alias))
            if alias:
                doc["alsoKnownAs"] = alias
                n["entidad con nombre alternativo"] += 1

            doc["blocks"] = bloques

    # --- 7-bis: los sinonimos que nombra el correo, en la pagina que los sirve
    #
    # La auditoria contra el sitio en vivo encontro que 'exotic hardwood',
    # 'exterior wood siding' y 'rainscreen' no aparecian en ninguna parte de su
    # pagina destino. Felipe los escribe uno a uno en su correo y tienen volumen
    # medido. No es relleno: son los nombres por los que se conoce eso mismo, y
    # se escriben como tales, en una frase que dice la verdad.
    SINONIMOS = {
        "/decking/tropical-hardwood/": (
            "The same boards are searched for as exotic hardwood, tropical hardwood decking "
            "and exotic hardwood decking. They are all names for this group: dense South "
            "American species that survive outdoors without chemical treatment. Ipe, Cumaru, "
            "Jatoba, Garapa, Massaranduba, Tigerwood and Piquia all sit here, each with its "
            "Janka hardness and expected service life published on its own page."),
        "/cladding-siding/": (
            "This is what the market also calls exterior wood siding, wood cladding and "
            "rainscreen siding. The three describe the same job done three ways: a face board "
            "over a ventilated cavity. Rainscreen refers to the detail, not the material, and "
            "every profile here can be installed as one when the battens leave the cavity open."),
        "/ceiling-soffit/": (
            "Tongue and groove ceiling, wood ceiling planks and wood soffit are the three names "
            "for the boards on this page. The profile is the same T&G milling; what changes is "
            "where it goes. Soffit is the underside of an overhang and takes the most moisture, "
            "so it is the one that decides the species."),
    }
    for coll in COLL:
        for doc in site[coll]:
            frase = SINONIMOS.get(doc["path"])
            if not frase: continue
            bloques = doc.get("blocks") or []
            ya = DEM.norm(" ".join(b.get("text", "") for b in bloques if b.get("t") == "p"))
            if DEM.norm(frase[:60]) in ya: continue
            corte = 1 if doc.get("answerBlock") else 0
            bloques.insert(corte + 1, H2("What else this is called"))
            bloques.insert(corte + 2, P(frase))
            doc["blocks"] = bloques
            n["sinonimo del correo de Felipe"] += 1

    # --- 7-ter: la rama de techos, que tiene 18.100 busquedas/mes y no es categoria
    ceiling = next((d for d in site["pages"] if d["path"] == "/ceiling-soffit/"), None)
    if ceiling and not ceiling.get("answerBlock"):
        ceiling["answerBlock"] = (
            "Tongue and groove ceiling boards are the T&G milled planks used for porch "
            "ceilings, soffits and interior feature ceilings. Brazilian Lumber mills them in "
            "Ipe, Cumaru, Garapa and Thermo Ayous, and stocks PVC and composite profiles for "
            "wet locations, at its Miami, Los Angeles and New Jersey yards. Measured US demand "
            "for tongue and groove ceiling is about 18,100 queries a month.")
        ceiling["blocks"] = [P(ceiling["answerBlock"])] + (ceiling.get("blocks") or [])
        ceiling["alsoKnownAs"] = ["Wood Ceiling Planks", "Wood Soffit", "T&G Ceiling"]
        n["bloque de respuesta"] += 1

    # --- 8: llms.txt
    cats = [c for c in site["categories"] if (c.get("productCount") or 0) > 0]
    cats.sort(key=lambda c: -(FIN.get(c["path"], {}).get("vol_cluster") or 0))
    guias = sorted(site["posts"], key=lambda p: -(p.get("clicks") or 0))[:25]
    zonas = [p for p in site["pages"] if p.get("sub") == "location"]

    L = ["# Brazilian Lumber", "",
         "> Supplier of tropical hardwood decking, composite and PVC decking, cladding, "
         "siding and dimensional lumber, with yards in Miami (FL), Los Angeles (CA) and "
         "New Jersey. Founded 2006. Stock is real and quoted per linear or square foot.", "",
         "Species we stock, with published Janka hardness, density and expected service "
         "life on each page. Trade names are given alongside the botanical name because the "
         "market searches both: Ipe is sold as Brazilian walnut, Cumaru as Brazilian teak, "
         "Jatoba as Brazilian cherry, Massaranduba as Brazilian redwood or bulletwood, and "
         "Red Balau (Batu) under Philippine mahogany terminology. None of these is the "
         "species the trade name borrows from, and every page says so.", "",
         "Last reviewed: %s" % HOY, "",
         "## Species data", ""]
    for s in DECKING:
        if s not in ESPECIES: continue
        e = ESPECIES[s]
        L.append("- **%s**%s: %s lbf Janka, %s kg/m3, %s. %s" % (
            e[0], (" (also sold as %s)" % TRADE[s]) if s in TRADE else "",
            format(e[1], ","), format(e[2], ","), e[4], e[3]))
    L += ["", "## Catalog", ""]
    for c in cats[:40]:
        L.append("- [%s](%s): %d products" % (c["title"], c["path"], c.get("productCount") or 0))
    L += ["", "## Guides", ""]
    for g in guias:
        L.append("- [%s](%s)" % (g["title"], g["path"]))
    L += ["", "## Where we deliver", "",
          "- " + ", ".join(p["title"].split(" in ")[-1].split(" Serving ")[-1] for p in zonas[:60]),
          "", "## Contact", "",
          "- [Request a quote](/request-a-quote/)",
          "- [Request samples](/request-samples/)",
          "- [Contact](/brazilian-lumber-contact/)", ""]
    # No se escribe en /public: un estatico se sirve sin pasar por la cabecera
    # X-Robots-Tag y se quedaba fuera del bloqueo del prototipo. Va como dato que
    # lee /llms.txt/route.ts, detras del mismo interruptor que robots.txt.
    WEBDATA = ROOT / "web" / "src" / "data"
    WEBDATA.mkdir(parents=True, exist_ok=True)
    (WEBDATA / "llms.json").write_text(
        json.dumps({"text": SALTO.join(L)}, ensure_ascii=False), encoding="utf-8")
    n["llms.txt"] = len(L)

    site["geo"] = {"aplicado": HOY, "cambios": dict(n)}
    json.dump(site, open(D / "site.json", "w", encoding="utf-8"), ensure_ascii=False)

    print("CAPA GEO/AEO")
    for k, v in sorted(n.items()): print("   %-34s %d" % (k, v))
    tot = sum(1 for c in COLL for d in site[c] if d.get("answerBlock"))
    print("   URLs con bloque de respuesta      %d de %d"
          % (tot, sum(len(site[c]) for c in COLL)))


if __name__ == "__main__":
    main()
