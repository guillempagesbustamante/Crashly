import sys
import folium
from PySide6.QtWidgets import QApplication, QDialog
from Prova_Mapa import Ui_Dialog


class FinestresMapa(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # 1. Crear el mapa amb el zoom i centre òptims per a una finestra de 832x590
        mapa_catalunya = folium.Map(location=[41.82, 1.75],zoom_start=8,min_zoom=8,max_zoom=14,
            # LÍMITES SCROLL
            min_lat=40.30,max_lat=42.90,min_lon=0.10,max_lon=3.40,
            # Impide salir de los límites
            max_bounds=True,
            # Permite mover SOLO dentro de Cataluña
            dragging=True,
            # Zoom con ratón
            scrollWheelZoom=True,
            zoom_control=True,
            tiles="OpenStreetMap")

        # 2. Exemple: Marcador a Montserrat per comprovar la interactivitat
        folium.Marker(
            location=[41.5958, 1.8302],
            popup="Muntanya de Montserrat",
            tooltip="Fes clic aquí"
        ).add_to(mapa_catalunya)

        # 3. Extreure el codi HTML del mapa a la memòria de Python
        dades_html = mapa_catalunya._repr_html_()

        # 4. Injectar l'HTML al teu widget anomenat "Mapa"
        self.ui.Mapa.setHtml(dades_html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    finestra = FinestresMapa()
    finestra.show()
    sys.exit(app.exec())
