import sys
import folium
from PySide6.QtWidgets import QApplication, QDialog
from Prova_Mapa import Ui_Dialog


class FinestresMapa(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # 1. Definir els límits geogràfics de contenció (reajustats per incloure tot el territori)
        # Sud-Oest (per sota del Delta de l'Ebre) i Nord-Est (més enllà de Girona/Pirineus)
        limits_catalunya = [[40.30, 0.10], [42.90, 3.40]]

        # 2. Crear el mapa amb el zoom i centre òptims per a una finestra de 832x590
        mapa_catalunya = folium.Map(
            location=[41.82, 1.75],  # Centre calculat per enquadrar perfectament de l'Aran a l'Ebre
            zoom_start=7.5,  # Zoom corregit per encabir tot el territori sense talls
            min_zoom=7,  # Evita que es puguin allunyar massa
            max_zoom=13,  # Permet apropar-se de manera controlada
            max_bounds=True,  # Activa el sistema de contenció perimetral
            bounds=limits_catalunya,  # Aplica les coordenades límit
            tiles="OpenStreetMap",

            # --- CONFIGURACIÓ DE MOVIMENT CONTROLAT ---
            dragging=False,  # Permetem lliscar NOMÉS el necessari per veure els extrems
            keyboard=True  # Permetem moure's amb el teclat dins dels límits
        )

        # 3. Exemple: Marcador a Montserrat per comprovar la interactivitat
        folium.Marker(
            location=[41.5958, 1.8302],
            popup="Muntanya de Montserrat",
            tooltip="Fes clic aquí"
        ).add_to(mapa_catalunya)

        # 4. Extreure el codi HTML del mapa a la memòria de Python
        dades_html = mapa_catalunya._repr_html_()

        # 5. Injectar l'HTML al teu widget anomenat "Mapa"
        self.ui.Mapa.setHtml(dades_html)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    finestra = FinestresMapa()
    finestra.show()
    sys.exit(app.exec())
