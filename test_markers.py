from Marker import Markers
import os
print(os.path.abspath("base_dades.csv"))
print(os.path.exists("base_dades.csv"))
m = Markers()

# Check data loads correctly
df = m.cargar_datos()
print(f"Total files: {len(df)}")
print(df.head())

# Check unique values for dropdowns
print("\nGravetat values:", m.valors_unics("D_GRAVETAT"))
print("TipAcc values:", m.valors_unics("tipAcc"))

# Test a filter
df_filtrat = m.filtrar(gravetat=m.valors_unics("D_GRAVETAT")[0])
print(f"\nFiltered rows: {len(df_filtrat)}")