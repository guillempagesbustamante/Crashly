
import folium

# Crear mapa
mapa = folium.Map(location=[41.8205, 1.8677], zoom_start=8)

# Accidentes ejemplo
folium.CircleMarker(
    location=[41.3851, 2.1734],
    radius=6,
    color="red",
    fill=True,
    fill_color="red",
    popup="Accidente grave - Barcelona"
).add_to(mapa)

folium.CircleMarker(
    location=[41.9794, 2.8214],
    radius=6,
    color="orange",
    fill=True,
    fill_color="orange",
    popup="Accidente leve - Girona"
).add_to(mapa)

# Guardar
mapa.save("mapa_catalunya.html")

print("Mapa generado correctamente")