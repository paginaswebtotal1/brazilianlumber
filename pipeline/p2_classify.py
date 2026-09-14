# -*- coding: utf-8 -*-
"""p2 - Clasifica cada producto en la taxonomia de destino y detecta atributos.
Salida: data/classified.json
"""
import json, re
from pathlib import Path
from taxonomia import ARBOL, MAP, ESPECIE
from kb import ESPECIES, MARCAS, MEDIDAS

D = Path(__file__).resolve().parent.parent / "data"

# ---------- deteccion de atributos desde el slug y el titulo ----------
DIM = re.compile(r"(?<![0-9])(5[-/]4|1|2|4|6|8)\s*[x×]\s*(2|4|6|8|10|12)(?![0-9])")

def medida(slug, titulo):
    # La tornilleria se nombra calibre x longitud, y la longitud suele llevar
    # fraccion: 8x2" y 8x2-1/2" son productos distintos. Leyendo solo "8x2" los
    # dos salian con la misma ficha.
    base = (slug + " " + titulo).lower()
    if re.search(r"screw|fastener|plug|clip|bolt|nail", base):
        m = re.search(r"(\d{1,2})\s*[x\u00d7]\s*(\d{1,2})(?:\s*[-\s]\s*(\d)[/-](\d))?", base)
        if m:
            largo = m.group(2)
            if m.group(3) and m.group(4):
                largo += "-{}/{}".format(m.group(3), m.group(4))
            return "{}x{}".format(m.group(1), largo)
    for s in (slug.replace("_", "-"), titulo.lower()):
        m = DIM.search(s.replace(" ", ""))
        if m:
            a = m.group(1).replace("-", "/")
            if a == "5/4":
                return f"5/4x{m.group(2)}"
            return f"{a}x{m.group(2)}"
    return None

ALIAS_ESP = {
 "ipe": "ipe", "cumaru": "cumaru", "garapa": "garapa", "jatoba": "jatoba",
 "tigerwood": "tigerwood", "massaranduba": "massaranduba", "piquia": "piquia",
 "teak": "teak", "red-oak": "red-oak", "white-oak": "white-oak", "oak": "red-oak",
 "maple": "maple", "walnut": "walnut", "sapele": "sapele",
 "santos-mahogany": "santos-mahogany", "african-mahogany": "mahogany", "mahogany": "mahogany",
 "cedar": "cedar", "cypress": "cypress", "douglas-fir": "douglas-fir", "fir": "douglas-fir",
 "spruce": "spruce", "pine": "pine", "redwood": "redwood", "ayous": "ayous",
 "bamboo": "bamboo", "durathermo": "ayous",
}
ORDEN_ESP = sorted(ALIAS_ESP, key=len, reverse=True)
ORDEN_MARCA = sorted(MARCAS, key=len, reverse=True)

def especie(slug, titulo, texto):
    base = f"{slug} {titulo}".lower().replace(" ", "-")
    for k in ORDEN_ESP:
        if k in base:
            return ALIAS_ESP[k]
    low = (texto or "")[:900].lower()
    for k in ORDEN_ESP:
        if re.search(r"\b" + k.replace("-", r"[ -]") + r"\b", low):
            return ALIAS_ESP[k]
    return None

def marca(slug, titulo, texto):
    base = f"{slug} {titulo}".lower().replace(" ", "").replace("-", "")
    for k in ORDEN_MARCA:
        if k.replace("-", "") in base:
            return k
    low = (texto or "")[:500].lower().replace(" ", "")
    for k in ORDEN_MARCA:
        if k.replace("-", "") in low:
            return k
    return None

GRADO = [("clear", "Clear"), ("standard", "Standard"), ("select", "Select"),
         ("rough", "Rough Sawn"), ("s4s", "S4S"), ("kd", "Kiln Dried"),
         ("grooved", "Grooved"), ("pregrooved", "Pre-Grooved")]

# Colecciones y gamas comerciales. Dos productos de la misma marca y medida
# pueden ser gamas distintas, con precio y acabado distintos.
COLECCIONES = [
    "enhance naturals", "enhance basics", "transcend lineage", "transcend",
    "select", "signature", "harvest collection", "vintage collection",
    "landmark collection", "arbor collection", "terrain", "prime plus",
    "legacy", "reserve", "vision", "lifestyle", "essence", "prestige",
    "terra collection", "terra", "solara", "grid strong", "silent haven",
    "smooth shield", "harmony", "origens", "jungle", "modern", "refined",
    "enduring", "premier", "classic",
]


def coleccion(slug, titulo):
    """Gama comercial dentro de la marca."""
    b = (slug.replace("-", " ") + " " + titulo).lower()
    for c in sorted(COLECCIONES, key=len, reverse=True):
        if c in b:
            return c.title()
    return None


def largo(slug, titulo):
    """Largo de la tabla en pies, cuando el nombre lo indica (1x6-16)."""
    b = slug + " " + titulo
    m = re.search(r"\d\s*[x\u00d7]\s*\d{1,2}\s*[-\u2013]\s*(8|10|12|14|16|18|20)\b", b.lower())
    if m:
        return int(m.group(1))
    m = re.search(r"\b(8|10|12|14|16|18|20)\s*(?:ft|foot|feet|')\b", b.lower())
    return int(m.group(1)) if m else None


def grado(slug, titulo):
    b = f"{slug} {titulo}".lower()
    out = [n for k, n in GRADO if k in b]
    return out[0] if out else None

# ---------- clasificador a la taxonomia ----------
# ---------------------------------------------------------------- clasificador
#
# ORDEN DE PRIORIDAD. Esto importa mas que los patrones en si.
#
# La primera version daba prioridad a la marca, y fue un error: mandaba TODO lo
# de DeckoTech a decking, incluidas sus vallas, sus puertas, su revestimiento y
# sus lamas. Resultado: 8 categorias del menu se quedaron vacias teniendo
# producto de sobra.
#
# Manda el TIPO de producto. Una valla es una valla, la fabrique quien la
# fabrique. La marca solo decide la subcategoria dentro de ese tipo.

# 1. Tipos de producto, del mas especifico al mas general.
TIPOS = [
    # cerramientos
    (r"\bgate\b|double[- ]gate|single[- ]gate", "fencing-gates/gates"),
    (r"fence|fencing", "fencing-gates"),
    # revestimiento
    (r"batten|louver", "cladding-siding/battens-louvers"),
    (r"wall[- ]?panel|slat[- ]?wall", "cladding-siding/wood-wall-panels"),
    (r"cladding|shiplap|siding|teto[- ]?vinilico|finishing[- ]?trim", "cladding-siding"),
    # suelo y superficies
    (r"deck[- ]?tile", "decking/deck-tiles"),
    (r"floor", "flooring/solid-hardwood"),
    (r"slab|live[- ]?edge", "slabs"),
    # paisajismo
    (r"turf|artificial[- ]?grass", "landscaping/artificial-turf"),
    (r"\bivy\b", "landscaping/artificial-ivy"),
    # accesorios: lo especifico antes que lo general
    (r"cleaner|brightener|brighten|maintenance|wash", "accessories/maintenance"),
    (r"drill|bit\b|cutter|arbor|\btool\b|saw\b|spacer|jig", "accessories/tools"),
    (r"\boil\b|sealer|seal\b|finish|stain|wisecoat|coating|glue|wax", "accessories/finishes-sealers"),
    (r"cable|railing|handrail|baluster|post[- ]?cap", "accessories/railing-cable"),
    (r"joist|pedestal|substructure|sleeper|grad\b|flashing|tape", "accessories/substructure"),
    (r"fastener|screw|plug|clip|bolt|nail|bracket", "accessories/fasteners"),
]

# 2. Subcategoria por marca DENTRO de un tipo, cuando el arbol la tiene.
MARCA_EN_TIPO = {
    "fencing-gates": {"deckotech": "fencing-gates/composite", "trex": "fencing-gates/composite",
                      "timbertech": "fencing-gates/composite"},
    "cladding-siding": {"deckotech": "cladding-siding/composite", "trex": "cladding-siding/composite",
                        "newtechwood": "cladding-siding/composite"},
}

# 3. Marca -> rama de decking, solo cuando el producto NO es de un tipo propio.
MARCA_RUTA = {
    "trex": "decking/composite/trex", "timbertech": "decking/composite/timbertech",
    "azek": "decking/composite/azek", "moistureshield": "decking/composite/moistureshield",
    "deckotech": "decking/composite/deckotech", "zuri": "decking/composite/zuri",
    "newtechwood": "decking/composite/newtechwood", "armadillo": "decking/composite/armadillo",
    "calibamboo": "decking/bamboo",
}

# 4. Maderas termotratadas: la especie decide la subcategoria.
TERMO = [(r"ayous", "decking/thermally-modified/ayous"),
         (r"durathermo", "decking/thermally-modified/durathermo")]

DOMESTICAS = {"red-oak", "white-oak", "maple", "walnut", "sapele", "mahogany",
              "santos-mahogany", "teak"}
BLANDAS = {"cedar", "cypress", "douglas-fir", "spruce", "pine", "redwood"}


def clasificar(slug, titulo, texto, esp, mrc, med):
    b = f"{slug} {titulo}".lower()

    # (a) El mapa explicito de slugs de categoria antigua es la palabra del estudio.
    if slug in MAP:
        return MAP[slug]

    # (b) El TIPO de producto manda sobre la marca.
    for rx, ruta in TIPOS:
        if not re.search(rx, b):
            continue
        # ¿tiene el arbol una subcategoria para esta marca dentro de este tipo?
        if mrc and ruta in MARCA_EN_TIPO and mrc in MARCA_EN_TIPO[ruta]:
            return MARCA_EN_TIPO[ruta][mrc]
        # revestimiento de madera maciza va al nodo de paneles
        if ruta == "cladding-siding" and esp:
            return "cladding-siding/wood-wall-panels"
        return ruta

    # (c) Madera termotratada: la especie decide.
    if re.search(r"thermal|thermo|termo", b):
        for rx, ruta in TERMO:
            if re.search(rx, b):
                return ruta
        return "decking/thermally-modified"

    # (d) Bambu y PVC generico sin marca.
    if re.search(r"bamboo", b):
        return "decking/bamboo"

    # (e) Ahora si, la marca.
    if mrc in MARCA_RUTA:
        return MARCA_RUTA[mrc]
    if mrc == "deckwise":
        return "accessories/fasteners"
    if mrc in ("grad", "wisewrap"):
        return "accessories/substructure"

    # (f) PVC sin marca reconocida.
    if re.search(r"\bpvc\b", b):
        return "decking/pvc"

    # (g) Especie. Una tropical en escuadria de estructura (2x, 4x, 6x) y sin
    # "decking" en el nombre es madera dimensional, no tarima.
    if esp in ESPECIE:
        if med and med.startswith(("2x", "4x", "6x", "8x")) and "deck" not in b:
            return "lumber/tropical-hardwood"
        return ESPECIE[esp]
    if esp in DOMESTICAS:
        return "lumber/domestic-hardwood"
    if esp in BLANDAS:
        return "lumber/softwood"
    if re.search(r"deck", b):
        return "decking"
    if re.search(r"lumber|timber|board", b):
        return "lumber/tropical-hardwood"
    return "accessories"


def secundarias(slug, titulo, principal, mrc):
    """Categorias adicionales en las que el producto tambien debe aparecer.

    La arquitectura del estudio lo contempla: como el producto vive siempre en
    /product/{slug}/, pertenecer a varias categorias NO genera una segunda URL.
    Asi una tarima de PVC de AZEK aparece en la rama de la marca y en la de PVC,
    que es donde la busca el cliente, sin duplicar nada.
    """
    b = f"{slug} {titulo}".lower()
    extra = []
    if re.search(r"\bpvc\b", b) and principal != "decking/pvc":
        extra.append("decking/pvc")
    if re.search(r"composite", b) and principal.startswith("fencing-gates"):
        extra.append("fencing-gates/composite")
    return [e for e in dict.fromkeys(extra) if e != principal]


def main():
    raw = json.load(open(D / "raw.json", encoding="utf-8"))
    surv = [d for d in raw if d["accion"] in ("CONSERVAR", "CONSERVAR-REESCRIBIR")]
    for d in surv:
        if d["tipo"] != "product":
            continue
        esp = especie(d["slug"], d["titulo"], d["texto"])
        mrc = marca(d["slug"], d["titulo"], d["texto"])
        med = medida(d["slug"], d["titulo"])
        d["attr"] = {
            "especie": esp, "marca": mrc, "medida": med,
            "grado": grado(d["slug"], d["titulo"]),
            "coleccion": coleccion(d["slug"], d["titulo"]),
            "largo": largo(d["slug"], d["titulo"]),
            "real": MEDIDAS.get(med, (None, None))[0] if med else None,
            "uso": MEDIDAS.get(med, (None, None))[1] if med else None,
        }
        d["cat"] = clasificar(d["slug"], d["titulo"], d["texto"], esp, mrc, med)
        d["cats_extra"] = secundarias(d["slug"], d["titulo"], d["cat"], mrc)
    json.dump(surv, open(D / "classified.json", "w", encoding="utf-8"), ensure_ascii=False)

    from collections import Counter
    prods = [d for d in surv if d["tipo"] == "product"]
    c = Counter(d["cat"] for d in prods)
    print(f"productos clasificados: {len(prods)}")
    for k, v in sorted(c.items()):
        flag = "" if k in ARBOL else "  <-- FUERA DE ARBOL"
        print(f"  {v:4d}  {k}{flag}")
    print("sin especie:", sum(1 for d in prods if not d["attr"]["especie"]))
    print("sin medida:", sum(1 for d in prods if not d["attr"]["medida"]))

if __name__ == "__main__":
    main()
