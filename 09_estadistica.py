"""
Ejercicio 9 — Estadística de una serie
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA
Materia: Programación

Consigna:
Escribir:
a) resumen(valores): Retorna un diccionario con 'n', 'minimo', 'maximo', 'promedio'
   y 'desvio' (desvío estándar muestral dividiendo por n - 1), o None si la lista está vacía.
   Si la lista tiene un único elemento, el desvío es 0.0.
b) fuera_de_rango(valores, minimo, maximo): Retorna una lista con las posiciones
   (índices) de los valores que caen estrictamente fuera del intervalo [minimo, maximo].
   Los dos extremos cuentan como adentro.

Control con la serie real de mediciones.log (pág. 13):
Corriendo resumen sobre la serie CH1 FREQ, el promedio debe diferir en menos
del 0.5% respecto a 1000 Hz, y el desvío estándar debe ser menor a 5 Hz.
"""

import math


def resumen(valores):
    """
    Calcula estadísticos descriptivos básicos sobre una muestra de datos numéricos.

    Fórmulas matemáticas:
        - Promedio (media aritmética): sum(valores) / n
        - Desvío estándar muestral: sqrt( sum((v - promedio)^2) / (n - 1) )
          (Se divide por n - 1 según la corrección de Bessel para muestras estadísticas).

    Parámetros:
        valores (list): Lista de valores numéricos de tipo float o int.

    Retorna:
        dict: Diccionario con las claves:
              {
                  'n': int,        # Cantidad de muestras válidas
                  'minimo': float, # Menor valor registrado en la serie
                  'maximo': float, # Mayor valor registrado en la serie
                  'promedio': float, # Media aritmética muestral
                  'desvio': float  # Desvío estándar muestral
              }
        None: Si la lista está vacía o el parámetro es nulo.

    Caso particular:
        Si n == 1, la fórmula dividiría por (1 - 1 = 0). En ese caso se asigna
        por definición un desvío estándar de 0.0 según lo estipulado en la consigna.
    """
    if not valores:
        return None

    n = len(valores)
    minimo = min(valores)
    maximo = max(valores)
    promedio = sum(valores) / n

    if n == 1:
        desvio = 0.0
    else:
        varianza = sum((v - promedio) ** 2 for v in valores) / (n - 1)
        desvio = math.sqrt(varianza)

    return {
        "n": n,
        "minimo": minimo,
        "maximo": maximo,
        "promedio": promedio,
        "desvio": desvio,
    }


def fuera_de_rango(valores, minimo, maximo):
    """
    Identifica las posiciones (índices 0-based) de aquellos valores que caen
    fuera del intervalo cerrado [minimo, maximo].

    Regla:
        Los extremos están incluidos en el rango válido.
        Un elemento en la posición i está fuera de rango si:
            valores[i] < minimo  o  valores[i] > maximo

    Parámetros:
        valores (list): Lista de valores numéricos.
        minimo (float): Límite inferior permitido.
        maximo (float): Límite superior permitido.

    Retorna:
        list: Lista de enteros con las posiciones de los elementos anómalos.
    """
    if not valores:
        return []

    return [i for i, v in enumerate(valores) if v < minimo or v > maximo]


# -----------------------------------------------------------------------------
# Bloque de Pruebas Unitarias (asserts)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import os

    # 1. Pruebas de resumen con una serie conocida: [2, 4, 4, 4, 5, 5, 7, 9]
    # n = 8, suma = 40 -> promedio = 5.0
    # suma de cuadrados respecto a la media = (2-5)^2 + 3*(4-5)^2 + 2*(5-5)^2 + (7-5)^2 + (9-5)^2
    #                                       = 9 + 3 + 0 + 4 + 16 = 32
    # varianza muestral = 32 / (8 - 1) = 32 / 7 ≈ 4.571428...
    # desvío = sqrt(32 / 7) ≈ 2.1380899...
    datos = [2, 4, 4, 4, 5, 5, 7, 9]
    res = resumen(datos)
    assert res["n"] == 8, "La cantidad de elementos debe ser 8"
    assert res["minimo"] == 2, "El mínimo debe ser 2"
    assert res["maximo"] == 9, "El máximo debe ser 9"
    assert res["promedio"] == 5.0, "El promedio debe ser 5.0"
    assert abs(res["desvio"] - math.sqrt(32 / 7)) < 1e-6, "El desvío estándar muestral no coincide"

    # 2. Caso con un único elemento (debe dar desvío 0.0 sin lanzar ZeroDivisionError)
    res_uno = resumen([42.0])
    assert res_uno["n"] == 1
    assert res_uno["minimo"] == 42.0
    assert res_uno["maximo"] == 42.0
    assert res_uno["promedio"] == 42.0
    assert res_uno["desvio"] == 0.0, "Para n=1 el desvío estándar debe ser exactamente 0.0"

    # 3. Caso raro: Lista vacía o None
    assert resumen([]) is None, "Una lista vacía debe retornar None"
    assert resumen(None) is None, "None debe retornar None"

    # 4. Pruebas de la función fuera_de_rango:
    vals = [10.0, 20.0, 5.0, 30.0, 45.0, 15.0]
    # Evaluamos intervalo [10.0, 30.0]:
    # 10.0 y 30.0 son los extremos (adentro).
    # 5.0 está fuera (índice 2) y 45.0 está fuera (índice 4).
    pos_fuera = fuera_de_rango(vals, 10.0, 30.0)
    assert pos_fuera == [2, 4], f"Posiciones fuera de rango inesperadas: {pos_fuera}"

    # Todos los valores dentro del rango
    assert fuera_de_rango([10, 20, 30], 10, 30) == [], "Si todos están adentro la lista debe ser vacía"
    # Lista vacía
    assert fuera_de_rango([], 10, 30) == []

    # 5. CONTROL CON LA SERIE DE VERDAD (consigna pág. 13):
    # Procesamos la serie CH1 FREQ de mediciones.log:
    # El promedio debe caer a menos del 0.5% de 1000 Hz
    # El desvío debe ser menor que 5 Hz.
    if os.path.exists("mediciones.log"):
        leer_log = __import__("08_log").leer_log
        series, _ = leer_log("mediciones.log")

        serie_frec_ch1 = series[("ADS3202", "CH1", "FREQ")]
        res_ch1_freq = resumen(serie_frec_ch1)

        error_rel_promedio = abs(res_ch1_freq["promedio"] - 1000.0) / 1000.0
        assert error_rel_promedio < 0.005, f"El promedio se desvió más del 0.5%: {error_rel_promedio * 100:.2f}%"
        assert res_ch1_freq["desvio"] < 5.0, f"El desvío es mayor a 5 Hz: {res_ch1_freq['desvio']}"

    print("09_estadistica.py: Todas las pruebas pasaron correctamente (OK).")
