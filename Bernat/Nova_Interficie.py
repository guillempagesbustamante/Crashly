import sys
import folium
from geopy.geocoders import Nominatim

from PySide6.QtWidgets import (
    QApplication, QComboBox, QDateEdit, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSpinBox, QStatusBar,
    QVBoxLayout, QWidget
)

from PySide6.QtWebEngineWidgets import QWebEngineView


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):

        MainWindow.resize(3000, 3000)
        MainWindow.setWindowTitle("Traffic Analytics Catalunya")

        # =========================
        # CENTRAL WIDGET
        # =========================

        self.centralwidget = QWidget(MainWindow)
        self.verticalLayoutMain = QVBoxLayout(self.centralwidget)

        # =========================
        # HEADER
        # =========================

        self.headerWidget = QWidget()
        self.headerLayout = QHBoxLayout(self.headerWidget)

        self.titleLabel = QLabel("Traffic Analytics Catalunya")
        self.headerLayout.addWidget(self.titleLabel)

        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText(
            "Buscar zona o carretera..."
        )
        self.headerLayout.addWidget(self.searchBar)

        self.filterButton = QPushButton("Filtros")
        self.headerLayout.addWidget(self.filterButton)

        self.exportButton = QPushButton("Exportar")
        self.headerLayout.addWidget(self.exportButton)

        self.verticalLayoutMain.addWidget(self.headerWidget)

        # =========================
        # PANEL SUPERIOR
        # =========================

        self.criticalPanel = QFrame()
        self.criticalLayout = QVBoxLayout(self.criticalPanel)

        self.criticalTitle = QLabel(
            "Foco crítico en Barcelona"
        )
        self.criticalLayout.addWidget(self.criticalTitle)

        self.criticalDescription = QLabel(
            "Zona de tránsito intenso con alta densidad de accidentes."
        )
        self.criticalLayout.addWidget(
            self.criticalDescription
        )

        self.verticalLayoutMain.addWidget(
            self.criticalPanel
        )

        # =========================
        # FILTROS
        # =========================

        self.filterGroup = QGroupBox("Filtros")
        self.filterLayout = QGridLayout(self.filterGroup)

        self.filterLayout.addWidget(
            QLabel("Fecha inicio"), 0, 0
        )

        self.dateStart = QDateEdit()
        self.filterLayout.addWidget(
            self.dateStart, 0, 1
        )

        self.filterLayout.addWidget(
            QLabel("Fecha fin"), 0, 2
        )

        self.dateEnd = QDateEdit()
        self.filterLayout.addWidget(
            self.dateEnd, 0, 3
        )

        self.verticalLayoutMain.addWidget(
            self.filterGroup
        )

        # =========================
        # ZONA CENTRAL
        # =========================

        self.middleWidget = QWidget()
        self.middleLayout = QHBoxLayout(
            self.middleWidget
        )

        # =========================
        # MAPA INTERACTIVO
        # =========================

        self.mapView = QWebEngineView()
        self.mapView.setMaximumSize(500, 300)

        self.middleLayout.addWidget(self.mapView)

        # IMPORTANTE:
        # añadir la zona central al layout principal

        self.verticalLayoutMain.addWidget(
            self.middleWidget
        )

        # =========================
        # CREAR MAPA FOLIUM
        # =========================

        mapa_catalunya = folium.Map(
            location=[41.82, 1.75],

            zoom_start=7,
            min_zoom=7,
            max_zoom=14,

            # límites Cataluña
            min_lat=40.30,
            max_lat=42.90,
            min_lon=0.10,
            max_lon=3.40,

            # bloquear movimiento fuera
            max_bounds=True,

            # permitir movimiento SOLO dentro
            dragging=True,

            # zoom ratón
            scrollWheelZoom=True,

            zoom_control=True,

            tiles="OpenStreetMap"
        )

        # =========================
        # MARCADOR EJEMPLO
        # =========================

        from geopy.geocoders import Nominatim

        geolocator = Nominatim(user_agent="accidents_app")

        direccion = "C-31 km 350, Torroella de Montgrí, Girona"

        location = geolocator.geocode(direccion)

        if location:
            print("Latitud:", location.latitude)
            print("Longitud:", location.longitude)
        else:
            print("No encontrada")

        latitud = location.latitude
        longitud = location.longitude

        folium.Marker(
            location=[latitud,longitud],
            popup="Torroella de Montgrí",
            tooltip="Accidente",
            icon=folium.Icon(icon = "star", markerColor="white", iconColor=("red"), icon_size=(5,5))
        ).add_to(mapa_catalunya)

        # =========================
        # HTML DEL MAPA
        # =========================

        html_mapa = mapa_catalunya.get_root().render()

        # cargar HTML en Qt
        self.mapView.setHtml(html_mapa)

        # =========================
        # DASHBOARD
        # =========================

        self.dashboardWidget = QWidget()

        self.dashboardLayout = QGridLayout(
            self.dashboardWidget
        )

        self.chart1 = QGroupBox(
            "Accidentes / época del año"
        )

        self.dashboardLayout.addWidget(
            self.chart1, 0, 0
        )

        self.chart2 = QGroupBox(
            "Vehículo / gravedad"
        )

        self.dashboardLayout.addWidget(
            self.chart2, 0, 1
        )

        self.verticalLayoutMain.addWidget(
            self.dashboardWidget
        )

        # =========================
        # CENTRAL WIDGET FINAL
        # =========================

        MainWindow.setCentralWidget(
            self.centralwidget
        )

        # STATUS BAR

        self.statusbar = QStatusBar()
        MainWindow.setStatusBar(self.statusbar)


# =========================
# EJECUCIÓN
# =========================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    MainWindow = QMainWindow()

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()

    sys.exit(app.exec())