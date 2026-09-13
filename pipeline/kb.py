# -*- coding: utf-8 -*-
"""Base de conocimiento de materiales. Datos tecnicos reales por especie y marca.
Sirve para generar contenido UNICO y factual en cada ficha, sin duplicar texto.
"""

# especie -> (nombre, Janka lbf, densidad kg/m3, color, durabilidad, nota)
ESPECIES = {
 "ipe":          ("Ipe", 3680, 1100, "deep olive-brown with fine, tight grain", "50+ years untreated", "Class A fire rating, the same rating as concrete and steel"),
 "cumaru":       ("Cumaru", 3540, 1085, "warm golden to reddish brown with interlocked grain", "30+ years untreated", "often specified as a lower-cost alternative to Ipe with nearly identical hardness"),
 "massaranduba": ("Massaranduba", 3190, 1100, "deep red that ages to a rich russet", "30+ years untreated", "one of the densest South American hardwoods in commercial supply"),
 "jatoba":       ("Jatoba", 2350, 910, "salmon red to orange-brown darkening to a deep russet", "25+ years untreated", "known commercially as Brazilian Cherry"),
 "tigerwood":    ("Tigerwood", 1850, 855, "orange-brown with dramatic dark striping", "25+ years untreated", "the boldest grain figure of the tropical decking species"),
 "piquia":       ("Piquia", 1700, 800, "light yellowish to grayish brown", "20+ years untreated", "also sold as White Ironwood, a value-priced tropical decking option"),
 "garapa":       ("Garapa", 1650, 830, "pale golden yellow that silvers evenly", "20+ years untreated", "the lightest colored tropical hardwood decking, and the coolest underfoot"),
 "teak":         ("Teak", 1070, 655, "golden brown with a naturally oily surface", "40+ years untreated", "the traditional marine decking species, prized for dimensional stability"),
 "red-oak":      ("Red Oak", 1290, 700, "light reddish brown with open pores", "interior use", "a domestic hardwood staple for flooring and millwork"),
 "white-oak":    ("White Oak", 1360, 755, "light to medium brown with closed pores", "20+ years treated", "closed cell structure makes it the oak of choice for exterior work"),
 "maple":        ("Hard Maple", 1450, 705, "creamy white with a subtle grain", "interior use", "a fine, uniform texture that takes stain and finish evenly"),
 "walnut":       ("Black Walnut", 1010, 610, "chocolate brown with purple undertones", "interior use", "the premier domestic hardwood for furniture and feature walls"),
 "sapele":       ("Sapele", 1410, 670, "medium reddish brown with a ribbon figure", "20+ years treated", "a stable African hardwood widely used for windows and doors"),
 "mahogany":     ("African Mahogany", 1070, 590, "pinkish to reddish brown", "interior and protected exterior", "a classic, easy working hardwood for millwork"),
 "santos-mahogany": ("Santos Mahogany", 2200, 900, "dark reddish brown", "25+ years untreated", "much harder than true mahogany, suited to high traffic floors"),
 "cedar":        ("Western Red Cedar", 350, 370, "reddish brown with pale sapwood", "15+ years untreated", "naturally rot resistant, light, and easy to work"),
 "cypress":      ("Cypress", 510, 510, "pale yellowish brown", "15+ years untreated", "contains cypressene, a natural preservative oil"),
 "douglas-fir":  ("Douglas Fir", 660, 530, "light reddish tan with a straight grain", "structural", "the highest strength to weight ratio of the common softwoods"),
 "spruce":       ("Spruce", 510, 450, "nearly white with a fine, even grain", "structural", "a light, stiff framing softwood"),
 "pine":         ("Southern Yellow Pine", 870, 640, "yellowish tan with visible growth rings", "structural, treated for exterior", "the standard pressure treated framing and decking softwood"),
 "redwood":      ("California Redwood", 450, 420, "rich reddish brown", "20+ years untreated", "naturally decay resistant and highly dimensionally stable"),
 "ayous":        ("Thermo Ayous", 700, 500, "uniform warm caramel brown through the full thickness", "25+ years untreated", "thermal modification removes the sugars that feed rot and insects"),
 "bamboo":       ("Bamboo", 3000, 1150, "carbonized amber to natural straw", "20+ years", "a rapidly renewable grass compressed into a dense decking board"),
}

# marca -> (nombre, material, garantia, nota tecnica)
MARCAS = {
 "trex":          ("Trex", "wood-alternative composite", "25-year limited residential fade and stain warranty", "made from 95% reclaimed wood and plastic film"),
 "timbertech":    ("TimberTech", "capped composite and capped polymer", "30-year limited fade and stain warranty", "a four-sided cap seals the board against moisture"),
 "azek":          ("AZEK", "capped cellular PVC", "50-year limited warranty", "contains no wood flour at all, so there is nothing in the board for mold to feed on"),
 "moistureshield": ("MoistureShield", "solid core composite", "50-year structural warranty", "the only composite rated for direct ground and underwater contact"),
 "deckotech":     ("DeckoTech", "co-extruded composite", "25-year limited warranty", "a co-extruded shell over a dense wood-polymer core"),
 "zuri":          ("Zuri", "PVC with a photographic wear layer", "25-year limited warranty", "a printed hardwood grain under a clear acrylic wear layer"),
 "newtechwood":   ("NewTechWood", "capped composite", "25-year limited warranty", "UltraShield capping on all four sides"),
 "armadillo":     ("Armadillo", "composite", "25-year limited warranty", "a low-sheen, textured surface"),
 "deckwise":      ("DeckWise", "hardwood installation hardware and finishes", "manufacturer warranty", "the reference brand for hidden fasteners and oils in tropical hardwood decking"),
 "calibamboo":    ("Cali Bamboo", "fused bamboo", "manufacturer warranty", "fused bamboo fiber with a Janka rating above most tropical hardwoods"),
 "grad":          ("GRAD", "aluminum substructure system", "manufacturer warranty", "a clip-on aluminum rail system that lets boards be removed and replaced individually"),
 "wisewrap":      ("WiseWrap", "joist protection tape", "manufacturer warranty", "a butyl tape that seals the joist top against standing water"),
}

# medidas nominales -> reales (pulgadas), para decking y lumber
MEDIDAS = {
 "1x4":   ('3/4" x 3-1/2"',  "decking board"),
 "1x6":   ('3/4" x 5-1/2"',  "decking board"),
 "1x8":   ('3/4" x 7-1/4"',  "decking and cladding board"),
 "1x12":  ('3/4" x 11-1/4"', "wide board for stair risers and fascia"),
 "5/4x4": ('1" x 3-1/2"',    "heavy decking board"),
 "5/4x6": ('1" x 5-1/2"',    "heavy decking board"),
 "5/4x8": ('1" x 7-1/4"',    "wide heavy decking board"),
 "5/4x12":('1" x 11-1/4"',   "wide heavy board for stair treads and fascia"),
 "2x2":   ('1-1/2" x 1-1/2"',"baluster and batten stock"),
 "2x4":   ('1-1/2" x 3-1/2"',"dimensional lumber"),
 "2x6":   ('1-1/2" x 5-1/2"',"dimensional lumber and stair tread stock"),
 "2x8":   ('1-1/2" x 7-1/4"',"structural dimensional lumber"),
 "2x10":  ('1-1/2" x 9-1/4"',"structural joist stock"),
 "2x12":  ('1-1/2" x 11-1/4"',"structural joist and stringer stock"),
 "4x4":   ('3-1/2" x 3-1/2"',"post stock"),
 "6x6":   ('3-1/2" x 5-1/2"',"heavy post and beam stock"),
 "8x8":   ('7-1/2" x 7-1/2"',"timber"),
}

# color de marca por rama, para el fallback visual cuando no hay foto
COLORES = {
 "ipe": "#5a4632", "cumaru": "#8a5a2b", "massaranduba": "#7b2f22", "jatoba": "#8c3b28",
 "tigerwood": "#a0522d", "garapa": "#c9a227", "piquia": "#b09a6b", "teak": "#a9793f",
 "decking": "#6b4f3a", "lumber": "#8b6f4e", "cladding-siding": "#7a6a58",
 "fencing-gates": "#5f6b5a", "flooring": "#94643f", "slabs": "#6e4b30",
 "landscaping": "#4a7c59", "accessories": "#4c5a66",
}
