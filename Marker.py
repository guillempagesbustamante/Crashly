from geopy.geocoders import Nominatim
import pandas as pd

class Markers:


    def cargar_datos(self):
        datos= pd.read_csv("base_dades.csv", usecols=["via","pk","nomMun"])
        return datos


    def marker(self,num):
        geolocator = Nominatim(user_agent="accidents_app")
        datos = self.cargar_datos()
        fila=datos.iloc[num]
        direccion=f"{fila['via']} {fila['nomMun']}"
        if fila['via']!="SE":
            location = geolocator.geocode(direccion)

            if location:
                print(location.latitude)
                print(location.longitude)
        else:
            pass

