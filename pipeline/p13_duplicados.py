# -*- coding: utf-8 -*-
"""p13 - Deteccion de contenido duplicado, en el origen y en el destino.

El planteamiento: una URL unica no garantiza un CONTENIDO unico. Si dos paginas
distintas dicen lo mismo, Google las trata como duplicado y los motores
generativos no saben cual citar. Da igual lo limpia que sea la arquitectura.

Se miden dos cosas:

  ORIGEN   Los 2.197 documentos de los 3 portales. Cuanto contenido esta
           repetido hoy, y cuanto de esa repeticion es ENTRE portales. Es el
           dato que justifica la unificacion con evidencia y no con intuicion.

  DESTINO  Los documentos del portal nuevo. Aqui la pregunta es incomoda y va
           contra el propio trabajo: el contenido generado, ¿se parece
           demasiado entre si? Si la respuesta es que si, el portal nuevo
           nace con el mismo problema que venia a resolver.

Metodo: TF-IDF sobre n-gramas de palabra y similitud del coseno, por bloques
para no reventar la memoria. Se trabaja sobre el texto ya extraido; no se
vuelve a pedir nada a los portales.

Umbrales:
    >= 0.90  practicamente identico
    >= 0.75  casi duplicado, es un riesgo real
    >= 0.60  parecido, tolerable entre productos de la misma familia

Salida: data/duplicados.json + hojas nuevas en el Excel
"""
import json, re, sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

D = Path(__file__).resolve().parent.parent / "data"
IDENTICO, CASI, PARECIDO = 0.90, 0.75, 0.60
BLOQUE = 400


def normaliza(t):
    t = (t or "").lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def texto_de_bloques(blocks):
    out = []
    for b in blocks or []:
        if b["t"] == "list":
            out.append(" ".join(b["items"]))
        elif b["t"] == "table":
            out.append(" ".join(str(c) for r in b["rows"] for c in r))
        elif b["t"] != "img":
            out.append(b.get("text", ""))
    return " ".join(out)


def pares_similares(textos, ids, umbral=PARECIDO, min_palabras=40):
    """Devuelve los pares por encima del umbral. Por bloques: la matriz
    completa de 2.197 x 2.197 cabe, pero la de 10.000 x 10.000 no, y este
    codigo tiene que seguir sirviendo cuando el catalogo crezca."""
    validos = [i for i, t in enumerate(textos) if len(t.split()) >= min_palabras]
    if len(validos) < 2:
        return []
    corpus = [textos[i] for i in validos]
    vec = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2,
                          sublinear_tf=True, max_features=200000)
    X = vec.fit_transform(corpus)
    pares = []
    n = X.shape[0]
    for ini in range(0, n, BLOQUE):
        fin = min(ini + BLOQUE, n)
        sim = (X[ini:fin] @ X.T).toarray()
        for fila in range(fin - ini):
            gi = ini + fila
            for gj in np.where(sim[fila] >= umbral)[0]:
                if gj <= gi:
                    continue
                pares.append((float(sim[fila][gj]), ids[validos[gi]], ids[validos[gj]]))
    pares.sort(reverse=True)
    return pares


def analiza_origen():
    raw = json.load(open(D / "raw.json", encoding="utf-8"))
    docs = [d for d in raw if d.get("texto") and len(d["texto"].split()) >= 40]
    textos = [normaliza(d["texto"]) for d in docs]
    ids = [(d["portal"], d["url_origen"], d["titulo"], d["tipo"]) for d in docs]

    print("ORIGEN: {} documentos con texto suficiente".format(len(docs)), flush=True)
    pares = pares_similares(textos, ids)
    print("  pares por encima de {}: {}".format(PARECIDO, len(pares)), flush=True)

    ident = [p for p in pares if p[0] >= IDENTICO]
    casi = [p for p in pares if CASI <= p[0] < IDENTICO]
    cruzado = [p for p in pares if p[1][0] != p[2][0]]

    # cuantos documentos distintos estan implicados
    implicados = {x[1] for x in pares} | {x[2] for x in pares}

    return {
        "documentos": len(docs),
        "pares_parecidos": len(pares),
        "pares_identicos": len(ident),
        "pares_casi": len(casi),
        "pares_entre_portales": len(cruzado),
        "documentos_implicados": len(implicados),
        "top": [{"similitud": round(s, 3), "a": a[1], "b": b[1],
                 "portal_a": a[0], "portal_b": b[0], "titulo": a[2]}
                for s, a, b in pares[:400]],
    }


def analiza_destino():
    site = json.load(open(D / "site.json", encoding="utf-8"))
    COLL = ("categories", "products", "posts", "postcats", "pages")
    docs = [d for c in COLL for d in site[c]
            if not d.get("noindex") and d.get("sub") != "junk"]
    textos = [normaliza(texto_de_bloques(d["blocks"])) for d in docs]
    ids = [(d["kind"], d["path"], d["title"], d.get("sub") or "") for d in docs]

    print("DESTINO: {} documentos indexables".format(len(docs)), flush=True)
    pares = pares_similares(textos, ids)
    print("  pares por encima de {}: {}".format(PARECIDO, len(pares)), flush=True)

    por_tipo = defaultdict(int)
    for s, a, b in pares:
        if s >= CASI:
            por_tipo["{} vs {}".format(a[0], b[0])] += 1

    implicados = {x[1] for x in pares if x[0] >= CASI} | {x[2] for x in pares if x[0] >= CASI}

    return {
        "documentos": len(docs),
        "pares_parecidos": len(pares),
        "pares_identicos": len([p for p in pares if p[0] >= IDENTICO]),
        "pares_casi": len([p for p in pares if CASI <= p[0] < IDENTICO]),
        "documentos_en_riesgo": len(implicados),
        "por_tipo": dict(por_tipo),
        "top": [{"similitud": round(s, 3), "a": a[1], "b": b[1],
                 "tipo_a": a[0], "tipo_b": b[0], "titulo_a": a[2], "titulo_b": b[2]}
                for s, a, b in pares[:400]],
    }


def main():
    quien = sys.argv[1] if len(sys.argv) > 1 else "ambos"
    out = {"umbrales": {"identico": IDENTICO, "casi": CASI, "parecido": PARECIDO}}

    if quien in ("ambos", "origen"):
        out["origen"] = analiza_origen()
        o = out["origen"]
        print("\n  practicamente identicos : {}".format(o["pares_identicos"]))
        print("  casi duplicados         : {}".format(o["pares_casi"]))
        print("  duplicados ENTRE portales: {}".format(o["pares_entre_portales"]))
        print("  documentos implicados   : {} de {} ({:.0f}%)".format(
            o["documentos_implicados"], o["documentos"],
            o["documentos_implicados"] / o["documentos"] * 100))

    if quien in ("ambos", "destino"):
        print()
        out["destino"] = analiza_destino()
        d = out["destino"]
        print("\n  practicamente identicos : {}".format(d["pares_identicos"]))
        print("  casi duplicados         : {}".format(d["pares_casi"]))
        print("  documentos en riesgo    : {} de {} ({:.1f}%)".format(
            d["documentos_en_riesgo"], d["documentos"],
            d["documentos_en_riesgo"] / d["documentos"] * 100))
        if d["por_tipo"]:
            print("\n  donde esta el problema:")
            for k, v in sorted(d["por_tipo"].items(), key=lambda x: -x[1]):
                print("    {:28s} {}".format(k, v))
        if d["top"]:
            print("\n  los 12 pares mas parecidos del portal nuevo:")
            for p in d["top"][:12]:
                print("    {:.3f}  {}".format(p["similitud"], p["a"][:52]))
                print("           {}".format(p["b"][:52]))

    json.dump(out, open(D / "duplicados.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("\n-> data/duplicados.json")


if __name__ == "__main__":
    main()
