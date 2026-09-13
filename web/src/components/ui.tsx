import Link from "next/link";
import { ChevronRight } from "lucide-react";
import Thumb from "./Thumb";
import type { Block, Doc } from "@/lib/data";

/** Migas de pan. Van en todas las páginas y alimentan el BreadcrumbList de schema.org. */
export function Breadcrumbs({ items }: { items: { path: string; title: string }[] }) {
  return (
    <nav aria-label="Breadcrumb" className="mb-5">
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
                <Link href={it.path} className="hover:text-ember-600 hover:underline">
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

/** Renderiza los bloques limpios que produjo el pipeline. */
export function Blocks({ blocks }: { blocks: Block[] }) {
  return (
    <div className="prose-bl">
      {blocks.map((b, i) => {
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
      <table className="w-full text-sm">
        <caption className="sr-only">Technical specifications</caption>
        <tbody>
          {rows.map(([k, v], i) => (
            <tr key={k + i} className="border-b border-bark-100 last:border-0">
              <th scope="row" className="w-1/2 px-4 py-2.5 text-left font-medium text-bark-600">
                {k}
              </th>
              <td className="px-4 py-2.5 text-bark-900">{v}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ProductCard({ doc, priority = false }: { doc: Doc; priority?: boolean }) {
  return (
    <Link
      href={doc.path}
      className="group block overflow-hidden rounded-[--radius-card] border border-bark-200 bg-white transition-shadow hover:shadow-md"
    >
      <Thumb src={doc.image} alt={doc.title} color={doc.color} priority={priority} label={doc.title} />
      <div className="p-3.5">
        {doc.categoryTitle && (
          <p className="mb-1 truncate text-[11px] uppercase tracking-wide text-bark-400">{doc.categoryTitle}</p>
        )}
        <h3 className="text-[15px] font-medium leading-snug text-bark-900 group-hover:text-ember-600">{doc.title}</h3>
        {doc.description && <p className="mt-1.5 line-clamp-2 text-[13px] text-bark-500">{doc.description}</p>}
      </div>
    </Link>
  );
}

export function PostCard({ doc, priority = false }: { doc: Doc; priority?: boolean }) {
  return (
    <Link
      href={doc.path}
      className="group block overflow-hidden rounded-[--radius-card] border border-bark-200 bg-white transition-shadow hover:shadow-md"
    >
      <Thumb src={doc.image} alt={doc.title} color={doc.color} ratio="16 / 9" priority={priority} label={doc.title} />
      <div className="p-4">
        {doc.catNames?.[0] && (
          <p className="mb-1 truncate text-[11px] uppercase tracking-wide text-bark-400">{doc.catNames[0]}</p>
        )}
        <h3 className="text-[15px] font-semibold leading-snug text-bark-900 group-hover:text-ember-600">{doc.title}</h3>
        {doc.description && <p className="mt-1.5 line-clamp-2 text-[13px] text-bark-500">{doc.description}</p>}
        {doc.date && (
          <time dateTime={doc.date} className="mt-2 block text-[11px] text-bark-400">
            {new Date(doc.date).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}
          </time>
        )}
      </div>
    </Link>
  );
}

export function CategoryCard({ doc }: { doc: Doc }) {
  return (
    <Link
      href={doc.path}
      className="group flex items-center gap-3 rounded-[--radius-card] border border-bark-200 bg-white p-3 transition-shadow hover:shadow-md"
    >
      <span className="w-16 shrink-0">
        <Thumb src={doc.image} alt="" color={doc.color} ratio="1 / 1" label={doc.title} />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm font-medium text-bark-900 group-hover:text-ember-600">{doc.title}</span>
        <span className="block text-xs text-bark-500">
          {doc.productCount ?? 0} product{(doc.productCount ?? 0) === 1 ? "" : "s"}
        </span>
      </span>
      <ChevronRight size={16} className="shrink-0 text-bark-300" aria-hidden />
    </Link>
  );
}

export function Section({
  title,
  href,
  linkLabel = "View all",
  children,
}: {
  title: string;
  href?: string;
  linkLabel?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="py-10">
      <div className="mb-5 flex items-baseline justify-between gap-4">
        <h2 className="font-[family-name:var(--font-display)] text-2xl font-semibold text-bark-900">{title}</h2>
        {href && (
          <Link href={href} className="shrink-0 text-sm font-medium text-ember-600 hover:underline">
            {linkLabel} →
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
