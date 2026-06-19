import os
import json
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(BASE_DIR, "geocode_cache.json")


class Markers:
    # Lista estricta de columnas mapeadas para nutrir los 3 paneles del Dashboard
    COLUMNES = [
        "via", "pk", "nomMun", "nomDem", "dat", "hor", "D_GRAVETAT", "tipAcc", "D_TIPUS_VIA",
        "F_VIANANTS_IMPLICADES", "F_BICICLETES_IMPLICADES", "F_CICLOMOTORS_IMPLICADES",
        "F_MOTOCICLETES_IMPLICADES", "F_VEH_LLEUGERS_IMPLICADES", "F_VEH_PESANTS_IMPLICADES",
        "F_ALTRES_UNIT_IMPLICADES", "D_LLUMINOSITAT", "grupHor", "grupDiaLab",
        "C_VELOCITAT_VIA", "D_CLIMATOLOGIA"
    ]

    def __init__(self):
        self.geolocator = Nominatim(user_agent="accidents_catalunya_dash")
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)
        self._dades = None
        self._geo_cache = self._carregar_cache()

    def _carregar_cache(self):
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _guardar_cache(self):
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(self._geo_cache, f, ensure_ascii=False, indent=2)

    def construir_cache(self):
        df = self.cargar_datos()
        adreces = df[df["via"] != "SE"][["via", "nomMun"]].drop_duplicates()
        total = len(adreces)
        print(f"Adreces úniques a comprovar en cache: {total}")

        nous = 0
        for i, (_, fila) in enumerate(adreces.iterrows(), 1):
            adreca = f"{fila['via']} {fila['nomMun']}"
            if adreca in self._geo_cache:
                continue

            try:
                location = self.geocode(adreca)
                self._geo_cache[adreca] = [location.latitude, location.longitude] if location else None
            except Exception as e:
                print(f"Error geocodificació '{adreca}': {e}")
                self._geo_cache[adreca] = None

            nous += 1
            if nous % 50 == 0:
                self._guardar_cache()

        self._guardar_cache()

    def cargar_datos(self):
        if self._dades is None:
            csv_path = os.path.join(BASE_DIR, "base_dades.csv")
            self._dades = pd.read_csv(csv_path, usecols=self.COLUMNES, encoding="utf-8-sig")
            self._dades["dat"] = pd.to_datetime(self._dades["dat"], dayfirst=True, errors="coerce")
        return self._dades

    def filtrar(self, data_inici=None, data_fi=None, gravetat=None):
        df = self.cargar_datos().copy()

        if data_inici:
            dt_inici = pd.to_datetime(data_inici, format="%d/%m/%Y", errors="coerce")
            if not pd.isna(dt_inici):
                df = df[df["dat"] >= dt_inici]

        if data_fi:
            dt_fi = pd.to_datetime(data_fi, format="%d/%m/%Y", errors="coerce")
            if not pd.isna(dt_fi):
                df = df[df["dat"] <= dt_fi]

        if gravetat and gravetat != "Seleccionar":
            df = df[df["D_GRAVETAT"].str.upper() == gravetat.upper()]

        return df

    def _coords_per_adreca(self, via, nom_mun):
        if via == "SE":
            return None, None
        adreca = f"{via} {nom_mun}"
        coords = self._geo_cache.get(adreca)
        if coords:
            return coords[0], coords[1]
        return None, None

    def obtenir_tots_marcadors(self, df=None):
        if df is None:
            df = self.cargar_datos()

        marcadors = []
        for _, fila in df.iterrows():
            lat, lon = self._coords_per_adreca(fila["via"], fila["nomMun"])
            if lat is not None:
                marcadors.append({
                    "lat": lat, "lon": lon, "dat": fila["dat"], "hor": fila["hor"],
                    "gravetat": fila["D_GRAVETAT"], "tipAcc": fila["tipAcc"], "municipi": fila["nomMun"]
                })
        return marcadors