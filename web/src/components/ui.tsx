import Link from "next/link";
import { ChevronRight, ArrowUpRight } from "lucide-react";
import Thumb from "./Thumb";
import type { Block, Doc } from "@/lib/data";

/** Migas de pan. Van en todas las páginas y alimentan el BreadcrumbList de schema.org. */
export function Breadcrumbs({ items }: { items: { path: string; title: string }[] }) {
  return (
    <nav aria-label="Breadcrumb" className="mb-6">
      <ol className="flex flex-wrap items-center gap-x-1.5 gap-y-1 text-[13px] text-bark-500">
        {items.map((it, i) => {
          const last = i === items.length - 1;
          return (
            <li key={it.path + i} className="flex items-center gap-1.5">
              {i > 0 && <ChevronRight size={13} className="text-bark-300" aria-hidden />}
              {last ? (
                <span aria-current="page" className="font-medium text-bark-700">
                  {it.title}
                </span>
              ) : (
                <Link href={it.path} className="transition-colors hover:text-ember-600">
                  {it.title}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

export function Blocks({ blocks }: { blocks: Block[] }) {
  return (
    <div className="prose-bl">
      {blocks.map((b, i) => {
        if (b.t === "img") {
          // Las fotos del cuerpo conservan su proporcion real, medida en el
          // pipeline: asi reservan su hueco y no mueven el texto al cargar.
          return (
            <figure key={i} className="my-8">
              <div
                className="media rounded-[--radius-card]"
                style={{ aspectRatio: b.w && b.h ? `${b.w} / ${b.h}` : "16 / 10" }}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={b.src} alt="" loading="lazy" decoding="async" width={b.w} height={b.h} />
              </div>
            </figure>
          );
        }
        if (b.t === "list") {
          return (
            <ul key={i}>
              {b.items.map((it, j) => (
                <li key={j}>{it}</li>
              ))}
            </ul>
          );
        }
        if (b.t === "h2") return <h2 key={i}>{b.text}</h2>;
        if (b.t === "h3") return <h3 key={i}>{b.text}</h3>;
        if (b.t === "h4") return <h4 key={i}>{b.text}</h4>;
        return <p key={i}>{b.text}</p>;
      })}
    </div>
  );
}

export function SpecTable({ rows }: { rows: [string, string][] }) {
  if (!rows.length) return null;
  return (
    <div className="overflow-hidden rounded-[--radius-card] border border-bark-200 bg-white">
      <table className="w-full text-[14px]">
        <caption className="sr-only">Technical specifications</caption>
        <tbody>
          {rows.map(([k, v], i) => (
            <tr key={k + i} className="border-b border-bark-100 last:border-0 even:bg-bark-50/60">
              <th scope="row" className="w-1/2 px-4 py-3 text-left font-medium text-bark-500">
                {k}
              </th>
              <td className="px-4 py-3 font-medium text-bark-900">{v}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Escalona la aparición de una rejilla sin añadir JavaScript. */
function delay(i: number) {
  return { animationDelay: `${Math.min(i, 11) * 45}ms` };
}

export function ProductCard({ doc, priority = false, i = 0 }: { doc: Doc; priority?: boolean; i?: number }) {
  return (
    <Link href={doc.path} className="card rise group block" style={delay(i)}>
      <Thumb
        src={doc.image}
        alt={doc.imageAlt ?? doc.title}
        color={doc.color}
        ratio="1 / 1"
        priority={priority}
        label={doc.title}
      />
      <div className="p-4">
        {doc.categoryTitle && (
          <p className="mb-1.5 truncate text-[11px] font-medium uppercase tracking-[0.09em] text-ember-600">
            {doc.categoryTitle}
          </p>
        )}
        <h3 className="text-[15px] font-semibold leading-snug text-bark-900">{doc.title}</h3>
        {doc.description && (
          <p className="mt-2 line-clamp-2 text-[13px] leading-relaxed text-bark-500">{doc.description}</p>
        )}
        {doc.attrs?.medida && (
          <p className="mt-3 inline-block rounded-full bg-bark-100 px-2.5 py-1 text-[11px] font-medium text-bark-600">
            {String(doc.attrs.medida).replace("x", " × ")}
          </p>
        )}
      </div>
    </Link>
  );
}

export function PostCard({ doc, priority = false, i = 0 }: { doc: Doc; priority?: boolean; i?: number }) {
  return (
    <Link href={doc.path} className="card rise group block" style={delay(i)}>
      <Thumb
        src={doc.image}
        alt={doc.imageAlt ?? doc.title}
        color={doc.color}
        ratio="16 / 10"
        priority={priority}
        label={doc.title}
      />
      <div className="p-5">
        {doc.catNames?.[0] && (
          <p className="mb-1.5 truncate text-[11px] font-medium uppercase tracking-[0.09em] text-ember-600">
            {doc.catNames[0]}
          </p>
        )}
        <h3 className="display text-[1.15rem] text-bark-900">{doc.title}</h3>
        {doc.description && (
          <p className="mt-2 line-clamp-2 text-[13.5px] leading-relaxed text-bark-500">{doc.description}</p>
        )}
        <p className="mt-3.5 flex items-center gap-3 text-[11.5px] text-bark-400">
          {doc.date && (
            <time dateTime={doc.date}>
              {new Date(doc.date).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })}
            </time>
          )}
          {doc.words ? <span>· {Math.max(1, Math.round(doc.words / 220))} min read</span> : null}
        </p>
      </div>
    </Link>
  );
}

/** Tarjeta de categoría con la foto a sangre y el texto encima. */
export function CategoryCard({ doc, i = 0, tall = false }: { doc: Doc; i?: number; tall?: boolean }) {
  return (
    <Link href={doc.path} className="card rise group relative block" style={delay(i)}>
      <Thumb
        src={doc.image}
        alt=""
        color={doc.color}
        ratio={tall ? "3 / 4" : "5 / 4"}
        label={doc.title}
        scrim
        sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 320px"
      />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10 p-4">
        <h3 className="display text-[1.2rem] text-white drop-shadow-sm">{doc.title}</h3>
        <p className="mt-0.5 flex items-center gap-1.5 text-[12px] text-white/75">
          {doc.productCount ?? 0} product{(doc.productCount ?? 0) === 1 ? "" : "s"}
          <ArrowUpRight size={13} className="transition-transform group-hover:translate-x-0.5" aria-hidden />
        </p>
      </div>
    </Link>
  );
}

/** Variante compacta, en fila, para listas densas de subcategorías. */
export function CategoryRow({ doc, i = 0 }: { doc: Doc; i?: number }) {
  return (
    <Link href={doc.path} className="card rise group flex items-center gap-4 p-3" style={delay(i)}>
      <span className="w-20 shrink-0 overflow-hidden rounded-lg">
        <Thumb src={doc.image} alt="" color={doc.color} ratio="1 / 1" label={doc.title} sizes="80px" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-[15px] font-semibold text-bark-900">{doc.title}</span>
        <span className="mt-0.5 block text-[12.5px] text-bark-500">
          {doc.productCount ?? 0} product{(doc.productCount ?? 0) === 1 ? "" : "s"}
        </span>
      </span>
      <ChevronRight
        size={17}
        className="shrink-0 text-bark-300 transition-transform group-hover:translate-x-0.5"
        aria-hidden
      />
    </Link>
  );
}

export function Section({
  title,
  kicker,
  href,
  linkLabel = "View all",
  children,
}: {
  title: string;
  kicker?: string;
  href?: string;
  linkLabel?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="py-12 lg:py-16">
      <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
        <div>
          {kicker && (
            <p className="mb-1.5 text-[11px] font-medium uppercase tracking-[0.16em] text-ember-600">{kicker}</p>
          )}
          <h2 className="display text-[1.9rem] text-bark-900 sm:text-[2.15rem]">{title}</h2>
        </div>
        {href && (
          <Link
            href={href}
            className="group flex shrink-0 items-center gap-1.5 text-sm font-medium text-bark-700 transition-colors hover:text-ember-600"
          >
            {linkLabel}
            <ArrowUpRight size={15} className="transition-transform group-hover:translate-x-0.5" aria-hidden />
          </Link>
        )}
      </div>
      {children}
    </section>
  );
}

export function JsonLd({ data }: { data: string }) {
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: data }} />;
}
