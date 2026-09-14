# -*- coding: utf-8 -*-
"""p16 - Verificador de coherencia del mapa.

Las cuatro cosas que aparecieron revisando a mano (el PDF que iba a
/accessories/, la portada que iba a una subpagina, el contenido duplicado y las
436 filas que decian "se mantiene" apuntando a otra URL) tienen algo en comun:
ninguna era un fallo de datos, todas eran una CONTRADICCION interna que se veia
leyendo dos columnas juntas.

Asi que en vez de seguir mirando filas sueltas, esto comprueba invariantes.
Cada regla es una afirmacion que el mapa deberia cumplir siempre; si falla, algo
esta mal aunque el dato parezca razonable por separado.

Salida: data/coherencia.json + AUDITORIA DE COHERENCIA.md
"""
import json, re, sys, pathlib
from collections import Counter, defaultdict

AQUI = pathlib.Path(__file__).resolve().parent
ROOT = AQUI.parent
D = ROOT / "data"
HOST = "https://brazilianlumber.com"

src = (AQUI / "p10_excel.py").read_text(encoding="utf-8").split("wb = Workbook()")[0]
src = src.replace("Path(__file__).resolve().parent.parent", "pathlib.Path(r'{}')".format(ROOT))
src = src.replace("Path(__file__).resolve().parent", "pathlib.Path(r'{}')".format(AQUI))
ns = {"pathlib": pathlib}
exec(src, ns)
universo = ns["universo"]
metricas = ns["metricas"]

S = json.load(open(D / "site.json", encoding="utf-8"))
COLL = ("categories", "products", "posts", "postcats", "pages")
docs = {d["path"]: d for c in COLL for d in S[c]}
RUTAS_APP = {"/", "/shop/", "/guides/", "/search/", "/redirect-map/"}
vivos = set(docs) | RUTAS_APP
noindex = {p for p, d in docs.items() if d.get("noindex") or d.get("sub") == "junk"}

SIN_DESTINO_OK = {"FICHERO", "NO-PUBLICO", "NOINDEX", "ELIMINAR"}
CON_DESTINO = {"CONSOLIDAR-301", "CONSERVAR-MUEVE", "ANCLA", "PARAMETRO",
               "ATRIBUTO", "DESCATALOGADO", "REVISAR"}


def ruta(u):
    if not u:
        return None
    r = u.replace(HOST, "")
    return r if r.startswith("/") else None


def clics(x):
    return metricas(x["url"]).get("clicks", 0)


fallos = defaultdict(list)


def marca(regla, x, extra=""):
    fallos[regla].append({"url": x["url"], "accion": x["accion"],
                          "destino": x.get("destino"), "clics": clics(x), "nota": extra})


# ------------------------------------------------------------------ reglas
for x in universo.values():
    a = x["accion"]
    d = x.get("destino")
    rd, ru = ruta(d), ruta(x["url"])

    # 1. Si la accion exige destino, tiene que haberlo.
    if a in CON_DESTINO and not d:
        marca("1. Dice que redirige pero no tiene destino", x)

    # 2. Si dice que se elimina, no puede tener destino.
    if a == "ELIMINAR" and d:
        marca("2. Dice que se elimina pero tiene destino", x)

    # 3. Si dice que se mantiene, el destino tiene que ser ella misma.
    if a in ("CONSERVAR", "CONSERVAR-REESCRIBIR") and rd and ru and rd.rstrip("/") != ru.rstrip("/"):
        marca("3. Dice que se mantiene pero apunta a otra URL", x)

    # 4. El destino tiene que existir en el portal.
    if rd and rd not in vivos:
        marca("4. El destino no existe en el portal nuevo", x, rd)

    # 5. Nada debe redirigir a una pagina noindex: es tirar el trafico.
    #
    # Con dos excepciones legitimas, que si no el aviso es ruido:
    #   - Una URL con parametro que va a su PROPIA version limpia. El carrito
    #     es noindex a proposito, y /checkout/?add-to-cart=... tiene que llevar
    #     al carrito, no a otro sitio.
    #   - El ancla, por lo mismo.
    _limpia = ruta(x["url"].split("?")[0].split("#")[0])
    _es_su_propia_base = _limpia and rd and _limpia.rstrip("/") == rd.rstrip("/")
    # Tercera excepcion: la misma pagina cambiando de dominio. El carrito de Los
    # Angeles va al carrito del portal unico, y que el carrito sea noindex es
    # una decision, no un error.
    _mismo_slug = False
    if rd:
        _o = x["url"].split("?")[0].split("#")[0].rstrip("/").rsplit("/", 1)[-1]
        _d = rd.rstrip("/").rsplit("/", 1)[-1]
        _mismo_slug = bool(_o) and _o == _d
    _es_su_propia_base = _es_su_propia_base or _mismo_slug
    if rd and rd in noindex and a in CON_DESTINO and not _es_su_propia_base:
        marca("5. Redirige a una pagina que esta en noindex", x, rd)

    # 6. Una redireccion a si misma no sirve de nada.
    if rd and ru and a in CON_DESTINO and rd.rstrip("/") == ru.rstrip("/"):
        marca("6. Redireccion a si misma", x)

    # 7. Ningun destino puede apuntar a los dominios que se apagan.
    if d and ("brazilianlumberlosangeles.com" in d or "brazilianlumbernewyork.com" in d):
        marca("7. El destino apunta a un dominio que se apaga", x, d)

    # 8. Una URL con trafico no deberia caer en un destino generico. Salvo las
    # portadas: que la raiz de un dominio vaya a la raiz es lo correcto.
    # La raiz de un dominio, con o sin parametros de campana, va a la raiz: es
    # lo correcto y no debe avisar.
    _base = x["url"].split("?")[0].split("#")[0].rstrip("/")
    _es_raiz = _base in ("https://brazilianlumber.com",
                         "https://brazilianlumberlosangeles.com",
                         "https://brazilianlumbernewyork.com",
                         "http://brazilianlumber.com",
                         "http://brazilianlumberlosangeles.com",
                         "http://brazilianlumbernewyork.com") or ru in (None, "/", "")
    if rd in ("/shop/", "/") and clics(x) >= 20 and a in CON_DESTINO and not _es_raiz:
        marca("8. URL con trafico que cae en un destino generico", x, rd)

    # 9. Las URLs finales tienen que estar bien formadas.
    if rd and (" " in rd or rd != rd.lower() or "//" in rd.strip("/")):
        marca("9. URL de destino mal formada", x, rd)

    # 10. Un fichero no redirige a una pagina.
    if a == "FICHERO" and d:
        marca("10. Un fichero con destino de pagina", x, d)

# ---- reglas sobre el portal resultante
for p, d in docs.items():
    # 11. Todo producto tiene que colgar de una categoria que exista.
    if d["kind"] == "product":
        cat = d.get("category")
        if not cat or cat not in docs:
            fallos["11. Producto en una categoria que no existe"].append(
                {"url": p, "accion": "", "destino": cat, "clics": d.get("clicks") or 0, "nota": ""})
    # 12. Toda subcategoria tiene que tener padre existente.
    if d["kind"] == "category" and d.get("parent") and d["parent"] not in docs:
        fallos["12. Categoria con un padre que no existe"].append(
            {"url": p, "accion": "", "destino": d["parent"], "clics": 0, "nota": ""})
    # 13. Las rutas tienen que ser limpias.
    if not re.fullmatch(r"/[a-z0-9\-/._]*/", p):
        fallos["13. Ruta con caracteres no limpios"].append(
            {"url": p, "accion": "", "destino": "", "clics": 0, "nota": ""})

# 16. Toda pagina de zona vive en /locations/. Dos rutas para el mismo tipo de
#     pagina es lo que hacia que /fresno/ y /locations/san-diego/ coexistieran.
for p, d in docs.items():
    if d.get("sub") == "location" and not p.startswith("/locations/"):
        fallos["16. Pagina de zona fuera de /locations/"].append(
            {"url": p, "accion": "", "destino": "", "clics": d.get("clicks") or 0, "nota": ""})

# 17. El titulo de una zona tiene que decir que es, no solo el nombre del sitio.
for p, d in docs.items():
    if d.get("sub") == "location" and not any(
            w in d.get("h1", "") for w in ("Lumber", "Decking", "Hardwood")):
        fallos["17. Zona cuyo titulo no dice que es"].append(
            {"url": p, "accion": "", "destino": d.get("h1", ""), "clics": d.get("clicks") or 0,
             "nota": ""})

# 14. Dos paginas distintas con el mismo titulo: candidatas a duplicado.
por_titulo = defaultdict(list)
for p, d in docs.items():
    if not d.get("noindex") and d.get("sub") != "junk":
        por_titulo[(d["kind"], d["title"].strip().lower())].append(p)
for (k, t), rutas in por_titulo.items():
    if len(rutas) > 1:
        fallos["14. Mismo titulo en varias URLs"].append(
            {"url": " | ".join(rutas), "accion": k, "destino": "", "clics": 0, "nota": t[:60]})

# 15. Toda URL con clics tiene que acabar en algo que exista.
for x in universo.values():
    c = clics(x)
    if c >= 5 and not x.get("destino") and x["accion"] not in SIN_DESTINO_OK:
        marca("15. URL con trafico y sin destino", x, "{} clics".format(c))


# ------------------------------------------------------------------ informe
def main():
    total = sum(len(v) for v in fallos.values())
    print("=" * 66)
    print("  {:,} URLs revisadas contra 17 reglas de coherencia".format(len(universo)))
    print("  {} incumplimientos".format(total))
    print("=" * 66)
    print()
    if not fallos:
        print("  Sin incoherencias.")
    for regla in sorted(fallos):
        filas = fallos[regla]
        cl = sum(f["clics"] for f in filas)
        print("{:60s} {:5d}   {} clics".format(regla[:60], len(filas), cl))
    print()
    for regla in sorted(fallos):
        filas = sorted(fallos[regla], key=lambda f: -f["clics"])
        print("\n--- {} ({}) ---".format(regla, len(filas)))
        for f in filas[:12]:
            print("  {:5d} clics  {}".format(f["clics"], f["url"][:78]))
            if f["destino"]:
                print("               -> {} {}".format(str(f["destino"])[:66], f["nota"][:30]))

    json.dump({k: v[:200] for k, v in fallos.items()},
              open(D / "coherencia.json", "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
