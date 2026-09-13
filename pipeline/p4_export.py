# -*- coding: utf-8 -*-
"""p4 - Exporta lo que consume la web: indice de busqueda, esquema y semilla de
Supabase, redirecciones y el informe de control de calidad.
"""
import json, re, os
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
WEB = ROOT / "web" / "src" / "data"
PUB = ROOT / "web" / "public"
WEB.mkdir(parents=True, exist_ok=True)
PUB.mkdir(parents=True, exist_ok=True)

S = json.load(open(D / "site.json", encoding="utf-8"))
COLL = ("categories", "products", "posts", "postcats", "pages")


def plain(doc, limit=420):
    out = []
    for b in doc.get("blocks", []):
        if b["t"] == "list":
            out.append(" ".join(b["items"]))
        else:
            out.append(b.get("text", ""))
        if sum(len(x) for x in out) > limit:
            break
    return re.sub(r"\s+", " ", " ".join(out))[:limit].strip()


def keywords(doc):
    """Terminos extra para que el buscador entienda sinonimos y medidas."""
    k = []
    a = doc.get("attrs") or {}
    if a.get("especie"):
        k.append(a["especie"].replace("-", " "))
    if a.get("marca"):
        k.append(a["marca"])
    if a.get("medida"):
        m = a["medida"]
        k += [m, m.replace("x", " x "), m.replace("x", "")]
    if a.get("grado"):
        k.append(a["grado"])
    if doc.get("categoryTitle"):
        k.append(doc["categoryTitle"])
    k += doc.get("catNames", [])
    return " ".join(dict.fromkeys(k))


def main():
    # ---------- indice de busqueda ----------
    idx = []
    for coll in COLL:
        for d in S[coll]:
            if d.get("kind") == "page" and d.get("sub") == "junk":
                continue
            idx.append({
                "id": d["path"],
                "t": d["title"],
                "k": d["kind"] if d["kind"] != "page" else "page:" + d.get("sub", "company"),
                "d": (d.get("description") or "")[:180],
                "b": plain(d),
                "w": keywords(d),
                "c": d.get("category") or d.get("parent") or "",
                "ct": d.get("categoryTitle") or "",
                "img": d.get("image") or "",
                "col": d.get("color") or "#6b4f3a",
                "p": round(float(d.get("clicks") or 0) + float(d.get("impressions") or 0) / 100, 1),
            })
    json.dump(idx, open(PUB / "search-index.json", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))

    # ---------- dataset que consume la web ----------
    json.dump(S, open(WEB / "site.json", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))

    # ---------- redirecciones ----------
    red = {r["from"]: r["to"] for r in S["redirects"]}
    json.dump(S["redirects"], open(WEB / "redirects.json", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))

    # ---------- esquema de Supabase ----------
    sql = """-- Brazilian Lumber - portal unico. Esquema para Supabase (PostgreSQL).
-- Ejecutar en Supabase Studio > SQL Editor. Idempotente.

create extension if not exists pg_trgm;
create extension if not exists unaccent;

drop table if exists documents cascade;

create table documents (
  path          text primary key,
  kind          text not null,
  sub           text,
  slug          text not null,
  title         text not null,
  h1            text,
  description   text,
  category      text,
  category_title text,
  parent        text,
  children      jsonb default '[]'::jsonb,
  blocks        jsonb default '[]'::jsonb,
  specs         jsonb default '[]'::jsonb,
  faq           jsonb default '[]'::jsonb,
  attrs         jsonb default '{}'::jsonb,
  gallery       jsonb default '[]'::jsonb,
  cats          jsonb default '[]'::jsonb,
  cat_names     jsonb default '[]'::jsonb,
  image         text,
  color         text,
  keywords      text,
  body          text,
  product_count int default 0,
  post_count    int default 0,
  clicks        numeric default 0,
  impressions   numeric default 0,
  noindex       boolean default false,
  origins       jsonb default '[]'::jsonb,
  modified      date,
  published_at  date,
  search        tsvector generated always as (
      setweight(to_tsvector('english', coalesce(title,'')), 'A') ||
      setweight(to_tsvector('english', coalesce(keywords,'')), 'A') ||
      setweight(to_tsvector('english', coalesce(description,'')), 'B') ||
      setweight(to_tsvector('english', coalesce(body,'')), 'C')
  ) stored
);

create index documents_search_idx   on documents using gin (search);
create index documents_trgm_idx     on documents using gin (title gin_trgm_ops);
create index documents_kind_idx     on documents (kind);
create index documents_category_idx on documents (category);
create index documents_parent_idx   on documents (parent);

-- Redirecciones 301 heredadas de los 3 portales.
drop table if exists redirects cascade;
create table redirects (
  from_url text primary key,
  to_path  text not null,
  portal   text,
  kind     text
);
create index redirects_to_idx on redirects (to_path);

-- Busqueda: ranking por relevancia textual + demanda real (clics de Search Console).
create or replace function search_documents(q text, k text default null, lim int default 24)
returns table (
  path text, kind text, title text, description text, image text, color text,
  category_title text, rank real
) language sql stable as $$
  select d.path, d.kind, d.title, d.description, d.image, d.color, d.category_title,
         (ts_rank(d.search, websearch_to_tsquery('english', q)) * 10
          + similarity(d.title, q) * 4
          + least(coalesce(d.clicks,0) / 200.0, 1.0))::real as rank
  from documents d
  where d.noindex = false
    and (k is null or d.kind = k)
    and (d.search @@ websearch_to_tsquery('english', q) or d.title % q)
  order by rank desc
  limit lim;
$$;

-- Sugerencias instantaneas para el autocompletado.
create or replace function suggest_documents(q text, lim int default 8)
returns table (path text, kind text, title text, image text, color text)
language sql stable as $$
  select d.path, d.kind, d.title, d.image, d.color
  from documents d
  where d.noindex = false and (d.title ilike q || '%' or d.title % q
        or d.search @@ websearch_to_tsquery('english', q))
  order by (d.title ilike q || '%') desc, similarity(d.title, q) desc,
           coalesce(d.clicks,0) desc
  limit lim;
$$;

-- Solo lectura publica. La escritura se hace con la service_role desde el seeder.
alter table documents enable row level security;
alter table redirects enable row level security;
drop policy if exists "public read documents" on documents;
drop policy if exists "public read redirects" on redirects;
create policy "public read documents" on documents for select using (true);
create policy "public read redirects" on redirects for select using (true);
"""
    (D / "supabase-schema.sql").write_text(sql, encoding="utf-8")
    (ROOT / "web").mkdir(exist_ok=True)
    (ROOT / "web" / "supabase-schema.sql").write_text(sql, encoding="utf-8")

    # ---------- filas listas para insertar ----------
    rows = []
    for coll in COLL:
        for d in S[coll]:
            rows.append({
                "path": d["path"], "kind": d["kind"], "sub": d.get("sub"),
                "slug": d["slug"], "title": d["title"], "h1": d.get("h1") or d["title"],
                "description": d.get("description"), "category": d.get("category"),
                "category_title": d.get("categoryTitle"), "parent": d.get("parent"),
                "children": d.get("children", []), "blocks": d.get("blocks", []),
                "specs": d.get("specs", []), "faq": d.get("faq", []),
                "attrs": d.get("attrs", {}), "gallery": d.get("gallery", []),
                "cats": d.get("cats", []), "cat_names": d.get("catNames", []),
                "image": d.get("image"), "color": d.get("color"),
                "keywords": keywords(d), "body": plain(d, 6000),
                "product_count": d.get("productCount", 0), "post_count": d.get("postCount", 0),
                "clicks": d.get("clicks") or 0, "impressions": d.get("impressions") or 0,
                "noindex": bool(d.get("noindex")) or d.get("sub") == "junk",
                "origins": d.get("origins", []),
                "modified": d.get("modified") or None,
                "published_at": d.get("date") or d.get("modified") or None,
            })
    json.dump(rows, open(D / "supabase-rows.json", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))

    # ---------- informe de control de calidad ----------
    prods = S["products"]
    cats = S["categories"]
    pages = S["pages"]
    vacias = [c for c in cats if c["productCount"] == 0]
    sin_img = [p for p in prods if not p["image"]]
    junk = [p for p in pages if p["sub"] == "junk"]
    dest = {r["to"] for r in S["redirects"]}
    todos = {d["path"] for c in COLL for d in S[c]}
    rotas = sorted(dest - todos)

    qa = []
    qa.append("# Control de calidad del prototipo\n")
    qa.append("Generado por `pipeline/p4_export.py` el " + S["generated"] + ".\n")
    qa.append("## Cifras\n")
    qa.append("| Concepto | Cantidad |\n|---|---|")
    qa.append("| URLs rastreadas en los 3 portales | {} |".format(S["stats"]["crawled"]))
    qa.append("| URLs finales del portal unico | {} |".format(len(todos)))
    qa.append("| Categorias de producto | {} |".format(len(cats)))
    qa.append("| Fichas de producto | {} |".format(len(prods)))
    qa.append("| Articulos del blog | {} |".format(len(S["posts"])))
    qa.append("| Categorias del blog | {} |".format(len(S["postcats"])))
    qa.append("| Paginas | {} |".format(len(pages)))
    qa.append("| Redirecciones 301 | {} |".format(len(S["redirects"])))
    qa.append("| URLs antiguas a noindex (etiquetas) | {} |".format(len(S["noindex"])))
    qa.append("| Fichas con contenido reescrito | {} |".format(S["stats"]["rewritten"]))
    qa.append("\n## Comprobaciones\n")
    qa.append("| Comprobacion | Resultado |\n|---|---|")
    qa.append("| Rutas duplicadas | {} |".format(
        len([k for k, v in Counter(d["path"] for c in COLL for d in S[c]).items() if v > 1])))
    qa.append("| Redirecciones que apuntan a una URL inexistente | {} |".format(len(rotas)))
    qa.append("| Descripciones meta vacias | {} |".format(
        sum(1 for c in COLL for d in S[c] if not d.get("description"))))
    qa.append("| Titulos vacios | {} |".format(sum(1 for c in COLL for d in S[c] if not d.get("title"))))
    qa.append("| Fichas sin categoria | {} |".format(sum(1 for p in prods if not p.get("category"))))
    if rotas:
        qa.append("\n### Redirecciones rotas\n")
        for r in rotas[:50]:
            qa.append("- `{}`".format(r))
    qa.append("\n## Puntos que necesitan una decision de negocio\n")
    qa.append("Nada de esto rompe el prototipo, pero conviene resolverlo antes de la migracion real.\n")
    qa.append("**1. Categorias del menu sin ningun producto ({}).** "
              "Existen en el arbol acordado pero ningun producto de los 3 portales cae en ellas. "
              "O se les asigna surtido, o se sacan del menu.\n".format(len(vacias)))
    for c in vacias:
        qa.append("- `{}` {}".format(c["path"], c["title"]))
    qa.append("\n**2. Paginas de prueba que sobrevivieron a la consolidacion ({}).** "
              "Estan publicadas en el prototipo para no perder ninguna URL, pero marcadas noindex y fuera "
              "del menu y del sitemap. Recomendacion: eliminarlas en la migracion real.\n".format(len(junk)))
    for p in junk:
        qa.append("- `{}` {}".format(p["path"], p["title"]))
    qa.append("\n**3. Fichas sin fotografia ({} de {}).** "
              "El prototipo las muestra con una portada generada por color de especie. "
              "Hay que subir la foto real antes de publicar.\n".format(len(sin_img), len(prods)))
    qa.append("\n**4. Paginas absorbidas por la taxonomia ({}).** "
              "Ocupaban la misma URL que un nodo de categoria; su contenido se fusiono dentro de la "
              "categoria.\n".format(len(S["absorbed"])))
    for a in S["absorbed"]:
        qa.append("- `{}` <- {}".format(a["into"], ", ".join(a["from"])))

    (ROOT / "QA-PROTOTIPO.md").write_text("\n".join(qa), encoding="utf-8")

    print("indice de busqueda:", len(idx), "docs -",
          round((PUB / "search-index.json").stat().st_size / 1024), "KB")
    print("filas supabase:", len(rows))
    print("categorias vacias:", len(vacias), "| fichas sin foto:", len(sin_img),
          "| paginas de prueba:", len(junk))
    print("redirecciones rotas:", len(rotas))


if __name__ == "__main__":
    main()
