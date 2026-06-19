import sys
import folium
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGridLayout, QSizePolicy
from PySide6.QtCore import QDate, QTimer  # <-- Importamos QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from Marker import Markers
from ui_main_window import Ui_MainWindow

# Inicializar caché si es necesario
Markers().construir_cache()


class MplCanvas(FigureCanvas):
    def __init__(self, width=3.8, height=3.2):
        self.figure = Figure(figsize=(width, height))
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.markers_engine = Markers()

        # Limpieza de señales automáticas de Qt Designer
        try:
            self.ui.dateEdit.dateTimeChanged.disconnect()
            self.ui.dateEdit_2.dateTimeChanged.disconnect()
            self.ui.comboBox_2.currentIndexChanged.disconnect()
            self.ui.comboBox_5.activated.disconnect()
            self.ui.pushButton.clicked.disconnect(self.ui.mapFrame.update)
        except Exception:
            pass

            # Nombres descriptivos de las pestañas
        self.ui.Dashboard.setTabText(0, "Tipus de via & Províncies")
        self.ui.Dashboard.setTabText(1, "Vehicles, Llums & Horaris")
        self.ui.Dashboard.setTabText(2, "Velocitat, Clima & Vies")

        # Forzar página 1 al iniciar
        self.ui.Dashboard.setCurrentIndex(0)

        # Configuración elástica del contenedor del mapa
        self.ui.mapFrame.setMinimumSize(600, 500)
        self.ui.mapFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.mapLayout = QVBoxLayout(self.ui.mapFrame)
        self.mapLayout.setContentsMargins(0, 0, 0, 0)

        # Guardamos el componente de vista web de manera global
        self.mapView = QWebEngineView()
        self.mapLayout.addWidget(self.mapView)

        # Corrección elástica de layouts en las pestañas del dashboard
        self.ui.Pg1.setLayout(QGridLayout())
        self.ui.Pg1.layout().setContentsMargins(5, 5, 5, 5)
        self.ui.Pg1.layout().addWidget(self.ui.frame)

        self.ui.Pg2.setLayout(QGridLayout())
        self.ui.Pg2.layout().setContentsMargins(5, 5, 5, 5)
        self.ui.Pg2.layout().addWidget(self.ui.frame_5)

        self.ui.Pg3.setLayout(QGridLayout())
        self.ui.Pg3.layout().setContentsMargins(5, 5, 5, 5)
        self.ui.Pg3.layout().addWidget(self.ui.frame_10)

        # Inyección de lienzos en la interfaz
        # --- PÁGINA 1 ---
        self.canvas_via = MplCanvas()
        self.canvas_province = MplCanvas()
        self.canvas_temporal = MplCanvas(width=4.5, height=2.5)
        self.inject_canvas(self.ui.viaFrame, self.canvas_via)
        self.inject_canvas(self.ui.provincesFrame, self.canvas_province)
        self.inject_canvas(self.ui.temporalFrame, self.canvas_temporal)

        # --- PÁGINA 2 ---
        self.canvas_vehicles = MplCanvas()
        self.canvas_llum = MplCanvas()
        self.canvas_horari = MplCanvas()
        self.canvas_dialab = MplCanvas()
        self.inject_canvas(self.ui.vehiclesFrame, self.canvas_vehicles)
        self.inject_canvas(self.ui.llumFrame, self.canvas_llum)
        self.inject_canvas(self.ui.labFrame, self.canvas_horari)
        self.inject_canvas(self.ui.frame_9, self.canvas_dialab)

        # --- PÁGINA 3 ---
        self.canvas_velocitat = MplCanvas()
        self.canvas_clima = MplCanvas()
        self.canvas_temporalvies = MplCanvas(width=4.5, height=2.5)
        self.inject_canvas(self.ui.velocitatFrame, self.canvas_velocitat)
        self.inject_canvas(self.ui.climaFrame, self.canvas_clima)
        self.inject_canvas(self.ui.temporalviesFrame, self.canvas_temporalvies)

        # Configuración de rangos de fechas (Intervalo de 1 año deslizable)
        self.MIN_FECHA_GLOBAL = QDate(2010, 1, 1)
        self.MAX_FECHA_GLOBAL = QDate(2023, 12, 31)
        self.ui.dateEdit.setMinimumDate(self.MIN_FECHA_GLOBAL)
        self.ui.dateEdit.setMaximumDate(self.MAX_FECHA_GLOBAL)
        self.ui.dateEdit_2.setMinimumDate(self.MIN_FECHA_GLOBAL)
        self.ui.dateEdit_2.setMaximumDate(self.MAX_FECHA_GLOBAL)

        self.ui.dateEdit.setDate(QDate(2022, 1, 1))
        self.ui.dateEdit_2.setDate(QDate(2023, 1, 1))

        self.ui.dateEdit.dateChanged.connect(self.on_date_inici_changed)
        self.ui.dateEdit_2.dateChanged.connect(self.on_date_fi_changed)

        # Inicializar gráficos estáticos de líneas (Históricos)
        self.inicializar_graficos_fijos()

        # Configuración de botones de la interfaz
        self.ui.pushButton.clicked.connect(self.procesar_filtros_y_actualizar)
        self.ui.pushButton_2.clicked.connect(self.limpiar_filtros)

        # ================================================================= #
        #  SOLUCIÓN MAPA INVISIBLE: LANZAMIENTO SEGURO POS-DIBUJADO        #
        # ================================================================= #
        # Esperamos 100ms a que la app abra físicamente para que el mapa reconozca su tamaño
        QTimer.singleShot(100, self.procesar_filtros_y_actualizar)

    def inject_canvas(self, frame_destino, canvas_objeto):
        layout = QVBoxLayout(frame_destino)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(canvas_objeto)

    def on_date_inici_changed(self, nueva_fecha_inici):
        self.ui.dateEdit.dateChanged.disconnect(self.on_date_inici_changed)
        self.ui.dateEdit_2.dateChanged.disconnect(self.on_date_fi_changed)

        fecha_fi_actual = self.ui.dateEdit_2.date()
        if nueva_fecha_inici > fecha_fi_actual:
            self.ui.dateEdit_2.setDate(nueva_fecha_inici)
            fecha_fi_actual = nueva_fecha_inici

        un_ano_adelante = nueva_fecha_inici.addYears(1)
        if fecha_fi_actual > un_ano_adelante:
            self.ui.dateEdit_2.setDate(un_ano_adelante)

        self.ui.dateEdit.dateChanged.connect(self.on_date_inici_changed)
        self.ui.dateEdit_2.dateChanged.connect(self.on_date_fi_changed)

    def on_date_fi_changed(self, nueva_fecha_fi):
        self.ui.dateEdit.dateChanged.disconnect(self.on_date_inici_changed)
        self.ui.dateEdit_2.dateChanged.disconnect(self.on_date_fi_changed)

        fecha_inici_actual = self.ui.dateEdit.date()
        if nueva_fecha_fi < fecha_inici_actual:
            self.ui.dateEdit.setDate(nueva_fecha_fi)
            fecha_inici_actual = nueva_fecha_fi

        un_ano_atras = nueva_fecha_fi.addYears(-1)
        if fecha_inici_actual < un_ano_atras:
            self.ui.dateEdit.setDate(un_ano_atras)

        self.ui.dateEdit.dateChanged.connect(self.on_date_inici_changed)
        self.ui.dateEdit_2.dateChanged.connect(self.on_date_fi_changed)

    def inicializar_graficos_fijos(self):
        df_completo = self.markers_engine.cargar_datos().copy()
        if df_completo.empty or "dat" not in df_completo.columns:
            return

        df_completo['any_extracted'] = df_completo['dat'].dt.year
        df_historico = df_completo[(df_completo['any_extracted'] >= 2010) & (df_completo['any_extracted'] <= 2023)]

        # Pág 1 Inferior: Histórico de Gravedad
        self.canvas_temporal.axes.clear()
        evolucion = df_historico.groupby(['any_extracted', 'D_GRAVETAT']).size().unstack(fill_value=0)
        for col in evolucion.columns:
            color = "#ef4444" if "mortal" in str(col).lower() else "#f97316"
            self.canvas_temporal.axes.plot(
                evolucion.index, evolucion[col], marker="o", linewidth=1.8, label=str(col), color=color
            )
        self.canvas_temporal.axes.set_title("Evolució temporal (2010-2023)", fontsize=8, fontweight="bold")
        self.canvas_temporal.axes.tick_params(labelsize=6)
        self.canvas_temporal.axes.grid(True, linestyle="--", alpha=0.4)
        self.canvas_temporal.axes.legend(loc="best", fontsize=6, frameon=False)
        self.canvas_temporal.figure.tight_layout()
        self.canvas_temporal.draw()

        # Pág 3 Inferior: Histórico de las 5 vías con más accidentes
        self.canvas_temporalvies.axes.clear()
        if "via" in df_historico.columns:
            top_5_vies = df_historico[df_historico["via"] != "SE"]["via"].value_counts().head(5).index.tolist()
            df_top_vies = df_historico[df_historico["via"].isin(top_5_vies)]

            evolucion_vies = df_top_vies.groupby(['any_extracted', 'via']).size().unstack(fill_value=0)
            for via in evolucion_vies.columns:
                self.canvas_temporalvies.axes.plot(
                    evolucion_vies.index, evolucion_vies[via], marker="s", linestyle="-", linewidth=1.5, label=str(via)
                )
            self.canvas_temporalvies.axes.set_title("Evolució temporal de les 5 vies amb més accidents", fontsize=8,
                                                    fontweight="bold")
            self.canvas_temporalvies.axes.tick_params(labelsize=6)
            self.canvas_temporalvies.axes.grid(True, linestyle="--", alpha=0.4)
            self.canvas_temporalvies.axes.legend(loc="best", fontsize=6, frameon=False, ncol=3)
        self.canvas_temporalvies.figure.tight_layout()
        self.canvas_temporalvies.draw()

    def procesar_filtros_y_actualizar(self):
        data_inici = self.ui.dateEdit.date().toString("dd/MM/yyyy")
        data_fi = self.ui.dateEdit_2.date().toString("dd/MM/yyyy")

        gravetat_sel = self.ui.comboBox_2.currentText()
        gravetat = None if gravetat_sel == "Seleccionar" else gravetat_sel

        df_filtrat = self.markers_engine.filtrar(data_inici=data_inici, data_fi=data_fi, gravetat=gravetat)
        if df_filtrat is None:
            df_filtrat = pd.DataFrame()

        provincia_sel = self.ui.comboBox_5.currentText()
        if provincia_sel != "Seleccionar" and not df_filtrat.empty:
            if "nomDem" in df_filtrat.columns:
                df_filtrat = df_filtrat[df_filtrat["nomDem"].str.upper() == provincia_sel.upper()]

        self.renderizar_mapa(df_filtrat)
        self.renderizar_graficos_sectoriales(df_filtrat)

    def renderizar_mapa(self, df):
        # Generar mapa base centrado en Cataluña con Folium
        mapa = folium.Map(
            location=[41.82, 1.75], zoom_start=8, min_zoom=7, max_zoom=14,
            min_lat=40.30, max_lat=42.90, min_lon=0.10, max_lon=3.40,
            max_bounds=True, tiles="OpenStreetMap"
        )
        lista_marcadors = self.markers_engine.obtenir_tots_marcadors(df)

        for m in lista_marcadors[:800]:
            color_nodo = "red" if "mortal" in str(m["gravetat"]).lower() else "orange"
            fecha_bonita = m['dat'].strftime('%d/%m/%Y') if hasattr(m['dat'], 'strftime') else str(m['dat'])
            folium.CircleMarker(
                location=[m["lat"], m["lon"]], radius=4, color=color_nodo, fill=True, fill_color=color_nodo,
                fill_opacity=0.6,
                popup=f"Fecha: {fecha_bonita}<br>Gravetat: {m['gravetat']}<br>Municipi: {m['municipi']}",
                tooltip=str(m["tipAcc"])
            ).add_to(mapa)

        # Inyectar de manera segura el render HTML en la vista web activa
        self.mapView.setHtml(mapa.get_root().render())

    def renderizar_graficos_sectoriales(self, df):
        if df.empty:
            return

        # --- PÁGINA 1 ---
        self.canvas_via.axes.clear()
        mapeo_vias = {
            "Via urbana( inclou carrer i carrer residencial)": "Via urbana",
            "Carretera convencional": "Carretera convencional",
            "Autovia": "Autovia",
            "Autopista": "Autopista",
            "CamÃ­ rural/pista forestal": "Camí rural",
            "Altres": "Altres"
        }
        tipos_vias = df["D_TIPUS_VIA"].fillna("Altres").map(lambda x: mapeo_vias.get(x, "Altres"))
        via_counts = tipos_vias.value_counts()
        wedges, _ = self.canvas_via.axes.pie(via_counts.values, startangle=90, radius=0.9)
        lbls_v = [f"{idx} ({(val / via_counts.sum() * 100):.1f}%)" for idx, val in
                  zip(via_counts.index, via_counts.values)]
        self.canvas_via.axes.legend(wedges, lbls_v, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2, fontsize=5,
                                    frameon=False)
        self.canvas_via.axes.set_title("Accidents per tipus de via", fontsize=8, fontweight="bold")
        self.canvas_via.draw()

        self.canvas_province.axes.clear()
        prov_counts = df["nomDem"].value_counts()
        wedges, _ = self.canvas_province.axes.pie(prov_counts.values, startangle=90, radius=0.9)
        lbls_p = [f"{str(idx).capitalize()} ({(val / prov_counts.sum() * 100):.1f}%)" for idx, val in
                  zip(prov_counts.index, prov_counts.values)]
        self.canvas_province.axes.legend(wedges, lbls_p, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2,
                                         fontsize=5, frameon=False)
        self.canvas_province.axes.set_title("Accidents per província", fontsize=8, fontweight="bold")
        self.canvas_province.draw()

        # --- PÁGINA 2 ---
        self.canvas_vehicles.axes.clear()
        columnas_vehiculos = {
            "F_VIANANTS_IMPLICADES": "Vianants",
            "F_BICICLETES_IMPLICADES": "Bicicletes",
            "F_CICLOMOTORS_IMPLICADES": "Ciclomotors",
            "F_MOTOCICLETES_IMPLICADES": "Motocicletes",
            "F_VEH_LLEUGERS_IMPLICADES": "Vehicles lleugers",
            "F_VEH_PESANTS_IMPLICADES": "Vehicles pesants",
            "F_ALTRES_UNIT_IMPLICADES": "Altres"
        }
        conteo_veh = {}
        for col, clase in columnas_vehiculos.items():
            if col in df.columns:
                conteo_veh[clase] = int((df[col] != 0).sum())

        veh_series = pd.Series(conteo_veh)
        if veh_series.sum() > 0:
            wedges, _ = self.canvas_vehicles.axes.pie(veh_series.values, startangle=90, radius=0.9)
            lbls_vh = [f"{idx} ({(val / veh_series.sum() * 100):.1f}%)" for idx, val in
                       zip(veh_series.index, veh_series.values)]
            self.canvas_vehicles.axes.legend(wedges, lbls_vh, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2,
                                             fontsize=5, frameon=False)
        self.canvas_vehicles.axes.set_title("Tipus de vehicles implicats", fontsize=8, fontweight="bold")
        self.canvas_vehicles.draw()

        self.canvas_llum.axes.clear()
        if "D_LLUMINOSITAT" in df.columns:
            llum_counts = df["D_LLUMINOSITAT"].fillna("Desconegut").value_counts()
            wedges, _ = self.canvas_llum.axes.pie(llum_counts.values, startangle=90, radius=0.9)
            lbls_ll = [f"{idx} ({(val / llum_counts.sum() * 100):.1f}%)" for idx, val in
                       zip(llum_counts.index, llum_counts.values)]
            self.canvas_llum.axes.legend(wedges, lbls_ll, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=1,
                                         fontsize=5, frameon=False)
        self.canvas_llum.axes.set_title("Distribució per lluminositat", fontsize=8, fontweight="bold")
        self.canvas_llum.draw()

        self.canvas_horari.axes.clear()
        if "grupHor" in df.columns:
            hor_counts = df["grupHor"].fillna("Altres").value_counts()
            wedges, _ = self.canvas_horari.axes.pie(hor_counts.values, startangle=90, radius=0.9)
            lbls_h = [f"{idx.capitalize()} ({(val / hor_counts.sum() * 100):.1f}%)" for idx, val in
                      zip(hor_counts.index, hor_counts.values)]
            self.canvas_horari.axes.legend(wedges, lbls_h, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=3,
                                           fontsize=5, frameon=False)
        self.canvas_horari.axes.set_title("Accidents per grup horari", fontsize=8, fontweight="bold")
        self.canvas_horari.draw()

        self.canvas_dialab.axes.clear()
        if "grupDiaLab" in df.columns:
            dia_counts = df["grupDiaLab"].fillna("Desconegut").value_counts()
            wedges, _ = self.canvas_dialab.axes.pie(dia_counts.values, startangle=90, radius=0.9)
            lbls_d = [f"{idx.capitalize()} ({(val / dia_counts.sum() * 100):.1f}%)" for idx, val in
                      zip(dia_counts.index, dia_counts.values)]
            self.canvas_dialab.axes.legend(wedges, lbls_d, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2,
                                           fontsize=5, frameon=False)
        self.canvas_dialab.axes.set_title("Grup de dia laboral", fontsize=8, fontweight="bold")
        self.canvas_dialab.draw()

        # --- PÁGINA 3 ---
        self.canvas_velocitat.axes.clear()
        if "C_VELOCITAT_VIA" in df.columns:
            vel_counts = df["C_VELOCITAT_VIA"].dropna().value_counts().head(6)
            if not vel_counts.empty:
                wedges, _ = self.canvas_velocitat.axes.pie(vel_counts.values, startangle=90, radius=0.9)
                lbls_vl = [f"{int(idx)} km/h ({(val / vel_counts.sum() * 100):.1f}%)" for idx, val in
                           zip(vel_counts.index, vel_counts.values)]
                self.canvas_velocitat.axes.legend(wedges, lbls_vl, loc="upper center", bbox_to_anchor=(0.5, -0.01),
                                                  ncol=2, fontsize=5, frameon=False)
        self.canvas_velocitat.axes.set_title("Velocitats regulades top 6", fontsize=8, fontweight="bold")
        self.canvas_velocitat.draw()

        self.canvas_clima.axes.clear()
        if "D_CLIMATOLOGIA" in df.columns:
            clima_counts = df["D_CLIMATOLOGIA"].fillna("Altres").value_counts()
            wedges, _ = self.canvas_clima.axes.pie(clima_counts.values, startangle=90, radius=0.9)
            lbls_c = [f"{idx} ({(val / clima_counts.sum() * 100):.1f}%)" for idx, val in
                      zip(clima_counts.index, clima_counts.values)]
            self.canvas_clima.axes.legend(wedges, lbls_c, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2,
                                          fontsize=5, frameon=False)
        self.canvas_clima.axes.set_title("Estat climatològic", fontsize=8, fontweight="bold")
        self.canvas_clima.draw()

    def limpiar_filtros(self):
        self.ui.comboBox_2.setCurrentIndex(0)
        self.ui.comboBox_5.setCurrentIndex(0)
        self.ui.dateEdit.setDate(QDate(2022, 1, 1))
        self.ui.dateEdit_2.setDate(QDate(2023, 1, 1))
        self.procesar_filtros_y_actualizar()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())