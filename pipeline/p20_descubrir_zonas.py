# -*- coding: utf-8 -*-
"""p20 - Descubrir zonas con demanda, en vez de adivinarlas.

p17 comprobo las ciudades que YA estaban en los portales. Eso valida lo que hay,
pero no encuentra lo que falta.

Aqui se le da la vuelta: se usa el endpoint de sugerencias de KeywordTool, que
sale del autocompletado real de Google, y se deja que sea el la lista de
ciudades. Salio al verificar San Pedro: Google no sugiere ni una consulta suya,
pero si sugiere San Leandro (70/mes) y San Luis Obispo (30), que no estaban en
ningun portal.

Salida: data/zonas_descubiertas.json
"""
import json, re, time
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"

KEY = [l.split("=", 1)[1].strip() for l in (ROOT / ".env.local").read_text(encoding="utf-8").splitlines()
       if l.startswith("KEYWORDTOOL_API_KEY")][0]
URL = "https://api.keywordtool.io/v2/search/suggestions/google"

# Semillas: el termino que gana (lumber yard, lumber) cruzado con los estados
# donde la empresa tiene almacen o entrega habitualmente.
SEMILLAS = [
    "lumber yard california", "lumber california", "lumber yard florida",
    "lumber florida", "lumber yard texas", "lumber texas",
    "lumber yard new jersey", "lumber new jersey", "lumber yard new york",
    "lumber new york", "lumber yard georgia", "lumber georgia",
    "lumber yard south carolina", "lumber yard los angeles",
    "lumber yard miami", "lumber yard houston", "lumber yard atlanta",
    "hardwood lumber california", "hardwood lumber florida",
    "ipe decking california", "ipe decking florida", "ipe decking texas",
    "decking supplier california", "decking supplier florida",
]

# Ciudades que ya estan cubiertas, para no contarlas como hallazgo.
def ya_cubiertas():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import ciudades as c
    s = {x.replace("-", " ").lower() for x in c.CIUDADES}
    s |= {v[0].lower() for v in c.CIUDADES.values()}
    try:
        site = json.load(open(D / "site.json", encoding="utf-8"))
        s |= {p["slug"].replace("-", " ").lower() for p in site["pages"]
              if p.get("sub") == "location"}
    except FileNotFoundError:
        pass
    return s


RUIDO = re.compile(r"\b(near me|jobs|hiring|salary|craigslist|home depot|lowes|menards|"
                   r"84 lumber|company|prices?|reviews?|hours|phone|number)\b", re.I)


def pide(semillas):
    p = [("apikey", KEY), ("metrics", "true"), ("metrics_location", 2840),
         ("metrics_language", "en"), ("metrics_network", "googlesearchnetwork"),
         ("output", "json")]
    p += [("keyword[]", s) for s in semillas]
    for intento in range(4):
        try:
            r = httpx.get(URL, params=p, timeout=240)
            if r.status_code == 200:
                return r.json().get("results", {})
            print("   [{}] reintento".format(r.status_code), flush=True)
        except Exception as e:
            print("   {} reintento".format(type(e).__name__), flush=True)
        time.sleep(4 + 4 * intento)
    return {}


def main():
    cubiertas = ya_cubiertas()
    print("{} semillas, {} zonas ya cubiertas".format(len(SEMILLAS), len(cubiertas)), flush=True)

    vistos = {}
    for i in range(0, len(SEMILLAS), 5):
        lote = SEMILLAS[i:i + 5]
        res = pide(lote)
        for semilla, lista in res.items():
            for x in lista or []:
                s = (x.get("string") or "").strip().lower()
                v = x.get("volume") or 0
                if v and s and not RUIDO.search(s):
                    if v > vistos.get(s, 0):
                        vistos[s] = v
        print("  {}/{}  acumulado: {} consultas con volumen".format(
            min(i + 5, len(SEMILLAS)), len(SEMILLAS), len(vistos)), flush=True)

    # se extrae la zona de cada consulta quitando el termino generico
    GENERICO = re.compile(r"\b(lumber yards?|lumber|hardwood|decking|ipe|supplier|"
                          r"wood|deck|in|the|of|and|yard|yards|supply|store|stores)\b", re.I)
    zonas = {}
    for s, v in vistos.items():
        zona = GENERICO.sub(" ", s)
        zona = re.sub(r"[^a-z\s]", " ", zona)
        zona = re.sub(r"\s+", " ", zona).strip()
        if len(zona) < 4 or len(zona.split()) > 4:
            continue
        z = zonas.setdefault(zona, {"volumen": 0, "consultas": []})
        z["volumen"] += v
        z["consultas"].append({"k": s, "v": v})
    for z in zonas.values():
        z["consultas"].sort(key=lambda x: -x["v"])

    nuevas = {k: v for k, v in zonas.items() if k not in cubiertas and v["volumen"] >= 30}
    json.dump({"zonas": zonas, "nuevas": nuevas},
              open(D / "zonas_descubiertas.json", "w", encoding="utf-8"), ensure_ascii=False)

    print()
    print("=" * 70)
    print("  {} consultas con volumen  ->  {} zonas".format(len(vistos), len(zonas)))
    print("  {} zonas con demanda que NO estan cubiertas".format(len(nuevas)))
    print("=" * 70)
    print()
    print("{:28s} {:>9s}   consulta principal".format("ZONA NUEVA", "VOL/MES"))
    print("-" * 70)
    for k, v in sorted(nuevas.items(), key=lambda x: -x[1]["volumen"])[:30]:
        print("{:28s} {:>9d}   {}".format(k[:28], v["volumen"], v["consultas"][0]["k"][:32]))


if __name__ == "__main__":
    main()
