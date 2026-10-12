from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd


INPUT_FILE = Path("data/raw/laliga_elo.csv")
OUTPUT_FILE = Path("data/processed/laliga_features.csv")

VENTAJA_LOCAL = 65.0


# Operaciones sobre partidos anteriores
def valor(numero):
    """Convierte un valor a decimal y conserva los datos ausentes como NaN."""
    if pd.isna(numero):
        return np.nan

    return float(numero)


def media(partidos, campo):
    """Calcula la media de un campo usando solo los valores disponibles."""
    valores = []

    for partido in partidos:
        if pd.notna(partido[campo]):
            valores.append(partido[campo])

    if not valores:
        return np.nan

    return float(np.mean(valores))


def proporcion(partidos, campos, condicion):
    """Calcula la proporción de partidos que cumplen una condición entre los que tienen los campos necesarios."""
    total_validos = 0
    total_cumplen = 0

    for partido in partidos:
        valido = True

        for campo in campos:
            if pd.isna(partido[campo]):
                valido = False
                break

        if valido:
            total_validos += 1

            if condicion(partido):
                total_cumplen += 1

    if total_validos == 0:
        return np.nan

    return total_cumplen / total_validos


def ratio(partidos, numerador, denominador):
    """Divide la suma del numerador entre la del denominador usando los mismos partidos válidos."""
    suma_numerador = 0
    suma_denominador = 0

    for partido in partidos:
        if pd.notna(partido[numerador]) and pd.notna(partido[denominador]):
            suma_numerador += partido[numerador]
            suma_denominador += partido[denominador]

    if suma_denominador == 0:
        return np.nan

    return suma_numerador / suma_denominador


def media_diferencia(partidos, campo_a, campo_b):
    """Calcula la media de las diferencias entre dos campos cuando ambos están disponibles."""
    diferencias = []

    for partido in partidos:
        if pd.notna(partido[campo_a]) and pd.notna(partido[campo_b]):
            diferencia = partido[campo_a] - partido[campo_b]
            diferencias.append(diferencia)

    if not diferencias:
        return np.nan

    return float(np.mean(diferencias))


def sumar_puntos(partidos):
    """Suma los puntos obtenidos en los partidos disponibles."""
    if not partidos:
        return np.nan

    puntos = 0

    for partido in partidos:
        puntos += partido["puntos"]

    return puntos


def contar_resultado(partidos, resultado):
    """Cuenta los partidos con un resultado concreto: victoria, empate o derrota."""
    if not partidos:
        return np.nan

    cantidad = 0

    for partido in partidos:
        if partido["resultado"] == resultado:
            cantidad += 1

    return cantidad


# Condiciones utilizadas para calcular proporciones
def porteria_cero(partido):
    """Indica si el equipo terminó el partido sin recibir goles."""
    return partido["gc"] == 0


def sin_marcar(partido):
    """Indica si el equipo terminó el partido sin marcar goles."""
    return partido["gf"] == 0


def ambos_marcan(partido):
    """Indica si los dos equipos marcaron al menos un gol."""
    return partido["gf"] > 0 and partido["gc"] > 0


def sin_perder(partido):
    """Indica si el equipo ganó o empató el partido."""
    return partido["gf"] >= partido["gc"]


def con_roja(partido):
    """Indica si el equipo recibió al menos una tarjeta roja."""
    return partido["rojas"] > 0


def ganando_descanso(partido):
    """Indica si el equipo iba ganando al descanso."""
    return partido["htgf"] > partido["htgc"]


def empatando_descanso(partido):
    """Indica si el equipo iba empatando al descanso."""
    return partido["htgf"] == partido["htgc"]


def proporcion_mas_goles(partidos, umbral):
    """Calculcula la proporción de partidos cuyos goles totales superan el umbral indicado."""
    total_validos = 0
    total_cumplen = 0

    for partido in partidos:
        if pd.notna(partido["gf"]) and pd.notna(partido["gc"]):
            total_validos += 1
            goles_totales = partido["gf"] + partido["gc"]

            if goles_totales > umbral:
                total_cumplen += 1

    if total_validos == 0:
        return np.nan

    return total_cumplen / total_validos


# Historial de cada equipo
def nuevo_estado():
    """Crea el historial reciente, los acumulados de temporada y la información de racha de un equipo."""
    return {
        "historial": deque(maxlen=10),
        "casa": deque(maxlen=5),
        "fuera": deque(maxlen=5),
        "temporada": [],
        "ultima_temporada": None,
        "ultima_fecha": None,
        "racha_tipo": None,
        "racha_longitud": 0,
    }


def iniciar_temporada(estados, equipos, anio):
    """Reinicia los acumulados de temporada y borra la forma reciente de los equipos que estuvieron fuera de Primera."""
    for equipo in equipos:
        if equipo not in estados:
            estados[equipo] = nuevo_estado()

        estado = estados[equipo]

        # Reiniciar la forma si estuvo fuera de Primera
        if estado["ultima_temporada"] != anio - 1:
            estado["historial"].clear()
            estado["casa"].clear()
            estado["fuera"].clear()
            estado["racha_tipo"] = None
            estado["racha_longitud"] = 0

        # Reiniciar los acumulados de temporada
        estado["temporada"] = []
        estado["ultima_temporada"] = anio


def registro_equipo(partido, es_local):
    """Organiza las estadísticas de un partido desde el punto de vista de un equipo y calcula su resultado y sus puntos."""
    if es_local:
        lado = "local"
        rival = "visitante"
    else:
        lado = "visitante"
        rival = "local"

    gf = valor(partido[f"goles_{lado}"])
    gc = valor(partido[f"goles_{rival}"])

    if gf > gc:
        resultado = "V"
        puntos = 3
    elif gf < gc:
        resultado = "D"
        puntos = 0
    else:
        resultado = "E"
        puntos = 1

    registro = {
        "fecha": partido["fecha_partido"],
        "es_local": es_local,
        "gf": gf,
        "gc": gc,
        "resultado": resultado,
        "puntos": puntos,
        "elo_rival": valor(partido[f"elo_{rival}_pre"]),
    }

    campos = {
        "xgf": f"goles_esperados_{lado}",
        "xga": f"goles_esperados_{rival}",
        "tiros_favor": f"tiros_{lado}",
        "tiros_contra": f"tiros_{rival}",
        "puerta_favor": f"tiros_a_puerta_{lado}",
        "puerta_contra": f"tiros_a_puerta_{rival}",
        "faltas": f"faltas_cometidas_{lado}",
        "amarillas": f"tarjetas_amarillas_{lado}",
        "rojas": f"tarjetas_rojas_{lado}",
        "corners_favor": f"corners_{lado}",
        "corners_contra": f"corners_{rival}",
        "htgf": f"goles_{lado}_descanso",
        "htgc": f"goles_{rival}_descanso",
    }

    for campo, columna in campos.items():
        registro[campo] = valor(partido[columna])

    return registro


# Métricas individuales
def metricas_equipo(estado, fecha):
    """Calcula la forma reciente, las medias, las proporciones, las rachas y los días desde el último partido de liga."""
    historial = list(estado["historial"])

    ventanas = {
        3: historial[-3:],
        5: historial[-5:],
        10: historial[-10:],
    }

    ultimos5 = ventanas[5]
    ultimos10 = ventanas[10]

    casa = list(estado["casa"])
    fuera = list(estado["fuera"])
    temporada = estado["temporada"]

    casa_temporada = []
    fuera_temporada = []

    for partido in temporada:
        if partido["es_local"]:
            casa_temporada.append(partido)
        else:
            fuera_temporada.append(partido)

    if historial:
        racha_longitud = estado["racha_longitud"]
    else:
        racha_longitud = np.nan

    if estado["ultima_fecha"] is None:
        dias_desde_ultimo = np.nan
    else:
        dias_desde_ultimo = (fecha - estado["ultima_fecha"]).days

    metricas = {
        "partidos_previos_5": len(ultimos5),
        "partidos_previos_10": len(ultimos10),
        "partidos_temporada": len(temporada),
        "partidos_casa_temporada": len(casa_temporada),
        "partidos_fuera_temporada": len(fuera_temporada),
        "partidos_casa_5": len(casa),
        "partidos_fuera_5": len(fuera),
        "racha_tipo": estado["racha_tipo"],
        "racha_longitud": racha_longitud,
        "puntos_por_partido_temporada": media(temporada, "puntos"),
        "puntos_por_partido_casa_temporada": media(casa_temporada, "puntos"),
        "puntos_por_partido_fuera_temporada": media(fuera_temporada, "puntos"),
        "dias_desde_ultimo_partido_liga": dias_desde_ultimo,
    }

    # Puntos en los últimos 3, 5 y 10 partidos
    for n in (3, 5, 10):
        metricas[f"puntos_{n}"] = sumar_puntos(ventanas[n])

    metricas["victorias_5"] = contar_resultado(ultimos5, "V")
    metricas["empates_5"] = contar_resultado(ultimos5, "E")

    # Goles, xG y tiros a puerta
    campos = [
        ("goles_favor", "gf"),
        ("goles_contra", "gc"),
        ("xg_favor", "xgf"),
        ("xg_contra", "xga"),
        ("tiros_puerta_favor", "puerta_favor"),
        ("tiros_puerta_contra", "puerta_contra"),
    ]

    for n in (5, 10):
        partidos = ventanas[n]

        for nombre, campo in campos:
            metricas[f"{nombre}_media_{n}"] = media(partidos, campo)

        partidos_con_xg = 0

        for partido in partidos:
            if pd.notna(partido["xgf"]) and pd.notna(partido["xga"]):
                partidos_con_xg += 1

        metricas[f"partidos_con_xg_{n}"] = partidos_con_xg
        metricas[f"elo_medio_rivales_{n}"] = media(partidos, "elo_rival")

    # Porterías a cero y partidos sin marcar
    metricas["porterias_cero_proporcion_10"] = proporcion(ultimos10, ["gc"], porteria_cero)
    metricas["sin_marcar_proporcion_10"] = proporcion(ultimos10, ["gf"], sin_marcar)

    # Partidos que superan cada umbral de goles
    for umbral in (1.5, 2.5, 3.5):
        nombre = str(umbral).replace(".", "_")
        metricas[f"mas_{nombre}_goles_proporcion_10"] = proporcion_mas_goles(ultimos10, umbral)

    metricas["ambos_marcan_proporcion_10"] = proporcion(ultimos10, ["gf", "gc"], ambos_marcan)

    # Rendimiento en casa y fuera
    grupos = {
        "casa": casa,
        "fuera": fuera,
    }

    campos = [
        ("goles_favor", "gf"),
        ("goles_contra", "gc"),
        ("xg_favor", "xgf"),
        ("xg_contra", "xga"),
    ]

    for condicion, partidos in grupos.items():
        for nombre, campo in campos:
            metricas[f"{nombre}_media_{condicion}_5"] = media(partidos, campo)

        metricas[f"sin_perder_proporcion_{condicion}_5"] = proporcion(partidos, ["gf", "gc"], sin_perder)

    # Diferencia entre goles reales y esperados
    metricas["goles_menos_xg_media_5"] = media_diferencia(ultimos5, "gf", "xgf")
    metricas["goles_recibidos_menos_xga_media_5"] = media_diferencia(ultimos5, "gc", "xga")

    # Calidad de ocasiones y efectividad
    ratios = [
        ("xg_por_tiro_5", "xgf", "tiros_favor"),
        ("xga_por_tiro_recibido_5", "xga", "tiros_contra"),
        ("tiros_a_puerta_proporcion_5", "puerta_favor", "tiros_favor"),
        ("goles_por_tiro_5", "gf", "tiros_favor"),
        ("goles_por_tiro_a_puerta_5", "gf", "puerta_favor"),
    ]

    for nombre, numerador, denominador in ratios:
        metricas[nombre] = ratio(ultimos5, numerador, denominador)

    metricas["tiros_favor_media_5"] = media(ultimos5, "tiros_favor")
    metricas["tiros_contra_media_5"] = media(ultimos5, "tiros_contra")

    # Disciplina y córneres
    for campo in ("faltas", "amarillas", "rojas", "corners_favor", "corners_contra"):
        metricas[f"{campo}_media_10"] = media(ultimos10, campo)

    metricas["partidos_con_roja_proporcion_10"] = proporcion(ultimos10, ["rojas"], con_roja)

    # Primera parte
    metricas["goles_favor_descanso_media_10"] = media(ultimos10, "htgf")
    metricas["goles_contra_descanso_media_10"] = media(ultimos10, "htgc")
    metricas["ganando_descanso_proporcion_10"] = proporcion(ultimos10, ["htgf", "htgc"], ganando_descanso)
    metricas["empatando_descanso_proporcion_10"] = proporcion(ultimos10, ["htgf", "htgc"], empatando_descanso)

    return metricas


# Comparaciones entre los dos equipos
def metricas_comparacion(local, visitante, partido):
    """Calcula diferencias y sumas entre las métricas de los equipos, además de la diferencia Elo ajustada por localía."""
    metricas = {}

    campos = [
        "puntos_5",
        "puntos_10",
        "puntos_por_partido_temporada",
        "goles_favor_media_5",
        "goles_contra_media_5",
        "xg_favor_media_5",
        "xg_contra_media_5",
        "tiros_puerta_favor_media_5",
        "corners_favor_media_10",
        "dias_desde_ultimo_partido_liga",
    ]

    for campo in campos:
        metricas[f"diferencia_{campo}_pre"] = local[campo] - visitante[campo]

    for campo in ("goles_favor_media_5", "goles_contra_media_5", "xg_favor_media_5", "xg_contra_media_5"):
        metricas[f"suma_{campo}_pre"] = local[campo] + visitante[campo]

    metricas["elo_diferencia_ajustada_pre"] = partido["elo_local_pre"] - partido["elo_visitante_pre"] + VENTAJA_LOCAL

    return metricas


# Últimos tres enfrentamientos directos
def metricas_h2h(historial, equipo_local, fecha):
    """Calcula los puntos del actual equipo local, la media de goles y los días desde el último enfrentamiento directo."""
    partidos = list(historial)

    puntos = 0
    goles_totales = []

    for partido in partidos:
        if partido["local"] == equipo_local:
            puntos += partido["puntos_local"]
        else:
            puntos += partido["puntos_visitante"]

        goles_totales.append(partido["goles_totales"])

    if partidos:
        media_goles = float(np.mean(goles_totales))
        dias_desde_ultimo = (fecha - partidos[-1]["fecha"]).days
    else:
        puntos = np.nan
        media_goles = np.nan
        dias_desde_ultimo = np.nan

    return {
        "h2h_partidos_previos_3_pre": len(partidos),
        "h2h_puntos_equipo_local_3_pre": puntos,
        "h2h_goles_totales_media_3_pre": media_goles,
        "h2h_dias_desde_ultimo_pre": dias_desde_ultimo,
    }


def actualizar_equipo(estado, registro):
    """Añade un partido terminado al historial del equipo y actualiza su última fecha y su racha."""
    estado["historial"].append(registro)

    if registro["es_local"]:
        estado["casa"].append(registro)
    else:
        estado["fuera"].append(registro)

    estado["temporada"].append(registro)
    estado["ultima_fecha"] = registro["fecha"]

    if estado["racha_tipo"] == registro["resultado"]:
        estado["racha_longitud"] += 1
    else:
        estado["racha_tipo"] = registro["resultado"]
        estado["racha_longitud"] = 1


# Cálculo del dataset completo
def calcular_metricas(df):
    """Calcula todas las variables prepartido usando únicamente los encuentros de fechas anteriores."""
    df = df.copy()
    df["fecha_partido"] = pd.to_datetime(df["fecha_partido"])
    df = df.sort_values(["fecha_partido", "equipo_local", "equipo_visitante"]).reset_index(drop=True)

    estados = {}
    enfrentamientos = {}
    filas = {}

    for temporada, partidos_temporada in df.groupby("temporada", sort=True):
        equipos = set(partidos_temporada["equipo_local"])
        equipos.update(partidos_temporada["equipo_visitante"])

        anio = int(temporada.split("/")[0])
        iniciar_temporada(estados, equipos, anio)

        for fecha, partidos_dia in partidos_temporada.groupby("fecha_partido", sort=True):
            # Calcular primero con el historial anterior al día
            for indice, partido in partidos_dia.iterrows():
                local = partido["equipo_local"]
                visitante = partido["equipo_visitante"]

                metricas_local = metricas_equipo(estados[local], fecha)
                metricas_visitante = metricas_equipo(estados[visitante], fecha)

                fila = {}

                for campo, numero in metricas_local.items():
                    fila[f"{campo}_local_pre"] = numero

                for campo, numero in metricas_visitante.items():
                    fila[f"{campo}_visitante_pre"] = numero

                comparaciones = metricas_comparacion(metricas_local, metricas_visitante, partido)
                fila.update(comparaciones)

                clave_h2h = tuple(sorted((local, visitante)))
                historial_h2h = enfrentamientos.get(clave_h2h, ())

                h2h = metricas_h2h(historial_h2h, local, fecha)
                fila.update(h2h)

                filas[indice] = fila

            # Incorporar después los resultados del día
            for _, partido in partidos_dia.iterrows():
                local = partido["equipo_local"]
                visitante = partido["equipo_visitante"]

                registro_local = registro_equipo(partido, True)
                registro_visitante = registro_equipo(partido, False)

                actualizar_equipo(estados[local], registro_local)
                actualizar_equipo(estados[visitante], registro_visitante)

                clave_h2h = tuple(sorted((local, visitante)))

                if clave_h2h not in enfrentamientos:
                    enfrentamientos[clave_h2h] = deque(maxlen=3)

                enfrentamientos[clave_h2h].append({
                    "fecha": fecha,
                    "local": local,
                    "goles_totales": registro_local["gf"] + registro_local["gc"],
                    "puntos_local": registro_local["puntos"],
                    "puntos_visitante": registro_visitante["puntos"],
                })

    metricas = pd.DataFrame.from_dict(filas, orient="index").reindex(df.index)

    # Reemplazar las métricas si ya existían
    df = df.drop(columns=metricas.columns, errors="ignore")

    return pd.concat([df, metricas], axis=1)


def main():
    """Lee el CSV con Elo, calcula las variables prepartido y guarda el archivo final."""
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    df = calcular_metricas(df)

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")

    print(f"Archivo generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()