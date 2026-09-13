import Link from "next/link";
import SearchBox from "@/components/SearchBox";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-2xl px-4 py-24 text-center">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ember-600">404</p>
      <h1 className="mt-3 font-[family-name:var(--font-display)] text-4xl font-semibold text-bark-900">
        That page is not part of the unified portal.
      </h1>
      <p className="mx-auto mt-4 max-w-lg text-[15px] leading-relaxed text-bark-600">
        Every address from the three original portals was either kept or mapped to a 301. If you reached this from an
        old link, search for what you need below.
      </p>
      <div className="mx-auto mt-8 max-w-lg">
        <SearchBox autoFocus />
      </div>
      <div className="mt-8 flex flex-wrap justify-center gap-2">
        {[
          ["/shop/", "Full catalog"],
          ["/guides/", "Guides"],
          ["/areas-we-serve/", "Areas we serve"],
          ["/contact/", "Contact"],
        ].map(([href, label]) => (
          <Link
            key={href}
            href={href}
            className="rounded-full border border-bark-300 bg-white px-4 py-2 text-sm text-bark-700 hover:border-ember-500 hover:text-ember-600"
          >
            {label}
          </Link>
        ))}
      </div>
    </div>
  );
}
