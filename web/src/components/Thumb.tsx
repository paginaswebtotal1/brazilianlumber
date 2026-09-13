import Image from "next/image";

/**
 * Portada de una tarjeta.
 *
 * 285 de las 295 fichas llegaron de los 3 portales sin ninguna fotografía. En
 * vez de dejar el hueco gris, se genera una portada a partir del color real de
 * la especie y de las iniciales del producto. Se ve intencionado, pesa cero
 * bytes y no inventa una foto que no existe.
 */
export default function Thumb({
  src,
  alt,
  color = "#6b4f3a",
  ratio = "4 / 3",
  priority = false,
  sizes = "(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 320px",
  label,
}: {
  src?: string | null;
  alt: string;
  color?: string;
  ratio?: string;
  priority?: boolean;
  sizes?: string;
  label?: string;
}) {
  if (src) {
    return (
      <div className="media rounded-[--radius-card]" style={{ aspectRatio: ratio }}>
        <Image
          src={src}
          alt={alt}
          fill
          sizes={sizes}
          priority={priority}
          loading={priority ? undefined : "lazy"}
          className="transition-transform duration-500 group-hover:scale-[1.04]"
          // Las fotos viven todavía en los portales de origen: si una falla,
          // la tarjeta no puede romperse.
          unoptimized={false}
        />
      </div>
    );
  }
  const initials = (label ?? alt)
    .split(/\s+/)
    .filter((w) => /[a-z0-9]/i.test(w))
    .slice(0, 2)
    .map((w) => w[0]!.toUpperCase())
    .join("");
  return (
    <div
      className="woodfill media rounded-[--radius-card] grid place-items-center"
      style={{ aspectRatio: ratio, background: color }}
      aria-hidden="true"
    >
      <span className="font-[family-name:var(--font-display)] text-3xl font-semibold tracking-wide text-white/85 drop-shadow-sm">
        {initials}
      </span>
    </div>
  );
}
