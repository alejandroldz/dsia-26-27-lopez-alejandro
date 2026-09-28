import pandas as pd
from pathlib import Path

class DataLoadError(Exception):
    """Error al cargar datos de origen."""

def load(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise DataLoadError(f"El archivo no existe: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise DataLoadError(f"Error al leer el archivo: {path}") from e
        
    