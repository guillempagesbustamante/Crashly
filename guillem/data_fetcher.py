import pandas as pd
from typing import Optional, List
import os


class CSVLoader:
    """Carga y valida datos de accidentes desde CSV"""

    def __init__(self, filepath: str):
        """
        Args:
            filepath: Ruta al archivo CSV
        """
        filepath:Base_dades.csv
        self.filepath = filepath
        self.df = None

    def load_data(self,
                  date_column: str = None,
                  time_column: str = None,
                  datetime_column: str = None,
                  separator: str = ',',
                  encoding: str = 'utf-8') -> pd.DataFrame:
        """
        Carga el CSV y prepara los datos


            date_column: Nombre de columna de fecha
            time_column: Nombre de columna de hora
            datetime_column: Nombre de columna datetime combinada
            separator: Separador del CSV
            encoding: Codificación del archivo
        """
        # Cargar CSV
        self.df = pd.read_csv(
            self.filepath,
            sep=separator,
            encoding=encoding
        )

        print(f"✅ CSV cargado: {len(self.df)} registros")
        print(f"📋 Columnas encontradas: {self.df.columns.tolist()}")

        # Preparar campo datetime
        self._prepare_datetime(date_column, time_column, datetime_column)

        return self.df

    def _prepare_datetime(self, date_column: str = None,
                          time_column: str = None,
                          datetime_column: str = None):
        """Prepara la columna datetime"""

        # Detectar automáticamente si no se especifica
        if not any([date_column, time_column, datetime_column]):
            datetime_column = self._detect_datetime_column()

        if datetime_column:
            # Ya existe una columna datetime
            self.df['datetime'] = pd.to_datetime(
                self.df[datetime_column],
                infer_datetime_format=True,
                errors='coerce'
            )
        elif date_column and time_column:
            # Combinar fecha y hora
            self.df['datetime'] = pd.to_datetime(
                self.df[date_column] + ' ' + self.df[time_column],
                infer_datetime_format=True,
                errors='coerce'
            )
        elif date_column:
            # Solo fecha
            self.df['datetime'] = pd.to_datetime(
                self.df[date_column],
                infer_datetime_format=True,
                errors='coerce'
            )

        # Verificar que se creó correctamente
        if 'datetime' not in self.df.columns:
            print("⚠️ No se pudo crear la columna datetime")
        else:
            null_dates = self.df['datetime'].isna().sum()
            if null_dates > 0:
                print(f"⚠️ {null_dates} fechas no pudieron ser parseadas")

            print(f"📅 Rango de fechas: {self.df['datetime'].min()} - {self.df['datetime'].max()}")

    def _detect_datetime_column(self) -> Optional[str]:
        """Detecta automáticamente columna de fecha/hora"""
        possible_names = [
            'datetime', 'date_time', 'timestamp', 'fecha_hora',
            'fecha', 'date', 'time', 'hora'
        ]

        for col in self.df.columns:
            col_lower = col.lower().replace(' ', '_')
            if any(name in col_lower for name in possible_names):
                print(f"🔍 Columna datetime detectada: '{col}'")
                return col

        print("❌ No se detectó columna datetime automáticamente")
        return None

    def get_data_info(self) -> dict:
        """Obtiene información básica del dataset"""
        if self.df is None:
            return {}

        info = {
            'total_records': len(self.df),
            'columns': self.df.columns.tolist(),
            'null_values': self.df.isnull().sum().to_dict(),
            'date_range': (
                f"{self.df['datetime'].min()} - {self.df['datetime'].max()}"
                if 'datetime' in self.df.columns else 'N/A'
            )
        }

        # Info de severidad si existe
        if 'severity' in self.df.columns:
            info['severity_distribution'] = self.df['severity'].value_counts().to_dict()

        return info