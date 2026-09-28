# ventas_app/cli.py

import argparse
import json
import logging
from pathlib import Path

from .loader import load
from .validator import validate
from .metrics import compute_metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    path = Path(args.input)
    output_path = Path(args.output)
    DATA_DIR = path.parent

    df = load(path)
    validos, errores = validate(df)

    metrics = compute_metrics(validos)

    logger.info("Filas totales: %d", len(df))
    logger.info("Filas válidas: %d", len(validos))
    logger.info("Filas inválidas: %d", len(errores))

    logger.info("Importe por región:\n%s", metrics["importe_por_region"].to_string())
    logger.info("Top 3 productos:\n%s", metrics["top_3"].to_string())
    logger.info("Clientes recurrentes:\n%s", metrics["clientes"].to_string())

    validos.to_csv(output_path, index=False)
    logger.info("Archivo limpio guardado en: %s", output_path)

    datos = {
        "filas_totales": int(len(df)),
        "filas_validas": int(len(validos)),
        "filas_invalidas": int(len(errores)),
        "importe_total": float(validos["importe"].sum()),
    }
    json_path = DATA_DIR / "calidad_datos.json"
    json_path.write_text(
        json.dumps(datos, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Métricas de calidad guardadas en: %s", json_path)


if __name__ == "__main__":
    main()