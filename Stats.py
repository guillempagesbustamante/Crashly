import pandas as pd




class Stats:
   """
stats generals aribitraries

ho fa tot respecte el cargar datos escollit, aixi que els filtres s'apliquen automaticament
   """


   def __init__(self, df: pd.DataFrame):
       self.df = df


   #  #
   #  filtres de temps                                                      #
   #  #


   def hora_mes_frequent(self):
       """torna la hora (0-23) on succeeixen mes accidents"""
       if self.df.empty:
           return None
       hores = self.df["hor"].dropna().astype(int)
       return int(hores.mode()[0])


   def distribucio_per_hora(self):
       """
       torna el nombre de accidents totals a cada hora
       """
       hores = self.df["hor"].dropna().astype(int)
       counts = hores.value_counts().to_dict()
       return {h: counts.get(h, 0) for h in range(24)}


   def distribucio_per_dia_setmana(self):
       """
      torna el nombre de accidents per a cada dia de la setmana
       """
       dies = ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte", "Diumenge"]
       df_valid = self.df.dropna(subset=["dat"])
       counts = df_valid["dat"].dt.dayofweek.value_counts().to_dict()
       return {dies[i]: counts.get(i, 0) for i in range(7)}


   def distribucio_per_mes(self):
       """torna el nombre de accidents per a cada mes (1-12)."""
       df_valid = self.df.dropna(subset=["dat"])
       counts = df_valid["dat"].dt.month.value_counts().to_dict()
       return {m: counts.get(m, 0) for m in range(1, 13)}


   def franja_mes_perillosa(self):
       """
       torna la franja de dia mes perillosa (mati tarda vespre nit)
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


   #  #
   #  clima velocitat vehicles                                            #
   #  #


   def distribucio_climatologia(self):
       """
       torna el nombre de accidents per a cada situacio climatologica. si no hi ha pose altres
       """
       if self.df.empty or "D_CLIMATOLOGIA" not in self.df.columns:
           return {}
       counts = self.df["D_CLIMATOLOGIA"].fillna("Altres").value_counts()
       return counts.to_dict()

   def distribucio_velocitats(self, top_n=6):
       """
       torna el top 6 nombre de accidents per a cada rang de velocitats, exclou NA i 999 ja que no aporten informacio interesant
       """
       if "C_VELOCITAT_VIA" not in self.df.columns:
           raise KeyError(
               "Falta la columna 'C_VELOCITAT_VIA'. Afegeix-la a Markers.COLUMNES "
               "per poder calcular aquesta estadística."
           )
       velocitats = self.df["C_VELOCITAT_VIA"].dropna()
       velocitats = velocitats[velocitats != 999]
       counts = velocitats.value_counts().head(top_n)
       return {int(k): v for k, v in counts.to_dict().items()}

   def recompte_vehicles_implicats(self):
       """
       torna el nombre de accidents en els que ha participat cada tipus de vehicle
       """
       columnes_vehiculos = {
           "F_VIANANTS_IMPLICADES": "Vianants",
           "F_BICICLETES_IMPLICADES": "Bicicletes",
           "F_CICLOMOTORS_IMPLICADES": "Ciclomotors",
           "F_MOTOCICLETES_IMPLICADES": "Motocicletes",
           "F_VEH_LLEUGERS_IMPLICADES": "Vehicles lleugers",
           "F_VEH_PESANTS_IMPLICADES": "Vehicles pesants",
           "F_ALTRES_UNIT_IMPLICADES": "Altres"
       }


       recompte = {}
       for col, etiqueta in columnes_vehiculos.items():
           if col in self.df.columns and not self.df.empty:
               recompte[etiqueta] = int((self.df[col] != 0).sum())
           else:
               recompte[etiqueta] = 0


       return dict(sorted(recompte.items(), key=lambda x: x[1], reverse=True))


   #  #
   #  gravetat i risc                                                    #
   #  #


   def taxa_mortalitat(self):
       """Percentatge de accidents mortals."""
       total = len(self.df)
       if total == 0:
           return 0.0
       mortals = len(self.df[self.df["D_GRAVETAT"] == "Accident mortal"])
       return round((mortals / total) * 100, 2)


   def probabilitat_gravetat(self, gravetat):
       """
       percentatge de accidents per a cada grau de gravetat
       """
       total = len(self.df)
       if total == 0:
           return 0.0
       n = len(self.df[self.df["D_GRAVETAT"] == gravetat])
       return round(n / total, 4)


   def mitjana_victimes(self):
       """ mitjana victimes, autoexplicatiu."""
       if "F_VICTIMES" not in self.df.columns:
           raise KeyError(
               "Falta la columna 'F_VICTIMES'. Afegeix-la a Markers.COLUMNES."
           )
       return round(self.df["F_VICTIMES"].mean(), 2)


   def risc_per_tipus_accident(self):
       """percentatge de mortalitat per a cada tipus daccident (atropellament, colisio etc."""
       resultat = {}
       for tipus in self.df["tipAcc"].dropna().unique():
           subset = self.df[self.df["tipAcc"] == tipus]
           total = len(subset)
           mortals = len(subset[subset["D_GRAVETAT"] == "Accident mortal"])
           resultat[tipus] = round((mortals / total) * 100, 2) if total else 0.0
       return dict(sorted(resultat.items(), key=lambda x: x[1], reverse=True))


   #  #
   # stats per ubicacio                                                     #
   #  #


   def municipis_mes_perillosos(self, top_n=10):
       """num de accidents per a cada municipi (top10)."""
       counts = self.df["nomMun"].value_counts().head(top_n)
       return counts.to_dict()


   def vies_mes_perilloses(self, top_n=10):
       """num de accidents per a cada via (top10). """
       counts = self.df[self.df["via"] != "SE"]["via"].value_counts().head(top_n)
       return counts.to_dict()


   def taxa_mortalitat_per_municipi(self, top_n=10):
       """ percentatge de accidents mortals per municipi top 10."""
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
       torna un dict amb la suma de cada tipus de vehicle involucrat en un accident en la base de dades
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
       """Torna el vehicle mes comu en accidents"""
       distribucio = self.distribucio_per_tipus_vehicle()
       if not distribucio:
           return None
       return max(distribucio, key=distribucio.get)

   def distribucio_per_lluminositat(self):
       """
       torna el nombre de accidents per a cada condicio de lluminositat.
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
      torna el percentatge de mortalitat per a cada condicio de lluminositat.
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
   #  #
   #  Resum                                                            #
   #  #


   def resum(self):
       """resum general de les dades."""
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
