from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(BASE_DIR, "geocode_cache.json")


class Markers:
    COLUMNES = ["via", "pk", "nomMun", "nomDem", "dat", "hor", "D_GRAVETAT", "tipAcc", "D_TIPUS_VIA"]

    def __init__(self):
        self.geolocator = Nominatim(user_agent="accidents_app")
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)
        self._dades = None
        self._geo_cache = self._carregar_cache()

    # ------------------------------------------------------------------ #
    #  GEOCODE CACHE  (geocode_cache.json)                                #
    # ------------------------------------------------------------------ #

    def _carregar_cache(self):
        """Load the on-disk geocode cache, or return an empty dict."""
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _guardar_cache(self):
        """Persist the in-memory cache to disk."""
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(self._geo_cache, f, ensure_ascii=False, indent=2)

    def construir_cache(self):
        """
        One-time setup: geocode every unique address in the dataset and save
        results to geocode_cache.json.
        """
        df = self.cargar_datos()
        adreces = (
            df[df["via"] != "SE"][["via", "nomMun"]]
            .drop_duplicates()
        )
        total = len(adreces)
        print(f"Total adreces úniques a geocodificar: {total}")

        nous = 0
        for i, (_, fila) in enumerate(adreces.iterrows(), 1):
            adreca = f"{fila['via']} {fila['nomMun']}"
            if adreca in self._geo_cache:
                continue

            try:
                location = self.geocode(adreca)
                self._geo_cache[adreca] = (
                    [location.latitude, location.longitude] if location else None
                )
            except Exception as e:
                print(f"  Error '{adreca}': {e}")
                self._geo_cache[adreca] = None

            nous += 1
            if nous % 50 == 0:
                self._guardar_cache()
                print(f"  [{i}/{total}] guardat ({nous} noves entrades)...")

        self._guardar_cache()
        print(f"Cache completada. {nous} noves entrades guardades a '{CACHE_PATH}'.")

    # ------------------------------------------------------------------ #
    #  DATA LOADING                                                        #
    # ------------------------------------------------------------------ #

    def cargar_datos(self):
        """Load and cache the full dataset (only needed columns)."""
        if self._dades is None:
            csv_path = os.path.join(BASE_DIR, "base_dades.csv")
            self._dades = pd.read_csv(csv_path, usecols=self.COLUMNES, encoding="utf-8-sig")
            self._dades["dat"] = pd.to_datetime(
                self._dades["dat"], dayfirst=True, errors="coerce"
            )
        return self._dades

    # ------------------------------------------------------------------ #
    #  FILTERING                                                           #
    # ------------------------------------------------------------------ #

    def filtrar(
            self,
            data_inici=None,
            data_fi=None,
            hora_inici=None,
            hora_fi=None,
            gravetat=None,
            tipus_acc=None,
            municipi=None,
    ):
        df = self.cargar_datos().copy()

        # Filtro de fecha de Inicio
        if data_inici:
            dt_inici = pd.to_datetime(data_inici, format="%d/%m/%Y", errors="coerce")
            if not pd.isna(dt_inici):
                df = df[df["dat"] >= dt_inici]

        # Filtro de fecha Fin
        if data_fi:
            dt_fi = pd.to_datetime(data_fi, format="%d/%m/%Y", errors="coerce")
            if not pd.isna(dt_fi):
                df = df[df["dat"] <= dt_fi]

        # Filtro de gravedad
        if gravetat and gravetat != "Seleccionar":
            df = df[df["D_GRAVETAT"].str.upper() == gravetat.upper()]

        return df

    # ------------------------------------------------------------------ #
    #  GEOCODING                                                         #
    # ------------------------------------------------------------------ #

    def _coords_per_adreca(self, via, nom_mun):
        """Look up (lat, lon) from cache. Returns (None, None) if not found."""
        if via == "SE":
            return None, None
        adreca = f"{via} {nom_mun}"
        coords = self._geo_cache.get(adreca)
        if coords:
            return coords[0], coords[1]
        return None, None

    def obtenir_tots_marcadors(self, df=None):
        """Return a list of marker dicts for every row in *df*."""
        if df is None:
            df = self.cargar_datos()

        marcadors = []
        for _, fila in df.iterrows():
            lat, lon = self._coords_per_adreca(fila["via"], fila["nomMun"])
            if lat is not None:
                marcadors.append({
                    "lat": lat,
                    "lon": lon,
                    "dat": fila["dat"],
                    "hor": fila["hor"],
                    "gravetat": fila["D_GRAVETAT"],
                    "tipAcc": fila["tipAcc"],
                    "municipi": fila["nomMun"],
                })
        return marcadors

    def valors_unics(self, columna):
        """Return sorted unique non-null values of a column."""
        return sorted(self.cargar_datos()[columna].dropna().unique().tolist())