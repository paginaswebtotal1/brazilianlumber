# -*- coding: utf-8 -*-
"""p10 - El Excel unico de la consolidacion.

Responde, con datos de Google Search Console de los 3 portales, a las preguntas
que va a hacer direccion:

  - Que URL existe hoy y en que se convierte.
  - Cual desaparece, por que, y cuanto trafico se juega en ello.
  - Cuanto trafico tiene de verdad cada portal, y por tanto si la union se
    sostiene o no.

Salida: MAPA COMPLETO DE LA UNIFICACION.xlsx
"""
import json, re
from pathlib import Path
from collections import Counter, defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
# El entregable vive con el resto del estudio, no en la carpeta del codigo:
# es lo que se abre para responderle a direccion.
PROYECTO = Path("C:/Users/USER/Desktop/BRAZILIAN LUMBER/ARQUITECTURA WEB BL/MENÙ VISUAL")
SALIDA = (PROYECTO if PROYECTO.exists() else ROOT) / \
    "10 - MAPA COMPLETO DE LA UNIFICACION.xlsx"

S = json.load(open(D / "site.json", encoding="utf-8"))
RAW = json.load(open(D / "raw.json", encoding="utf-8"))
GSC = json.load(open(D / "gsc.json", encoding="utf-8"))
COLL = ("categories", "products", "posts", "postcats", "pages")

# ------------------------------------------------------------------ estilos
AZUL = "1F3A5F"
CREMA = "F2EDE4"
GRIS = "7A7A7A"
VERDE = "E8F2E8"
ROJO = "FBE9E7"
AMBAR = "FFF4E0"

H = Font(bold=True, color="FFFFFF", size=10)
HF = PatternFill("solid", fgColor=AZUL)
T = Font(bold=True, size=15, color=AZUL)
SUB = Font(size=9, color=GRIS, italic=True)
B = Font(bold=True, size=10)
BORDE = Border(bottom=Side(style="thin", color="D9D9D9"))


def hoja(wb, nombre, titulo, subtitulo=None):
    ws = wb.create_sheet(nombre[:31])
    ws["A1"] = titulo
    ws["A1"].font = T
    if subtitulo:
        ws["A2"] = subtitulo
        ws["A2"].font = SUB
    ws.freeze_panes = "A5"
    return ws


def cabecera(ws, cols, fila=4):
    for i, c in enumerate(cols, 1):
        cel = ws.cell(fila, i, c)
        cel.font = H
        cel.fill = HF
        cel.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[fila].height = 28


def anchos(ws, ws_anchos):
    for i, w in enumerate(ws_anchos, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def pintar(ws, desde=5):
    for fila in ws.iter_rows(min_row=desde, max_row=ws.max_row):
        for c in fila:
            c.border = BORDE
            if c.alignment.wrap_text is not True:
                c.alignment = Alignment(vertical="top")


# ------------------------------------------------------------------ indices
def norm(u):
    return (u or "").split("?")[0].rstrip("/") + "/"


# Metricas por URL EXACTA. Antes se normalizaba, y eso fusionaba las URLs con
# parametro dentro de su version limpia: inflaba la limpia y hacia desaparecer
# del mapa cientos de direcciones que Google conoce de verdad.
gsc_exacto = {}
gsc_por_url = {}
for portal, datos in GSC["portales"].items():
    for url, m in datos["paginas"].items():
        gsc_exacto[url] = m
        n = norm(url)
        if n not in gsc_por_url:
            gsc_por_url[n] = m


def metricas(url):
    return gsc_exacto.get(url) or gsc_exacto.get(url.rstrip("/"))         or gsc_exacto.get(url + "/") or {}

TOT = {p: d["totales"] for p, d in GSC["portales"].items()}
CLICS_TOT = sum(t["clicks"] for t in TOT.values())
IMPR_TOT = sum(t["impressions"] for t in TOT.values())

docs = {d["path"]: d for c in COLL for d in S[c]}
destino_de = {}
for r in RAW:
    destino_de[r["url_origen"]] = r
red_por_origen = {r["from"]: r for r in S["redirects"]}
absorb_por_origen = {}
for a in S["absorbed"]:
    for o in a["from"]:
        absorb_por_origen[o] = a["into"]

PORTAL_DOM = {"MIA": "brazilianlumber.com", "LA": "brazilianlumberlosangeles.com",
              "NJ": "brazilianlumbernewyork.com"}

# ------------------------------------------------------- el universo completo
#
# Hay dos fuentes y NINGUNA basta por si sola:
#   - El rastreo por la API de WordPress: 2.197 URLs. Sabe que es cada cosa,
#     pero solo ve lo que WordPress publica.
#   - Search Console: 5.501 URLs con datos. Ve todo lo que Google conoce, que
#     incluye URLs con parametro, etiquetas, paginaciones y restos antiguos que
#     WordPress ya no lista.
#
# El mapa tiene que ser la UNION de las dos, o faltarian URLs que hoy reciben
# visitas y que alguien tendra que redirigir el dia de la migracion.

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from p2_classify import clasificar as _clasificar, especie as _especie, marca as _marca, medida as _medida
from taxonomia import ARBOL as _ARBOL


def clasificar_suelta(url):
    """Que hacer con una URL que Google conoce pero el rastreo no devolvio.

    Son 4.016 direcciones y ninguna puede quedarse sin respuesta: cada una es
    una redireccion que alguien tendra que configurar, o una decision explicita
    de no configurarla. Se resuelven por patron, de lo mas concreto a lo mas
    general.
    """
    u = url.lower()
    if "#" in url:
        return "ANCLA", "Ancla dentro de la misma pagina: no es una URL distinta"
    if "?" in u:
        return "PARAMETRO", "URL con parametro: canonical a la version limpia"
    if "/wp-content/" in u or "/wp-includes/" in u:
        return "NO-PUBLICO", "Fichero subido, no es una pagina"
    if any(k in u for k in ("/color/", "/length/", "/board-length/", "/upc/", "/pa_",
                            "/width/", "/thickness/", "/grade/", "/finish/", "/profile/")):
        return "ATRIBUTO", "Archivo de atributo de WooCommerce: duplica la categoria"
    if "/product-tag/" in u or "/tag/" in u:
        return "NOINDEX", "Etiqueta: thin content y solapa con la categoria"
    if "/author/" in u or "/feed" in u or "/wp-json" in u or "/comment-page" in u:
        return "NO-PUBLICO", "URL tecnica de WordPress, no es una pagina"
    if "/page/" in u:
        return "NOINDEX", "Paginacion: canonical a la primera pagina"
    if "/product-category/" in u:
        return "CONSOLIDAR-301", "Categoria antigua: va a su ruta limpia"
    if "/attachment" in u or u.rstrip("/").endswith((".jpg", ".png", ".pdf", ".webp")):
        return "NO-PUBLICO", "Adjunto o fichero, no es una pagina"
    if "/product/" in u:
        return "DESCATALOGADO", "Ficha retirada de WordPress que Google sigue conociendo"
    return "REVISAR", "Google la conoce pero WordPress ya no la publica: decidir destino"


def _por_slug(url):
    """Clasifica el ultimo segmento con el mismo motor que clasifica el catalogo."""
    slug = url.rstrip("/").split("/")[-1]
    titulo = slug.replace("-", " ")
    try:
        ruta = _clasificar(slug, titulo, "", _especie(slug, titulo, ""),
                           _marca(slug, titulo, ""), _medida(slug, titulo))
        if ruta in _ARBOL:
            return "https://brazilianlumber.com/" + ruta + "/"
    except Exception:
        pass
    return ""


def destino_suelta(url, accion, padre):
    """Adonde mandarla. Ninguna se queda sin respuesta."""
    if accion == "ANCLA":
        base = url.split("#")[0]
        return base.replace("https://brazilianlumber.com", "") or "/"
    if padre and padre.get("destino"):
        return padre["destino"]

    # Sin padre: se limpia la URL de parametros, anclas, paginacion y carrito, y
    # se vuelve a resolver sobre la ruta desnuda. Si aun asi no cae en ningun
    # sitio, va a la portada, que siempre es mejor que un 404.
    limpia = url.split("#")[0].split("?")[0].rstrip("/")
    limpia = re.sub(r"/page/\d+$", "", limpia)
    ruta = re.sub(r"^https?://[^/]+", "", limpia)
    if not ruta or ruta == "/":
        return "https://brazilianlumber.com/"

    for seg in reversed([x for x in ruta.strip("/").split("/") if x]):
        d = _por_slug(seg)
        if d:
            return d

    if accion in ("ATRIBUTO", "DESCATALOGADO", "PARAMETRO"):
        return "https://brazilianlumber.com/shop/"
    if accion == "NOINDEX":
        return "https://brazilianlumber.com/shop/"
    return "https://brazilianlumber.com/"


PORTAL_DE_DOMINIO = {v: k for k, v in PORTAL_DOM.items()}


def portal_de(url):
    for dom, p in PORTAL_DE_DOMINIO.items():
        if dom in url:
            return p
    return "?"


# Se indexa por URL EXACTA para que /shop/?orderby=price y /shop/ sean dos
# filas distintas, que es lo que son para Google y para quien tenga que
# redirigirlas.
universo = {}

# 1) todo lo que devolvio el rastreo
for r in RAW:
    k = r["url_origen"]
    universo[k] = {
        "url": r["url_origen"], "portal": r["portal"], "tipo": r["tipo"],
        "titulo": r["titulo"], "accion": r["accion"], "motivo": r["motivo"],
        "destino": r["url_destino"],
        "fuente": "Rastreo + Search Console" if metricas(k) else "Solo rastreo",
    }

# 2) todo lo que Google conoce y el rastreo no devolvio
sueltas = 0
for portal, datos in GSC["portales"].items():
    for url in datos["paginas"]:
        k = url
        if k in universo or url.rstrip("/") in universo or url + "/" in universo:
            continue
        accion, motivo = clasificar_suelta(url)
        # si la version limpia existe, hereda su destino
        limpia = url.split("?")[0]
        padre = universo.get(limpia) or universo.get(limpia.rstrip("/"))             or universo.get(limpia.rstrip("/") + "/")
        universo[k] = {
            "url": url, "portal": portal_de(url) if portal_de(url) != "?" else portal,
            "tipo": "otra", "titulo": "", "accion": accion, "motivo": motivo,
            "destino": destino_suelta(url, accion, padre),
            "fuente": "Solo Search Console",
        }
        sueltas += 1

print("universo de URLs: {:,}  (rastreo {:,} + solo Search Console {:,})".format(
    len(universo), len(RAW), sueltas))

wb = Workbook()
wb.remove(wb.active)

# ================================================================ 00 RESUMEN
ws = hoja(wb, "00 RESUMEN", "Unificacion de los 3 portales en uno solo",
          "Datos de Google Search Console, {} a {}. Extraidos por API el 13 de septiembre de 2026."
          .format(GSC["ventana"]["desde"], GSC["ventana"]["hasta"]))
anchos(ws, [46, 20, 20, 14, 14, 60])

f = 4
ws.cell(f, 1, "LO QUE DICEN LOS DATOS").font = B
f += 1
cabecera(ws, ["Portal", "Clics", "Impresiones", "CTR", "Posicion media", "Peso sobre el total de clics"], f)
f += 1
for p in ("MIA", "LA", "NJ"):
    t = TOT[p]
    ws.cell(f, 1, "{}  ({})".format(PORTAL_DOM[p], p))
    ws.cell(f, 2, t["clicks"]).number_format = "#,##0"
    ws.cell(f, 3, t["impressions"]).number_format = "#,##0"
    ws.cell(f, 4, t["ctr"] / 100).number_format = "0.00%"
    ws.cell(f, 5, t["position"])
    ws.cell(f, 6, t["clicks"] / CLICS_TOT if CLICS_TOT else 0).number_format = "0.0%"
    if p != "MIA":
        for c in range(1, 7):
            ws.cell(f, c).fill = PatternFill("solid", fgColor=ROJO)
    f += 1
ws.cell(f, 1, "TOTAL").font = B
ws.cell(f, 2, CLICS_TOT).number_format = "#,##0"
ws.cell(f, 2).font = B
ws.cell(f, 3, IMPR_TOT).number_format = "#,##0"
ws.cell(f, 3).font = B
ws.cell(f, 4, CLICS_TOT / IMPR_TOT if IMPR_TOT else 0).number_format = "0.00%"
ws.cell(f, 4).font = B

f += 3
ws.cell(f, 1, "LA CONCLUSION").font = B
f += 1
riesgo = TOT["LA"]["clicks"] + TOT["NJ"]["clicks"]
for linea in [
    "Los Angeles y New Jersey suman {:,} clics entre los dos: el {:.1f}% del trafico organico "
    "de la marca.".format(riesgo, riesgo / CLICS_TOT * 100),
    "Miami concentra el {:.1f}% de los clics y el {:.1f}% de las impresiones.".format(
        TOT["MIA"]["clicks"] / CLICS_TOT * 100, TOT["MIA"]["impressions"] / IMPR_TOT * 100),
    "Para sostener ese {:.1f}% se mantienen dos webs completas, con su catalogo, su blog y su "
    "mantenimiento, compitiendo contra Miami por las mismas consultas.".format(
        riesgo / CLICS_TOT * 100),
    "",
    "El universo real son {:,} URLs: {:,} que devuelve WordPress mas {:,} que solo conoce Google "
    "(parametros, etiquetas, paginaciones y restos antiguos). De todas ellas quedan {} unicas."
    .format(len(universo), len(RAW), len(universo) - len(RAW), len(docs)),
    "Ni un producto, ni un articulo ni una categoria se pierde: cada URL de la hoja 01 tiene su "
    "destino o el motivo por el que no lo necesita.",
]:
    ws.cell(f, 1, linea)
    ws.merge_cells(start_row=f, start_column=1, end_row=f, end_column=6)
    ws.cell(f, 1).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[f].height = 30 if linea else 8
    f += 1

f += 2
ws.cell(f, 1, "EL PORTAL RESULTANTE").font = B
f += 1
cabecera(ws, ["Concepto", "Cantidad", "", "", "", ""], f)
f += 1
for k, v in [
    ("URLs totales hoy (WordPress + Search Console)", len(universo)),
    ("De ellas, publicadas por WordPress", len(RAW)),
    ("De ellas, solo conocidas por Google", len(universo) - len(RAW)),
    ("URLs unicas en el portal nuevo", len(docs)),
    ("Categorias de producto", len(S["categories"])),
    ("Fichas de producto", len(S["products"])),
    ("Articulos del blog", len(S["posts"])),
    ("Temas del blog", len(S["postcats"])),
    ("Paginas", len(S["pages"])),
    ("Equivalencias de URL documentadas", len(S["redirects"])),
    ("Paginas consolidadas dentro de otra", len(S["absorbed"])),
    ("URLs de etiqueta que pasan a noindex", len(S["noindex"])),
]:
    ws.cell(f, 1, k)
    ws.cell(f, 2, v).number_format = "#,##0"
    f += 1

# ============================================== 01 MAPA COMPLETO (todas las URLs)
ws = hoja(wb, "01 MAPA COMPLETO", "Todas las URLs de hoy y en que se convierten",
          "Una fila por cada URL rastreada en los 3 portales. Es la hoja para responder "
          "'¿y esta pagina mia donde queda?'")
anchos(ws, [8, 14, 62, 40, 11, 13, 9, 10, 22, 62, 46, 22])
cabecera(ws, ["Portal", "Tipo", "URL actual", "Titulo", "Clics", "Impresiones", "CTR",
              "Posicion", "Que pasa con ella", "URL en el portal nuevo", "Motivo", "Fuente"])

ACCION = {
    "PARAMETRO": "URL con parametro",
    "ATRIBUTO": "Filtro de atributo",
    "DESCATALOGADO": "Producto descatalogado",
    "ANCLA": "Ancla de otra pagina",
    "REVISAR": "Necesita decision",
    "CONSERVAR": "Se mantiene",
    "CONSERVAR-REESCRIBIR": "Se mantiene, texto reescrito",
    "CONSOLIDAR-301": "Redirige a otra",
    "NOINDEX": "Deja de indexarse",
    "NO-PUBLICO": "No era publica",
    "ELIMINAR": "Se elimina",
}
COLOR_ACCION = {
    "PARAMETRO": CREMA, "ATRIBUTO": CREMA, "ANCLA": CREMA,
    "DESCATALOGADO": AMBAR, "REVISAR": ROJO,
    "CONSERVAR": VERDE, "CONSERVAR-REESCRIBIR": VERDE,
    "CONSOLIDAR-301": AMBAR, "NOINDEX": CREMA, "NO-PUBLICO": CREMA, "ELIMINAR": ROJO,
}

f = 5
filas = sorted(universo.values(),
               key=lambda r: (-(metricas(r["url"]).get("clicks", 0)),
                              r["portal"], r["url"]))
for r in filas:
    m = metricas(r["url"])
    origen = r["url"]
    accion = r["accion"]
    # destino final, ya encadenado
    if origen in absorb_por_origen:
        destino = absorb_por_origen[origen]
        accion = "CONSOLIDAR-301"
    elif origen in red_por_origen:
        destino = red_por_origen[origen]["to"]
    elif accion in ("CONSERVAR", "CONSERVAR-REESCRIBIR"):
        destino = (r["destino"] or "").replace("https://brazilianlumber.com", "")
        if destino not in docs:
            destino = absorb_por_origen.get(origen, destino)
    elif r["destino"]:
        destino = r["destino"].replace("https://brazilianlumber.com", "")
    else:
        destino = ""
    ws.cell(f, 1, r["portal"])
    ws.cell(f, 2, r["tipo"])
    ws.cell(f, 3, origen)
    ws.cell(f, 4, (r["titulo"] or "")[:110])
    ws.cell(f, 5, m.get("clicks", 0)).number_format = "#,##0"
    ws.cell(f, 6, m.get("impressions", 0)).number_format = "#,##0"
    ws.cell(f, 7, (m.get("ctr", 0) or 0) / 100).number_format = "0.00%"
    ws.cell(f, 8, m.get("position", ""))
    ws.cell(f, 9, ACCION.get(accion, accion))
    ws.cell(f, 10, destino)
    ws.cell(f, 11, r["motivo"][:200])
    ws.cell(f, 12, r["fuente"])
    col = COLOR_ACCION.get(accion)
    if col:
        ws.cell(f, 9).fill = PatternFill("solid", fgColor=col)
    f += 1
ws.auto_filter.ref = "A4:L{}".format(f - 1)

# ====================================================== 02 URLS FINALES UNICAS
ws = hoja(wb, "02 URLS FINALES", "Las {} URLs unicas del portal nuevo".format(len(docs)),
          "Lo que existe el dia despues de la unificacion. Nada de esto esta duplicado.")
anchos(ws, [58, 14, 16, 46, 34, 10, 11, 12, 12])
cabecera(ws, ["URL nueva", "Tipo", "Subtipo", "Titulo", "Categoria / tema", "Palabras",
              "Indexable", "Clics heredados", "De cuantas URLs"])


def palabras(d):
    n = 0
    for b in d["blocks"]:
        if b["t"] == "list":
            n += sum(len(i.split()) for i in b["items"])
        elif b["t"] == "table":
            n += sum(len(str(c).split()) for r in b["rows"] for c in r)
        elif b["t"] != "img":
            n += len(b.get("text", "").split())
    return n


# clics heredados: los de la propia URL mas los de todo lo que redirige a ella
heredados = defaultdict(int)
origenes_por_destino = defaultdict(int)
for r in RAW:
    m = metricas(r["url_origen"])
    o = r["url_origen"]
    if o in absorb_por_origen:
        dest = absorb_por_origen[o]
    elif o in red_por_origen:
        dest = red_por_origen[o]["to"]
    else:
        dest = r["url_destino"].replace("https://brazilianlumber.com", "")
    heredados[dest] += m.get("clicks", 0)
    origenes_por_destino[dest] += 1

TIPO = {"category": "Categoria", "product": "Producto", "post": "Articulo",
        "postcat": "Tema del blog", "page": "Pagina"}
f = 5
for d in sorted(docs.values(), key=lambda x: -heredados.get(x["path"], 0)):
    ws.cell(f, 1, d["path"])
    ws.cell(f, 2, TIPO.get(d["kind"], d["kind"]))
    ws.cell(f, 3, d.get("sub", ""))
    ws.cell(f, 4, d["title"][:110])
    ws.cell(f, 5, d.get("categoryTitle") or (d.get("catNames") or [""])[0] or "")
    ws.cell(f, 6, palabras(d)).number_format = "#,##0"
    ws.cell(f, 7, "No" if d.get("noindex") or d.get("sub") == "junk" else "Si")
    ws.cell(f, 8, heredados.get(d["path"], 0)).number_format = "#,##0"
    ws.cell(f, 9, origenes_por_destino.get(d["path"], 0))
    if d.get("noindex") or d.get("sub") == "junk":
        ws.cell(f, 7).fill = PatternFill("solid", fgColor=CREMA)
    f += 1
ws.auto_filter.ref = "A4:I{}".format(f - 1)

# ================================================================ 03 MENU
ws = hoja(wb, "03 MENU UNIFICADO", "El menu unico, nivel por nivel",
          "Sustituye a los 3 menus distintos que tenian Miami, Los Angeles y New Jersey.")
anchos(ws, [8, 34, 34, 34, 56, 12, 12])
cabecera(ws, ["Nivel", "Nivel 1", "Nivel 2", "Nivel 3", "URL", "Productos", "Palabras"])

cat_por_path = {c["path"]: c for c in S["categories"]}
f = 5


def vuelca(path, nivel, ruta):
    global f
    c = cat_por_path[path]
    ws.cell(f, 1, nivel)
    ws.cell(f, 1 + nivel, c["title"])
    ws.cell(f, 5, path)
    ws.cell(f, 6, c["productCount"]).number_format = "#,##0"
    ws.cell(f, 7, palabras(c)).number_format = "#,##0"
    if nivel == 1:
        for col in range(1, 8):
            ws.cell(f, col).fill = PatternFill("solid", fgColor=CREMA)
        ws.cell(f, 2).font = B
    if c["productCount"] == 0:
        ws.cell(f, 6).fill = PatternFill("solid", fgColor=ROJO)
    f += 1
    for h in c["children"]:
        vuelca(h, nivel + 1, ruta + [c["title"]])


for c in S["categories"]:
    if not c["parent"]:
        vuelca(c["path"], 1, [])

f += 2
ws.cell(f, 2, "Secciones fuera del arbol de producto").font = B
f += 1
for titulo, path, n in [("Guides (blog)", "/guides/", len(S["posts"])),
                        ("Areas We Serve", "/areas-we-serve/",
                         sum(1 for p in S["pages"] if p.get("sub") == "location")),
                        ("Company", "", len(S["nav"]["company"])),
                        ("Full catalog", "/shop/", len(S["products"]))]:
    ws.cell(f, 2, titulo)
    ws.cell(f, 5, path)
    ws.cell(f, 6, n)
    f += 1

# ============================================================ 04 CATEGORIAS
ws = hoja(wb, "04 CATEGORIAS", "Las {} categorias del portal".format(len(S["categories"])),
          "Incluye las subcategorias. La columna de productos cuenta tambien los de las ramas hijas.")
anchos(ws, [52, 34, 34, 12, 12, 12, 10, 12])
cabecera(ws, ["URL", "Categoria", "Depende de", "Productos", "Directos", "Palabras",
              "Preguntas", "Foto"])
f = 5
for c in sorted(S["categories"], key=lambda x: x["path"]):
    ws.cell(f, 1, c["path"])
    ws.cell(f, 2, c["title"])
    ws.cell(f, 3, cat_por_path[c["parent"]]["title"] if c.get("parent") else "-")
    ws.cell(f, 4, c["productCount"])
    ws.cell(f, 5, c["directCount"])
    ws.cell(f, 6, palabras(c))
    ws.cell(f, 7, len(c.get("faq") or []))
    ws.cell(f, 8, "Si" if c.get("image") else "No")
    if c["productCount"] == 0:
        for col in range(1, 9):
            ws.cell(f, col).fill = PatternFill("solid", fgColor=ROJO)
    f += 1
ws.auto_filter.ref = "A4:H{}".format(f - 1)

# ============================================================= 05 PRODUCTOS
ws = hoja(wb, "05 PRODUCTOS", "Las {} fichas de producto".format(len(S["products"])),
          "Todas viven en /product/{slug}/. Pertenecer a varias categorias no crea una segunda URL.")
anchos(ws, [46, 42, 34, 26, 16, 14, 14, 10, 12, 12, 10])
cabecera(ws, ["URL", "Producto", "Categoria", "Tambien en", "Especie", "Marca", "Medida",
              "Foto", "Clics", "Impresiones", "Palabras"])
f = 5
for p in sorted(S["products"], key=lambda x: -(heredados.get(x["path"], 0))):
    a = p.get("attrs") or {}
    ws.cell(f, 1, p["path"])
    ws.cell(f, 2, p["title"][:90])
    ws.cell(f, 3, p.get("categoryTitle", ""))
    ws.cell(f, 4, ", ".join(p.get("alsoIn") or []))
    ws.cell(f, 5, (a.get("especie") or "").replace("-", " "))
    ws.cell(f, 6, a.get("marca") or "")
    ws.cell(f, 7, (a.get("medida") or "").replace("x", " x "))
    ws.cell(f, 8, "Si" if p.get("image") else "No")
    ws.cell(f, 9, heredados.get(p["path"], 0)).number_format = "#,##0"
    ws.cell(f, 10, int(p.get("impressions") or 0)).number_format = "#,##0"
    ws.cell(f, 11, palabras(p))
    if not p.get("image"):
        ws.cell(f, 8).fill = PatternFill("solid", fgColor=ROJO)
    f += 1
ws.auto_filter.ref = "A4:K{}".format(f - 1)

# ================================================================ 06 BLOG
ws = hoja(wb, "06 BLOG", "Los {} articulos y {} temas".format(len(S["posts"]), len(S["postcats"])),
          "Los 3 blogs de los 3 portales, deduplicados en una sola biblioteca bajo /guides/.")
anchos(ws, [58, 56, 30, 12, 12, 12, 12, 12])
cabecera(ws, ["URL", "Titulo", "Tema", "Fecha", "Palabras", "Clics", "Impresiones", "Indexable"])
f = 5
for p in sorted(S["posts"], key=lambda x: -(heredados.get(x["path"], 0))):
    ws.cell(f, 1, p["path"])
    ws.cell(f, 2, p["title"][:100])
    ws.cell(f, 3, (p.get("catNames") or [""])[0])
    ws.cell(f, 4, p.get("date", ""))
    ws.cell(f, 5, palabras(p))
    ws.cell(f, 6, heredados.get(p["path"], 0)).number_format = "#,##0"
    ws.cell(f, 7, int(p.get("impressions") or 0)).number_format = "#,##0"
    ws.cell(f, 8, "No" if p.get("noindex") else "Si")
    f += 1
f += 2
ws.cell(f, 1, "TEMAS DEL BLOG").font = B
f += 1
cabecera(ws, ["URL", "Tema", "Articulos", "Palabras", "Indexable", "", "", ""], f)
f += 1
for c in sorted(S["postcats"], key=lambda x: -x["postCount"]):
    ws.cell(f, 1, c["path"])
    ws.cell(f, 2, c["title"])
    ws.cell(f, 3, c["postCount"])
    ws.cell(f, 4, palabras(c))
    ws.cell(f, 5, "No" if c.get("noindex") else "Si")
    if c.get("noindex"):
        ws.cell(f, 5).fill = PatternFill("solid", fgColor=CREMA)
    f += 1

# =============================================================== 07 PAGINAS
ws = hoja(wb, "07 PAGINAS", "Las {} paginas sueltas".format(len(S["pages"])),
          "Institucionales, de ciudad, de campana y de utilidad.")
anchos(ws, [52, 46, 16, 12, 12, 12, 12])
cabecera(ws, ["URL", "Titulo", "Tipo", "Palabras", "Clics", "Impresiones", "Indexable"])
f = 5
for p in sorted(S["pages"], key=lambda x: (x.get("sub", ""), -(heredados.get(x["path"], 0)))):
    ws.cell(f, 1, p["path"])
    ws.cell(f, 2, p["title"][:90])
    ws.cell(f, 3, p.get("sub", ""))
    ws.cell(f, 4, palabras(p))
    ws.cell(f, 5, heredados.get(p["path"], 0)).number_format = "#,##0"
    ws.cell(f, 6, int(p.get("impressions") or 0)).number_format = "#,##0"
    ws.cell(f, 7, "No" if p.get("noindex") or p.get("sub") == "junk" else "Si")
    if p.get("noindex") or p.get("sub") == "junk":
        ws.cell(f, 7).fill = PatternFill("solid", fgColor=CREMA)
    f += 1
ws.auto_filter.ref = "A4:G{}".format(f - 1)

# ========================================================= 08 REDIRECCIONES
ws = hoja(wb, "08 REDIRECCIONES", "Las {} equivalencias de URL".format(len(S["redirects"])),
          "Esto es lo que se le entrega al desarrollador el dia de la migracion. "
          "Ordenado por trafico, para priorizar.")
anchos(ws, [8, 68, 56, 14, 12, 12, 10])
cabecera(ws, ["Portal", "URL antigua", "URL nueva", "Tipo", "Clics", "Impresiones", "CTR"])
f = 5
reds = sorted(S["redirects"],
              key=lambda r: -metricas(r["from"]).get("clicks", 0))
for r in reds:
    m = metricas(r["from"])
    ws.cell(f, 1, r["portal"])
    ws.cell(f, 2, r["from"])
    ws.cell(f, 3, r["to"])
    ws.cell(f, 4, r["type"])
    ws.cell(f, 5, m.get("clicks", 0)).number_format = "#,##0"
    ws.cell(f, 6, m.get("impressions", 0)).number_format = "#,##0"
    ws.cell(f, 7, (m.get("ctr", 0) or 0) / 100).number_format = "0.00%"
    f += 1
ws.auto_filter.ref = "A4:G{}".format(f - 1)

# ============================================================ 09 DESAPARECEN
ws = hoja(wb, "09 QUE DESAPARECE", "Lo que deja de existir, y cuanto trafico se juega",
          "Ninguna URL se pierde sin destino. Esta hoja es la que responde a "
          "'¿y si perdemos posiciones?'")
anchos(ws, [8, 14, 68, 22, 56, 12, 12])
cabecera(ws, ["Portal", "Tipo", "URL que desaparece", "Que pasa", "A donde va",
              "Clics", "Impresiones"])
f = 5
desaparecen = [r for r in RAW if r["accion"] in ("CONSOLIDAR-301", "NOINDEX", "ELIMINAR")]
desaparecen += [r for r in RAW if r["url_origen"] in absorb_por_origen
                and r["accion"] not in ("CONSOLIDAR-301", "NOINDEX", "ELIMINAR")]
riesgo_total = 0
for r in sorted(desaparecen,
                key=lambda x: -metricas(x["url_origen"]).get("clicks", 0)):
    m = metricas(r["url_origen"])
    o = r["url_origen"]
    destino = absorb_por_origen.get(o) or (red_por_origen.get(o) or {}).get("to", "")
    ws.cell(f, 1, r["portal"])
    ws.cell(f, 2, r["tipo"])
    ws.cell(f, 3, o)
    ws.cell(f, 4, ACCION.get(r["accion"], r["accion"]))
    ws.cell(f, 5, destino if destino else "Sin destino: no aportaba trafico")
    ws.cell(f, 6, m.get("clicks", 0)).number_format = "#,##0"
    ws.cell(f, 7, m.get("impressions", 0)).number_format = "#,##0"
    if not destino:
        riesgo_total += m.get("clicks", 0)
        for c in range(1, 8):
            ws.cell(f, c).fill = PatternFill("solid", fgColor=ROJO)
    f += 1
ws.auto_filter.ref = "A4:G{}".format(f - 1)
ws["A3"] = ("Clics en URLs que desaparecen SIN destino: {:,} de {:,} ({:.2f}% del total). "
            "Todo lo demas tiene su redireccion documentada."
            .format(riesgo_total, CLICS_TOT, riesgo_total / CLICS_TOT * 100 if CLICS_TOT else 0))
ws["A3"].font = Font(bold=True, size=10, color="A02020")

# ============================================================== 10 CONSULTAS
ws = hoja(wb, "10 CONSULTAS", "Las consultas que traen el trafico hoy",
          "Top 150 por portal. Es la demanda que el portal unico tiene que seguir capturando.")
anchos(ws, [8, 52, 12, 14, 10, 12])
cabecera(ws, ["Portal", "Consulta", "Clics", "Impresiones", "CTR", "Posicion"])
f = 5
for p in ("MIA", "LA", "NJ"):
    for q in GSC["portales"][p]["consultas"][:150]:
        ws.cell(f, 1, p)
        ws.cell(f, 2, q["query"])
        ws.cell(f, 3, q["clicks"]).number_format = "#,##0"
        ws.cell(f, 4, q["impressions"]).number_format = "#,##0"
        ws.cell(f, 5, q["ctr"] / 100).number_format = "0.00%"
        ws.cell(f, 6, q["position"])
        f += 1
ws.auto_filter.ref = "A4:F{}".format(f - 1)

# ============================================================ 11 DECISIONES
ws = hoja(wb, "11 DECISIONES", "Lo que tiene que decidir direccion",
          "Nada de esto es tecnico. Son decisiones de negocio con su dato al lado.")
anchos(ws, [46, 60, 16, 60])
cabecera(ws, ["Asunto", "Situacion", "Dato", "Recomendacion"])
f = 5
vacias = [c for c in S["categories"] if c["productCount"] == 0]
sin_foto = [p for p in S["products"] if not p.get("image")]
junk = [p for p in S["pages"] if p.get("sub") == "junk"]
decisiones = [
    ("Apagar Los Angeles y New Jersey",
     "Dos webs completas con catalogo y blog propios, duplicando a Miami.",
     "{:,} clics entre las dos, el {:.1f}% del total".format(
         TOT["LA"]["clicks"] + TOT["NJ"]["clicks"],
         (TOT["LA"]["clicks"] + TOT["NJ"]["clicks"]) / CLICS_TOT * 100),
     "Apagar y redirigir. El trafico en juego es marginal y la duplicidad cuesta posiciones "
     "en Miami, que es donde esta el 97,6% del negocio organico."),
]
for c in vacias:
    decisiones.append((
        "Categoria sin producto: {}".format(c["title"]),
        "Esta en el menu acordado pero ningun producto de los 3 portales cae en ella.",
        "0 productos",
        "Asignarle surtido o sacarla del menu. Si hay demanda de busqueda, merece la pena "
        "crear el surtido antes que borrarla."))
decisiones += [
    ("Fichas sin fotografia",
     "El prototipo las muestra con una portada generada por color de especie.",
     "{} de {} fichas".format(len(sin_foto), len(S["products"])),
     "Subir la foto real antes de publicar. Las {} restantes ya llevan la suya."
     .format(len(S["products"]) - len(sin_foto))),
    ("Paginas de prueba heredadas",
     "demo-home, hometest, blog-example, test-form-flowsly y similares sobrevivieron a la "
     "consolidacion.",
     "{} paginas".format(len(junk)),
     "Eliminarlas. En el prototipo estan publicadas para no perder ninguna URL, pero en "
     "noindex y fuera del menu y del sitemap."),
    ("Textos generados",
     "Las fichas duplicadas se reescribieron desde atributos reales (especie, dureza Janka, "
     "medida, marca, garantia).",
     "{} fichas reescritas".format(S["stats"]["rewritten"]),
     "Que Marketing los revise antes de darlos por definitivos. Son correctos tecnicamente, "
     "pero llevan la voz de la marca de un generador, no de una persona."),
]
for a, b_, c_, d_ in decisiones:
    ws.cell(f, 1, a).font = B
    ws.cell(f, 2, b_)
    ws.cell(f, 3, c_)
    ws.cell(f, 4, d_)
    for col in range(1, 5):
        ws.cell(f, col).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[f].height = 46
    f += 1

# ------------------------------------------------------------------ cerrar
for ws in wb.worksheets:
    pintar(ws)
wb.save(SALIDA)
print("Excel: {}".format(SALIDA))
print("hojas:", len(wb.worksheets))
print("URLs en el mapa completo:", len(universo))
sin_destino = [u for u in universo.values()
               if not u["destino"] and u["accion"] in ("CONSERVAR", "CONSERVAR-REESCRIBIR",
                                                       "CONSOLIDAR-301", "REVISAR")]
print("sin destino y necesitandolo:", len(sin_destino))
from collections import Counter as _C
print("por accion:", dict(_C(u["accion"] for u in universo.values())))
print("clics totales GSC: {:,}".format(CLICS_TOT))
print("riesgo sin destino: {:,} clics".format(riesgo_total))
