import sys
import os

# Configuració del path per prioritzar els mòduls locals
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import folium
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy
from PySide6.QtCore import QDate, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from Marker import Markers
from Stats import Stats
from ui_main_window import Ui_MainWindow


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
        self.df_global = self.markers_engine.cargar_datos()

        # Desconnexió preventiva de senyals
        for widget, signal in [(self.ui.dateEdit, self.ui.dateEdit.dateTimeChanged),
                               (self.ui.dateEdit_2, self.ui.dateEdit_2.dateTimeChanged),
                               (self.ui.comboBox_2, self.ui.comboBox_2.currentIndexChanged),
                               (self.ui.comboBox_5, self.ui.comboBox_5.activated)]:
            try:
                if widget.receivers(signal) > 0:
                    widget.disconnect()
            except Exception:
                pass

        # Configuració bàsica del Dashboard
        pestanyes = ["Tipus de Vies, Províncies i Vies", "Clima, Lluminositat i Horaris",
                     "Velocitat, Vehicles i Històric d'accidents"]
        for i, text in enumerate(pestanyes):
            self.ui.Dashboard.setTabText(i, text)
        self.ui.Dashboard.setCurrentIndex(0)

        # Contenidor del mapa interactiu
        self.mapLayout = self.ui.mapFrame.layout() or QVBoxLayout(self.ui.mapFrame)
        self.mapLayout.setContentsMargins(0, 0, 0, 0)
        self.mapLayout.setSpacing(0)
        self.mapView = QWebEngineView()
        self.mapView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.mapLayout.addWidget(self.mapView)

        # Inicialització i injecció de tots els Canvas de Matplotlib
        self.canvas_via, self.canvas_province = MplCanvas(), MplCanvas()
        self.canvas_temporalvies = MplCanvas(width=4.5, height=2.5)
        self.canvas_clima, self.canvas_llum = MplCanvas(), MplCanvas()
        self.canvas_horari, self.canvas_dialab = MplCanvas(), MplCanvas()
        self.canvas_velocitat, self.canvas_vehicles = MplCanvas(), MplCanvas()
        self.canvas_temporal = MplCanvas(width=4.5, height=2.5)

        vistes_canvas = [
            (self.ui.viaFrame, self.canvas_via), (self.ui.provincesFrame, self.canvas_province),
            (self.ui.temporalviesFrame, self.canvas_temporalvies), (self.ui.climaFrame, self.canvas_clima),
            (self.ui.llumFrame, self.canvas_llum), (self.ui.labFrame, self.canvas_horari),
            (self.ui.horaFrame, self.canvas_dialab), (self.ui.velocitatFrame, self.canvas_velocitat),
            (self.ui.vehiclesFrame, self.canvas_vehicles), (self.ui.temporalFrame, self.canvas_temporal)
        ]
        for frame, canvas in vistes_canvas:
            self.inject_canvas(frame, canvas)

        # Definició i configuració de límits i filtres temporals
        self.MIN_FECHA_GLOBAL, self.MAX_FECHA_GLOBAL = QDate(2010, 1, 1), QDate(2023, 12, 31)
        for ed in [self.ui.dateEdit, self.ui.dateEdit_2]:
            ed.setMinimumDate(self.MIN_FECHA_GLOBAL)
            ed.setMaximumDate(self.MAX_FECHA_GLOBAL)

        self.ui.dateEdit.blockSignals(True)
        self.ui.dateEdit_2.blockSignals(True)
        self.ui.dateEdit.setDate(QDate(2022, 1, 1))
        self.ui.dateEdit_2.setDate(QDate(2023, 1, 1))
        self.ui.comboBox_2.setCurrentText("Seleccionar")
        self.ui.comboBox_5.setCurrentText("Seleccionar")
        self.ui.dateEdit.blockSignals(False)
        self.ui.dateEdit_2.blockSignals(False)

        self.ui.dateEdit.dateChanged.connect(self.on_date_inici_changed)
        self.ui.dateEdit_2.dateChanged.connect(self.on_date_fi_changed)

        self.inicializar_graficos_fijos()
        QTimer.singleShot(150, self.aplicar_filtros_manualmente)
        QTimer.singleShot(1000, self.markers_engine.construir_cache)

    def inject_canvas(self, frame_destino, canvas_objeto):
        layout = frame_destino.layout() or QVBoxLayout(frame_destino)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(canvas_objeto)

    def on_date_inici_changed(self, nueva_fecha_inici):
        self.ui.dateEdit.dateChanged.disconnect()
        self.ui.dateEdit_2.dateChanged.disconnect()

        fecha_fi_actual = self.ui.dateEdit_2.date()
        if nueva_fecha_inici > fecha_fi_actual:
            self.ui.dateEdit_2.setDate(nueva_fecha_inici)
            fecha_fi_actual = nueva_fecha_inici

        if fecha_fi_actual > nueva_fecha_inici.addYears(1):
            self.ui.dateEdit_2.setDate(nueva_fecha_inici.addYears(1))

        self.ui.dateEdit.dateChanged.connect(self.on_date_inici_changed)
        self.ui.dateEdit_2.dateChanged.connect(self.on_date_fi_changed)

    def on_date_fi_changed(self, nueva_fecha_fi):
        self.ui.dateEdit.dateChanged.disconnect()
        self.ui.dateEdit_2.dateChanged.disconnect()

        fecha_inici_actual = self.ui.dateEdit.date()
        if nueva_fecha_fi < fecha_inici_actual:
            self.ui.dateEdit.setDate(nueva_fecha_fi)
            fecha_inici_actual = nueva_fecha_fi

        if fecha_inici_actual < nueva_fecha_fi.addYears(-1):
            self.ui.dateEdit.setDate(nueva_fecha_fi.addYears(-1))

        self.ui.dateEdit.dateChanged.connect(self.on_date_inici_changed)
        self.ui.dateEdit_2.dateChanged.connect(self.on_date_fi_changed)

    def inicializar_graficos_fijos(self):
        if self.df_global.empty or "dat" not in self.df_global.columns:
            return

        df_copy = self.df_global.copy()
        df_copy['any_extracted'] = df_copy['dat'].dt.year
        df_historico = df_copy[(df_copy['any_extracted'] >= 2010) & (df_copy['any_extracted'] <= 2023)]

        # --- Gràfic de Tendència Global (Pàgina 3) ---
        self.canvas_temporal.axes.clear()
        evolucion = df_historico.groupby(['any_extracted', 'D_GRAVETAT']).size().unstack(fill_value=0)
        for col in evolucion.columns:
            color = "#ef4444" if "mortal" in str(col).lower() else "#f97316"
            self.canvas_temporal.axes.plot(evolucion.index, evolucion[col], marker="o", markersize=4, linewidth=1.8,
                                           label=str(col), color=color)
        self.canvas_temporal.axes.set_title("Evolució temporal global d'accidents greus i mortals (2010-2023)",
                                            fontsize=8, fontweight="bold")
        self.canvas_temporal.axes.tick_params(labelsize=6)
        self.canvas_temporal.axes.grid(True, linestyle="--", alpha=0.4)
        self.canvas_temporal.axes.legend(loc="best", fontsize=5, frameon=True, framealpha=0.8)
        self.canvas_temporal.figure.tight_layout()
        self.canvas_temporal.draw()

        # --- Gràfic de l'Evolució Històrica de Vies (Pàgina 1) ---
        self.canvas_temporalvies.axes.clear()
        if "via" in df_historico.columns:
            top_5_vies = df_historico[df_historico["via"] != "SE"]["via"].value_counts().head(5).index.tolist()
            df_top_vies = df_historico[df_historico["via"].isin(top_5_vies)]
            evolucion_vies = df_top_vies.groupby(['any_extracted', 'via']).size().unstack(fill_value=0)
            for via in evolucion_vies.columns:
                self.canvas_temporalvies.axes.plot(evolucion_vies.index, evolucion_vies[via], marker="o", markersize=4,
                                                   linestyle="-", linewidth=1.5, label=str(via))
            self.canvas_temporalvies.axes.set_title("Evolució de les 5 vies amb més accidentalitat", fontsize=8,
                                                    fontweight="bold")
            self.canvas_temporalvies.axes.tick_params(labelsize=6)
            self.canvas_temporalvies.axes.grid(True, linestyle="--", alpha=0.4)
            self.canvas_temporalvies.axes.legend(loc="best", fontsize=5, frameon=True, framealpha=0.8)
        self.canvas_temporalvies.figure.tight_layout()
        self.canvas_temporalvies.draw()

    def aplicar_filtros_manualmente(self):
        gravetat_sel = self.ui.comboBox_2.currentText()
        gravetat = None if gravetat_sel in ["Seleccionar", ""] else gravetat_sel

        # 1. Recuperem el resultat del filtre
        res = self.markers_engine.filtrar(
            data_inici=self.ui.dateEdit.date().toString("dd/MM/yyyy"),
            data_fi=self.ui.dateEdit_2.date().toString("dd/MM/yyyy"),
            gravetat=gravetat
        )

        # 2. Comprovem de forma segura si és None sense usar l'operador 'or' directe sobre el DataFrame
        df_filtrat = res if res is not None else pd.DataFrame()

        provincia_sel = self.ui.comboBox_5.currentText()
        if provincia_sel not in ["Seleccionar", ""] and not df_filtrat.empty and "nomDem" in df_filtrat.columns:
            df_filtrat = df_filtrat[df_filtrat["nomDem"].str.upper() == provincia_sel.upper()]

        self.renderizar_mapa(df_filtrat)
        self.renderizar_graficos_sectoriales(df_filtrat)

    def renderizar_mapa(self, df):
        mapa = folium.Map(
            location=[41.82, 1.75], zoom_start=8, min_zoom=7, max_zoom=14,
            min_lat=40.30, max_lat=42.90, min_lon=0.10, max_lon=3.40,
            max_bounds=True, tiles="OpenStreetMap"
        )
        lista_marcadors = self.markers_engine.obtenir_tots_marcadors(df)

        for m in lista_marcadors[:1000]:
            color_nodo = "red" if "mortal" in str(m["gravetat"]).lower() else "orange"
            fecha_bonita = m['dat'].strftime('%d/%m/%Y') if hasattr(m['dat'], 'strftime') else str(m['dat'])
            folium.CircleMarker(
                location=[m["lat"], m["lon"]], radius=4, color=color_nodo, fill=True, fill_color=color_nodo,
                fill_opacity=0.6,
                popup=f"Data: {fecha_bonita}<br>Gravetat: {m['gravetat']}<br>Municipi: {m['municipi']}",
                tooltip=str(m["tipAcc"])
            ).add_to(mapa)

        self.mapView.setHtml(mapa.get_root().render())

    def renderizar_graficos_sectoriales(self, df):
        canvas_list = [self.canvas_via, self.canvas_province, self.canvas_clima, self.canvas_llum,
                       self.canvas_horari, self.canvas_dialab, self.canvas_velocitat, self.canvas_vehicles]

        for canvas in canvas_list:
            canvas.axes.clear()

        if df.empty:
            for canvas in canvas_list:
                canvas.draw()
            return

        stats_dinamicas = Stats(df)

        def sanejar_text(text):
            if not isinstance(text, str):
                return str(text)
            reemplacos = {
                "MatÃ-": "Matí", "CamÃ\u00ad": "Camí", "CamÃ¯": "Camí", "Ã¨": "è", "Ã©": "é",
                "Ã ": "à", "Ã¡": "á", "Ã¬": "ì", "Ã­": "í", "Ã²": "ò", "Ã³": "ó", "Ã¹": "ù",
                "Ãº": "ú", "Ã¯": "ï", "Ã¼": "ü", "Â·": "·", "Ã’": "Ò", "Ã€": "À", "Ã±": "ñ", "Ã§": "ç"
            }
            for malmes, correcte in reemplacos.items():
                text = text.replace(malmes, correcte)
            return text

        # Helper intern per optimitzar i reutilitzar la creació de diagrames de pastís (Evita duplicar codi)
        def _crear_pastis(canvas, data_dict, titol, ncol=2, bbox=(0.5, -0.01),
                          format_label=lambda idx: sanejar_text(idx)):
            if not data_dict:
                canvas.draw()
                return
            categories, valors = list(data_dict.keys()), list(data_dict.values())
            total = sum(valors)
            wedges, _ = canvas.axes.pie(valors, startangle=90, radius=0.65)
            lbls = [f"{format_label(idx)} ({(val / total * 100):.1f}%)" for idx, val in zip(categories, valors)]
            canvas.axes.legend(wedges, lbls, loc="upper center", bbox_to_anchor=bbox, ncol=ncol, fontsize=5,
                               frameon=False)
            canvas.axes.set_title(titol, fontsize=8, fontweight="bold")
            canvas.figure.tight_layout()
            canvas.draw()

        # PÀGINA 1
        mapeo_vias = {
            "Via urbana( inclou carrer i carrer residencial)": "Via urbana",
            "Carretera convencional": "Carretera convencional",
            "Autovia": "Autovia", "Autopista": "Autopista", "Camí rural/pista forestal": "Camí rural",
            "Altres": "Altres"
        }
        vias_series = df["D_TIPUS_VIA"].fillna("Altres").map(
            lambda x: mapeo_vias.get(x, "Altres")).value_counts().to_dict()
        _crear_pastis(self.canvas_via, vias_series, "Accidents per tipus de via")

        prov_dict = df["nomDem"].value_counts().to_dict()
        _crear_pastis(self.canvas_province, prov_dict, "Accidents per província",
                      format_label=lambda x: sanejar_text(str(x).capitalize()))

        # PÀGINA 2
        _crear_pastis(self.canvas_clima, stats_dinamicas.distribucio_climatologia(), "Estat climatològic")
        _crear_pastis(self.canvas_llum, stats_dinamicas.distribucio_per_lluminositat(), "Distribució per lluminositat",
                      ncol=1, bbox=(0.5, -0.02))

        hor_dict = df["grupHor"].fillna("Altres").value_counts().to_dict() if "grupHor" in df.columns else {}
        _crear_pastis(self.canvas_horari, hor_dict, "Accidents per grup horari", ncol=3,
                      format_label=lambda x: sanejar_text(str(x)).capitalize())

        dict_hores = stats_dinamicas.distribucio_per_hora()
        if dict_hores:
            self.canvas_dialab.axes.bar(list(dict_hores.keys()), list(dict_hores.values()), color="#3b82f6", alpha=0.8)
            self.canvas_dialab.axes.set_title("Distribució exacta per hora", fontsize=8, fontweight="bold")
            self.canvas_dialab.axes.set_xticks([0, 4, 8, 12, 16, 20, 23])
            self.canvas_dialab.axes.tick_params(labelsize=6)
            self.canvas_dialab.axes.grid(True, linestyle=":", alpha=0.3)
        self.canvas_dialab.figure.tight_layout()
        self.canvas_dialab.draw()

        # PÀGINA 3
        _crear_pastis(self.canvas_velocitat, stats_dinamicas.distribucio_velocitats(top_n=6),
                      "Velocitats regulades top 6", format_label=lambda x: f"{int(x)} km/h")

        veh_dict = {k: v for k, v in stats_dinamicas.recompte_vehicles_implicats().items() if v > 0}
        _crear_pastis(self.canvas_vehicles, veh_dict, "Tipus de vehicles implicats")

    def limpiar_filtros(self):
        self.ui.dateEdit.blockSignals(True)
        self.ui.dateEdit_2.blockSignals(True)
        self.ui.comboBox_2.setCurrentText("Seleccionar")
        self.ui.comboBox_5.setCurrentText("Seleccionar")
        self.ui.dateEdit.setDate(QDate(2022, 1, 1))
        self.ui.dateEdit_2.setDate(QDate(2023, 1, 1))
        self.ui.dateEdit.blockSignals(False)
        self.ui.dateEdit_2.blockSignals(False)
        self.aplicar_filtros_manualmente()


if __name__ == "__main__":
    os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"
    sys.argv.append("--disable-gpu")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())