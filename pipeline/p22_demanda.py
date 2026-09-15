# -*- coding: utf-8 -*-
"""Nucleo de datos del archivo 11.

Cruza la demanda medida (Keyword Tool / Google Ads, Semrush US y Search Console)
contra las 797 URLs del portal unificado, y clasifica cada termino en las cinco
capas de intencion que pidio Felipe el 3 de septiembre de 2026.

No inventa ni una cifra: cada volumen lleva su fuente en la columna de al lado.
"""
import json, re, csv, unicodedata, collections, os

MENU = "C:\\Users\\USER\\Desktop\\BRAZILIAN LUMBER\\ARQUITECTURA WEB BL\\MEN\u00d9 VISUAL"
DATA = "C:\\Users\\USER\\Desktop\\BL-PORTAL-UNICO\\data"
SCR  = os.path.join(MENU, "5 - SCRIPTS Y DATOS")
XL10 = os.path.join(MENU, "10 - MAPA COMPLETO DE LA UNIFICACION.xlsx")

def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s.lower().strip())

STOP = {"the","a","an","of","for","and","to","in","on","with","is","are","best","how",
        "what","why","vs","your","you","it","at","by","or","from","near","me","my",
        "can","do","does","i","be","this","that","top","new","2024","2025","2026"}

def toks(s):
    return set(t for t in re.split(r"[^a-z0-9/]+", norm(s)) if t and t not in STOP and len(t) > 1)

# ---------------------------------------------------------------- 1. fuentes
site   = json.load(open(os.path.join(DATA, "site.json"), encoding="utf-8"))
gsc    = json.load(open(os.path.join(DATA, "gsc.json"), encoding="utf-8"))
zonas  = json.load(open(os.path.join(DATA, "zonas_renombradas.json"), encoding="utf-8"))
zdesc  = json.load(open(os.path.join(DATA, "zonas_descubiertas.json"), encoding="utf-8"))
matrix = json.load(open(os.path.join(SCR, "matrix_final.json"), encoding="latin-1"))
excl   = json.load(open(os.path.join(SCR, "excluidas.json"), encoding="latin-1"))

semrush = {}
with open(os.path.join(SCR, "semrush_us.tsv"), encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        semrush[norm(row["keyword"])] = row

# --- extraccion propia del 15 de septiembre de 2026 -------------------------
# Google Ads Keyword Planner y Keyword Tool (keywordtool.io), los dos de pago,
# sacados a mano para tapar los huecos que dejaron las fuentes anteriores.
# Manda sobre todo lo demas: es el dato mas fresco y el mas defendible, porque
# Google Ads es la fuente que el propio correo de Felipe cita.
FUENTE_ADS = "Google Ads Keyword Planner (15 sep 2026)"
FUENTE_KT  = "Keyword Tool / keywordtool.io (15 sep 2026)"

ads = {}
with open(os.path.join(SCR, "google_ads_2026-09-15.tsv"), encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        v = int(float(row["volume"] or 0))
        ads[norm(row["keyword"])] = dict(vol=v, comp=row.get("competition", ""),
                                         cpc=row.get("bid_low", ""),
                                         cpc_alto=row.get("bid_high", ""))

ktool = {}
with open(os.path.join(SCR, "keywordtool_2026-09-15.tsv"), encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        k = norm(row["keyword"])
        v = int(float(row["volume"] or 0))
        if v > ktool.get(k, {}).get("vol", 0):
            ktool[k] = dict(vol=v, semilla=row.get("semilla", ""))

# ---------------------------------------------------- 2. mapa URL vieja -> nueva
import openpyxl
wb10 = openpyxl.load_workbook(XL10, read_only=True, data_only=True)
MAPA_ROWS = [r for r in wb10["01 MAPA COMPLETO"].iter_rows(min_row=5, values_only=True) if r[2]]
MENU_ROWS = [r for r in wb10["03 MENU UNIFICADO"].iter_rows(min_row=5, values_only=True) if r[0]]
RESUMEN   = [r for r in wb10["00 RESUMEN"].iter_rows(min_row=1, values_only=True)]
old2new = {}
for r in MAPA_ROWS:
    old2new[norm(r[2]).rstrip("/") + "/"] = r[9]

MANUAL = {
    "https://brazilianlumber.com/product-category/cleaner/": "/accessories/maintenance/",
    "https://brazilianlumber.com/product-category/deck-tiles/": "/decking/deck-tiles/",
    "https://brazilianlumber.com/product-category/ipe-deck-tiles/": "/decking/deck-tiles/",
    "https://brazilianlumber.com/product-category/poplar-wood-wall-panels/": "/cladding-siding/wood-wall-panels/",
    "https://brazilianlumber.com/request-samples/": "/brazilian-lumber-contact/",
}
for k, v in MANUAL.items():
    old2new.setdefault(norm(k).rstrip("/") + "/", v)

def a_nueva(u):
    return old2new.get(norm(u).rstrip("/") + "/")

# --------------------------------------------------------- 3. paginas finales
FIN = {}
def add(rec, tipo, subtipo=""):
    FIN[rec["path"]] = dict(
        path=rec["path"], tipo=tipo, subtipo=subtipo,
        titulo=rec.get("title", ""), h1=rec.get("h1", ""),
        clicks=float(rec.get("clicks") or 0),
        impressions=float(rec.get("impressions") or 0),
        noindex=bool(rec.get("noindex")), extra=rec)

for c in site["categories"]: add(c, "Categoria")
for p in site["products"]:   add(p, "Producto")
for p in site["posts"]:      add(p, "Articulo")
for p in site["postcats"]:   add(p, "Tema del blog")
for p in site["pages"]:      add(p, "Pagina", p.get("sub", ""))

hered = collections.defaultdict(lambda: [0.0, 0.0, 0])
for r in MAPA_ROWS:
    n = r[9]
    if not n: continue
    hered[n][0] += float(r[4] or 0)
    hered[n][1] += float(r[5] or 0)
    hered[n][2] += 1
for p, v in FIN.items():
    h = hered.get(p)
    if h: v["clicks_h"], v["impr_h"], v["origenes"] = h[0], h[1], h[2]
    else:  v["clicks_h"], v["impr_h"], v["origenes"] = v["clicks"], v["impressions"], 0

# padres: para heredar el cluster de la categoria
PADRE = {}
for p in site["products"]:
    PADRE[p["path"]] = p.get("category") or "/shop/"
for p in site["posts"]:
    cats = p.get("cats") or []
    PADRE[p["path"]] = cats[0] if cats else "/guides/"
for c in site["categories"]:
    par = c.get("parent")
    if par and par != "None": PADRE[c["path"]] = par

# ------------------------------------------------------- 4. capas de intencion
ESPECIES = ["ipe","cumaru","garapa","jatoba","tigerwood","massaranduba","piquia","batu",
            "red balau","balau","ayous","thermo ash","cypress","cedar","redwood","pine",
            "poplar","oak","walnut","bamboo","acacia","angelim","muiracatiara",
            "thermally modified","thermo","itauba","sucupira","purpleheart"]
TRADE = ["brazilian walnut","brazilian teak","brazilian cherry","brazilian oak",
         "brazilian redwood","brazilian koa","philippine mahogany","bulletwood","mahogany",
         "teak","exotic hardwood","tropical hardwood","exotic wood","brazilian hardwood",
         "brazilian wood","ironwood","hardwood"]
BENEFIT = ["rot","rot-resistant","durable","durability","waterproof","water resistant",
           "water-resistant","fire","class a","fire-rated","fire rated","low maintenance",
           "low-maintenance","maintenance","termite","insect","coastal","pool","salt",
           "weather","warp","mold","mildew","best wood","longest lasting","hardest","janka",
           "stability","non slip","non-slip","splinter","sustainable","fsc","moisture",
           "shrink","cupping","fade","stain","seal","clean","oil","protect"]
TRANS = ["near me","supplier","suppliers","distributor","dealer","lumber yard","lumberyard",
         "wholesale","price","prices","pricing","cost","buy","for sale","quote","sample",
         "samples","delivery","store","contractor","builder","installer"]
APP = ["decking","deck","siding","cladding","rainscreen","ceiling","soffit","tongue and groove",
       "fence","fencing","gate","dock","pergola","sauna","panel","panels","flooring","lumber",
       "board","boards","slab","railing","trim","screen","louver","batten","shiplap","patio",
       "porch","stairs","bench","planter","beam","post","turf","tile","tiles","wall","pavers"]

GEOS = set(norm(z).replace("-", " ") for z in zonas)
GEOS |= set(norm(z) for z in zdesc.get("zonas", {}))
GEOS |= {"miami","florida","california","los angeles","new jersey","new york","northeast",
         "south florida","southern california","broward","palm beach","orlando","tampa",
         "naples","chicago","colorado","texas","georgia","fort lauderdale","boca raton"}

def capa(kw, previa=""):
    if previa:
        p = norm(previa)
        for n in "12345":
            if p.startswith(n): return int(n)
    k = " " + norm(kw) + " "
    if any(" " + g + " " in k for g in GEOS) or any(" " + t in k for t in TRANS):
        return 5
    if any(" " + t + " " in k for t in TRADE): return 3
    if any(" " + b in k for b in BENEFIT):     return 2
    if any(" " + e + " " in k for e in ESPECIES): return 4
    if any(" " + a + " " in k for a in APP):   return 1
    return 1

CAPA_ES = {0:"Sin clasificar",1:"1 - Aplicacion",2:"2 - Beneficio / problema",
           3:"3 - Nombre comercial",4:"4 - Especie",5:"5 - Transaccional / local"}
CAPA_EN = {0:"Unclassified",1:"1 - Application",2:"2 - Benefit / problem",
           3:"3 - Common / trade name",4:"4 - Species",5:"5 - Transactional / local"}

# --------------------------------------------------- 5. asignacion de keywords
ASIG = collections.defaultdict(list)
KW = {}

def put(kw, vol, fuente, url=None, extra=None):
    k = norm(kw)
    if not k: return None
    d = KW.get(k)
    if d is None:
        d = dict(kw=k, vol=int(float(vol or 0)), fuente=fuente, cpc="", kd="", comp="",
                 intent="", imp=0, clk=0, pos="", capa=0, cat="", ubic="",
                 url_nueva="", url_vieja="", ambigua="")
        KW[k] = d
    if extra: d.update({x: y for x, y in extra.items() if y not in (None, "")})
    if vol and int(float(vol)) > d["vol"]:
        d["vol"] = int(float(vol)); d["fuente"] = fuente
    if url and not d["url_nueva"]:
        d["url_nueva"] = url
        ASIG[url].append(d)
    return d

# 5a. la matriz de 400 que ya vio Felipe
for m in matrix:
    n = a_nueva(m["url"])
    d = put(m["kw"], m["vol"], m["src"], n, dict(
        cpc=m.get("cpc"), kd=m.get("kd"), comp=m.get("comp"), intent=m.get("intent"),
        imp=m.get("imp") or 0, clk=m.get("clk") or 0, pos=m.get("pos"),
        cat=m.get("cat"), ubic=m.get("ubic"), url_vieja=m["url"],
        ambigua=m.get("ambigua")))
    d["capa"] = capa(m["kw"], m.get("layer", ""))
    d["en_matriz"] = True

# 5b. keywords locales por zona (Keyword Tool / Google Ads)
slug2page = {}
for p in FIN:
    slug2page.setdefault(p.strip("/").split("/")[-1], p)
for zslug, z in zonas.items():
    destino = slug2page.get(zslug)
    if not destino or destino not in FIN: continue
    for item in z["keywords"]:
        d = put(item["k"], item["v"], "Keyword Tool (Google Ads)", destino,
                dict(cat="Transaccional/local"))
        d["capa"] = 5

# 5b-bis. La extraccion del 15 de septiembre. Va antes que Semrush porque es el
# dato mas reciente y el que viene de la fuente que cita el propio correo.
for k, d in ads.items():
    if not d["vol"]: continue
    x = put(k, d["vol"], FUENTE_ADS, None,
            dict(comp=d["comp"], cpc=d["cpc"], cat="Extraccion 15-sep"))
    x["capa"] = capa(k, CAPA_ES.get(x["capa"], "") if x["capa"] else "")
for k, d in ktool.items():
    if not d["vol"]: continue
    x = put(k, d["vol"], FUENTE_KT, None, dict(cat="Extraccion 15-sep"))
    if not x["capa"]: x["capa"] = capa(k)

# 5c/5d. Semrush US: primero coincidencia exacta con el titulo, luego mejor encaje
def candidatos(path, rec):
    t = norm(rec["titulo"]); s = path.strip("/").split("/")[-1].replace("-", " ")
    out = [t, s]
    for suf in ("decking","lumber","wood","siding","flooring","panels","boards"):
        if t.endswith(" " + suf): out.append(t[:-(len(suf) + 1)])
        out += [t + " " + suf, s + " " + suf]
    out.append(norm(rec["extra"].get("h1") or ""))
    seen, res = set(), []
    for c in out:
        c = norm(c)
        if c and c not in seen: seen.add(c); res.append(c)
    return res

for path, rec in FIN.items():
    if ASIG.get(path) or rec["tipo"] == "Producto": continue
    for c in candidatos(path, rec):
        if c in semrush and not KW.get(c, {}).get("url_nueva"):
            r = semrush[c]
            d = put(c, r["volume"], "Semrush US", path, dict(
                cpc=r.get("cpc"), kd=r.get("kd"), comp=r.get("competition"), intent=r.get("intent")))
            d["capa"] = capa(c)
            break

# --- tokens de lugar: evitan que una consulta nacional caiga en una pagina de zona ---
LUGARES = set()
for g in GEOS:
    LUGARES |= set(g.split())
LUGARES |= {"miami","orlando","tampa","naples","jacksonville","boca","raton","lauderdale",
            "myers","key","west","palm","beach","wellington","coconut","grove","coral",
            "gables","atlanta","savannah","charleston","columbia","beaufort","milton",
            "berkeley","johns","creek","georgia","carolina","austin","houston","dallas",
            "worth","antonio","paso","galveston","corpus","christi","texas","albany",
            "buffalo","rochester","syracuse","island","jersey","york","bahamas",
            "caribbean","islands","angeles","diego","francisco","jose","mateo","marcos",
            "sacramento","stockton","modesto","fresno","oakland","sunnyvale","fremont",
            "riverside","bernardino","fontana","anaheim","ana","clarita","barbara",
            "monica","malibu","burbank","pasadena","altadena","brentwood","hollywood",
            "carpinteria","chula","vista","costa","mesa","laguna","huntington","long",
            "oxnard","bakersfield","california","orange","county","northeast","chicago",
            "colorado","massachusetts","scottsdale","az","nj","fl","ca","ny"}
LUGARES -= {"wood","lumber","deck","decking","yard","near","me"}

def lugares_de(txt):
    return toks(txt) & LUGARES

# --- indice de tokens de todas las URLs finales, para el emparejamiento ---
IDX = []
for p, r in FIN.items():
    base = toks(r["titulo"]) | toks(p.replace("/", " ").replace("-", " "))
    if r["tipo"] == "Producto":
        at = r["extra"].get("attrs") or {}
        base |= toks(" ".join(str(v) for v in at.values() if v))
    IDX.append((p, base, r["tipo"], base & LUGARES))

PESO_TIPO = {"Categoria": 1.30, "Pagina": 1.15, "Tema del blog": 1.05,
             "Articulo": 1.00, "Producto": 0.85}

def emparejar(kw, minimo=2):
    """Devuelve la URL final que mejor cubre la consulta, o None.

    Regla de lugar: una consulta con ciudad solo puede caer en una pagina de esa
    ciudad, y una pagina de zona solo acepta consultas que nombren su zona. Sin
    esto, 'lumber yard' (18.100/mes, nacional) acababa en /locations/orlando/.
    """
    t = toks(kw)
    if len(t) < minimo: return None
    lk = t & LUGARES
    best, bs = None, 0.0
    for p, base, tipo, lp in IDX:
        if lp and not (lk & lp): continue
        if lk and not lp: continue
        inter = len(t & base)
        if inter < minimo: continue
        sc = (inter / len(t)) * PESO_TIPO[tipo] + inter * 0.01
        if sc > bs: best, bs = p, sc
    return best if bs >= 0.70 else None

for k in [x for x in semrush if x not in KW]:
    n = emparejar(k)
    if n:
        r = semrush[k]
        d = put(k, r["volume"], "Semrush US", n, dict(
            cpc=r.get("cpc"), kd=r.get("kd"), comp=r.get("competition"), intent=r.get("intent")))
        d["capa"] = capa(k)

# 5d-bis. Coloca lo que trajo la extraccion del 15 de septiembre.
# Primero por coincidencia exacta con el titulo de una pagina, que es la
# asignacion mas segura; lo que quede, por el emparejador de siempre.
titulo2path = {}
for p, r in FIN.items():
    for c in (norm(r["titulo"]), p.strip("/").split("/")[-1].replace("-", " ")):
        if c: titulo2path.setdefault(c, p)

# Tabla de sinonimos comerciales. El emparejador trabaja con palabras, y
# 'brazilian cherry' no comparte ninguna con 'Jatoba Decking': sin esta tabla,
# 1.900 busquedas/mes se quedaban sin pagina. Es exactamente el problema que
# describe el correo de Felipe, resuelto a mano y especie por especie.
RUTAS = [
    (r"\bbrazilian cherry\b",                    "/decking/tropical-hardwood/jatoba/"),
    (r"\bbrazilian walnut\b",                    "/decking/tropical-hardwood/ipe/"),
    (r"\bbrazilian teak\b",                      "/decking/tropical-hardwood/cumaru/"),
    (r"\bbrazilian oak\b",                       "/decking/tropical-hardwood/garapa/"),
    (r"\bbrazilian redwood\b|\bbulletwood\b",    "/decking/tropical-hardwood/massaranduba/"),
    (r"\bbrazilian koa\b",                       "/decking/tropical-hardwood/tigerwood/"),
    (r"\bphilippine mahogany\b|\bmahogany deck|\bdeck mahogany\b|\bmahogany for deck|"
     r"\bred balau\b|\bbatu deck",               "/batu/"),
    (r"\bteak deck|\bteak wood deck",            "/decking/tropical-hardwood/cumaru/"),
    (r"\btrex\b",                                "/decking/composite/trex/"),
    (r"\btimbertech\b",                          "/decking/composite/timbertech/"),
    (r"\bazek\b",                                "/decking/composite/azek/"),
    (r"\bmoistureshield\b",                      "/decking/composite/moistureshield/"),
    (r"\bzuri\b",                                "/decking/composite/zuri/"),
    (r"\bnewtechwood\b|\bnew tech wood\b",       "/decking/composite/newtechwood/"),
    (r"\barmadillo\b",                           "/decking/composite/armadillo/"),
    (r"\bdeckotech\b",                           "/decking/composite/deckotech/"),
    (r"\bfastener|\bdeck screw|\bhidden clip",   "/accessories/fasteners/"),
    (r"\bcable railing|\brailing system",        "/accessories/railing-cable/"),
    (r"\bdeck (stain|sealer|oil|cleaner)|\bwood (stain|sealer|oil)\b|\bbrighten",
                                                 "/accessories/finishes-sealers/"),
    (r"\bengineered (hardwood |wood )?floor",    "/flooring/engineered/"),
    (r"\bsolid hardwood floor|\bhardwood floor",  "/flooring/solid-hardwood/"),
    (r"\bfaux wood|\bfake wood|\bimitation wood|\bsynthetic wood|\bplastic wood|"
     r"\bcomposite wood deck|\bwood composite deck", "/decking/composite/"),
    (r"\bpressure treated\b|\bpt wood\b|\btreated wood deck", "/lumber/softwood/"),
    (r"\bthermally modified|\bmodified wood deck|\baccoya\b", "/decking/thermally-modified/"),
    (r"\bipe\b|\bepay\b|\bironwood\b",           "/decking/tropical-hardwood/ipe/"),
    (r"\bcumaru\b",                              "/decking/tropical-hardwood/cumaru/"),
    (r"\bgarapa\b",                              "/decking/tropical-hardwood/garapa/"),
    (r"\btiger ?wood\b",                         "/decking/tropical-hardwood/tigerwood/"),
    (r"\bredwood deck|\bcedar (wood )?deck",     "/lumber/softwood/"),
    (r"\bdeck tile",                             "/decking/deck-tiles/"),
    (r"\bsoffit\b|\btongue and groove\b|\bceiling plank", "/ceiling-soffit/"),
    (r"\brainscreen\b|\bwood cladding\b|\bexterior wood siding\b", "/cladding-siding/"),
    (r"\bwall panel|\bwood paneling\b",          "/cladding-siding/wood-wall-panels/"),
    (r"\bfenc(e|ing)\b|\bgate",                  "/fencing-gates/"),
    (r"\bdeck railing|\brailing design",         "/accessories/railing-cable/"),
    (r"\bslab\b",                                "/slabs/"),
    (r"\bartificial (turf|grass)\b",             "/landscaping/artificial-turf/"),
    (r"\bartificial ivy\b",                      "/landscaping/artificial-ivy/"),
    (r"\bdeck(ing)? (cost|price|calculator)\b|\bcost per square foot\b", "/calculator/"),
    (r"\brot|\btermite|\bmoisture resistant|\bwater resistant|\bdoes not rot|"
     r"\bpool deck\b|\bcoastal\b|\blow maintenance\b|\blongest lasting\b|"
     r"\bbest wood\b|\bbest hardwood\b",         "/decking/tropical-hardwood/"),
    (r"\bwood deck|\bdecking board|\bdecking material|\bwooden deck", "/decking/"),
    (r"\bsauna\b|\bboat dock\b|\bpergola\b|\bdock deck", "/decking/tropical-hardwood/"),
    (r"\blumber yard\b|\bsupplier\b|\bdistributor\b|\bwholesale\b", "/shop/"),
]
RUTAS = [(re.compile(p), d) for p, d in RUTAS]

def por_regla(kw):
    for rx, destino in RUTAS:
        if rx.search(kw) and destino in FIN: return destino
    return None

for k, d in sorted(KW.items(), key=lambda kv: -kv[1]["vol"]):
    if d["url_nueva"] or not d["vol"]: continue
    n = titulo2path.get(k) or por_regla(k) or emparejar(k)
    if n:
        d["url_nueva"] = n
        ASIG[n].append(d)

# 5e. las consultas reales de Search Console (demanda propia medida)
QUERIES = []
vistas = {}
for pid, pdata in gsc["portales"].items():
    for q in pdata["consultas"]:
        QUERIES.append((pid, q))
        k = norm(q["query"])
        a = vistas.setdefault(k, dict(imp=0, clk=0, pos=q["position"]))
        a["imp"] += q["impressions"]; a["clk"] += q["clicks"]
        a["pos"] = min(a["pos"], q["position"])

for k, a in vistas.items():
    d = KW.get(k)
    if d:
        d["imp"] = max(d["imp"], a["imp"]); d["clk"] = max(d["clk"], a["clk"])
        if not d["pos"]: d["pos"] = a["pos"]
        continue
    n = emparejar(k)
    if n:
        d = put(k, 0, "Search Console (consulta propia medida)", n,
                dict(imp=a["imp"], clk=a["clk"], pos=a["pos"]))
        d["capa"] = capa(k)

# --------------------------------------- 5f. correccion de marca
# La matriz vieja mandaba 'timbertech' a /azek/ porque en el portal antiguo
# compartian categoria. En el arbol nuevo cada marca tiene la suya.
MARCAS = {"timbertech": "/decking/composite/timbertech/",
          "moistureshield": "/decking/composite/moistureshield/",
          "zuri": "/decking/composite/zuri/",
          "newtechwood": "/decking/composite/newtechwood/",
          "armadillo": "/decking/composite/armadillo/",
          "deckotech": "/decking/composite/deckotech/",
          "azek": "/decking/composite/azek/",
          "trex": "/decking/composite/trex/",
          "durathermo": "/decking/thermally-modified/durathermo/"}
for marca, destino in MARCAS.items():
    if destino not in FIN: continue
    for d in list(KW.values()):
        if marca in d["kw"] and d["url_nueva"] and d["url_nueva"] != destino:
            # solo si la marca es la parte fuerte de la consulta, no una mencion de paso
            otras = [m for m in MARCAS if m != marca and m in d["kw"]]
            if otras: continue
            ASIG[d["url_nueva"]].remove(d)
            d["url_nueva"] = destino
            ASIG[destino].append(d)

# Correccion por nombre comercial y por familia de producto. Estas reglas son
# decisiones de negocio, no coincidencias de palabras, asi que mandan sobre lo
# que hubiera decidido el emparejador: 'mahogany decking' no es caoba domestica,
# es la pagina de Red Balau, y eso no lo puede deducir un algoritmo de tokens.
CORRECCIONES = [
    (r"\bbrazilian cherry\b",                  "/decking/tropical-hardwood/jatoba/"),
    (r"\bbrazilian walnut\b",                  "/decking/tropical-hardwood/ipe/"),
    (r"\bbrazilian teak\b",                    "/decking/tropical-hardwood/cumaru/"),
    (r"\bbrazilian oak\b",                     "/decking/tropical-hardwood/garapa/"),
    (r"\bbrazilian redwood\b|\bbulletwood\b",  "/decking/tropical-hardwood/massaranduba/"),
    (r"\bphilippine mahogany\b|\bmahogany deck|\bdeck mahogany\b|\bmahogany for deck|"
     r"\bred balau\b|\bbatu deck",             "/batu/"),
    (r"\bteak deck|\bteak wood deck",          "/decking/tropical-hardwood/cumaru/"),
    (r"\bfastener|\bhidden clip|\bdeck screw", "/accessories/fasteners/"),
    (r"\bengineered (hardwood |wood )?floor",  "/flooring/engineered/"),
]
for pat, destino in CORRECCIONES:
    rx = re.compile(pat)
    if destino not in FIN: continue
    for d in list(KW.values()):
        if d["url_nueva"] and d["url_nueva"] != destino and rx.search(d["kw"]):
            ASIG[d["url_nueva"]].remove(d)
            d["url_nueva"] = destino
            ASIG[destino].append(d)

# ------------------------------------------------------------ 6. por URL final
def sube(path, visto=None):
    """Sube por el arbol hasta encontrar un antepasado con keyword."""
    visto = visto or set()
    cur = PADRE.get(path)
    while cur and cur not in visto:
        visto.add(cur)
        if ASIG.get(cur): return cur
        cur = PADRE.get(cur)
    return None

def orden_kw(d):
    """Ordena por volumen, pero una keyword de intencion ambigua nunca encabeza.

    'pergola' son 201.000 busquedas/mes y no todas buscan madera: sirve para
    dimensionar el cluster, no para titular la pagina.
    """
    return (1 if d.get("ambigua") else 0, -(d["vol"] or d["imp"] / 100.0))

for path, rec in FIN.items():
    ks = sorted(ASIG.get(path, []), key=orden_kw)
    rec["kws"] = ks
    rec["propias"] = len(ks)
    rec["heredada_de"] = ""
    if not ks:
        padre = sube(path)
        if padre:
            rec["heredada_de"] = padre
            ks = sorted(ASIG[padre], key=orden_kw)[:3]
    rec["kw_principal"]  = ks[0]["kw"] if ks else ""
    rec["vol_principal"] = ks[0]["vol"] if ks else 0
    rec["vol_cluster"]   = sum(k["vol"] for k in ASIG.get(path, []))
    rec["n_kw"]          = len(ASIG.get(path, []))
    rec["capa"]          = ks[0]["capa"] if ks else 0
    rec["secundarias"]   = ", ".join(k["kw"] for k in ks[1:7])
    if not rec["capa"]:
        # sin keyword: la capa se deduce de la propia pagina, que tambien es un dato
        if rec["subtipo"] == "location":
            rec["capa"] = 5
        elif rec["tipo"] == "Producto":
            at = rec["extra"].get("attrs") or {}
            rec["capa"] = 4 if at.get("especie") else capa(rec["titulo"])
        else:
            rec["capa"] = capa(rec["titulo"] + " " + path.replace("/", " ").replace("-", " "))
    if rec["propias"]:
        rec["fuente_vol"] = ks[0]["fuente"]
    elif rec["heredada_de"]:
        rec["fuente_vol"] = "Heredada de %s" % rec["heredada_de"]
    elif rec["impr_h"]:
        rec["fuente_vol"] = "Search Console (impresiones de la propia pagina)"
    else:
        rec["fuente_vol"] = "Sin demanda medida"

# ------------------------------------------------- 7. mercado de cada pagina
# Felipe pidio separar Florida, California y el Noreste. Los slugs se resuelven
# a estado con la tabla de ciudades del portal, no adivinando por el nombre.
EST = {
 "CA": """altadena anaheim bakersfield brentwood burbank california carpinteria chula-vista
    costa-mesa fontana fremont fresno hollywood huntington-beach laguna-beach long-beach
    los-angeles malibu modesto north-hollywood oakland orange-county oxnard pasadena
    riverside sacramento san-bernardino san-diego san-francisco san-jose san-marcos
    san-mateo santa-ana santa-barbara santa-clarita santa-monica stockton sunnyvale
    west-los-angeles""",
 "FL": """boca-raton coconut-grove coral-gables fort-lauderdale fort-myers jacksonville
    key-west miami naples orlando palm-beach tampa wellington broward florida""",
 "NE": "albany buffalo long-island new-jersey new-york rochester-syracuse northeast massachusetts",
 "SE": "atlanta beaufort berkeley-lake charleston columbia georgia johns-creek milton savannah south-carolina",
 "TX": "austin corpus-christi dallas-fort-worth el-paso galveston houston san-antonio texas",
 "INT": "bahamas islands-of-the-caribbean caribbean",
 "OTRO": "chicago colorado scottsdale arizona az",
}
SLUG2EST = {}
for est, lista in EST.items():
    for s in lista.split():
        SLUG2EST.setdefault(s, est)

MERCADO_ES = {"FL": "Florida", "CA": "California", "NE": "Noreste",
              "SE": "Sureste (Georgia y las Carolinas)", "TX": "Texas",
              "INT": "Caribe e internacional", "OTRO": "Otros mercados"}
MERCADO_EN = {"FL": "Florida", "CA": "California", "NE": "Northeast",
              "SE": "Southeast (Georgia and the Carolinas)", "TX": "Texas",
              "INT": "Caribbean and international", "OTRO": "Other markets"}
ORDEN_MERCADO = {"FL": 0, "CA": 1, "NE": 2, "SE": 3, "TX": 4, "INT": 5, "OTRO": 6}

SUFIJO = {"fl": "FL", "la": "CA", "nj": "NE", "ny": "NE", "ca": "CA", "az": "OTRO",
          "tx": "TX", "sf": "CA", "sd": "CA"}

def mercado(path, titulo=""):
    """Estado de una pagina de zona, o None si no es una pagina geografica."""
    slug = path.strip("/").split("/")[-1]
    if slug in SLUG2EST: return SLUG2EST[slug]
    cola = slug.rsplit("-", 1)[-1]
    if cola in SUFIJO and "-" in slug: return SUFIJO[cola]
    palabras = re.split(r"[^a-z0-9]+", norm(path + " " + titulo))
    txt = " ".join(palabras)
    for s, est in sorted(SLUG2EST.items(), key=lambda kv: -len(kv[0])):
        if s.replace("-", " ") in txt: return est
    return None

for path, rec in FIN.items():
    rec["mercado"] = mercado(path, rec["titulo"]) if rec["subtipo"] in ("location", "landing") else None

# demanda total por URL: volumen externo si lo hay, si no impresiones propias
for path, rec in FIN.items():
    rec["demanda"] = rec["vol_cluster"] if rec["vol_cluster"] else round(rec["impr_h"] / 16.0)
    rec["demanda_tipo"] = "Volumen/mes" if rec["vol_cluster"] else "Impresiones/mes"

if __name__ == "__main__":
    con = [p for p, r in FIN.items() if r["n_kw"]]
    her = [p for p, r in FIN.items() if not r["n_kw"] and r["heredada_de"]]
    imp = [p for p, r in FIN.items() if not r["n_kw"] and not r["heredada_de"] and r["impr_h"]]
    nada = [p for p, r in FIN.items() if not r["n_kw"] and not r["heredada_de"] and not r["impr_h"]]
    print("URLs:", len(FIN), "| keyword propia:", len(con), "| heredada:", len(her),
          "| solo impresiones:", len(imp), "| sin dato:", len(nada))
    print("pool de keywords:", len(KW), "| colocadas:", sum(1 for k in KW.values() if k["url_nueva"]))
    print("volumen mensual colocado:", sum(k["vol"] for k in KW.values() if k["url_nueva"]))
    cap = collections.Counter(k["capa"] for k in KW.values() if k["url_nueva"])
    print("capas:", sorted(cap.items()))
    for p in nada[:15]: print("   sin dato:", p, FIN[p]["tipo"])
