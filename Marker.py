from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(BASE_DIR, "geocode_cache.json")


class Markers:

    COLUMNES = ["via", "pk", "nomMun", "nomDem","dat", "hor", "D_GRAVETAT", "tipAcc", "D_SUBTIPUS_ACCIDENT"]

    def __init__(self):
        self.geolocator = Nominatim(user_agent="accidents_app")
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)
        self._dades = None                        # DataFrame cache
        self._geo_cache = self._carregar_cache()  # address → [lat, lon] | null

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
        results to geocode_cache.json.  Run this ONCE from a script or shell:

            from markers import Markers
            Markers().construir_cache()

        After that, the app never calls Nominatim at runtime again.
        Progress is saved every 50 addresses so you can safely interrupt
        and resume — already-cached addresses are skipped automatically.
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
                continue  # already cached, skip

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
                self._dades["dat"], dayfirst=False, errors="coerce"
            )
        return self._dades

    # ------------------------------------------------------------------ #
    #  FILTERING                                                           #
    # ------------------------------------------------------------------ #

    def filtrar(
        self,
        data_inici=None,   # "DD/MM/YYYY"  – start date (inclusive)
        data_fi=None,      # "DD/MM/YYYY"  – end date   (inclusive)
        hora_inici=None,   # int 0-23       – start hour (inclusive)
        hora_fi=None,      # int 0-23       – end hour   (inclusive)
        gravetat=None,     # str or list    – e.g. "Mort" / ["Mort","Ferit greu"]
        tipus_acc=None,    # str or list    – value(s) from tipAcc
        municipi=None,
        provincia=None
    ):
        """
        Return a filtered DataFrame. All parameters are optional;
        omit any to skip that filter.
        """
        df = self.cargar_datos().copy()

        if data_inici:
            df = df[df["dat"] >= pd.to_datetime(data_inici, dayfirst=True)]
        if data_fi:
            df = df[df["dat"] <= pd.to_datetime(data_fi, dayfirst=True)]

        if hora_inici is not None:
            df = df[df["hor"] >= hora_inici]
        if hora_fi is not None:
            df = df[df["hor"] <= hora_fi]

        if gravetat:
            if isinstance(gravetat, str):
                gravetat = [gravetat]
            df = df[df["D_GRAVETAT"].isin(gravetat)]

        if tipus_acc:
            if isinstance(tipus_acc, str):
                tipus_acc = [tipus_acc]
            df = df[df["tipAcc"].isin(tipus_acc)]

        if provincia:
            if isinstance(provincia, str):
                provincia = [provincia]
            df = df[df["nomDem"].isin(provincia)]

        return df.reset_index(drop=True)

    # ------------------------------------------------------------------ #
    #  GEOCODING  (cache-first, no live calls at runtime)                 #
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
        """
        Return a list of marker dicts for every row in *df* that has
        coordinates in the cache.  Pass the result of filtrar() here.

            [{"lat": ..., "lon": ..., "gravetat": ..., "dat": ..., ...}, ...]
        """
        if df is None:
            df = self.cargar_datos()

        marcadors = []
        for _, fila in df.iterrows():
            lat, lon = self._coords_per_adreca(fila["via"], fila["nomMun"])
            if lat is not None:
                marcadors.append({
                    "lat":      lat,
                    "lon":      lon,
                    "dat":      fila["dat"],
                    "hor":      fila["hor"],
                    "gravetat": fila["D_GRAVETAT"],
                    "tipAcc":   fila["tipAcc"],
                    "municipi": fila["nomMun"],
                })
        return marcadors

    # ------------------------------------------------------------------ #
    #  HELPER – unique values for building UI dropdowns                   #
    # ------------------------------------------------------------------ #

    def valors_unics(self, columna):
        """Return sorted unique non-null values of a column."""
        return sorted(self.cargar_datos()[columna].dropna().unique().tolist())