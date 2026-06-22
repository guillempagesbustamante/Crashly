from Marker import Markers
Markers().construir_cache()

"""crea el json, en la versio antiga (stats), el crea de 50 en 50, i no parava fins que acabava o el paraves """

"""la alternativa ara seria:

from Marker import Markers

m = Markers()
while True:
    abans = len(m._geo_cache)
    m.construir_cache()
    despres = len(m._geo_cache)
    if despres == abans:
        break  # no hi havia res nou per geocodificar
print("Cache completa!")





"""