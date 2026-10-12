# Football Project

Pipeline para descargar partidos de LaLiga, calcular Elo y generar metricas
historicas para modelos de prediccion.

## Requisitos

- Python 3.12 o superior.
- [UV](https://docs.astral.sh/uv/getting-started/installation/).

## Instalacion

Desde la raiz del proyecto:

```bash
uv sync
```

Para instalar tambien las dependencias de desarrollo:

```bash
uv sync --dev
```

## Configuracion

Por defecto, el pipeline descarga datos desde la temporada 2014/2015. Para
cambiar el año inicial, define `ANIO_INICIO` en un archivo `.env`:

```text
ANIO_INICIO=2014
```

## Ejecucion

El archivo `--output` es obligatorio. Los archivos intermedios solo se guardan
si se indican sus opciones:

```bash
uv run python src/football_project/dataset/main.py ^
  --output data/processed/laliga_features.csv ^
  --output-raw data/raw/laliga.csv ^
  --output-elo data/raw/laliga_elo.csv
```

Para guardar solo el resultado final:

```bash
uv run python src/football_project/dataset/main.py --output data/processed/laliga_features.csv
```

El pipeline realiza estos pasos:

1. Descarga y limpia los partidos.
2. Completa los xG disponibles.
3. Calcula los ratings Elo.
4. Genera las metricas historicas.

## Estructura

```text
football-project/
├── data/
│   ├── raw/
│   └── processed/
├── src/football_project/dataset/
│   ├── descargar_laliga.py
│   ├── elo.py
│   ├── main.py
│   └── metricas_acumuladas.py
├── pyproject.toml
└── uv.lock
```

## Archivos principales

| Archivo | Contenido |
| --- | --- |
| `data/raw/laliga.csv` | Partidos descargados y limpiados. |
| `data/raw/laliga_elo.csv` | Partidos con variables Elo. |
| `data/processed/laliga_features.csv` | Dataset final con metricas historicas. |

## Columnas del dataset final

El archivo final contiene 186 columnas. Para no repetir las variables
equivalentes, `{local/visitante}` representa las dos variantes de una misma
metrica. Por ejemplo, `puntos_5_{local/visitante}_pre` representa
`puntos_5_local_pre` y `puntos_5_visitante_pre`.

| Grupo | Columna |
| --- | --- |
| Partido | `temporada` |
| Partido | `fecha_partido` |
| Partido | `hora_inicio` |
| Partido | `equipo_local` |
| Partido | `equipo_visitante` |
| Partido | `goles_{local/visitante}` |
| Partido | `resultado_final` |
| Partido | `goles_{local/visitante}_descanso` |
| Partido | `resultado_descanso` |
| Partido | `goles_esperados_{local/visitante}` |
| Partido | `tiros_{local/visitante}` |
| Partido | `tiros_a_puerta_{local/visitante}` |
| Partido | `faltas_cometidas_{local/visitante}` |
| Partido | `corners_{local/visitante}` |
| Partido | `tarjetas_amarillas_{local/visitante}` |
| Partido | `tarjetas_rojas_{local/visitante}` |
| Elo | `elo_local_pre` |
| Elo | `elo_visitante_pre` |
| Elo | `elo_diferencia_pre` |
| Elo | `elo_expectativa_local_pre` |
| Historial | `partidos_previos_5_{local/visitante}_pre` |
| Historial | `partidos_previos_10_{local/visitante}_pre` |
| Historial | `partidos_temporada_{local/visitante}_pre` |
| Historial | `partidos_casa_temporada_{local/visitante}_pre` |
| Historial | `partidos_fuera_temporada_{local/visitante}_pre` |
| Historial | `partidos_casa_5_{local/visitante}_pre` |
| Historial | `partidos_fuera_5_{local/visitante}_pre` |
| Historial | `racha_tipo_{local/visitante}_pre` |
| Historial | `racha_longitud_{local/visitante}_pre` |
| Historial | `puntos_por_partido_temporada_{local/visitante}_pre` |
| Historial | `puntos_por_partido_casa_temporada_{local/visitante}_pre` |
| Historial | `puntos_por_partido_fuera_temporada_{local/visitante}_pre` |
| Historial | `dias_desde_ultimo_partido_liga_{local/visitante}_pre` |
| Forma | `puntos_{3,5,10}_{local/visitante}_pre` |
| Forma | `victorias_5_{local/visitante}_pre` |
| Forma | `empates_5_{local/visitante}_pre` |
| Ataque y defensa | `goles_favor_media_5_{local/visitante}_pre` |
| Ataque y defensa | `goles_contra_media_5_{local/visitante}_pre` |
| Ataque y defensa | `xg_favor_media_5_{local/visitante}_pre` |
| Ataque y defensa | `xg_contra_media_5_{local/visitante}_pre` |
| Ataque y defensa | `tiros_puerta_favor_media_5_{local/visitante}_pre` |
| Ataque y defensa | `tiros_puerta_contra_media_5_{local/visitante}_pre` |
| Ataque y defensa | `partidos_con_xg_5_{local/visitante}_pre` |
| Ataque y defensa | `elo_medio_rivales_5_{local/visitante}_pre` |
| Ataque y defensa | `goles_favor_media_10_{local/visitante}_pre` |
| Ataque y defensa | `goles_contra_media_10_{local/visitante}_pre` |
| Ataque y defensa | `xg_favor_media_10_{local/visitante}_pre` |
| Ataque y defensa | `xg_contra_media_10_{local/visitante}_pre` |
| Ataque y defensa | `tiros_puerta_favor_media_10_{local/visitante}_pre` |
| Ataque y defensa | `tiros_puerta_contra_media_10_{local/visitante}_pre` |
| Ataque y defensa | `partidos_con_xg_10_{local/visitante}_pre` |
| Ataque y defensa | `elo_medio_rivales_10_{local/visitante}_pre` |
| Rendimiento | `porterias_cero_proporcion_10_{local/visitante}_pre` |
| Rendimiento | `sin_marcar_proporcion_10_{local/visitante}_pre` |
| Rendimiento | `mas_{1_5,2_5,3_5}_goles_proporcion_10_{local/visitante}_pre` |
| Rendimiento | `ambos_marcan_proporcion_10_{local/visitante}_pre` |
| Rendimiento | `goles_favor_media_casa_5_{local/visitante}_pre` |
| Rendimiento | `goles_contra_media_casa_5_{local/visitante}_pre` |
| Rendimiento | `xg_favor_media_casa_5_{local/visitante}_pre` |
| Rendimiento | `xg_contra_media_casa_5_{local/visitante}_pre` |
| Rendimiento | `sin_perder_proporcion_casa_5_{local/visitante}_pre` |
| Rendimiento | `goles_favor_media_fuera_5_{local/visitante}_pre` |
| Rendimiento | `goles_contra_media_fuera_5_{local/visitante}_pre` |
| Rendimiento | `xg_favor_media_fuera_5_{local/visitante}_pre` |
| Rendimiento | `xg_contra_media_fuera_5_{local/visitante}_pre` |
| Rendimiento | `sin_perder_proporcion_fuera_5_{local/visitante}_pre` |
| Calidad | `goles_menos_xg_media_5_{local/visitante}_pre` |
| Calidad | `goles_recibidos_menos_xga_media_5_{local/visitante}_pre` |
| Calidad | `xg_por_tiro_5_{local/visitante}_pre` |
| Calidad | `xga_por_tiro_recibido_5_{local/visitante}_pre` |
| Calidad | `tiros_a_puerta_proporcion_5_{local/visitante}_pre` |
| Calidad | `goles_por_tiro_5_{local/visitante}_pre` |
| Calidad | `goles_por_tiro_a_puerta_5_{local/visitante}_pre` |
| Calidad | `tiros_favor_media_5_{local/visitante}_pre` |
| Calidad | `tiros_contra_media_5_{local/visitante}_pre` |
| Disciplina | `faltas_media_10_{local/visitante}_pre` |
| Disciplina | `amarillas_media_10_{local/visitante}_pre` |
| Disciplina | `rojas_media_10_{local/visitante}_pre` |
| Disciplina | `corners_favor_media_10_{local/visitante}_pre` |
| Disciplina | `corners_contra_media_10_{local/visitante}_pre` |
| Disciplina | `partidos_con_roja_proporcion_10_{local/visitante}_pre` |
| Descanso | `goles_favor_descanso_media_10_{local/visitante}_pre` |
| Descanso | `goles_contra_descanso_media_10_{local/visitante}_pre` |
| Descanso | `ganando_descanso_proporcion_10_{local/visitante}_pre` |
| Descanso | `empatando_descanso_proporcion_10_{local/visitante}_pre` |
| Comparacion | `diferencia_puntos_5_pre` |
| Comparacion | `diferencia_puntos_10_pre` |
| Comparacion | `diferencia_puntos_por_partido_temporada_pre` |
| Comparacion | `diferencia_goles_favor_media_5_pre` |
| Comparacion | `diferencia_goles_contra_media_5_pre` |
| Comparacion | `diferencia_xg_favor_media_5_pre` |
| Comparacion | `diferencia_xg_contra_media_5_pre` |
| Comparacion | `diferencia_tiros_puerta_favor_media_5_pre` |
| Comparacion | `diferencia_corners_favor_media_10_pre` |
| Comparacion | `diferencia_dias_desde_ultimo_partido_liga_pre` |
| Comparacion | `suma_goles_favor_media_5_pre` |
| Comparacion | `suma_goles_contra_media_5_pre` |
| Comparacion | `suma_xg_favor_media_5_pre` |
| Comparacion | `suma_xg_contra_media_5_pre` |
| Comparacion | `elo_diferencia_ajustada_pre` |
| H2H | `h2h_partidos_previos_3_pre` |
| H2H | `h2h_puntos_equipo_local_3_pre` |
| H2H | `h2h_goles_totales_media_3_pre` |
| H2H | `h2h_dias_desde_ultimo_pre` |

## Comprobaciones

```bash
uv run pytest
uv run ruff check .
uv build
```

Los datos proceden principalmente de
[Football-Data.co.uk](https://www.football-data.co.uk/) y Understat
