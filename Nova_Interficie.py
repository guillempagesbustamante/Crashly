import sys
import folium
from geopy.geocoders import Nominatim

from PySide6.QtWidgets import (
    QApplication, QDateEdit, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QStatusBar,
    QVBoxLayout, QWidget
)

from PySide6.QtWebEngineWidgets import QWebEngineView

# =========================
# MATPLOTLIB
# =========================

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):

    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(111)

        super().__init__(fig)


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):

        MainWindow.resize(1400, 900)
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
        self.mapView.setMinimumHeight(400)

        self.middleLayout.addWidget(self.mapView)

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

            min_lat=40.30,
            max_lat=42.90,
            min_lon=0.10,
            max_lon=3.40,

            max_bounds=True,
            dragging=True,

            scrollWheelZoom=True,

            zoom_control=True,

            tiles="OpenStreetMap"
        )

        # =========================
        # MARCADOR EJEMPLO
        # =========================

        geolocator = Nominatim(
            user_agent="accidents_app"
        )

        direccion = (
            "C-31 km 350, Torroella de Montgrí, Girona"
        )

        location = geolocator.geocode(direccion)

        if location:

            folium.Marker(
                location=[
                    location.latitude,
                    location.longitude
                ],

                popup="Torroella de Montgrí",

                tooltip="Accidente",

                icon=folium.Icon(
                    icon="star",
                    markerColor="white",
                    iconColor="red"
                )

            ).add_to(mapa_catalunya)

        html_mapa = mapa_catalunya.get_root().render()

        self.mapView.setHtml(html_mapa)

        # =========================
        # DASHBOARD
        # =========================

        self.dashboardWidget = QWidget()

        self.dashboardLayout = QGridLayout(
            self.dashboardWidget
        )

        # -------------------------
        # PIE VEHÍCULOS
        # -------------------------

        self.chart1 = QGroupBox(
            "Accidentes por tipo de vehículo"
        )

        self.chart1Layout = QVBoxLayout(
            self.chart1
        )

        self.dashboardLayout.addWidget(
            self.chart1, 0, 0
        )

        # -------------------------
        # PIE PROVINCIAS
        # -------------------------

        self.chart2 = QGroupBox(
            "Accidentes por provincia"
        )

        self.chart2Layout = QVBoxLayout(
            self.chart2
        )

        self.dashboardLayout.addWidget(
            self.chart2, 0, 1
        )

        # -------------------------
        # LÍNEAS TEMPORALES
        # -------------------------

        self.chart3 = QGroupBox(
            "Evolución gravedad (2010–2024)"
        )

        self.chart3Layout = QVBoxLayout(
            self.chart3
        )

        self.dashboardLayout.addWidget(
            self.chart3, 0, 2
        )

        # =========================
        # GRÁFICO 1
        # =========================

        canvas1 = MplCanvas()

        vehiculos = [
            "Turismo",
            "Moto",
            "Camión",
            "Bicicleta"
        ]

        accidentes = [
            65,
            20,
            10,
            5
        ]

        canvas1.axes.pie(
            accidentes,
            labels=vehiculos,
            autopct="%1.1f%%"
        )

        canvas1.axes.set_title(
            "Vehículos implicados"
        )

        self.chart1Layout.addWidget(
            canvas1
        )

        # =========================
        # GRÁFICO 2
        # =========================

        canvas2 = MplCanvas()

        provincias = [
            "Barcelona",
            "Girona",
            "Lleida",
            "Tarragona"
        ]

        accidentes_prov = [
            55,
            15,
            10,
            20
        ]

        canvas2.axes.pie(
            accidentes_prov,
            labels=provincias,
            autopct="%1.1f%%"
        )

        canvas2.axes.set_title(
            "Distribución provincial"
        )

        self.chart2Layout.addWidget(
            canvas2
        )

        # =========================
        # GRÁFICO 3
        # =========================

        canvas3 = MplCanvas()

        años = list(range(2010, 2025))

        mortales = [
            120,115,110,108,100,
            98,95,92,90,85,
            83,80,78,75,72
        ]

        graves = [
            300,290,280,270,260,
            255,250,245,240,235,
            230,225,220,215,210
        ]

        leves = [
            1200,1180,1170,1150,1130,
            1120,1110,1090,1080,1070,
            1060,1040,1030,1020,1000
        ]

        canvas3.axes.plot(
            años,
            mortales,
            marker="o",
            label="Mortales"
        )

        canvas3.axes.plot(
            años,
            graves,
            marker="o",
            label="Graves"
        )

        canvas3.axes.plot(
            años,
            leves,
            marker="o",
            label="Leves"
        )

        canvas3.axes.set_title(
            "Evolución anual"
        )

        canvas3.axes.set_xlabel("Año")

        canvas3.axes.set_ylabel(
            "Número de accidentes"
        )

        canvas3.axes.legend()

        self.chart3Layout.addWidget(
            canvas3
        )

        # =========================
        # AÑADIR DASHBOARD
        # =========================

        self.verticalLayoutMain.addWidget(
            self.dashboardWidget
        )

        # =========================
        # CENTRAL WIDGET FINAL
        # =========================

        MainWindow.setCentralWidget(
            self.centralwidget
        )

        # =========================
        # STATUS BAR
        # =========================

        self.statusbar = QStatusBar()

        MainWindow.setStatusBar(
            self.statusbar
        )


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