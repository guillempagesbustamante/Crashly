from Marker1 import Markers
from Stats1 import Stats

m = Markers()

# Stats on full dataset
s = Stats(m.cargar_datos())
print(s.resum())
print(s.distribucio_per_hora())
print(s.taxa_mortalitat_per_municipi(top_n=5))

# Stats on a filtered subset (e.g. only fatal accidents)
df_filtrat = m.filtrar(gravetat="Accident mortal")
s_filtrat = Stats(df_filtrat)
print(s_filtrat.franja_mes_perillosa())