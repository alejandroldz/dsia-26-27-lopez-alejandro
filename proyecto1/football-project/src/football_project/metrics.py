import pandas as pd


def compute_metrics(validos: pd.DataFrame) -> dict[str, object]:
    """Calcula un resumen sencillo de los partidos válidos."""
    resultados = (
        validos["resultado_final"]
        .value_counts()
        .rename_axis("resultado")
        .reset_index(name="partidos")
    )
    goles_por_equipo = pd.concat(
        [
            validos[["equipo_local", "goles_local"]].rename(
                columns={"equipo_local": "equipo", "goles_local": "goles"}
            ),
            validos[["equipo_visitante", "goles_visitante"]].rename(
                columns={
                    "equipo_visitante": "equipo",
                    "goles_visitante": "goles",
                }
            ),
        ]
    )
    goles_por_equipo = (
        goles_por_equipo.groupby("equipo", as_index=False)["goles"]
        .sum()
        .sort_values("goles", ascending=False)
    )

    return {
        "resultados": resultados,
        "goles_por_equipo": goles_por_equipo,
        "goles_por_partido": (
            validos["goles_local"] + validos["goles_visitante"]
        ).mean(),
    }