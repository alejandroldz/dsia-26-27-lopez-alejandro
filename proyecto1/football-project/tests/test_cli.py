import json
from pathlib import Path

from football_project.cli import main


def test_main_writes_clean_csv_and_quality_json(
    tmp_path: Path, monkeypatch
) -> None:
    input_path = tmp_path / "partidos.csv"
    output_path = tmp_path / "processed" / "partidos_limpios.csv"
    input_path.write_text(
        "temporada,fecha_partido,equipo_local,equipo_visitante,"
        "goles_local,goles_visitante,resultado_final\n"
        "2024/2025,2024-08-01,A,B,2,1,H\n"
        "2024/2025,fecha-invalida,C,D,0,0,D\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "football-project",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    main()

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8-sig").count("\n") == 2
    quality = json.loads(
        (output_path.parent / "calidad_datos.json").read_text(
            encoding="utf-8"
        )
    )
    assert quality == {
        "filas_totales": 2,
        "filas_validas": 1,
        "filas_invalidas": 1,
        "goles_totales": 3,
        "goles_por_partido": 3.0,
    }
