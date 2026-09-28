import pandas as pd


class ValidationError(Exception):
    """Datos que no cumplen reglas de negocio."""


def validate(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame['unidades'] = pd.to_numeric(frame["unidades"], errors="coerce") 
    frame['precio_unitario'] = pd.to_numeric(frame["precio_unitario"], errors="coerce") 
    mascara = (
        frame["unidades"].notna()
        & (frame["unidades"] > 0)
        & frame["precio_unitario"].notna()
        & (frame["precio_unitario"] > 0)
    )
    new_frame = frame[mascara].copy()
    errores = frame[~mascara].copy() 
    new_frame["importe"] = new_frame["unidades"] * new_frame["precio_unitario"]
    return new_frame, errores