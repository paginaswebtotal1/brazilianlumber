# -*- coding: utf-8 -*-
"""p5 - Comprueba que las 838 URLs del portal responden 200 y que el SEO basico
esta en cada una. Se ejecuta contra el servidor local.
"""
import json, sys, re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3456"
D = Path(__file__).resolve().parent.parent / "data"
S = json.load(open(D / "site.json", encoding="utf-8"))
COLL = ("categories", "products", "posts", "postcats", "pages")

docs = [d for c in COLL for d in S[c]]
extra = ["/", "/shop/", "/guides/", "/search/?q=ipe", "/robots.txt", "/sitemap.xml"]


def get(path):
    try:
        r = Request(BASE + path, headers={"User-Agent": "bl-qa"})
        with urlopen(r, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore"), dict(resp.headers)
    except HTTPError as e:
        return e.code, "", {}
    except URLError as e:
        return 0, str(e), {}


def check(d):
    path = d if isinstance(d, str) else d["path"]
    code, html, hdr = get(path)
    out = {"path": path, "code": code}
    if code == 200 and not path.endswith((".txt", ".xml")):
        out["h1"] = len(re.findall(r"<h1[\s>]", html))
        out["title"] = bool(re.search(r"<title>[^<]{10,}</title>", html))
        out["desc"] = bool(re.search(r'name="description"\s+content="[^"]{40,}"', html))
        out["canonical"] = bool(re.search(r'rel="canonical"', html))
        out["jsonld"] = len(re.findall(r'type="application/ld\+json"', html))
        out["crumbs"] = 'aria-label="Breadcrumb"' in html
        out["noindex"] = "noindex" in (hdr.get("X-Robots-Tag", "") + html[:4000])
    return out


with ThreadPoolExecutor(max_workers=12) as ex:
    res = list(ex.map(check, extra + docs))

bad = [r for r in res if r["code"] != 200]
page = [r for r in res if r["code"] == 200 and "h1" in r]
print(f"comprobadas {len(res)} URLs")
print(f"  no 200          : {len(bad)}")
for r in bad[:15]:
    print("     ", r["code"], r["path"])
print(f"  sin un unico H1 : {sum(1 for r in page if r['h1'] != 1)}")
for r in [r for r in page if r["h1"] != 1][:10]:
    print("     ", r["h1"], r["path"])
print(f"  sin <title>     : {sum(1 for r in page if not r['title'])}")
print(f"  sin description : {sum(1 for r in page if not r['desc'])}")
print(f"  sin canonical   : {sum(1 for r in page if not r['canonical'])}")
print(f"  sin JSON-LD     : {sum(1 for r in page if r['jsonld'] == 0)}")
print(f"  sin migas       : {sum(1 for r in page if not r['crumbs'])}")
print(f"  SIN noindex     : {sum(1 for r in page if not r['noindex'])}  (debe ser 0 en el prototipo)")
json.dump(res, open(D / "check.json", "w", encoding="utf-8"), ensure_ascii=False)
