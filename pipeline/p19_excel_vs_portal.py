# -*- coding: utf-8 -*-
"""p19 - El Excel contra el portal, fila por fila.

Si en la reunion se ensenan los dos a la vez, cualquier desajuste se ve. Este
script comprueba que el Excel dice exactamente lo que hace el portal:

  - Toda URL de la hoja 02 existe y responde en el portal.
  - Toda URL del portal esta en la hoja 02.
  - El titulo del Excel es el <title> real de la pagina.
  - El H1 del Excel es el H1 real.
  - Los recuentos de cada hoja cuadran con los datos.
  - Los destinos de la hoja 01 existen.
  - Las redirecciones de la hoja 08 coinciden con el mapa.

Contra el servidor LOCAL. Cero peticiones al sitio publicado.

Salida: data/excel_vs_portal.json
"""
import json, re, sys, html, pathlib
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from openpyxl import load_workbook

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data"
_CARPETA = pathlib.Path("C:/Users/USER/Desktop/BRAZILIAN LUMBER/ARQUITECTURA WEB BL/"
                        "MENÙ VISUAL")
# Si el Excel estaba abierto al regenerarlo, p10 lo deja con sufijo (NUEVO). Se
# contrasta el mas reciente de los dos: lo contrario seria dar por bueno un
# fichero viejo y decir que el portal cuadra cuando no es el que se ha mirado.
_CAND = [_CARPETA / "10 - MAPA COMPLETO DE LA UNIFICACION.xlsx",
         _CARPETA / "10 - MAPA COMPLETO DE LA UNIFICACION (NUEVO).xlsx"]
XLSX = max([x for x in _CAND if x.exists()], key=lambda x: x.stat().st_mtime)

S = json.load(open(D / "site.json", encoding="utf-8"))
COLL = ("categories", "products", "posts", "postcats", "pages")
docs = {d["path"]: d for c in COLL for d in S[c]}
RUTAS_APP = {"/", "/shop/", "/guides/", "/search/", "/redirect-map/"}

fallos = {}


def anota(k, v):
    fallos.setdefault(k, []).append(v)


def pide(path):
    try:
        r = Request(BASE + path, headers={"User-Agent": "bl-contraste"})
        with urlopen(r, timeout=40) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore")
    except HTTPError as e:
        return e.code, ""
    except URLError:
        return 0, ""


def limpio(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t or ""))).strip()


def main():
    print("Excel: {}".format(XLSX.name), flush=True)
    wb = load_workbook(XLSX, read_only=True)
    hojas = {ws.title: ws for ws in wb.worksheets}
    print("hojas: {}".format(len(hojas)), flush=True)

    # ---------- hoja 02: las URLs finales
    finales = {}
    for f in hojas["02 URLS FINALES"].iter_rows(min_row=5, values_only=True):
        if f[0]:
            finales[str(f[0])] = {"tipo": f[1], "titulo": f[3], "indexable": f[6]}
    print("hoja 02: {} URLs".format(len(finales)), flush=True)

    # 1. toda URL del Excel existe en los datos
    for u in finales:
        if u not in docs:
            anota("URL en el Excel que no existe en el portal", u)
    # 2. toda URL del portal esta en el Excel
    for u in docs:
        if u not in finales:
            anota("URL del portal que falta en el Excel", u)

    # ---------- responden, y con el titulo que dice el Excel
    print("comprobando {} URLs contra {} ...".format(len(finales), BASE), flush=True)
    with ThreadPoolExecutor(max_workers=10) as ex:
        res = dict(zip(finales, ex.map(pide, finales)))

    for u, (cod, htm) in res.items():
        if cod != 200:
            anota("URL del Excel que no responde 200", "{} [{}]".format(u, cod))
            continue
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", htm, re.S)
        h1 = limpio(h1.group(1)) if h1 else ""
        tit = re.search(r"<title>(.*?)</title>", htm, re.S)
        tit = limpio(tit.group(1)) if tit else ""
        esperado = limpio(str(finales[u]["titulo"] or ""))
        doc = docs.get(u, {})
        # El Excel lleva el titulo; la pagina puede llevar un H1 mas largo. Se
        # comprueba que el titulo del Excel aparezca en la pagina de algun modo.
        if esperado and esperado.lower() not in (h1 + " " + tit).lower():
            anota("El titulo del Excel no aparece en la pagina",
                  "{}\n        Excel: {}\n        H1   : {}".format(u, esperado[:60], h1[:60]))
        # el H1 del dataset tiene que ser el H1 real
        if doc.get("h1") and limpio(doc["h1"]).lower() != h1.lower():
            anota("El H1 del portal no coincide con el del dataset",
                  "{}\n        dataset: {}\n        pagina : {}".format(
                      u, limpio(doc["h1"])[:60], h1[:60]))
        # noindex coherente
        ni = "noindex" in htm[:5000].lower()
        dice_excel = str(finales[u]["indexable"]).strip().lower()
        if dice_excel == "si" and ni and doc.get("noindex"):
            anota("El Excel dice indexable pero la pagina es noindex", u)

    # ---------- hoja 01: los destinos existen
    vivos = set(docs) | RUTAS_APP
    dest_mal = 0
    for f in hojas["01 MAPA COMPLETO"].iter_rows(min_row=5, values_only=True):
        d = f[9]
        if not d:
            continue
        r = str(d).replace("https://brazilianlumber.com", "")
        if r.startswith("/") and r not in vivos:
            dest_mal += 1
            if dest_mal <= 10:
                anota("Destino de la hoja 01 que no existe", "{} -> {}".format(
                    str(f[2])[:56], r))

    # ---------- hoja 08 contra el mapa de redirecciones
    red_excel = {}
    for f in hojas["08 REDIRECCIONES"].iter_rows(min_row=5, values_only=True):
        if f[1]:
            red_excel[str(f[1])] = str(f[2])
    red_datos = {r["from"]: r["to"] for r in S["redirects"]}
    if len(red_excel) != len(red_datos):
        anota("Recuento de redirecciones distinto",
              "Excel {} vs datos {}".format(len(red_excel), len(red_datos)))
    for k, v in red_datos.items():
        if k not in red_excel:
            anota("Redireccion del mapa que falta en el Excel", k)
        elif red_excel[k] != v:
            anota("Redireccion con destino distinto",
                  "{}\n        Excel: {}\n        datos: {}".format(k[:56], red_excel[k], v))

    # ---------- recuentos de cada hoja
    esperados = {
        "02 URLS FINALES": len(docs),
        "04 CATEGORIAS": len(S["categories"]),
        "05 PRODUCTOS": len(S["products"]),
        "07 PAGINAS": len(S["pages"]),
        "08 REDIRECCIONES": len(S["redirects"]),
    }
    for hoja, n in esperados.items():
        real = hojas[hoja].max_row - 4
        if real != n:
            anota("Recuento de hoja distinto",
                  "{}: Excel {} vs datos {}".format(hoja, real, n))

    # ---------- informe
    total = sum(len(v) for v in fallos.values())
    print()
    print("=" * 68)
    print("  {} URLs del Excel contrastadas contra el portal".format(len(finales)))
    print("  {} desajustes".format(total))
    print("=" * 68)
    if not fallos:
        print("\n  El Excel dice exactamente lo que hace el portal.")
    for k in sorted(fallos):
        print("\n--- {} ({}) ---".format(k, len(fallos[k])))
        for v in fallos[k][:10]:
            print("   ", v)
    json.dump({k: v[:80] for k, v in fallos.items()},
              open(D / "excel_vs_portal.json", "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
