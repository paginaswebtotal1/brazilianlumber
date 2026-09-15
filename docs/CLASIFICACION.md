# Por que 235 URLs acababan en /accessories/

**14 de septiembre de 2026.** Lo encontraste tu mirando el Excel: `/product-tag/1x4/`
decia que dejaba de indexarse y que iba a `/accessories/`, y detras venia una lista
larguisima de URLs al mismo sitio. La pregunta era la correcta: *una etiqueta de medida
no es un accesorio, ¿por que va ahi?*

## Lo que pasaba

El estudio clasificaba cada ficha y cada archivo **leyendo su nombre**. Funciona para
`ipe-1x6`, pero no para lo que no se llama como lo que es. Y al final del clasificador
habia una linea que lo remataba: lo que no reconocia, a `/accessories/`.

Asi que ese cajon recogia tres cosas distintas, y ninguna era un accesorio:

| Lo que caia ahi | Cuantas | Que es en realidad |
|---|---|---|
| Archivos de largo (`/length/12/`, `/board-length/lf/`) | 89 | Un filtro que cruza tarima y madera |
| Etiquetas de producto (`/product-tag/1x4/`, `/product-tag/brazilian-hardwood/`) | 44 | Medidas y materiales |
| Archivos de color (`/color/slate-gray/`, `/color/kona/`) | 20 | Colores de composite y PVC |
| `/shop/` con parametros, UPC, tallas, cantidades | 44 | El catalogo |
| Fichas que el nombre no delata | 11 | Cesped, paneles vegetales, teto vinilico |
| Otros | 27 | |

Las 11 fichas son el ejemplo mas claro del problema. Ninguna dice en su titulo lo que es:

- **Ciro Green** y **Diana Blush** -> cesped artificial y panel vegetal
- **Origens Tauari**, **Teca Castanho**, **Agar Castanho**, **Jungle Duma** (8 en total) -> teto vinilico
- **Ayous 1x6** -> madera termotratada

## Lo que se ha hecho

La tienda ya sabia todo esto. WooCommerce publica, para cada ficha, **su categoria, sus
etiquetas y sus atributos** en `/wp-json/wc/store/v1/products`, y esa API no la filtra
Cloudflare. Es un dato de origen, no una deduccion. Se han traido las 309 fichas de los
tres portales y ahora:

1. **Cada producto va a la rama que dice la tienda.** Las 295 fichas tienen categoria
   real y todas menos la promocional `hot-deals` encajan en el arbol nuevo.

2. **El nombre sigue mandando en lo que la tienda no sabe.** La tienda mete un 4x4 de
   Ipe en "Ipe Wood" igual que una tabla de 1x6, porque su arbol no tiene un nodo de
   madera dimensional. La escuadria la da el nombre, y por eso `/lumber/tropical-hardwood/`
   tiene ahora 38 fichas y no cero. Lo mismo con puertas, lamas, baldosas y tornilleria.

3. **Cada archivo de atributo y cada etiqueta van a donde estan sus productos.** No hay
   que adivinar `/color/slate-gray/`: se sabe exactamente que fichas lo llevan. Si todas
   son AZEK, la URL es de AZEK.

4. **Lo que de verdad cruza ramas va a `/shop/`.** `/length/12/` lista tablas de terraza
   y escuadrias de estructura a la vez: no hay una categoria honesta, y el catalogo con
   filtros es literalmente lo que era ese archivo. Decir `/shop/` es exacto; decir
   `/accessories/` era falso.

## Resultado

| | Antes | Ahora |
|---|---:|---:|
| URLs que acaban en `/accessories/` | 235 | **22** |
| Fichas sin subcategoria propia | 11 | **0** |
| Redirecciones documentadas | 776 | **1.505** |
| Clics en URLs que desaparecen sin destino | 357 | **0** |
| Categorias del menu sin producto | 3 | **3** (las mismas, y son decision de negocio) |

Las 22 que quedan en `/accessories/` si son accesorios, y estan en los tres portales: la
propia categoria antigua "Decking Accessories" con su paginacion, y las etiquetas
`deckwise`, `deck-wise`, `deck-maintenance` y `deck-and-wood-brightener`, que abarcan
tornilleria, aceites y mantenimiento a la vez, asi que su sitio es la raiz de accesorios
y no una subcategoria.

## Efecto de rebote: se llenaron categorias que estaban vacias

Al mandar cada ficha por su tipo y no por su marca, salieron a la luz productos que
estaban escondidos:

- `/fencing-gates/composite/` y `/fencing-gates/gates/`: 3 fichas (antes 0)
- `/cladding-siding/battens-louvers/`: 2 (antes 0)
- `/decking/deck-tiles/`: 3 (antes 1)
- `/decking/composite/moistureshield/`, `/decking/bamboo/`: 1 cada una (antes 0)
- `/lumber/tropical-hardwood/`: 38 (antes 0)

Un producto puede estar en varias categorias sin generar una segunda URL, porque la ficha
vive siempre en `/product/{slug}/`. Por eso una tarima de Armadillo aparece en su marca y
tambien en PVC, que es donde la busca el cliente.

## Lo que sigue siendo decision tuya, no mia

Tres categorias del menu no tienen ni una ficha en ninguno de los tres portales:

- `/fencing-gates/wood/` (valla de madera maciza)
- `/flooring/engineered/` (suelo de ingenieria)
- `/decking/thermally-modified/durathermo/` (Durathermo)

O se les da producto, o se quitan del menu. No las he tocado porque eso es catalogo, no
arquitectura.

## Comprobaciones pasadas despues del cambio

| Verificacion | Resultado |
|---|---|
| 6.169 URLs contra 17 reglas de coherencia | 0 incumplimientos |
| 5.501 URLs de Search Console | 0 fuera del mapa, 0 destinos rotos |
| 69.195 clics | 100,00% con destino correcto |
| 797 URLs del portal | todas 200, H1 unico, title, description, canonical, JSON-LD, noindex |
| 740 destinos distintos | 0 caidos, 0 cadenas, 0 bucles |
| El Excel contra el portal, fila por fila | 0 desajustes |
| Contenido duplicado | 11.625 pares casi identicos en el origen, 36 en el portal nuevo |
