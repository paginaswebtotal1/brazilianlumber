# Supabase: cómo conectarlo

El portal funciona sin base de datos. Esto es para cuando se quiera que el contenido viva en PostgreSQL y se pueda editar sin tocar el código.

## 1. Crear el proyecto

En [supabase.com](https://supabase.com), plan **Free**. Región: `us-east-1`, la más cercana a los tres almacenes.

El plan gratuito da 500 MB de base de datos. El dataset completo ocupa unos 25 MB, así que sobra de largo.

## 2. Crear el esquema

En **SQL Editor**, pegar y ejecutar el contenido de `web/supabase-schema.sql`. Crea:

- La tabla `documents` con las 838 páginas y una columna `search` de tipo `tsvector` generada automáticamente, con pesos: título y palabras clave en A, descripción en B, cuerpo en C.
- La tabla `redirects` con las 622 equivalencias.
- La función `search_documents(q, k, lim)`: combina relevancia textual, similitud por trigramas (para las erratas) y los clics reales de Search Console.
- La función `suggest_documents(q, lim)` para el autocompletado.
- Índices GIN sobre `search` y sobre el título.
- Row Level Security activado, con lectura pública y escritura solo con la clave de servicio.

## 3. Cargar los datos

En `web/.env.local`:

```
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

Las tres están en **Settings → API**.

```bash
cd web
npm run seed
```

Carga los 838 documentos y las 622 redirecciones, y termina haciendo una búsqueda de prueba para confirmar que la función responde.

## 4. Seguridad

- `SUPABASE_SERVICE_ROLE_KEY` **no se sube nunca** al repositorio ni al navegador. Solo se usa en el seeder, en local. Está en `.gitignore`.
- La clave `anon` sí es pública por diseño: con RLS activado solo puede leer.
- Si alguna vez se filtra la clave de servicio, se rota desde **Settings → API → Reset**.

## 5. Cómo saber cuál se está usando

`GET /api/search/?q=ipe` devuelve un campo `source`:

- `"supabase"` — está leyendo de PostgreSQL
- `"local"` — está usando el dataset generado
