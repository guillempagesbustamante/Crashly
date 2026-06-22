import sys
import os


# EVITAR CONFLICTES DE NOM: Forcem a Python a buscar primer a la teva carpeta local
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


import folium
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy
from PySide6.QtCore import QDate, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


from Marker import Markers
from Stats import Stats  # <--- Importació neta i segura del teu fitxer local 'stats.py'
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


       # Carreguem el DataFrame complet un sol cop per a l'històric global fons
       self.df_global = self.markers_engine.cargar_datos()


       # ================================================================= #
       #  BLINDATGE EXTREM DE SENYALS (Eliminar automatismes residuals)    #
       # ================================================================= #
       try:
           if self.ui.dateEdit.receivers(self.ui.dateEdit.dateTimeChanged) > 0:
               self.ui.dateEdit.dateTimeChanged.disconnect()
           if self.ui.dateEdit_2.receivers(self.ui.dateEdit_2.dateTimeChanged) > 0:
               self.ui.dateEdit_2.dateTimeChanged.disconnect()
           if self.ui.comboBox_2.receivers(self.ui.comboBox_2.currentIndexChanged) > 0:
               self.ui.comboBox_2.currentIndexChanged.disconnect()
           if self.ui.comboBox_5.receivers(self.ui.comboBox_5.activated) > 0:
               self.ui.comboBox_5.activated.disconnect()
       except Exception:
           pass


       # Noms de les pestanyes del Dashboard
       self.ui.Dashboard.setTabText(0, "Vies, Províncies & Històric Vies")
       self.ui.Dashboard.setTabText(1, "Clima, Llums & Horaris")
       self.ui.Dashboard.setTabText(2, "Velocitat, Vehicles & Històric")


       # Forçar visualització de la primera pàgina a l'inici
       self.ui.Dashboard.setCurrentIndex(0)


       # ================================================================= #
       #  CONFIGURACIÓ DE L'ENTORN DEL MAPA INTERACTIU (QWebEngineView)   #
       # ================================================================= #
       if self.ui.mapFrame.layout() is None:
           self.mapLayout = QVBoxLayout(self.ui.mapFrame)
           self.mapLayout.setContentsMargins(0, 0, 0, 0)
           self.mapLayout.setSpacing(0)
       else:
           self.mapLayout = self.ui.mapFrame.layout()


       self.mapView = QWebEngineView()
       self.mapView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
       self.mapLayout.addWidget(self.mapView)


       # ================================================================= #
       #  INJECCIÓ DELS GRÀFICS DE MATPLOTLIB DINS ELS FRAMES DE QT        #
       # ================================================================= #
       # --- PÀGINA 1 ---
       self.canvas_via = MplCanvas()
       self.canvas_province = MplCanvas()
       self.canvas_temporalvies = MplCanvas(width=4.5, height=2.5)
       self.inject_canvas(self.ui.viaFrame, self.canvas_via)
       self.inject_canvas(self.ui.provincesFrame, self.canvas_province)
       self.inject_canvas(self.ui.temporalviesFrame, self.canvas_temporalvies)


       # --- PÀGINA 2 ---
       self.canvas_clima = MplCanvas()
       self.canvas_llum = MplCanvas()
       self.canvas_horari = MplCanvas()
       self.canvas_dialab = MplCanvas()
       self.inject_canvas(self.ui.climaFrame, self.canvas_clima)
       self.inject_canvas(self.ui.llumFrame, self.canvas_llum)
       self.inject_canvas(self.ui.labFrame, self.canvas_horari)
       self.inject_canvas(self.ui.horaFrame, self.canvas_dialab)


       # --- PÀGINA 3 ---
       self.canvas_velocitat = MplCanvas()
       self.canvas_vehicles = MplCanvas()
       self.canvas_temporal = MplCanvas(width=4.5, height=2.5)
       self.inject_canvas(self.ui.velocitatFrame, self.canvas_velocitat)
       self.inject_canvas(self.ui.vehiclesFrame, self.canvas_vehicles)
       self.inject_canvas(self.ui.temporalFrame, self.canvas_temporal)


       # ================================================================= #
       #  GESTIÓ DE RANGS DE FECHES CONSTRETES                            #
       # ================================================================= #
       self.MIN_FECHA_GLOBAL = QDate(2010, 1, 1)
       self.MAX_FECHA_GLOBAL = QDate(2023, 12, 31)


       self.ui.dateEdit.setMinimumDate(self.MIN_FECHA_GLOBAL)
       self.ui.dateEdit.setMaximumDate(self.MAX_FECHA_GLOBAL)
       self.ui.dateEdit_2.setMinimumDate(self.MIN_FECHA_GLOBAL)
       self.ui.dateEdit_2.setMaximumDate(self.MAX_FECHA_GLOBAL)


       # Configuració d'estats neutres inicials evitant parpelleigs
       self.ui.dateEdit.blockSignals(True)
       self.ui.dateEdit_2.blockSignals(True)
       self.ui.dateEdit.setDate(QDate(2022, 1, 1))
       self.ui.dateEdit_2.setDate(QDate(2023, 1, 1))
       self.ui.comboBox_2.setCurrentText("Seleccionar")
       self.ui.comboBox_5.setCurrentText("Seleccionar")
       self.ui.dateEdit.blockSignals(False)
       self.ui.dateEdit_2.blockSignals(False)


       # Control exclusiu intern de coherència de dates
       self.ui.dateEdit.dateChanged.connect(self.on_date_inici_changed)
       self.ui.dateEdit_2.dateChanged.connect(self.on_date_fi_changed)


       # Dibuixar els gràfics fixos històrics de fons utilitzant Stats de base
       self.inicializar_graficos_fijos()


       # Carrega inicial asíncrona al obrir l'aplicació
       QTimer.singleShot(150, self.aplicar_filtros_manualmente)
       QTimer.singleShot(1000, self.markers_engine.construir_cache)


   def inject_canvas(self, frame_destino, canvas_objeto):
       if frame_destino.layout() is None:
           layout = QVBoxLayout(frame_destino)
           layout.setContentsMargins(0, 0, 0, 0)
           layout.addWidget(canvas_objeto)
       else:
           frame_destino.layout().addWidget(canvas_objeto)


   def on_date_inici_changed(self, nueva_fecha_inici):
       self.ui.dateEdit.dateChanged.disconnect()
       self.ui.dateEdit_2.dateChanged.disconnect()


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
       self.ui.dateEdit.dateChanged.disconnect()
       self.ui.dateEdit_2.dateChanged.disconnect()


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
       if self.df_global.empty or "dat" not in self.df_global.columns:
           return


       # --- Gràfic Històric Global (Pàgina 3) ---
       self.canvas_temporal.axes.clear()
       df_copy = self.df_global.copy()
       df_copy['any_extracted'] = df_copy['dat'].dt.year
       df_historico = df_copy[(df_copy['any_extracted'] >= 2010) & (df_copy['any_extracted'] <= 2023)]
       evolucion = df_historico.groupby(['any_extracted', 'D_GRAVETAT']).size().unstack(fill_value=0)


       for col in evolucion.columns:
           color = "#ef4444" if "mortal" in str(col).lower() else "#f97316"
           self.canvas_temporal.axes.plot(
               evolucion.index, evolucion[col], marker="o", linewidth=1.8, label=str(col), color=color
           )
       self.canvas_temporal.axes.set_title("Evolució temporal global (2010-2023)", fontsize=8, fontweight="bold")
       self.canvas_temporal.axes.tick_params(labelsize=6)
       self.canvas_temporal.axes.grid(True, linestyle="--", alpha=0.4)
       self.canvas_temporal.axes.legend(loc="best", fontsize=6, frameon=False)
       self.canvas_temporal.figure.tight_layout()
       self.canvas_temporal.draw()


       # --- Gràfic Històric de Vies (Pàgina 1) ---
       self.canvas_temporalvies.axes.clear()
       if "via" in df_historico.columns:
           top_5_vies = df_historico[df_historico["via"] != "SE"]["via"].value_counts().head(5).index.tolist()
           df_top_vies = df_historico[df_historico["via"].isin(top_5_vies)]


           evolucion_vies = df_top_vies.groupby(['any_extracted', 'via']).size().unstack(fill_value=0)
           for via in evolucion_vies.columns:
               self.canvas_temporalvies.axes.plot(
                   evolucion_vies.index, evolucion_vies[via], marker="s", linestyle="-", linewidth=1.5, label=str(via)
               )
           self.canvas_temporalvies.axes.set_title("Evolució de les 5 vies principals", fontsize=8, fontweight="bold")
           self.canvas_temporalvies.axes.tick_params(labelsize=6)
           self.canvas_temporalvies.axes.grid(True, linestyle="--", alpha=0.4)
           self.canvas_temporalvies.axes.legend(loc="best", fontsize=6, frameon=False, ncol=3)
       self.canvas_temporalvies.figure.tight_layout()
       self.canvas_temporalvies.draw()


   def aplicar_filtros_manualmente(self):
       data_inici = self.ui.dateEdit.date().toString("dd/MM/yyyy")
       data_fi = self.ui.dateEdit_2.date().toString("dd/MM/yyyy")


       gravetat_sel = self.ui.comboBox_2.currentText()
       gravetat = None if gravetat_sel in ["Seleccionar", ""] else gravetat_sel


       df_filtrat = self.markers_engine.filtrar(data_inici=data_inici, data_fi=data_fi, gravetat=gravetat)
       if df_filtrat is None:
           df_filtrat = pd.DataFrame()


       provincia_sel = self.ui.comboBox_5.currentText()
       if provincia_sel not in ["Seleccionar", ""] and not df_filtrat.empty:
           if "nomDem" in df_filtrat.columns:
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
       # Si el subconjunt és buit, netegem tots els quadres de gràfics
       if df.empty:
           for canvas in [self.canvas_via, self.canvas_province, self.canvas_clima,
                          self.canvas_llum, self.canvas_horari, self.canvas_dialab,
                          self.canvas_velocitat, self.canvas_vehicles]:
               canvas.axes.clear()
               canvas.draw()
           return


       # INSTANCIEM LA CLASSE STATS DE MANERA DINÀMICA AMB ELS FILTRES ACTIUS
       stats_dinamicas = Stats(df)


       # ================================================================= #
       #  PÀGINA 1: VIES I PROVÍNCIES (Es manté la renderització visual)   #
       # ================================================================= #
       self.canvas_via.axes.clear()
       mapeo_vias = {
           "Via urbana( inclou carrer i carrer residencial)": "Via urbana",
           "Carretera convencional": "Carretera convencional",
           "Autovia": "Autovia",
           "Autopista": "Autopista",
           "CamÃ\u00ad rural/pista forestal": "Camí rural",
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


       # ================================================================= #
       #  PÀGINA 2: CLIMA, LLUMS I HORARIS (ADAPTAT 100% AMB CODI STATS)   #
       # ================================================================= #


       # 1. Gràfic de Climatologia des de Stats
       self.canvas_clima.axes.clear()
       dict_clima = stats_dinamicas.distribucio_climatologia()
       if dict_clima:
           categories_c = list(dict_clima.keys())
           valors_c = list(dict_clima.values())
           total_c = sum(valors_c)
           wedges, _ = self.canvas_clima.axes.pie(valors_c, startangle=90, radius=0.9)
           lbls_c = [f"{idx} ({(val / total_c * 100):.1f}%)" for idx, val in zip(categories_c, valors_c)]
           self.canvas_clima.axes.legend(wedges, lbls_c, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2,
                                         fontsize=5, frameon=False)
       self.canvas_clima.axes.set_title("Estat climatològic (Stats)", fontsize=8, fontweight="bold")
       self.canvas_clima.draw()


       # 2. Gràfic de Lluminositat des de Stats
       self.canvas_llum.axes.clear()
       dict_llum = stats_dinamicas.distribucio_lluminositat()
       if dict_llum:
           categories_ll = list(dict_llum.keys())
           valors_ll = list(dict_llum.values())
           total_ll = sum(valors_ll)
           wedges, _ = self.canvas_llum.axes.pie(valors_ll, startangle=90, radius=0.9)
           lbls_ll = [f"{idx} ({(val / total_ll * 100):.1f}%)" for idx, val in zip(categories_ll, valors_ll)]
           self.canvas_llum.axes.legend(wedges, lbls_ll, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=1,
                                        fontsize=5, frameon=False)
       self.canvas_llum.axes.set_title("Distribució per lluminositat (Stats)", fontsize=8, fontweight="bold")
       self.canvas_llum.draw()


       # 3. Gràfic de Grups Horaris (Es manté des del df actiu)
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


       # 4. Gràfic de línies de la Distribució Exacta per Hores des de Stats
       self.canvas_dialab.axes.clear()
       dict_hores = stats_dinamicas.distribucio_per_hora()
       if dict_hores:
           hores_x = list(dict_hores.keys())
           counts_y = list(dict_hores.values())
           self.canvas_dialab.axes.bar(hores_x, counts_y, color="#3b82f6", alpha=0.8)
           self.canvas_dialab.axes.set_title("Distribució exacta per hora (Stats)", fontsize=8, fontweight="bold")
           self.canvas_dialab.axes.set_xticks([0, 4, 8, 12, 16, 20, 23])
           self.canvas_dialab.axes.tick_params(labelsize=6)
           self.canvas_dialab.axes.grid(True, linestyle=":", alpha=0.3)
       self.canvas_dialab.draw()


       # ================================================================= #
       #  PÀGINA 3: VELOCITAT I VEHICLES (ADAPTAT 100% AMB CODI STATS)    #
       # ================================================================= #


       # 1. Gràfic de Velocitats Regulades des de Stats (Top 6)
       self.canvas_velocitat.axes.clear()
       dict_vel = stats_dinamicas.distribucio_velocitats(top_n=6)
       if dict_vel:
           categories_v = list(dict_vel.keys())
           valors_v = list(dict_vel.values())
           total_v = sum(valors_v)
           wedges, _ = self.canvas_velocitat.axes.pie(valors_v, startangle=90, radius=0.9)
           lbls_vl = [f"{int(idx)} km/h ({(val / total_v * 100):.1f}%)" for idx, val in zip(categories_v, valors_v)]
           self.canvas_velocitat.axes.legend(wedges, lbls_vl, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2,
                                             fontsize=5, frameon=False)
       self.canvas_velocitat.axes.set_title("Velocitats regulades top 6 (Stats)", fontsize=8, fontweight="bold")
       self.canvas_velocitat.draw()


       # 2. Gràfic de Tipus de Vehicles implicats des de Stats
       self.canvas_vehicles.axes.clear()
       dict_veh = stats_dinamicas.recompte_vehicles_implicats()
       # Filtrem per mostrar només els que tinguin alguna implicació (> 0) i no col·lapsar la vista
       dict_veh_filtrat = {k: v for k, v in dict_veh.items() if v > 0}


       if dict_veh_filtrat:
           categories_vh = list(dict_veh_filtrat.keys())
           valors_vh = list(dict_veh_filtrat.values())
           total_vh = sum(valors_vh)
           wedges, _ = self.canvas_vehicles.axes.pie(valors_vh, startangle=90, radius=0.9)
           lbls_vh = [f"{idx} ({(val / total_vh * 100):.1f}%)" for idx, val in zip(categories_vh, valors_vh)]
           self.canvas_vehicles.axes.legend(wedges, lbls_vh, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2,
                                            fontsize=5, frameon=False)
       self.canvas_vehicles.axes.set_title("Tipus de vehicles implicats (Stats)", fontsize=8, fontweight="bold")
       self.canvas_vehicles.draw()


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
   import os


   os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"
   sys.argv.append("--disable-gpu")


   app = QApplication(sys.argv)
   window = MainWindow()
   window.show()
   sys.exit(app.exec())
