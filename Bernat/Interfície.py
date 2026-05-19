# -*- coding: utf-8 -*-

################################################################################
## Form generated manually to emulate Qt Designer style
## Aplicación: Traffic Analytics Catalunya
## View tonta (solo diseño visual)
################################################################################

from PySide6.QtCore import (QCoreApplication, QRect)
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDateEdit, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QSpinBox, QStatusBar, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")

        MainWindow.resize(1400, 900)
        MainWindow.setWindowTitle("Traffic Analytics Catalunya")

        # CENTRAL WIDGET
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayoutMain = QVBoxLayout(self.centralwidget)
        self.verticalLayoutMain.setObjectName("verticalLayoutMain")

        # =========================
        # HEADER
        # =========================
        self.headerWidget = QWidget(self.centralwidget)
        self.headerLayout = QHBoxLayout(self.headerWidget)

        self.titleLabel = QLabel("Traffic Analytics Catalunya")
        self.headerLayout.addWidget(self.titleLabel)

        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Buscar zona o carretera...")
        self.headerLayout.addWidget(self.searchBar)

        self.filterButton = QPushButton("Filtros")
        self.headerLayout.addWidget(self.filterButton)

        self.exportButton = QPushButton("Exportar")
        self.headerLayout.addWidget(self.exportButton)

        self.verticalLayoutMain.addWidget(self.headerWidget)

        # =========================
        # PANEL DESTACADO
        # =========================
        self.criticalPanel = QFrame()
        self.criticalPanel.setFrameShape(QFrame.StyledPanel)

        self.criticalLayout = QVBoxLayout(self.criticalPanel)

        self.criticalTitle = QLabel("Foco crítico en Barcelona")
        self.criticalLayout.addWidget(self.criticalTitle)

        self.criticalDescription = QLabel(
            "Zona de tránsito intenso con alta densidad de accidentes."
        )
        self.criticalLayout.addWidget(self.criticalDescription)

        self.verticalLayoutMain.addWidget(self.criticalPanel)

        # =========================
        # FILTROS
        # =========================
        self.filterGroup = QGroupBox("Filtros")
        self.filterLayout = QGridLayout(self.filterGroup)

        # Fecha inicio
        self.filterLayout.addWidget(QLabel("Fecha inicio"), 0, 0)
        self.dateStart = QDateEdit()
        self.filterLayout.addWidget(self.dateStart, 0, 1)

        # Fecha fin
        self.filterLayout.addWidget(QLabel("Fecha fin"), 0, 2)
        self.dateEnd = QDateEdit()
        self.filterLayout.addWidget(self.dateEnd, 0, 3)

        # Tipo vía
        self.filterLayout.addWidget(QLabel("Tipo de vía"), 1, 0)
        self.roadTypeCombo = QComboBox()
        self.roadTypeCombo.addItems(
            ["Autopista", "Autovía", "Carretera", "Urbano"]
        )
        self.filterLayout.addWidget(self.roadTypeCombo, 1, 1)

        # Tipo vehículo
        self.filterLayout.addWidget(QLabel("Tipo vehículo"), 1, 2)
        self.vehicleTypeCombo = QComboBox()
        self.vehicleTypeCombo.addItems(
            ["Coche", "Moto", "Autobús", "Camión", "Peatón", "Bicicleta"]
        )
        self.filterLayout.addWidget(self.vehicleTypeCombo, 1, 3)

        # Víctimas
        self.filterLayout.addWidget(QLabel("Nº víctimas"), 2, 0)
        self.victimsSpin = QSpinBox()
        self.filterLayout.addWidget(self.victimsSpin, 2, 1)

        # Clima
        self.filterLayout.addWidget(QLabel("Clima"), 2, 2)
        self.weatherCombo = QComboBox()
        self.weatherCombo.addItems(
            ["Soleado", "Lluvia", "Niebla", "Nieve", "Viento"]
        )
        self.filterLayout.addWidget(self.weatherCombo, 2, 3)

        # Gravedad
        self.filterLayout.addWidget(QLabel("Gravedad"), 3, 0)
        self.severityCombo = QComboBox()
        self.severityCombo.addItems(
            ["Leve", "Grave", "Muerte"]
        )
        self.filterLayout.addWidget(self.severityCombo, 3, 1)

        self.verticalLayoutMain.addWidget(self.filterGroup)

        # =========================
        # SECCIÓN CENTRAL
        # =========================
        self.middleWidget = QWidget()
        self.middleLayout = QHBoxLayout(self.middleWidget)

        # TABLA
        self.accidentTable = QTableWidget()
        self.accidentTable.setColumnCount(7)

        headers = [
            "Fecha", "Tipo vía", "Vehículo",
            "Víctimas", "Velocidad", "Clima", "Gravedad"
        ]

        self.accidentTable.setHorizontalHeaderLabels(headers)
        self.accidentTable.setRowCount(5)

        # Datos de ejemplo
        for row in range(5):
            for col in range(7):
                self.accidentTable.setItem(
                    row, col, QTableWidgetItem("...")
                )

        self.middleLayout.addWidget(self.accidentTable)

        # MAPA PLACEHOLDER
        self.mapView = QLabel("Mapa de Cataluña (Folium / QWebEngineView)")
        self.mapView.setFrameShape(QFrame.Box)
        self.mapView.setMinimumSize(600, 400)
        self.middleLayout.addWidget(self.mapView)

        self.verticalLayoutMain.addWidget(self.middleWidget)

        # =========================
        # DASHBOARD
        # =========================
        self.dashboardWidget = QWidget()
        self.dashboardLayout = QGridLayout(self.dashboardWidget)

        self.chart1 = QGroupBox("Accidentes / época del año")
        self.dashboardLayout.addWidget(self.chart1, 0, 0)

        self.chart2 = QGroupBox("Vehículo / gravedad")
        self.dashboardLayout.addWidget(self.chart2, 0, 1)

        self.chart3 = QGroupBox("Vehículos accidentados")
        self.dashboardLayout.addWidget(self.chart3, 0, 2)

        self.chart4 = QGroupBox("Accidentes / clima")
        self.dashboardLayout.addWidget(self.chart4, 1, 0)

        self.chart5 = QGroupBox("Tipos de vía")
        self.dashboardLayout.addWidget(self.chart5, 1, 1)

        self.verticalLayoutMain.addWidget(self.dashboardWidget)

        # SET CENTRAL WIDGET
        MainWindow.setCentralWidget(self.centralwidget)

        # STATUS BAR
        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)


# =========================
# EJECUCIÓN
# =========================
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()
    sys.exit(app.exec())