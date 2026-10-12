import json
import re
import unicodedata
from datetime import date
from io import StringIO
from os import getenv
from pathlib import Path
from typing import Any


import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

ANIO_INICIO = int(getenv("ANIO_INICIO", "2014"))
FECHA_INICIO = pd.Timestamp(f"{ANIO_INICIO}-07-01")
FECHA_FIN = pd.Timestamp(date.today())
OUTPUT_FILE = Path("data/raw/laliga.csv")

COLUMNAS = {
    "Date": "fecha_partido",
    "Time": "hora_inicio",
    "HomeTeam": "equipo_local",
    "AwayTeam": "equipo_visitante",
    "FTHG": "goles_local",
    "FTAG": "goles_visitante",
    "FTR": "resultado_final",
    "HTHG": "goles_local_descanso",
    "HTAG": "goles_visitante_descanso",
    "HTR": "resultado_descanso",
    "HxG": "goles_esperados_local",
    "AxG": "goles_esperados_visitante",
    "HS": "tiros_local",
    "AS": "tiros_visitante",
    "HST": "tiros_a_puerta_local",
    "AST": "tiros_a_puerta_visitante",
    "HF": "faltas_cometidas_local",
    "AF": "faltas_cometidas_visitante",
    "HC": "corners_local",
    "AC": "corners_visitante",
    "HY": "tarjetas_amarillas_local",
    "AY": "tarjetas_amarillas_visitante",
    "HR": "tarjetas_rojas_local",
    "AR": "tarjetas_rojas_visitante",
}

NUMERICAS = [
    "FTHG", "FTAG", "HTHG", "HTAG", "HxG", "AxG",
    "HS", "AS", "HST", "AST", "HF", "AF",
    "HC", "AC", "HY", "AY", "HR", "AR",
]

OBLIGATORIAS = [
    "Date", "HomeTeam", "AwayTeam",
    "FTHG", "FTAG", "FTR",
]

EQUIVALENCIAS = {
    "ath bilbao": "athletic bilbao",
    "athletic club": "athletic bilbao",
    "athletic club bilbao": "athletic bilbao",
    "ath madrid": "atletico madrid",
    "atletico de madrid": "atletico madrid",
    "sociedad": "real sociedad",
    "la coruna": "deportivo la coruna",
    "deportivo de la coruna": "deportivo la coruna",
    "sp gijon": "sporting gijon",
    "sporting de gijon": "sporting gijon",
    "espanol": "espanyol",
    "rcd espanyol": "espanyol",
    "vallecano": "rayo vallecano",
    "betis": "real betis",
    "real betis balompie": "real betis",
    "celta vigo": "celta",
    "celta de vigo": "celta",
    "deportivo alaves": "alaves",
    "real valladolid": "valladolid",
    "ud las palmas": "las palmas",
    "sd eibar": "eibar",
    "sd huesca": "huesca",
    "real oviedo": "oviedo",
    "rcd mallorca": "mallorca",
    "sevilla fc": "sevilla",
    "fc barcelona": "barcelona",
}


def descargar_texto(url: str, sesion: requests.Session) -> str:
    """Descarga el contenido de la URL y lo devuelve como texto."""
    respuesta = sesion.get(url, timeout=60)
    respuesta.raise_for_status()
    return respuesta.text


def normalizar_equipo(nombre: object) -> str:
    """Convierte el nombre del equipo a minúsculas y sin acentos."""
    nombre = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode()

    nombre = re.sub(r"[^a-z0-9]+", " ", nombre.lower()).strip()

    return EQUIVALENCIAS.get(nombre, nombre)


def descargar_temporada(anio: int, sesion: requests.Session) -> pd.DataFrame:
    codigo = f"{anio % 100:02d}{(anio + 1) % 100:02d}"
    url = f"https://www.football-data.co.uk/mmz4281/{codigo}/SP1.csv"

    df = pd.read_csv(StringIO(descargar_texto(url, sesion)))
    df.columns = df.columns.str.strip()
    df = df.dropna(how="all")

    faltantes = set(OBLIGATORIAS) - set(df.columns)
    if faltantes:
        raise ValueError(f"{anio}/{anio + 1}: faltan {sorted(faltantes)}")

    # Conservar las columnas elegidas y limpiar espacios
    df = df.reindex(columns=list(COLUMNAS)).astype("string")

    for columna in df.columns:
        df[columna] = (df[columna].str.strip().replace("", pd.NA))

    # Admitir años de dos o cuatro cifras
    fechas = df["Date"]
    df["Date"] = pd.to_datetime(
        fechas, format="%d/%m/%Y", errors="coerce").fillna(
        pd.to_datetime(
            fechas, format="%d/%m/%y", errors="coerce"
        )
    )

    if df["Date"].isna().any():
        raise ValueError(f"{anio}: hay fechas inválidas.")

    for columna in NUMERICAS:
        df[columna] = pd.to_numeric(df[columna])

    for columna in ["FTR", "HTR"]:
        df[columna] = df[columna].str.upper()

    df = df.loc[df["Date"].between(FECHA_INICIO, FECHA_FIN)].copy()


    if df[OBLIGATORIAS].isna().any().any():
        raise ValueError(f"{anio}: hay datos esenciales incompletos.")

    df.insert(0, "temporada", f"{anio}/{anio + 1}")
    return df


def descargar_xg(anio: int,sesion: requests.Session) -> dict[tuple[pd.Timestamp, str, str], dict[str, Any]]:
    pagina_url = f"https://understat.com/league/La_liga/{anio}"

    respuesta = sesion.get(
        f"https://understat.com/getLeagueData/La%20liga/{anio}",
        headers={
            "Referer": pagina_url,
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=60,
    )
    respuesta.raise_for_status()
    partidos = respuesta.json()["dates"]

    indice = {}

    for partido in partidos:
        goles = partido.get("goals") or {}
        xg = partido.get("xG") or {}

        valores = [goles.get("h"), goles.get("a"), xg.get("h"), xg.get("a")]
        if any(valor in (None, "") for valor in valores):
            continue

        clave = (
            pd.Timestamp(partido["datetime"]).normalize(),
            normalizar_equipo(partido["h"]["title"]),
            normalizar_equipo(partido["a"]["title"]),
        )

        xg_local = float(xg["h"])
        xg_visitante = float(xg["a"])

        indice[clave] = {
            "goles_local": int(goles["h"]),
            "goles_visitante": int(goles["a"]),
            "xg_local": xg_local,
            "xg_visitante": xg_visitante,
        }

    return indice


def enriquecer_xg(df: pd.DataFrame, sesion: requests.Session) -> pd.DataFrame: 
    for temporada, grupo in df.groupby("temporada"):
        pendientes = grupo.loc[
            grupo[["HxG", "AxG"]].isna().all(axis=1)
        ]

        if pendientes.empty:
            continue

        partidos = descargar_xg(int(temporada.split("/")[0]), sesion)

        for indice, fila in pendientes.iterrows():
            fecha = fila["Date"].normalize()
            local = normalizar_equipo(fila["HomeTeam"])
            visitante = normalizar_equipo(fila["AwayTeam"])

            partido = partidos.get((fecha, local, visitante))

            # Buscar a ±1 día si no coincide la fecha exacta
            if partido is None:
                candidatos = [
                    datos
                    for clave, datos in partidos.items()
                    if (
                        clave[1] == local
                        and clave[2] == visitante
                        and abs(clave[0] - fecha) <= pd.Timedelta(days=1)
                        and datos["goles_local"] == fila["FTHG"]
                        and datos["goles_visitante"] == fila["FTAG"]
                    )
                ]

                if len(candidatos) != 1:
                    continue

                partido = candidatos[0]

            # Comprobar también el marcador de las coincidencias exactas
            if (
                partido["goles_local"] != fila["FTHG"]
                or partido["goles_visitante"] != fila["FTAG"]
            ):
                continue

            df.at[indice, "HxG"] = partido["xg_local"]
            df.at[indice, "AxG"] = partido["xg_visitante"]

    return df


def descargar_dataset() -> pd.DataFrame:
    ultima_temporada = (
        FECHA_FIN.year
        if FECHA_FIN.month >= 8
        else FECHA_FIN.year - 1
    )

    if not 2014 <= ANIO_INICIO <= ultima_temporada:
        raise ValueError("ANIO_INICIO está fuera del intervalo válido.")

    with requests.Session() as sesion:
        datasets = []

        for anio in range(ANIO_INICIO, ultima_temporada + 1):
            temporada = descargar_temporada(anio, sesion)
            datasets.append(temporada)
            print(f"{anio}/{anio + 1}: {len(temporada)} partidos")

        df = pd.concat(datasets, ignore_index=True)

        print("\nObteniendo goles esperados de Understat...")
        df = enriquecer_xg(df, sesion)

    completos = df[["HxG", "AxG"]].notna().all(axis=1)

    for columna in NUMERICAS:
        if columna not in ["HxG", "AxG"]:
            df[columna] = df[columna].astype("Int64")

    # Mantener las fechas y nombres originales de Football-Data
    df = df.sort_values(["Date", "HomeTeam", "AwayTeam"]).reset_index(drop=True)

    df = df.rename(columns=COLUMNAS)

    print(f"\nPartidos con ambos xG: {completos.sum()} de {len(df)}")
    print(f"Partidos pendientes de xG: {(~completos).sum()}")

    return df


def main() -> None:
    df = descargar_dataset()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, date_format="%Y-%m-%d")

    print(f"Archivo generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()