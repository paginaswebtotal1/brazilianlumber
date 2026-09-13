# Decisiones de arquitectura y por qué

Las que un desarrollador va a cuestionar, contestadas por adelantado.

## Por qué Next.js y no React a secas

Un React normal (Vite, create-react-app) entrega al navegador un HTML vacío y pinta el contenido con JavaScript. Googlebot sabe esperar; muchos rastreadores de citación de IA no. Con Next.js el HTML sale completo del servidor en la primera respuesta.

Sigue siendo React: mismos componentes, mismos hooks.

## Por qué el prototipo no redirige

Porque es una maqueta del destino, no la migración. Hacer 301 aquí no aporta nada a lo que se quiere enseñar, y confunde: da la impresión de que el prototipo es el sitio real funcionando en paralelo.

El mapa de equivalencias es documentación: hoja 08 del Excel, `data/redirect-map.csv`, y `/redirect-map/` dentro del propio prototipo. Se convierte en 301 el día de la migración, configurado en cada uno de los tres dominios.

## Por qué los productos no cuelgan de la categoría

Un producto está en varias categorías. Si la URL fuera `/categoria/producto/`, el mismo producto tendría varias direcciones y habría que elegir una canónica, que es exactamente el lío que tienen hoy los tres portales.

Con `/product/{slug}/` plano el problema no existe. La categoría se ve en las migas de pan y en el enlazado, no en la URL. Es la regla que ya venía fijada en `taxonomia.py` de la carpeta 8.

## Por qué los filtros no van en la URL

Los tres portales generaban 1.379 URLs con parámetro, todas indexables y casi idénticas entre sí. Es una de las causas principales de la duplicidad.

En el portal nuevo los filtros del catálogo viven en el estado del cliente. Filtrar no crea ninguna dirección. Las URLs indexables son exactamente las de la taxonomía.

Si más adelante se quisiera que un filtro concreto fuese indexable (por ejemplo `ipe 5/4x6`, porque tiene demanda propia), lo correcto es crear una página de categoría de verdad, no un parámetro.

## Por qué el buscador es de cliente y no una llamada al servidor

Con 827 documentos, el índice completo pesa unos 120 KB comprimido. Descargarlo una vez y resolver en memoria es más rápido que cualquier ida y vuelta al servidor: menos de 10 ms por pulsación frente a 100-300 ms.

El índice **no** se descarga en la carga inicial: eso arruinaría el LCP. Se precarga cuando el usuario pasa el ratón por el buscador o lo enfoca, lo que da 200-300 ms de ventaja antes de la primera letra.

La ruta `/api/search/` existe para lo otro: funcionar sin JavaScript, integraciones y rastreadores.

Con un catálogo diez veces mayor esta decisión se invertiría y habría que ir a PostgreSQL siempre. El camino ya está construido; sería cambiar qué capa manda.

## Por qué el contenido se genera y no se copia

488 páginas de los tres portales tenían contenido duplicado, incluido un grupo de 135 fichas de Ipe con la misma descripción palabra por palabra. Copiarlas tal cual habría trasladado el problema al sitio nuevo.

El contenido se compone a partir de atributos reales de cada producto: especie, dureza Janka, densidad, color, vida útil, medida nominal y real, marca, garantía y grado. Con 23 especies y 12 marcas en `kb.py`, dos fichas distintas nunca generan el mismo texto.

Cuando el texto original **no** estaba duplicado, se conserva y se le añade la parte técnica. No se ha tirado nada que fuese único.

Son datos técnicos correctos, no invenciones. Aun así, Marketing debería revisarlos antes de publicarlos como definitivos.

## Por qué la base de datos es opcional

Porque el prototipo lo va a abrir dirección, probablemente sin avisar y probablemente desde el móvil. Un proyecto gratuito de Supabase se suspende por inactividad. Si el sitio dependiera de él, la demo se caería.

Con el dataset local como respaldo, el portal responde siempre. Supabase aporta el modo real: contenido editable sin tocar código y búsqueda en PostgreSQL.

## Por qué las fichas sin foto llevan una portada generada

285 de las 295 fichas llegaron sin ninguna imagen. Un hueco gris repetido 285 veces se lee como un sitio roto. Una portada con el color real de la especie y las iniciales del producto se lee como una decisión.

Y sobre todo: no inventa una fotografía que no existe. En `QA-PROTOTIPO.md` están listadas las que necesitan foto real.
