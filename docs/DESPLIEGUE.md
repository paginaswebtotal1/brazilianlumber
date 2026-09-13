# Cómo publicar el prototipo

El objetivo es una URL que se le pueda pasar a dirección, que cargue rápido y que **ningún buscador pueda indexar**.

## Antes de nada: la variable que no se toca

```
NEXT_PUBLIC_INDEXABLE=false
```

Mientras esté en `false`:

- `robots.txt` responde `Disallow: /` para todos los agentes
- todas las páginas llevan `<meta name="robots" content="noindex, nofollow">`
- todas las respuestas llevan la cabecera `X-Robots-Tag: noindex, nofollow, noarchive, nosnippet, noimageindex`
- el `sitemap.xml` no se declara en `robots.txt`

Son tres capas porque hay rastreadores que ignoran una u otra. La cabecera HTTP es la única que respetan todos.

Ponerla en `true` solo el día que este sea el sitio de producción, en el dominio de producción.

---

## Opción recomendada: Vercel (gratis)

Es el camino más corto y el que mejor soporta el renderizado en servidor de Next.js.

1. Entrar en [vercel.com](https://vercel.com) con la cuenta de GitHub.
2. **Add New → Project** y elegir el repositorio.
3. **Root Directory: `web`**. Es el único ajuste que hay que cambiar; el resto se detecta solo.
4. En **Environment Variables**, añadir:
   ```
   NEXT_PUBLIC_INDEXABLE = false
   NEXT_PUBLIC_SITE_URL  = https://<lo-que-asigne-vercel>.vercel.app
   ```
   La segunda se puede rellenar después del primer despliegue, cuando ya se conoce el dominio, y volver a desplegar.
5. **Deploy**. Tarda alrededor de dos minutos.

### Añadir contraseña (opcional pero recomendable)

En Vercel, **Settings → Deployment Protection → Password Protection**. Una sola contraseña para todo el sitio. Con eso el prototipo no es accesible ni por accidente, más allá del bloqueo a buscadores.

---

## Alternativa: Cloudflare Pages

Cloudflare Pages no ejecuta Next.js con renderizado en servidor de forma nativa; hace falta el adaptador:

```bash
cd web
npm i -D @opennextjs/cloudflare wrangler
npx opennextjs-cloudflare build
npx wrangler pages deploy .open-next/assets
```

Funciona, pero son más piezas que pueden fallar el día de la demo. Si no hay una razón para usar Cloudflare, Vercel es menos trabajo.

Lo que sí conviene usar de Cloudflare es el **DNS y el proxy** si más adelante se pone un dominio propio delante.

---

## Alternativa: Hostinger

Solo sirve si el plan es **VPS**. El alojamiento compartido de Hostinger no ejecuta Node.js, y este portal no es HTML estático.

Con un VPS:

```bash
git clone <repo> && cd <repo>/web
npm ci
npm run build
npm i -g pm2
pm2 start "npm run start" --name bl-portal
pm2 save
```

Después, un proxy inverso (Nginx) del puerto 80/443 al 3000, y Certbot para el certificado.

---

## Una nota sobre las imágenes

Las fotografías siguen alojadas en los tres portales de origen: el prototipo las enlaza, no las copia. Están declaradas en `next.config.ts` como `remotePatterns`.

Dos consecuencias:

- Si Cloudflare llegara a bloquear el hotlinking desde otro dominio, las fotos dejarían de verse. Las 285 fichas que ya no tienen foto muestran una portada generada, así que el sitio no se rompe, pero se vería más pobre.
- En la migración real las imágenes hay que subirlas al portal nuevo. No es una tarea de este prototipo.
