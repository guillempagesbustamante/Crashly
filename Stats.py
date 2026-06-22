import pandas as pd


class Stats:
    """
    Statistics helper for the accident dataset.

    Pass in any DataFrame returned by Markers.cargar_datos() or
    Markers.filtrar() — every method here works on whatever subset
    you give it, so filtered stats "just work" the same way.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

    # ------------------------------------------------------------------ #
    #  TIME PATTERNS                                                      #
    # ------------------------------------------------------------------ #

    def hora_mes_frequent(self):
        """Return the hour (0-23) with the most accidents."""
        if self.df.empty:
            return None
        hores = self.df["hor"].dropna().astype(int)
        return int(hores.mode()[0])

    def distribucio_per_hora(self):
        """
        Return a dict {hour: count} for all 24 hours (0 if no accidents
        in that hour), useful for a bar chart.
        """
        hores = self.df["hor"].dropna().astype(int)
        counts = hores.value_counts().to_dict()
        return {h: counts.get(h, 0) for h in range(24)}

    def distribucio_per_dia_setmana(self):
        """
        Return a dict {day_name: count}, Monday through Sunday,
        based on the 'dat' column.
        """
        dies = ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte", "Diumenge"]
        df_valid = self.df.dropna(subset=["dat"])
        counts = df_valid["dat"].dt.dayofweek.value_counts().to_dict()
        return {dies[i]: counts.get(i, 0) for i in range(7)}

    def distribucio_per_mes(self):
        """Return a dict {month_number (1-12): count}."""
        df_valid = self.df.dropna(subset=["dat"])
        counts = df_valid["dat"].dt.month.value_counts().to_dict()
        return {m: counts.get(m, 0) for m in range(1, 13)}

    def franja_mes_perillosa(self):
        """
        Return the most dangerous time-of-day band:
        Matí (6-12), Tarda (12-18), Vespre (18-22), Nit (22-6).
        """
        def franja(h):
            if 6 <= h < 12:
                return "Matí"
            elif 12 <= h < 18:
                return "Tarda"
            elif 18 <= h < 22:
                return "Vespre"
            else:
                return "Nit"

        if self.df.empty:
            return None
        hores = self.df["hor"].dropna().astype(int)
        franges = hores.apply(franja)
        return franges.mode()[0]

    # ------------------------------------------------------------------ #
    #  SEVERITY & RISK                                                    #
    # ------------------------------------------------------------------ #

    def taxa_mortalitat(self):
        """Return the % of accidents in this dataset that were fatal."""
        total = len(self.df)
        if total == 0:
            return 0.0
        mortals = len(self.df[self.df["D_GRAVETAT"] == "Accident mortal"])
        return round((mortals / total) * 100, 2)

    def probabilitat_gravetat(self, gravetat):
        """
        Return the probability (0-1) that a random accident in this
        dataset has the given gravetat value (e.g. "Accident mortal").
        """
        total = len(self.df)
        if total == 0:
            return 0.0
        n = len(self.df[self.df["D_GRAVETAT"] == gravetat])
        return round(n / total, 4)

    def mitjana_victimes(self):
        """
        Average victims per accident.
        Requires an 'F_VICTIMES' column — add it to Markers.COLUMNES if
        you want this to work (it's not loaded by default right now).
        """
        if "F_VICTIMES" not in self.df.columns:
            raise KeyError(
                "Falta la columna 'F_VICTIMES'. Afegeix-la a Markers.COLUMNES "
                "per poder calcular aquesta estadística."
            )
        return round(self.df["F_VICTIMES"].mean(), 2)

    def risc_per_tipus_accident(self):
        """
        Return a dict {tipus_accident: mortality_rate_%} showing which
        accident types are deadliest.
        """
        resultat = {}
        for tipus in self.df["tipAcc"].dropna().unique():
            subset = self.df[self.df["tipAcc"] == tipus]
            total = len(subset)
            mortals = len(subset[subset["D_GRAVETAT"] == "Accident mortal"])
            resultat[tipus] = round((mortals / total) * 100, 2) if total else 0.0
        return dict(sorted(resultat.items(), key=lambda x: x[1], reverse=True))

    # ------------------------------------------------------------------ #
    #  LOCATION-BASED                                                     #
    # ------------------------------------------------------------------ #

    def municipis_mes_perillosos(self, top_n=10):
        """Return a dict {municipi: count} for the top_n towns by accident count."""
        counts = self.df["nomMun"].value_counts().head(top_n)
        return counts.to_dict()

    def vies_mes_perilloses(self, top_n=10):
        """
        Return a dict {via: count} for the top_n roads by accident count.
        Excludes "SE" (no specific road / urban accident without a road code).
        """
        counts = self.df[self.df["via"] != "SE"]["via"].value_counts().head(top_n)
        return counts.to_dict()

    def taxa_mortalitat_per_municipi(self, top_n=10):
        """
        Return a dict {municipi: mortality_rate_%} for the top_n towns
        with the highest fatality rate (minimum 5 accidents to avoid
        statistical noise from towns with very few records).
        """
        resultat = {}
        for municipi in self.df["nomMun"].dropna().unique():
            subset = self.df[self.df["nomMun"] == municipi]
            total = len(subset)
            if total < 5:
                continue
            mortals = len(subset[subset["D_GRAVETAT"] == "Accident mortal"])
            resultat[municipi] = round((mortals / total) * 100, 2)

        ordenat = dict(sorted(resultat.items(), key=lambda x: x[1], reverse=True))
        return dict(list(ordenat.items())[:top_n])

    def distribucio_per_tipus_vehicle(self):
        """
        Return a dict {tipus_vehicle: total_implicats} summing how many
        vehicles of each type were involved across all accidents in this
        dataset. Requires the F_*_IMPLICADES columns in Markers.COLUMNES.
        """
        columnes_vehicle = {
            "Vianants": "F_VIANANTS_IMPLICADES",
            "Bicicletes": "F_BICICLETES_IMPLICADES",
            "Ciclomotors": "F_CICLOMOTORS_IMPLICADES",
            "Motocicletes": "F_MOTOCICLETES_IMPLICADES",
            "Vehicles lleugers": "F_VEH_LLEUGERS_IMPLICADES",
            "Vehicles pesants": "F_VEH_PESANTS_IMPLICADES",
            "Altres": "F_ALTRES_UNIT_IMPLICADES",
        }

        resultat = {}
        for nom, columna in columnes_vehicle.items():
            if columna not in self.df.columns:
                raise KeyError(
                    f"Falta la columna '{columna}'. Afegeix-la a Markers.COLUMNES "
                    "per poder calcular aquesta estadística."
                )
            resultat[nom] = int(self.df[columna].fillna(0).sum())

        return dict(sorted(resultat.items(), key=lambda x: x[1], reverse=True))

    def tipus_vehicle_mes_implicat(self):
        """Return the vehicle type most frequently involved in accidents."""
        distribucio = self.distribucio_per_tipus_vehicle()
        if not distribucio:
            return None
        return max(distribucio, key=distribucio.get)

    def distribucio_per_lluminositat(self):
        """
        Return a dict {condicio_lluminositat: count}, e.g.
        "Ple dia", "Crepuscle", "Nit amb enllumenat", "Nit sense enllumenat", etc.
        Requires the D_LLUMINOSITAT column in Markers.COLUMNES.
        """
        if "D_LLUMINOSITAT" not in self.df.columns:
            raise KeyError(
                "Falta la columna 'D_LLUMINOSITAT'. Afegeix-la a Markers.COLUMNES "
                "per poder calcular aquesta estadística."
            )
        counts = self.df["D_LLUMINOSITAT"].dropna().value_counts()
        return counts.to_dict()

    def taxa_mortalitat_per_lluminositat(self):
        """
        Return a dict {condicio_lluminositat: mortality_rate_%} showing
        which lighting conditions are deadliest.
        """
        if "D_LLUMINOSITAT" not in self.df.columns:
            raise KeyError(
                "Falta la columna 'D_LLUMINOSITAT'. Afegeix-la a Markers.COLUMNES "
                "per poder calcular aquesta estadística."
            )
        resultat = {}
        for condicio in self.df["D_LLUMINOSITAT"].dropna().unique():
            subset = self.df[self.df["D_LLUMINOSITAT"] == condicio]
            total = len(subset)
            mortals = len(subset[subset["D_GRAVETAT"] == "Accident mortal"])
            resultat[condicio] = round((mortals / total) * 100, 2) if total else 0.0
        return dict(sorted(resultat.items(), key=lambda x: x[1], reverse=True))
    # ------------------------------------------------------------------ #
    #  SUMMARY                                                            #
    # ------------------------------------------------------------------ #

    def resum(self):
        """Quick all-in-one summary dict — handy for a dashboard overview."""
        return {
            "total_accidents": len(self.df),
            "taxa_mortalitat_%": self.taxa_mortalitat(),
            "hora_mes_frequent": self.hora_mes_frequent(),
            "franja_mes_perillosa": self.franja_mes_perillosa(),
            "municipi_mes_perillos": (
                self.df["nomMun"].value_counts().idxmax() if not self.df.empty else None
            ),
            "via_mes_perillosa": (
                self.df[self.df["via"] != "SE"]["via"].value_counts().idxmax()
                if not self.df[self.df["via"] != "SE"].empty else None
            ),
        }