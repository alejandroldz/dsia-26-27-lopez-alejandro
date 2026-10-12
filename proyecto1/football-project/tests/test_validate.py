import pandas as pd
import pytest

from football_project.validate import ValidationError, validate


def test_validate_separates_valid_and_invalid_matches() -> None:
    frame = pd.DataFrame(
        [
            {
                "temporada": "2024/2025",
                "fecha_partido": "2024-08-01",
                "equipo_local": "A",
                "equipo_visitante": "B",
                "goles_local": "2",
                "goles_visitante": "1",
                "resultado_final": "H",
            },
            {
                "temporada": "2024/2025",
                "fecha_partido": "2024-08-02",
                "equipo_local": "C",
                "equipo_visitante": "D",
                "goles_local": "-1",
                "goles_visitante": "0",
                "resultado_final": "A",
            },
            {
                "temporada": "2024/2025",
                "fecha_partido": "2024-08-03",
                "equipo_local": "E",
                "equipo_visitante": "F",
                "goles_local": "0",
                "goles_visitante": "0",
                "resultado_final": "H",
            },
        ]
    )

    validos, errores = validate(frame)

    assert len(validos) == 1
    assert len(errores) == 2
    assert validos.iloc[0]["resultado_final"] == "H"
    assert pd.api.types.is_datetime64_any_dtype(validos["fecha_partido"])
    assert pd.api.types.is_numeric_dtype(validos["goles_local"])


def test_validate_rejects_missing_required_columns() -> None:
    with pytest.raises(ValidationError, match="Faltan columnas obligatorias"):
        validate(pd.DataFrame({"equipo_local": ["A"]}))
