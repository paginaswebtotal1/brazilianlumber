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

def grado(slug, titulo):
    b = f"{slug} {titulo}".lower()
    out = [n for k, n in GRADO if k in b]
    return out[0] if out else None

# ---------- clasificador a la taxonomia ----------
PISTAS = [
 (r"deck[- ]?tile", "decking/deck-tiles"),
 (r"joist|pedestal|substructure|grad\b|sleeper", "accessories/substructure"),
 (r"fastener|screw|plug|clip|bit|drill|bolt|nail", "accessories/fasteners"),
 (r"oil|sealer|seal\b|finish|stain|coat|brighten|clean|wisecoat|glue", "accessories/finishes-sealers"),
 (r"cable|railing|handrail|baluster", "accessories/railing-cable"),
 (r"wall[- ]?panel|cladding|siding|shiplap|slat[- ]?wall", "cladding-siding/wood-wall-panels"),
 (r"batten|louver", "cladding-siding/battens-louvers"),
 (r"fence|fencing", "fencing-gates/wood"),
 (r"\bgate\b", "fencing-gates/gates"),
 (r"floor", "flooring/solid-hardwood"),
 (r"slab|live[- ]?edge", "slabs"),
 (r"turf|artificial[- ]?grass", "landscaping/artificial-turf"),
 (r"\bivy\b", "landscaping/artificial-ivy"),
 (r"bamboo", "decking/bamboo"),
 (r"\bpvc\b", "decking/pvc"),
 (r"thermal|thermo|durathermo|ayous", "decking/thermally-modified"),
 (r"composite", "decking/composite"),
 (r"deck", "decking/tropical-hardwood"),
 (r"lumber|timber|board", "lumber/tropical-hardwood"),
]
MARCA_RUTA = {
 "trex": "decking/composite/trex", "timbertech": "decking/composite/timbertech",
 "azek": "decking/composite/azek", "moistureshield": "decking/composite/moistureshield",
 "deckotech": "decking/composite/deckotech", "zuri": "decking/composite/zuri",
 "newtechwood": "decking/composite/newtechwood", "armadillo": "decking/composite/armadillo",
 "calibamboo": "decking/bamboo", "grad": "accessories/substructure",
 "wisewrap": "accessories/substructure",
}
DOMESTICAS = {"red-oak", "white-oak", "maple", "walnut", "sapele", "mahogany",
              "santos-mahogany", "teak"}
BLANDAS = {"cedar", "cypress", "douglas-fir", "spruce", "pine", "redwood"}

def clasificar(slug, titulo, texto, esp, mrc, med):
    b = f"{slug} {titulo}".lower()
    # 1. marca manda cuando es una linea de composite/PVC
    if mrc and mrc in MARCA_RUTA:
        r = MARCA_RUTA[mrc]
        if mrc == "deckwise":
            pass
        elif re.search(r"pvc", b) and mrc in ("azek", "timbertech", "moistureshield", "trex"):
            return "decking/pvc"
        else:
            return r
    if mrc == "deckwise":
        if re.search(r"oil|sealer|coat|clean|brighten|finish", b):
            return "accessories/finishes-sealers"
        if re.search(r"clean|brighten", b):
            return "accessories/maintenance"
        return "accessories/fasteners"
    # 2. mapa explicito de slugs de categoria antigua
    if slug in MAP:
        return MAP[slug]
    # 3. especie tropical de decking
    if esp in ESPECIE and not re.search(r"wall[- ]?panel|floor|slab|fence|tile", b):
        if med and med.startswith(("2x", "4x", "6x", "8x")) and "deck" not in b:
            return "lumber/tropical-hardwood"
        return ESPECIE[esp]
    # 4. pistas por palabra clave
    for rx, ruta in PISTAS:
        if re.search(rx, b):
            if ruta == "lumber/tropical-hardwood":
                if esp in DOMESTICAS:
                    return "lumber/domestic-hardwood"
                if esp in BLANDAS:
                    return "lumber/softwood"
            if ruta == "decking/tropical-hardwood" and esp in ESPECIE:
                return ESPECIE[esp]
            return ruta
    # 5. por especie sola
    if esp in DOMESTICAS:
        return "lumber/domestic-hardwood"
    if esp in BLANDAS:
        return "lumber/softwood"
    if esp in ESPECIE:
        return ESPECIE[esp]
    return "accessories"

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
            "real": MEDIDAS.get(med, (None, None))[0] if med else None,
            "uso": MEDIDAS.get(med, (None, None))[1] if med else None,
        }
        d["cat"] = clasificar(d["slug"], d["titulo"], d["texto"], esp, mrc, med)
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
