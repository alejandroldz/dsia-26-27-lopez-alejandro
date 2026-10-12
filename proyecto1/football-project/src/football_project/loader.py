from pathlib import Path

import pandas as pd


class DataLoadError(Exception):
    """Error al cargar datos de partidos."""


def load(path: Path) -> pd.DataFrame:
    """Carga el CSV de partidos de LaLiga."""
    if not path.exists():
        raise DataLoadError(f"El archivo no existe: {path}")

    try:
        return pd.read_csv(path)
    except:
        raise DataLoadError(f"Error al leer el archivo: {path}") 