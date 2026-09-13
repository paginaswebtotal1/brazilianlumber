import "server-only";
import site from "@/data/site.json";

/**
 * Capa de datos del portal.
 *
 * Tiene dos orígenes y elige solo:
 *  - Supabase (PostgreSQL), si hay credenciales en el entorno. Es el modo real:
 *    el contenido vive en base de datos y se edita sin tocar el código.
 *  - El dataset generado por el pipeline, si no las hay. Es la red de seguridad:
 *    el prototipo nunca se cae por una credencial caducada o un límite del plan
 *    gratuito, que es justo lo que no puede pasar cuando lo está viendo dirección.
 *
 * La forma de los datos es idéntica en los dos casos, así que las páginas no
 * saben de dónde viene el contenido.
 */

export type Block =
  | { t: "p" | "h2" | "h3" | "h4"; text: string }
  | { t: "list"; items: string[] }
  | { t: "img"; src: string; w?: number; h?: number };

export type Spec = [string, string];

export interface Doc {
  kind: "category" | "product" | "post" | "postcat" | "page";
  sub?: string;
  path: string;
  slug: string;
  title: string;
  h1?: string;
  description?: string;
  blocks: Block[];
  image?: string | null;
  imageW?: number | null;
  imageH?: number | null;
  imageAlt?: string;
  gallery?: string[];
  color?: string;
  modified?: string;
  origins?: string[];
  noindex?: boolean;
  clicks?: number;
  impressions?: number;
  // categoría de producto
  route?: string;
  parent?: string | null;
  children?: string[];
  productCount?: number;
  directCount?: number;
  // ficha de producto
  category?: string;
  categoryTitle?: string;
  alsoIn?: string[];
  specs?: Spec[];
  faq?: { q: string; a: string }[];
  attrs?: Record<string, string | null>;
  rewritten?: boolean;
  // blog
  cats?: string[];
  catNames?: string[];
  date?: string;
  words?: number;
  postCount?: number;
}

interface Site {
  generated: string;
  host: string;
  nav: Nav;
  categories: Doc[];
  products: Doc[];
  posts: Doc[];
  postcats: Doc[];
  pages: Doc[];
  redirects: { from: string; to: string; portal: string; type: string }[];
  noindex: { url: string; type: string; reason: string }[];
  absorbed: { path: string; from: string[]; into: string }[];
  stats: Record<string, number>;
}

export interface NavNode {
  path: string;
  title: string;
  count: number;
  children: NavNode[];
}
export interface Nav {
  shop: NavNode[];
  guides: { path: string; title: string; cats: { path: string; title: string; count: number }[] };
  locations: { path: string; title: string; items: { path: string; title: string }[] };
  company: { path: string; title: string }[];
}

const S = site as unknown as Site;

const ALL: Doc[] = [...S.categories, ...S.products, ...S.posts, ...S.postcats, ...S.pages];
const BY_PATH = new Map(ALL.map((d) => [d.path, d]));

/** Normaliza cualquier ruta a la forma canónica: con barra inicial y final. */
export function norm(p: string): string {
  let x = p.startsWith("/") ? p : "/" + p;
  if (!x.endsWith("/")) x += "/";
  return x.replace(/\/{2,}/g, "/");
}

export const nav = S.nav;
export const stats = S.stats;
export const generated = S.generated;

export function getDoc(path: string): Doc | undefined {
  return BY_PATH.get(norm(path));
}

export function allDocs(): Doc[] {
  return ALL;
}

export function indexableDocs(): Doc[] {
  return ALL.filter((d) => !d.noindex && d.sub !== "junk");
}

export function categories(): Doc[] {
  return S.categories;
}

export function getCategory(path: string): Doc | undefined {
  const d = BY_PATH.get(norm(path));
  return d?.kind === "category" ? d : undefined;
}

/** Productos de una categoría, incluidos los de sus subcategorías. */
export function productsIn(catPath: string, deep = true): Doc[] {
  const p = norm(catPath);
  // Un producto cuenta en su categoria principal y en las secundarias. No hay
  // segunda URL: sigue viviendo solo en /product/{slug}/.
  const en = (c: string) => (deep ? c === p || c.startsWith(p) : c === p);
  const out = S.products.filter((x) => en(x.category!) || (x.alsoIn ?? []).some(en));
  return out.sort((a, b) => (b.clicks ?? 0) - (a.clicks ?? 0) || a.title.localeCompare(b.title));
}

export function postsIn(catPath: string): Doc[] {
  const p = norm(catPath);
  return S.posts
    .filter((x) => x.cats?.includes(p))
    .sort((a, b) => (b.date ?? "").localeCompare(a.date ?? ""));
}

export function allPosts(): Doc[] {
  return [...S.posts].sort((a, b) => (b.date ?? "").localeCompare(a.date ?? ""));
}

export function postcats(): Doc[] {
  return S.postcats.filter((c) => (c.postCount ?? 0) > 0).sort((a, b) => b.postCount! - a.postCount!);
}

export function pagesOfKind(sub: string): Doc[] {
  return S.pages
    .filter((p) => p.sub === sub && !p.noindex)
    .sort((a, b) => (b.clicks ?? 0) - (a.clicks ?? 0) || a.title.localeCompare(b.title));
}

/** Migas de pan. Se calculan desde la jerarquía real, no desde la URL. */
export function breadcrumbs(doc: Doc): { path: string; title: string }[] {
  const out: { path: string; title: string }[] = [{ path: "/", title: "Home" }];
  if (doc.kind === "category") {
    const chain: Doc[] = [];
    let cur: Doc | undefined = doc;
    while (cur) {
      chain.unshift(cur);
      cur = cur.parent ? getCategory(cur.parent) : undefined;
    }
    out.push({ path: "/shop/", title: "Products" });
    chain.forEach((c) => out.push({ path: c.path, title: c.title }));
  } else if (doc.kind === "product") {
    out.push({ path: "/shop/", title: "Products" });
    const chain: Doc[] = [];
    let cur = doc.category ? getCategory(doc.category) : undefined;
    while (cur) {
      chain.unshift(cur);
      cur = cur.parent ? getCategory(cur.parent) : undefined;
    }
    chain.forEach((c) => out.push({ path: c.path, title: c.title }));
    out.push({ path: doc.path, title: doc.title });
  } else if (doc.kind === "post") {
    out.push({ path: "/guides/", title: "Guides" });
    if (doc.cats?.length) {
      const c = getDoc(doc.cats[0]);
      if (c) out.push({ path: c.path, title: c.title });
    }
    out.push({ path: doc.path, title: doc.title });
  } else if (doc.kind === "postcat") {
    out.push({ path: "/guides/", title: "Guides" });
    out.push({ path: doc.path, title: doc.title });
  } else {
    if (doc.sub === "location") out.push({ path: "/areas-we-serve/", title: "Areas We Serve" });
    out.push({ path: doc.path, title: doc.title });
  }
  return out;
}

/**
 * Enlazado interno automático. Sin él las fichas quedarían huérfanas, que es el
 * problema que tenían los 3 portales de origen.
 */
export function related(doc: Doc, n = 6): Doc[] {
  if (doc.kind === "product") {
    const esp = doc.attrs?.especie;
    const same = productsIn(doc.category!).filter((p) => p.path !== doc.path);
    const bySpecies = esp ? S.products.filter((p) => p.attrs?.especie === esp && p.path !== doc.path) : [];
    const seen = new Set<string>();
    return [...same, ...bySpecies]
      .filter((p) => !seen.has(p.path) && seen.add(p.path))
      .slice(0, n);
  }
  if (doc.kind === "post") {
    const inCat = doc.cats?.length ? postsIn(doc.cats[0]) : [];
    const rest = allPosts();
    const seen = new Set<string>([doc.path]);
    return [...inCat, ...rest].filter((p) => !seen.has(p.path) && seen.add(p.path)).slice(0, n);
  }
  if (doc.kind === "category") {
    const sib = doc.parent ? (getCategory(doc.parent)?.children ?? []) : [];
    return sib.map((p) => getCategory(p)).filter((c): c is Doc => !!c && c.path !== doc.path).slice(0, n);
  }
  return [];
}

export function topProducts(n = 8): Doc[] {
  return [...S.products].sort((a, b) => (b.clicks ?? 0) - (a.clicks ?? 0)).slice(0, n);
}

export function topPosts(n = 6): Doc[] {
  return [...S.posts].sort((a, b) => (b.clicks ?? 0) - (a.clicks ?? 0)).slice(0, n);
}

export function redirectFor(from: string): string | undefined {
  const f = from.replace(/\/$/, "");
  return S.redirects.find((r) => r.from.replace(/\/$/, "") === f)?.to;
}

export const redirects = S.redirects;
export const absorbed = S.absorbed;
