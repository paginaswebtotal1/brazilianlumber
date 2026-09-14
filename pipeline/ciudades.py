# -*- coding: utf-8 -*-
"""Datos reales por ciudad, para que cada pagina de zona diga algo propio.

El problema de origen: los 3 portales tenian 135 paginas de ciudad con el MISMO
texto de 3.220 palabras y solo cambiaba el nombre. Resultado medido en Search
Console: posicion media 23,5 y un CTR del 0,42%. Estan en la pagina 3 de Google
precisamente por eso.

Recrearlas iguales seria repetir el error. Asi que cada una lleva lo que de
verdad cambia de una a otra y condiciona la eleccion de la madera:

  terreno  costa / valle / interior / desierto / montana
  condado  el area metropolitana real
  almacen  cual de los tres despacha
  nota     el factor local que decide la especificacion

La sal, la humedad, la amplitud termica y la radiacion no son adorno: son lo
que hace que en Santa Monica falle un tornillo galvanizado y en Palm Springs se
abra una tabla mal secada.
"""

# slug -> (nombre, estado, condado o area, terreno, almacen)
CIUDADES = {
    # ---- costa de Los Angeles
    "santa-monica": ("Santa Monica", "CA", "Los Angeles County", "costa", "Los Angeles"),
    "venice": ("Venice", "CA", "Los Angeles County", "costa", "Los Angeles"),
    "marina-del-rey": ("Marina del Rey", "CA", "Los Angeles County", "costa", "Los Angeles"),
    "manhattan-beach": ("Manhattan Beach", "CA", "Los Angeles County", "costa", "Los Angeles"),
    "redondo-beach": ("Redondo Beach", "CA", "Los Angeles County", "costa", "Los Angeles"),
    "el-segundo": ("El Segundo", "CA", "Los Angeles County", "costa", "Los Angeles"),
    "malibu": ("Malibu", "CA", "Los Angeles County", "costa", "Los Angeles"),
    "pacific-palisades": ("Pacific Palisades", "CA", "Los Angeles County", "costa", "Los Angeles"),
    "rancho-palos-verdes": ("Rancho Palos Verdes", "CA", "Los Angeles County", "costa", "Los Angeles"),
    "san-pedro": ("San Pedro", "CA", "Los Angeles County", "costa", "Los Angeles"),
    "long-beach": ("Long Beach", "CA", "Los Angeles County", "costa", "Los Angeles"),
    "seal-beach": ("Seal Beach", "CA", "Orange County", "costa", "Los Angeles"),
    "huntington-beach": ("Huntington Beach", "CA", "Orange County", "costa", "Los Angeles"),
    "laguna-beach": ("Laguna Beach", "CA", "Orange County", "costa", "Los Angeles"),
    "costa-mesa": ("Costa Mesa", "CA", "Orange County", "costa", "Los Angeles"),
    "oxnard": ("Oxnard", "CA", "Ventura County", "costa", "Los Angeles"),
    "carpinteria": ("Carpinteria", "CA", "Santa Barbara County", "costa", "Los Angeles"),
    "montecito": ("Montecito", "CA", "Santa Barbara County", "costa", "Los Angeles"),
    "chula-vista": ("Chula Vista", "CA", "San Diego County", "costa", "Los Angeles"),

    # ---- Los Angeles urbano
    "hollywood": ("Hollywood", "CA", "Los Angeles County", "urbano", "Los Angeles"),
    "west-hollywood": ("West Hollywood", "CA", "Los Angeles County", "urbano", "Los Angeles"),
    "north-hollywood": ("North Hollywood", "CA", "Los Angeles County", "valle", "Los Angeles"),
    "west-los-angeles": ("West Los Angeles", "CA", "Los Angeles County", "urbano", "Los Angeles"),
    "beverly-hills": ("Beverly Hills", "CA", "Los Angeles County", "urbano", "Los Angeles"),
    "brentwood": ("Brentwood", "CA", "Los Angeles County", "urbano", "Los Angeles"),
    "silver-lake": ("Silver Lake", "CA", "Los Angeles County", "urbano", "Los Angeles"),
    "glendale": ("Glendale", "CA", "Los Angeles County", "valle", "Los Angeles"),
    "burbank": ("Burbank", "CA", "Los Angeles County", "valle", "Los Angeles"),
    "pasadena": ("Pasadena", "CA", "Los Angeles County", "valle", "Los Angeles"),
    "south-pasadena": ("South Pasadena", "CA", "Los Angeles County", "valle", "Los Angeles"),
    "sierra-madre": ("Sierra Madre", "CA", "Los Angeles County", "montana", "Los Angeles"),
    "la-canada": ("La Canada Flintridge", "CA", "Los Angeles County", "montana", "Los Angeles"),
    "la-crescenta": ("La Crescenta", "CA", "Los Angeles County", "montana", "Los Angeles"),
    "montrose": ("Montrose", "CA", "Los Angeles County", "montana", "Los Angeles"),
    "arcadia": ("Arcadia", "CA", "Los Angeles County", "valle", "Los Angeles"),
    "encino": ("Encino", "CA", "Los Angeles County", "valle", "Los Angeles"),
    "woodland-hills": ("Woodland Hills", "CA", "Los Angeles County", "valle", "Los Angeles"),
    "calabasas": ("Calabasas", "CA", "Los Angeles County", "valle", "Los Angeles"),
    "santa-clarita": ("Santa Clarita", "CA", "Los Angeles County", "interior", "Los Angeles"),
    "whittier": ("Whittier", "CA", "Los Angeles County", "interior", "Los Angeles"),
    "diamond-bar": ("Diamond Bar", "CA", "Los Angeles County", "interior", "Los Angeles"),

    # ---- Orange County e interior
    "anaheim": ("Anaheim", "CA", "Orange County", "interior", "Los Angeles"),
    "santa-ana": ("Santa Ana", "CA", "Orange County", "interior", "Los Angeles"),
    "irvine": ("Irvine", "CA", "Orange County", "interior", "Los Angeles"),
    "tustin": ("Tustin", "CA", "Orange County", "interior", "Los Angeles"),
    "brea": ("Brea", "CA", "Orange County", "interior", "Los Angeles"),
    "orange-county": ("Orange County", "CA", "Orange County", "interior", "Los Angeles"),
    "riverside": ("Riverside", "CA", "Riverside County", "desierto", "Los Angeles"),
    "moreno-valley": ("Moreno Valley", "CA", "Riverside County", "desierto", "Los Angeles"),
    "san-bernardino": ("San Bernardino", "CA", "San Bernardino County", "desierto", "Los Angeles"),
    "fontana": ("Fontana", "CA", "San Bernardino County", "desierto", "Los Angeles"),
    "bakersfield": ("Bakersfield", "CA", "Kern County", "desierto", "Los Angeles"),

    # ---- norte de California
    "san-francisco": ("San Francisco", "CA", "Bay Area", "costa", "Los Angeles"),
    "oakland": ("Oakland", "CA", "Bay Area", "costa", "Los Angeles"),
    "fremont": ("Fremont", "CA", "Bay Area", "interior", "Los Angeles"),
    "san-mateo": ("San Mateo", "CA", "Bay Area", "costa", "Los Angeles"),
    "sunnyvale": ("Sunnyvale", "CA", "Bay Area", "interior", "Los Angeles"),
    "stockton": ("Stockton", "CA", "Central Valley", "interior", "Los Angeles"),
    "modesto": ("Modesto", "CA", "Central Valley", "interior", "Los Angeles"),
    "hardwoods-in-summerland": ("Summerland", "CA", "Santa Barbara County", "costa", "Los Angeles"),
}

# lo que de verdad cambia la especificacion, por terreno
TERRENO = {
    "costa": (
        "salt air",
        "Salt air is the hardest condition there is for a deck. It corrodes coated and "
        "galvanized fasteners within a season and leaves a rust stain around every fixing, so "
        "here stainless steel is not a recommendation, it is the only option. Dense tropical "
        "hardwood and capped composite both hold up; anything that relies on a film finish to "
        "survive does not.",
        ["Ipe", "Cumaru", "capped composite"],
    ),
    "urbano": (
        "shade and reflected heat",
        "Tight urban lots mean a deck that is half in shade and half in full sun all day. That "
        "split is what causes uneven weathering: the sunny half silvers in a season while the "
        "shaded half stays dark and holds moisture. Airflow underneath matters more here than "
        "the choice of board.",
        ["Ipe", "Garapa", "Trex"],
    ),
    "valle": (
        "wide daily temperature swing",
        "The valley swings hard between afternoon heat and night cooling, and that daily cycle "
        "is what opens joints and loosens fasteners over time. Kiln dried stock and a generous "
        "gap at install absorb the movement; green lumber does not.",
        ["Ipe", "Cumaru", "Garapa"],
    ),
    "interior": (
        "dry heat and a long rainless season",
        "Inland heat pulls moisture out of the board faster than anywhere on the coast. The "
        "failure mode here is not rot, it is checking and cupping from drying too fast, so "
        "moisture content at delivery matters more than natural durability.",
        ["Ipe", "Garapa", "capped composite"],
    ),
    "desierto": (
        "extreme surface temperature and ultraviolet load",
        "Surface temperature is the deciding factor here. A dark board in full inland sun gets "
        "hot enough to be uncomfortable barefoot, and the ultraviolet load fades an "
        "unprotected surface within one season. Lighter species run measurably cooler: Garapa "
        "is the usual answer when the deck sees afternoon sun with no shade.",
        ["Garapa", "Ipe", "capped composite"],
    ),
    "montana": (
        "elevation, fire code and freeze at night",
        "Elevation brings two things: a real overnight freeze in winter and, in these "
        "foothills, wildfire code. Ipe carries a Class A flame spread rating, the same as "
        "concrete and steel, which is why it gets specified in the hillside communities where "
        "the code requires it.",
        ["Ipe", "Cumaru", "thermally modified"],
    ),
}


def datos(slug):
    return CIUDADES.get(slug)


def contexto(terreno):
    return TERRENO.get(terreno, TERRENO["interior"])
