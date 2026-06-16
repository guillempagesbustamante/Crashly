import sys
import folium

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from geopy.geocoders import Nominatim

from ui_main_window import Ui_MainWindow


class MplCanvas(FigureCanvas):

    def __init__(self):
        self.figure = Figure(figsize=(5, 4))
        self.axes = self.figure.add_subplot(111)

        super().__init__(self.figure)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_map()
        self.setup_dashboard()

    def setup_map(self):

        self.mapView = QWebEngineView()

        self.ui.verticalLayout.addWidget(self.mapView)

        mapa = folium.Map(
            location=[41.82, 1.75],
            zoom_start=8,
            min_zoom=8,
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

        geolocator = Nominatim(user_agent="crashle")

        direccion = "C-31 km 350, Torroella de Montgrí, Girona"

        location = geolocator.geocode(direccion)

        if location:
            folium.Marker(
                [location.latitude, location.longitude],
                popup="Torroella de Montgrí",
                tooltip="Accident",
                icon=folium.Icon(
                    color="red",
                    icon="info-sign"
                )
            ).add_to(mapa)

        html = mapa.get_root().render()

        self.mapView.setHtml(html)

    def setup_dashboard(self):

        self.create_via_chart()
        self.create_province_chart()
        self.create_temporal_chart()

    def create_via_chart(self):

        canvas = MplCanvas()

        labels = [
            "Autopista",
            "Autovia",
            "Rural/Forestal",
            "Carretera",
            "Altres"
        ]

        values = [520, 180, 90, 110, 300]

        wedges, _, _ = canvas.axes.pie(
            values,
            autopct="%1.1f%%",
            startangle=90,
            radius=0.8
        )
        canvas.axes.legend(
            wedges,
            labels,
            loc="best",
            fontsize=5,
            frameon=False
        )

        canvas.axes.set_title("Accidents per tipus de via")

        canvas.figure.tight_layout()

        self.ui.verticalLayout_2.addWidget(canvas)

    def create_province_chart(self):

        canvas = MplCanvas()

        labels = [
            "Barcelona",
            "Girona",
            "Lleida",
            "Tarragona"
        ]

        values = [620, 120, 80, 140]

        wedges, _, _ = canvas.axes.pie(
            values,
            autopct="%1.1f%%",
            startangle=90,
            radius=0.8
        )
        canvas.axes.legend(
            wedges,
            labels,
            loc="best",
            fontsize=5,
            frameon=False
        )

        canvas.axes.set_title("Accidents per província")

        canvas.figure.tight_layout()

        self.ui.verticalLayout_3.addWidget(canvas)

    def create_temporal_chart(self):

        canvas = MplCanvas()

        years = list(range(2010, 2024))

        mortals = [
            45, 42, 40, 38, 35,
            34, 31, 30, 28, 26,
            24, 23, 22, 22
        ]

        greus = [
            180, 175, 170, 168, 160,
            155, 150, 145, 140, 135,
            130, 126, 122, 122
        ]

        canvas.axes.plot(
            years,
            mortals,
            marker="o",
            label="Mortals"
        )

        canvas.axes.plot(
            years,
            greus,
            marker="o",
            label="Greus"
        )

        canvas.axes.set_title("Evolució temporal")
        canvas.axes.set_xlabel("Any")
        canvas.axes.set_ylabel("Accidents")

        canvas.axes.legend(
            loc="upper center",
            bbox_to_anchor=(-0.2, 1.2),
            ncol=1,
            frameon=False,
            fontsize=7
        )
        canvas.figure.tight_layout()
        canvas.figure.subplots_adjust(bottom=0.2)

        self.ui.verticalLayout_4.addWidget(canvas)


# =========================
# EJECUCIÓN
# =========================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
