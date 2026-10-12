import argparse
from pathlib import Path

import pandas as pd

from football_project.dataset.descargar_laliga import descargar_dataset
from football_project.dataset.elo import calcular_elo
from football_project.dataset.metricas_acumuladas import calcular_metricas


def guardar(df: pd.DataFrame, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        ruta,
        index=False,
        encoding="utf-8-sig",
        date_format="%Y-%m-%d",
    )
    print(f"Archivo generado: {ruta}")


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta el pipeline completo de datos de LaLiga.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Ruta del archivo final con las metricas acumuladas.",
    )
    parser.add_argument(
        "--output-raw",
        type=Path,
        help="Ruta opcional para guardar el dataset descargado.",
    )
    parser.add_argument(
        "--output-elo",
        type=Path,
        help="Ruta opcional para guardar el dataset con Elo.",
    )
    return parser.parse_args()


def main() -> None:
    opciones = argumentos()

    # Descarga y prepara los partidos.
    df_raw = descargar_dataset()
    if opciones.output_raw is not None:
        guardar(df_raw, opciones.output_raw)

    # Calcula el Elo usando solo los datos anteriores a cada partido.
    df_elo = calcular_elo(df_raw)
    if opciones.output_elo is not None:
        guardar(df_elo, opciones.output_elo)

    # Calcula las metricas historicas y guarda siempre el resultado final.
    df_final = calcular_metricas(df_elo)
    guardar(df_final, opciones.output)


if __name__ == "__main__":
    main()
