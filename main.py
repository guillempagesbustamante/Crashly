import sys
import folium
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QDate
from PySide6.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Importamos la lógica de tu compañero y tu interfaz
from Marker import Markers
from ui_main_window import Ui_MainWindow


class MplCanvas(FigureCanvas):
    def __init__(self):
        # Mantenemos espacio óptimo para la leyenda inferior
        self.figure = Figure(figsize=(4, 3.6))
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Inicializamos el motor de datos de tu compañero
        self.markers_engine = Markers()

        # Creamos e insertamos la vista del mapa una sola vez
        self.mapView = QWebEngineView()
        self.ui.verticalLayout.addWidget(self.mapView)

        # Creamos e insertamos los tres lienzos de Matplotlib
        self.canvas_via = MplCanvas()
        self.canvas_province = MplCanvas()
        self.canvas_temporal = MplCanvas()

        self.ui.verticalLayout_2.addWidget(self.canvas_via)
        self.ui.verticalLayout_3.addWidget(self.canvas_province)
        self.ui.verticalLayout_4.addWidget(self.canvas_temporal)

        # Configurar las fechas por defecto correctas en la interfaz (2010 a 2023)
        self.ui.dateEdit.setDate(QDate(2010, 1, 1))
        self.ui.dateEdit_2.setDate(QDate(2023, 12, 31))

        # Impedir físicamente bajar del año 2010 y subir del año 2023 en los calendarios
        self.ui.dateEdit.setMinimumDate(QDate(2010, 1, 1))
        self.ui.dateEdit.setMaximumDate(QDate(2023, 12, 31))

        self.ui.dateEdit_2.setMinimumDate(QDate(2010, 1, 1))
        self.ui.dateEdit_2.setMaximumDate(QDate(2023, 12, 31))

        # --- Gráfico temporal FIJO nada más iniciar la página web ---
        self.inicializar_grafico_temporal_fijo()

        # --- Conexión correcta de los Push Buttons ---
        self.ui.pushButton.clicked.connect(self.procesar_filtros_y_actualizar)
        self.ui.pushButton_2.clicked.connect(self.limpiar_filtros)

        # Carga inicial de la web: mapa y sectores con los filtros por defecto (Muestra todo)
        self.procesar_filtros_y_actualizar()

    def inicializar_grafico_temporal_fijo(self):
        """Carga TODO el histórico de datos sin importar los filtros y dibuja el gráfico de líneas"""
        df_completo = self.markers_engine.cargar_datos().copy()

        self.canvas_temporal.axes.clear()

        if not df_completo.empty and "dat" in df_completo.columns:
            df_completo['any_extracted'] = df_completo['dat'].dt.year

            df_historico = df_completo[(df_completo['any_extracted'] >= 2010) & (df_completo['any_extracted'] <= 2023)]

            evolucion = df_historico.groupby(['any_extracted', 'D_GRAVETAT']).size().unstack(fill_value=0)

            for columna in evolucion.columns:
                color_linea = "#ef4444" if "mortal" in str(columna).lower() else "#f97316"
                self.canvas_temporal.axes.plot(
                    evolucion.index,
                    evolucion[columna],
                    marker="o",
                    linewidth=2,
                    label=str(columna),
                    color=color_linea
                )

        self.canvas_temporal.axes.set_title("Evolució temporal (2010-2023)", fontsize=9, fontweight="bold")
        self.canvas_temporal.axes.set_xlabel("Any", fontsize=7)
        self.canvas_temporal.axes.set_ylabel("Accidents", fontsize=7)
        self.canvas_temporal.axes.tick_params(labelsize=7)
        self.canvas_temporal.axes.grid(True, linestyle="--", alpha=0.5)
        self.canvas_temporal.axes.legend(loc="best", fontsize=7, frameon=False)

        self.canvas_temporal.figure.tight_layout()
        self.canvas_temporal.draw()

    def procesar_filtros_y_actualizar(self):
        """Lee la interfaz, gestiona el estado 'Seleccionar' y actualiza Mapa y Sectores"""
        data_inici = self.ui.dateEdit.date().toString("dd/MM/yyyy")
        data_fi = self.ui.dateEdit_2.date().toString("dd/MM/yyyy")

        gravetat_sel = self.ui.comboBox_2.currentText()
        gravetat = None if gravetat_sel == "Seleccionar" else gravetat_sel

        df_filtrat = self.markers_engine.filtrar(
            data_inici=data_inici,
            data_fi=data_fi,
            gravetat=gravetat
        )

        if df_filtrat is None:
            df_filtrat = pd.DataFrame()

        provincia_sel = self.ui.comboBox_5.currentText()
        if provincia_sel != "Seleccionar" and not df_filtrat.empty:
            if "nomDem" in df_filtrat.columns:
                df_filtrat = df_filtrat[df_filtrat["nomDem"].str.upper() == provincia_sel.upper()]

        self.renderizar_mapa(df_filtrat)
        self.renderizar_graficos_sectoriales(df_filtrat)

    def renderizar_mapa(self, df):
        """Dibuja en el mapa los marcadores basados en el dataframe filtrado actual"""
        mapa = folium.Map(
            location=[41.82, 1.75], zoom_start=8, min_zoom=8, max_zoom=14,
            min_lat=40.30, max_lat=42.90, min_lon=0.10, max_lon=3.40,
            max_bounds=True, tiles="OpenStreetMap"
        )

        lista_marcadors = self.markers_engine.obtenir_tots_marcadors(df)

        for m in lista_marcadors[:600]:
            color_nodo = "red" if "mortal" in str(m["gravetat"]).lower() else "orange"
            fecha_bonita = m['dat'].strftime('%d/%m/%Y') if hasattr(m['dat'], 'strftime') else str(m['dat'])

            folium.CircleMarker(
                location=[m["lat"], m["lon"]],
                radius=4,
                color=color_nodo,
                fill=True,
                fill_color=color_nodo,
                fill_opacity=0.6,
                popup=f"Fecha: {fecha_bonita}<br>Gravetat: {m['gravetat']}<br>Municipi: {m['municipi']}",
                tooltip=str(m["tipAcc"])
            ).add_to(mapa)

        html = mapa.get_root().render()
        self.mapView.setHtml(html)

    def renderizar_graficos_sectoriales(self, df):
        """Calcula los datos según los filtros y pinta los diagramas de queso con leyenda"""

        # --- 1. SECTORIAL TIPOS DE VÍA (SEPARADO RURAL Y PORCENTAJES EN LEYENDA) ---
        self.canvas_via.axes.clear()
        if not df.empty and "D_TIPUS_VIA" in df.columns:
            # MAPEO EN CATALÁN: Volvemos a separar 'Camí rural/pista forestal' de 'Altres'
            mapeo_vias = {
                "Via urbana( inclou carrer i carrer residencial)": "Via urbana",
                "Carretera convencional": "Carretera convencional",
                "Autovia": "Autovia",
                "Autopista": "Autopista",
                "CamÃ­ rural/pista forestal": "Camí rural/forestal",
                "Altres": "Altres"
            }

            tipos_vias = df["D_TIPUS_VIA"].fillna("Altres").map(lambda x: mapeo_vias.get(x, "Altres"))
            via_counts = tipos_vias.value_counts()
            total_vias = via_counts.sum()

            # SOLUCIÓN AL APELOTONAMIENTO: Ocultamos texto interno en el gráfico para que no se superponga
            wedges, _ = self.canvas_via.axes.pie(
                via_counts.values,
                startangle=90,
                radius=1
            )

            # Construimos las etiquetas de la leyenda integrando los porcentajes reales de forma limpia
            etiquetas_con_pct = [
                f"{index} ({(val / total_vias * 100):.1f}%)"
                for index, val in zip(via_counts.index, via_counts.values)
            ]

            # Ubicación óptima: debajo del gráfico sin colisiones de texto
            self.canvas_via.axes.legend(
                wedges, etiquetas_con_pct,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.05),
                ncol=2,
                fontsize=6,
                frameon=False
            )
        self.canvas_via.axes.set_title("Accidents per tipus de via", fontsize=9, fontweight="bold")
        self.canvas_via.figure.tight_layout()
        self.canvas_via.draw()

        # --- 2. SECTORIAL PROVINCIAS (PORCENTAJES EN LEYENDA) ---
        self.canvas_province.axes.clear()
        if not df.empty and "nomDem" in df.columns:
            prov_counts = df["nomDem"].value_counts()
            total_prov = prov_counts.sum()

            wedges, _ = self.canvas_province.axes.pie(
                prov_counts.values,
                startangle=90,
                radius=1
            )

            nombres_provincias_con_pct = [
                f"{str(index).capitalize()} ({(val / total_prov * 100):.1f}%)"
                for index, val in zip(prov_counts.index, prov_counts.values)
            ]

            self.canvas_province.axes.legend(
                wedges, nombres_provincias_con_pct,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.05),
                ncol=2,
                fontsize=6,
                frameon=False
            )
        self.canvas_province.axes.set_title("Accidents per província", fontsize=9, fontweight="bold")
        self.canvas_province.figure.tight_layout()
        self.canvas_province.draw()

    def limpiar_filtros(self):
        """Botón Netejar hace un RESET completo volviendo al estado inicial"""
        self.ui.comboBox_2.setCurrentIndex(0)
        self.ui.comboBox_5.setCurrentIndex(0)

        self.ui.dateEdit.setDate(QDate(2010, 1, 1))
        self.ui.dateEdit_2.setDate(QDate(2023, 12, 31))

        self.procesar_filtros_y_actualizar()


# =========================
# EJECUCIÓN DEL PROGRAMA
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())