from pathlib import Path

import pandas as pd
import pytest

from football_project.loader import DataLoadError, load


def test_load_reads_csv_with_utf8_bom(tmp_path: Path) -> None:
    path = tmp_path / "partidos.csv"
    path.write_text(
        "\ufefftemporada,equipo_local,equipo_visitante\n"
        "2024/2025,Equipo A,Equipo B\n",
        encoding="utf-8",
    )

    result = load(path)

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == [
        "temporada",
        "equipo_local",
        "equipo_visitante",
    ]
    assert result.iloc[0]["equipo_local"] == "Equipo A"


def test_load_raises_when_file_does_not_exist(tmp_path: Path) -> None:
    with pytest.raises(DataLoadError, match="no existe"):
        load(tmp_path / "inexistente.csv")
