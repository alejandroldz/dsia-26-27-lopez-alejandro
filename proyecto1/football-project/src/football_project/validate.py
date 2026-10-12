import pandas as pd


class ValidationError(Exception):
    """Datos que no cumplen las reglas básicas de un partido."""


REQUIRED_COLUMNS = {
    "temporada",
    "fecha_partido",
    "equipo_local",
    "equipo_visitante",
    "goles_local",
    "goles_visitante",
    "resultado_final",
}


def validate(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa los partidos válidos de los que contienen datos inválidos."""
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValidationError(
            f"Faltan columnas obligatorias: {', '.join(sorted(missing))}"
        )

    data = frame.copy()
    data["fecha_partido"] = pd.to_datetime(
        data["fecha_partido"], errors="coerce"
    )
    data["goles_local"] = pd.to_numeric(data["goles_local"], errors="coerce")
    data["goles_visitante"] = pd.to_numeric(
        data["goles_visitante"], errors="coerce"
    )

    resultado = pd.Series(pd.NA, index=data.index, dtype="object")
    resultado.loc[data["goles_local"] > data["goles_visitante"]] = "H"
    resultado.loc[data["goles_local"] < data["goles_visitante"]] = "A"
    resultado.loc[data["goles_local"] == data["goles_visitante"]] = "D"
    equipos_validos = (
        data["equipo_local"].notna()
        & data["equipo_local"].astype("string").str.strip().ne("")
        & data["equipo_visitante"].notna()
        & data["equipo_visitante"].astype("string").str.strip().ne("")
        & data["equipo_local"].ne(data["equipo_visitante"])
    )
    mascara = (
        data["fecha_partido"].notna()
        & equipos_validos
        & data["goles_local"].notna()
        & data["goles_visitante"].notna()
        & (data["goles_local"] >= 0)
        & (data["goles_visitante"] >= 0)
        & data["resultado_final"].isin(["H", "D", "A"])
        & data["resultado_final"].eq(resultado)
    )

    return data[mascara].copy(), data[~mascara].copy()