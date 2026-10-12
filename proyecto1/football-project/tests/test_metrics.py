import pandas as pd
import pytest

from football_project.metrics import compute_metrics


def test_compute_metrics_summarizes_results_and_goals() -> None:
    matches = pd.DataFrame(
        [
            {
                "equipo_local": "A",
                "equipo_visitante": "B",
                "goles_local": 2,
                "goles_visitante": 1,
                "resultado_final": "H",
            },
            {
                "equipo_local": "B",
                "equipo_visitante": "C",
                "goles_local": 0,
                "goles_visitante": 0,
                "resultado_final": "D",
            },
        ]
    )

    result = compute_metrics(matches)

    assert result["resultados"].to_dict("records") == [
        {"resultado": "H", "partidos": 1},
        {"resultado": "D", "partidos": 1},
    ]
    assert result["goles_por_equipo"].to_dict("records") == [
        {"equipo": "A", "goles": 2},
        {"equipo": "B", "goles": 1},
        {"equipo": "C", "goles": 0},
    ]
    assert result["goles_por_partido"] == pytest.approx(1.5)


def test_compute_metrics_handles_empty_input() -> None:
    matches = pd.DataFrame(
        columns=[
            "equipo_local",
            "equipo_visitante",
            "goles_local",
            "goles_visitante",
            "resultado_final",
        ]
    )

    result = compute_metrics(matches)

    assert result["resultados"].empty
    assert result["goles_por_equipo"].empty
    assert pd.isna(result["goles_por_partido"])
