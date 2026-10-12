from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/raw/laliga.csv")
OUTPUT_FILE = Path("data/raw/laliga_elo.csv")

ELO_INICIAL = 1500.0
K = 20.0
VENTAJA_LOCAL = 65.0
ESCALA = 400.0


def expectativa_local(elo_local: float, elo_visitante: float) -> float:
    """Calcula la expectativa del local antes del partido."""
    diferencia = elo_local + VENTAJA_LOCAL - elo_visitante

    return 1 / (1 + 10 ** (-diferencia / ESCALA))


def resultado_local(goles_local: int, goles_visitante: int) -> float:
    """Victoria = 1, empate = 0.5, derrota = 0."""
    if goles_local > goles_visitante:
        return 1.0

    if goles_local < goles_visitante:
        return 0.0

    return 0.5


def multiplicador_goles(goles_local: int, goles_visitante: int) -> float:
    """Pondera la actualización según la diferencia de goles."""
    diferencia = abs(goles_local - goles_visitante)

    if diferencia <= 1:
        return 1.0

    if diferencia == 2:
        return 1.5

    return (11 + diferencia) / 8


def actualizar_elo(elo_local: float, elo_visitante: float, goles_local: int, goles_visitante: int, expectativa: float) -> tuple[float, float]:
    """Actualiza los ratings después del partido."""
    resultado = resultado_local(goles_local, goles_visitante)

    multiplicador = multiplicador_goles(goles_local, goles_visitante)

    cambio = K * multiplicador * (resultado - expectativa)

    return elo_local + cambio, elo_visitante - cambio


def iniciar_temporada(ratings: dict[str, float], equipos_actuales: set[str], equipos_anteriores: set[str]) -> dict[str, float]:
    """Inicializa los ascendidos con el promedio de los descendidos."""
    if not equipos_anteriores:
        return {
            equipo: ELO_INICIAL
            for equipo in equipos_actuales
        }

    descendidos = equipos_anteriores - equipos_actuales
    ascendidos = equipos_actuales - equipos_anteriores

    elo_ascendidos = (
        sum(ratings[equipo] for equipo in descendidos)
        / len(descendidos)
        if descendidos
        else ELO_INICIAL
    )

    return {
        equipo: (
            elo_ascendidos
            if equipo in ascendidos
            else ratings[equipo]
        )
        for equipo in equipos_actuales
    }


def calcular_elo(df: pd.DataFrame) -> pd.DataFrame:
    """Añade los ratings previos a cada encuentro."""
    df = df.copy()
    df["fecha_partido"] = pd.to_datetime(df["fecha_partido"])

    df = df.sort_values(["fecha_partido", "equipo_local", "equipo_visitante"]).reset_index(drop=True)

    ratings = {}
    equipos_anteriores = set()
    registros = {}

    for _, temporada in df.groupby("temporada", sort=True):
        equipos_actuales = (
            set(temporada["equipo_local"])
            | set(temporada["equipo_visitante"])
        )

        # Ajustar los ascendidos al comenzar la temporada
        ratings = iniciar_temporada(
            ratings,
            equipos_actuales,
            equipos_anteriores,
        )

        # Todos los partidos del día usan los ratings previos a ese día
        for _, partidos_dia in temporada.groupby( "fecha_partido", sort=True):
            actualizaciones = {}

            for indice, partido in partidos_dia.iterrows():
                local = partido["equipo_local"]
                visitante = partido["equipo_visitante"]

                elo_local = ratings[local]
                elo_visitante = ratings[visitante]

                expectativa = expectativa_local(elo_local, elo_visitante)

                # Guardar las métricas antes de utilizar el marcador
                registros[indice] = {
                    "elo_local_pre": elo_local,
                    "elo_visitante_pre": elo_visitante,
                    "elo_diferencia_pre": elo_local - elo_visitante,
                    "elo_expectativa_local_pre": expectativa,
                }

                nuevo_local, nuevo_visitante = actualizar_elo(elo_local, elo_visitante, partido["goles_local"], partido["goles_visitante"], expectativa)

                actualizaciones[local] = nuevo_local
                actualizaciones[visitante] = nuevo_visitante

            # Aplicar los resultados para los días siguientes
            ratings.update(actualizaciones)

        equipos_anteriores = equipos_actuales

    metricas = pd.DataFrame.from_dict(registros, orient="index")

    for columna in metricas:
        df[columna] = metricas[columna]

    return df


def main() -> None:
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    df = calcular_elo(df)

    df.to_csv(OUTPUT_FILE, index=False, date_format="%Y-%m-%d")

    print(f"Archivo generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()