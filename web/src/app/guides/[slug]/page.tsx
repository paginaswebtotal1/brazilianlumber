import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { Blocks, Breadcrumbs, JsonLd, PostCard, Section } from "@/components/ui";
import Thumb from "@/components/Thumb";
import { breadcrumbs, getDoc, postsIn, related } from "@/lib/data";
import { articleSchema, breadcrumbSchema, collectionSchema, graph, metaFor } from "@/lib/seo";

/**
 * /guides/{slug}/ resuelve dos cosas distintas: un artículo o un tema del blog.
 *
 * Comparten espacio de nombres porque así lo fijó el mapa de URLs acordado. El
 * control de calidad del pipeline verifica en cada build que ningún slug de
 * artículo choca con uno de tema (hoy: 0 colisiones sobre 299 URLs).
 */

type Params = { params: Promise<{ slug: string }> };

export const revalidate = 300;

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { slug } = await params;
  const doc = getDoc(`/guides/${slug}/`);
  if (!doc) return {};
  return metaFor(doc);
}

export default async function GuidePage({ params }: Params) {
  const { slug } = await params;
  const doc = getDoc(`/guides/${slug}/`);
  if (!doc || (doc.kind !== "post" && doc.kind !== "postcat")) notFound();

  const crumbs = breadcrumbs(doc);

  // ---------------------------------------------- tema del blog
  if (doc.kind === "postcat") {
    const posts = postsIn(doc.path);
    return (
      <div className="mx-auto max-w-7xl px-4 py-8">
        <Breadcrumbs items={crumbs} />
        <header className="max-w-3xl">
          <p className="text-xs font-medium uppercase tracking-wider text-ember-600">Guide topic</p>
          <h1 className="mt-1.5 font-[family-name:var(--font-display)] text-4xl font-semibold leading-tight text-bark-900">
            {doc.h1 ?? doc.title}
          </h1>
          <div className="mt-4">
            <Blocks blocks={doc.blocks} />
          </div>
        </header>
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {posts.map((p, i) => (
            <PostCard key={p.path} doc={p} priority={i < 3} />
          ))}
        </div>
        {posts.length === 0 && (
          <p className="mt-8 text-sm text-bark-500">
            No articles under this topic yet.{" "}
            <Link href="/guides/" className="text-ember-600 underline">
              Browse all guides
            </Link>
            .
          </p>
        )}
        <JsonLd data={graph(collectionSchema(doc, posts), breadcrumbSchema(crumbs))} />
      </div>
    );
  }

  // ---------------------------------------------- artículo
  const more = related(doc, 3);
  return (
    <article className="mx-auto max-w-7xl px-4 py-8">
      <Breadcrumbs items={crumbs} />

      <div className="mx-auto max-w-3xl">
        <header>
          {doc.catNames?.[0] && doc.cats?.[0] && (
            <Link href={doc.cats[0]} className="text-xs font-medium uppercase tracking-wider text-ember-600">
              {doc.catNames[0]}
            </Link>
          )}
          <h1 className="mt-1.5 font-[family-name:var(--font-display)] text-4xl font-semibold leading-[1.15] text-bark-900">
            {doc.h1 ?? doc.title}
          </h1>
          <p className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-[13px] text-bark-500">
            {doc.date && (
              <time dateTime={doc.date}>
                {new Date(doc.date).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}
              </time>
            )}
            {doc.words ? <span>· {Math.max(1, Math.round(doc.words / 220))} min read</span> : null}
          </p>
        </header>

        {doc.image && (
          <div className="mt-6">
            <Thumb src={doc.image} alt={doc.title} color={doc.color} ratio="16 / 9" priority sizes="100vw" />
          </div>
        )}

        <div className="mt-7">
          <Blocks blocks={doc.blocks} />
        </div>

        {doc.catNames && doc.catNames.length > 0 && (
          <footer className="mt-10 border-t border-bark-200 pt-5">
            <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-bark-400">Topics</h2>
            <ul className="flex flex-wrap gap-2">
              {doc.cats!.map((c, i) => (
                <li key={c}>
                  <Link
                    href={c}
                    className="inline-block rounded-full border border-bark-200 bg-white px-3 py-1 text-[13px] text-bark-700 hover:border-ember-500 hover:text-ember-600"
                  >
                    {doc.catNames![i]}
                  </Link>
                </li>
              ))}
            </ul>
          </footer>
        )}
      </div>

      {more.length > 0 && (
        <Section title="Keep reading" href="/guides/">
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {more.map((p) => (
              <PostCard key={p.path} doc={p} />
            ))}
          </div>
        </Section>
      )}

      <JsonLd data={graph(articleSchema(doc), breadcrumbSchema(crumbs))} />
    </article>
  );
}
