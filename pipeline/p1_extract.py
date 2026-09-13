# -*- coding: utf-8 -*-
"""p1 - Extrae y limpia el contenido de los 3 portales a un dataset unico.

Fuente: 8 - CONSOLIDACION DE URLS/datos/{mapa.json, rest_full.jsonl}
Salida: data/raw.json
"""
import json, re, html, os, sys, hashlib
from pathlib import Path

SRC = Path(r"C:\Users\USER\Desktop\BRAZILIAN LUMBER\ARQUITECTURA WEB BL\MENÙ VISUAL\8 - CONSOLIDACION DE URLS\datos")
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

# ---------- limpieza de WordPress / Visual Composer ----------
SHORTCODE = re.compile(r"\[/?[a-z0-9_]+[^\]]*\]", re.I)
SCRIPTSTYLE = re.compile(r"<(script|style|noscript)[^>]*>.*?</\1>", re.I | re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)
TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"[ \t\r\f\v]+")
NL = re.compile(r"\n{3,}")

def unesc(s):
    # los dumps traen &#8221; &#8243; etc. de las comillas tipograficas del VC
    for _ in range(2):
        s = html.unescape(s)
    return s

def fix_mojibake(s):
    """Repara texto latin-1 mal decodificado (guiones y comillas tipograficas)."""
    repl = {
        "\u2013": "-", "\u2014": " - ", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u00a0": " ",
        "\ufffd": "", "\u00d7": "x", "\u2032": "'", "\u2033": '"',
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    return s

def strip_html(s):
    s = SCRIPTSTYLE.sub(" ", s)
    s = COMMENT.sub(" ", s)
    s = SHORTCODE.sub(" ", s)
    s = re.sub(r"</(p|div|h[1-6]|li|tr|br)>", "\n", s, flags=re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = TAG.sub(" ", s)
    s = unesc(s)
    s = fix_mojibake(s)
    s = WS.sub(" ", s)
    s = "\n".join(l.strip() for l in s.split("\n"))
    s = NL.sub("\n\n", s)
    return s.strip()

IMG = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.I)
def images(s):
    out, seen = [], set()
    for u in IMG.findall(s):
        u = unesc(u).strip()
        if not u.startswith("http"):
            continue
        if re.search(r"\.(svg|gif)$", u, re.I):
            continue
        if any(k in u.lower() for k in ("logo", "icon", "placeholder", "spinner", "loader")):
            continue
        # normaliza los thumbnails de WP (-300x200.jpg) al original
        u = re.sub(r"-\d{2,4}x\d{2,4}(\.(jpe?g|png|webp))$", r"\1", u, flags=re.I)
        if u not in seen:
            seen.add(u); out.append(u)
    return out[:12]

# ---------- bloques estructurados ----------
BLOCK = re.compile(r"<(h[2-4]|p|ul|ol|table)\b[^>]*>(.*?)</\1>", re.I | re.S)
LI = re.compile(r"<li\b[^>]*>(.*?)</li>", re.I | re.S)

def blocks(raw):
    """Convierte el HTML de WP en bloques limpios y ordenados."""
    src = SCRIPTSTYLE.sub(" ", raw)
    src = COMMENT.sub(" ", src)
    src = SHORTCODE.sub(" ", src)
    out = []
    for m in BLOCK.finditer(src):
        tag = m.group(1).lower()
        inner = m.group(2)
        if tag in ("ul", "ol"):
            items = [strip_html(x) for x in LI.findall(inner)]
            items = [i for i in items if 1 < len(i) < 400]
            if items:
                out.append({"t": "list", "items": items[:20]})
        elif tag == "table":
            continue
        else:
            txt = strip_html(inner)
            if not txt or len(txt) < 3:
                continue
            if tag.startswith("h"):
                if len(txt) < 200:
                    out.append({"t": tag, "text": txt})
            else:
                for part in txt.split("\n\n"):
                    part = part.strip()
                    if len(part) > 25:
                        out.append({"t": "p", "text": part})
    # dedup consecutivo
    clean, prev = [], None
    for b in out:
        k = json.dumps(b, sort_keys=True)
        if k != prev:
            clean.append(b)
        prev = k
    return clean[:60]

# ---------- carga ----------
def main():
    mapa = json.load(open(SRC / "mapa.json", encoding="utf-8"))
    rest = {}
    for line in open(SRC / "rest_full.jsonl", encoding="utf-8"):
        r = json.loads(line)
        key = (r.get("_portal"), r.get("_endpoint"), r.get("id"))
        rest[key] = r

    # index por url de origen para cruzar con el mapa
    by_link = {}
    for r in rest.values():
        lk = (r.get("link") or "").strip()
        if lk:
            by_link.setdefault(lk.rstrip("/") + "/", r)

    docs, miss = [], 0
    for m in mapa:
        r = by_link.get(m["url_origen"].rstrip("/") + "/")
        if r is None:
            miss += 1
        raw = ""
        exc = ""
        if r:
            c = r.get("content")
            raw = c.get("rendered", "") if isinstance(c, dict) else (c or "")
            e = r.get("excerpt")
            exc = e.get("rendered", "") if isinstance(e, dict) else (e or "")
            if not raw and r.get("description"):
                raw = r["description"]
        d = {
            "portal": m["portal"],
            "tipo": m["tipo"],
            "accion": m["accion"],
            "url_origen": m["url_origen"],
            "url_destino": m["url_destino"],
            "canonical": m["canonical"],
            "slug": m["slug"],
            "titulo": fix_mojibake(unesc(m["titulo"] or "")).strip(),
            "palabras": m["palabras"],
            "clics": m["clics"],
            "impresiones": m["impresiones"],
            "modificado": m["modificado"],
            "motivo": m["motivo"],
            "wp_id": r.get("id") if r else None,
            "parent": r.get("parent") if r else None,
            "fecha": (r.get("date") or "")[:10] if r else "",
            "blocks": blocks(raw) if raw else [],
            "texto": strip_html(raw) if raw else "",
            "excerpt": strip_html(exc)[:600] if exc else "",
            "imagenes": images(raw) if raw else [],
            "cat_ids": r.get("categories") if r else None,
            "cat_parent": r.get("parent") if (r and r.get("_tax")) else None,
            "cat_count": r.get("count") if (r and r.get("_tax")) else None,
        }
        d["hash"] = hashlib.md5(d["texto"][:4000].encode("utf-8")).hexdigest()[:12] if d["texto"] else ""
        docs.append(d)

    json.dump(docs, open(OUT / "raw.json", "w", encoding="utf-8"), ensure_ascii=False)
    surv = [d for d in docs if d["accion"] in ("CONSERVAR", "CONSERVAR-REESCRIBIR")]
    print(f"docs={len(docs)} sin_contenido_rest={miss} supervivientes={len(surv)}")
    print("con texto:", sum(1 for d in surv if d["texto"]))
    print("con imagen:", sum(1 for d in surv if d["imagenes"]))
    from collections import Counter
    print("hashes duplicados:", sum(1 for h, n in Counter(d["hash"] for d in surv if d["hash"]).items() if n > 1))

if __name__ == "__main__":
    main()
