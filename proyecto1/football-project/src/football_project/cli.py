import argparse
import json
import logging
from pathlib import Path

from football_project.loader import load
from football_project.metrics import compute_metrics
from football_project.validate import validate

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Valida y resume partidos de LaLiga."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    data = load(args.input)
    validos, errores = validate(data)
    metrics = compute_metrics(validos)

    logger.info("Filas totales: %d", len(data))
    logger.info("Filas válidas: %d", len(validos))
    logger.info("Filas inválidas: %d", len(errores))
    logger.info("Resultados:\n%s", metrics["resultados"].to_string(index=False))
    logger.info(
        "Goles por equipo:\n%s",
        metrics["goles_por_equipo"].head(3).to_string(index=False),
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    validos.to_csv(args.output, index=False, encoding="utf-8-sig")
    logger.info("Archivo limpio guardado en: %s", args.output)

    quality = {
        "filas_totales": int(len(data)),
        "filas_validas": int(len(validos)),
        "filas_invalidas": int(len(errores)),
        "goles_totales": int(
            validos["goles_local"].sum() + validos["goles_visitante"].sum()
        ),
        "goles_por_partido": (
            0.0 if validos.empty else float(metrics["goles_por_partido"])
        ),
    }
    quality_path = args.output.parent / "calidad_datos.json"
    quality_path.write_text(
        json.dumps(quality, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Métricas de calidad guardadas en: %s", quality_path)


if __name__ == "__main__":
    main()