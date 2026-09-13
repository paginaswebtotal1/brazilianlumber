-- Brazilian Lumber - portal unico. Esquema para Supabase (PostgreSQL).
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
