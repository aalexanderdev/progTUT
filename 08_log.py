"""
Ejercicio 8 — El registro de la sesión
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA
Materia: Programación

Consigna:
Procesar el archivo de registro histórico 'mediciones.log'.
Cada línea representa una medición con 6 campos:
  fecha hora equipo canal magnitud valor
  Ejemplo: 2026-09-08 09:14:02 ADS3202 CH1 FREQ 1.000431E+03

Escribir:
a) analizar_linea(linea): Retorna el par (medicion, motivo). Uno de los dos siempre es None.
   - Si la línea es válida: (dict_medicion, None)
   - Si se rechaza: (None, motivo_error)
   - Si se ignora (en blanco o inicia con '#'): (None, None)
b) leer_log(ruta): Recorre el archivo y devuelve las series de valores agrupadas por
   (equipo, canal, magnitud), más la lista de líneas rechazadas con motivo y número de línea.

Atención especial: "Hay una línea que parece rota y no lo está" (pág. 13):
Existe una línea separada por tabulaciones ('\\t') en lugar de espacios.
linea.split() sin argumentos separa por cualquier espacio en blanco (incluyendo tabs),
mientras que split(" ") la descartaría erróneamente.
"""

import math

a_numero = __import__("02_magnitudes").a_numero


def analizar_linea(linea):
    """
    Analiza y valida sintáctica y semánticamente una línea del archivo de log.

    Reglas de clasificación:
      1. Se ignora:
         - Línea en blanco o que contiene únicamente espacios.
         - Línea que inicia con el carácter '#' (comentarios de encabezado).
      2. Se rechaza:
         - Línea que no tiene exactamente seis campos.
         - Hora imposible (formato distinto a HH:MM:SS o valores fuera del rango 00:00:00 - 23:59:59).
         - Canal no reconocido (distinto a 'CH1' y 'CH2').
         - Magnitud no admitida (distinta a 'FREQ', 'PKPK' y 'CYCRMS').
         - Valor no convertible a número real o valor 'NaN' / 'Inf'.

    Parámetros:
        linea (str): Línea de texto cruda leída del archivo.

    Retorna:
        tuple: (medicion, motivo)
               - Si válida: ({fecha, hora, equipo, canal, magnitud, valor}, None)
               - Si rechazada: (None, "Motivo del rechazo")
               - Si ignorada: (None, None)
    """
    if linea is None:
        return (None, "Línea nula")

    # 1. Detección de líneas ignoradas: vacías o comentarios con '#'
    texto = linea.strip()
    if not texto or texto.startswith("#"):
        return (None, None)

    # 2. Separación de campos:
    # linea.split() agrupa cualquier secuencia de espacios o tabulaciones (\t),
    # capturando de forma transparente la línea con tabs del archivo.
    partes = linea.split()
    if len(partes) != 6:
        return (None, "No tiene exactamente seis campos")

    fecha, hora, equipo, canal, magnitud, valor_str = partes

    # 3. Validación de hora estricta (HH:MM:SS)
    partes_hora = hora.split(":")
    if len(partes_hora) != 3:
        return (None, "Hora imposible")
    try:
        h = int(partes_hora[0])
        m = int(partes_hora[1])
        s = int(partes_hora[2])
    except ValueError:
        return (None, "Hora imposible")

    if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59):
        return (None, "Hora imposible")

    # 4. Validación de canal (únicamente canales del ADS3202: CH1 o CH2)
    if canal not in ("CH1", "CH2"):
        return (None, "Canal que no es CH1 ni CH2")

    # 5. Validación de magnitud
    if magnitud not in ("FREQ", "PKPK", "CYCRMS"):
        return (None, "Magnitud que no es FREQ, PKPK ni CYCRMS")

    # 6. Validación de valor numérico:
    # Se descartan cadenas con coma decimal, texto arbitrario y valores 'NaN' (Línea 65 del log)
    try:
        valor = float(valor_str)
        if math.isnan(valor) or math.isinf(valor):
            return (None, "Valor que no se puede convertir a número")
    except ValueError:
        return (None, "Valor que no se puede convertir a número")

    # Si cumple todas las condiciones, se retorna la medición estructurada
    medicion = {
        "fecha": fecha,
        "hora": hora,
        "equipo": equipo,
        "canal": canal,
        "magnitud": magnitud,
        "valor": valor,
    }
    return (medicion, None)


def leer_log(ruta):
    """
    Lee y procesa un archivo de log de sesiones de laboratorio.

    Parámetros:
        ruta (str): Ruta al archivo de texto (ej. "mediciones.log").

    Retorna:
        tuple: (series, rechazadas)
            - series (dict): Diccionario cuyas claves son tuplas (equipo, canal, magnitud)
                             y sus valores son listas de flotantes [valor1, valor2, ...].
            - rechazadas (list): Lista de diccionarios para cada línea descartada:
                                 {'linea': int, 'motivo': str, 'texto': str}.
    """
    series = {}
    rechazadas = []

    with open(ruta, "r", encoding="utf-8") as archivo:
        for num_linea, linea in enumerate(archivo, start=1):
            medicion, motivo = analizar_linea(linea)

            if medicion is None and motivo is None:
                # Comentario o línea en blanco: se ignora sin registrar rechazo
                continue
            elif motivo is not None:
                # Línea anómala: se documenta en la lista de rechazadas
                rechazadas.append({
                    "linea": num_linea,
                    "motivo": motivo,
                    "texto": linea.strip(),
                })
            else:
                # Línea válida: se acumula el valor en la serie correspondiente
                clave = (medicion["equipo"], medicion["canal"], medicion["magnitud"])
                if clave not in series:
                    series[clave] = []
                series[clave].append(medicion["valor"])

    return series, rechazadas


# -----------------------------------------------------------------------------
# Bloque de Pruebas Unitarias (asserts)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import os

    # 1. Pruebas unitarias de analizar_linea:
    # Línea válida normal
    linea_ok = "2026-09-08 09:14:02 ADS3202 CH1 FREQ 1.000431E+03\n"
    med, mot = analizar_linea(linea_ok)
    assert mot is None, "Una línea bien formada no debe reportar motivo de rechazo"
    assert med["canal"] == "CH1" and med["magnitud"] == "FREQ"
    assert abs(med["valor"] - 1000.431) < 1e-3

    # Línea separada por tabulaciones (caso específico de la consigna pág. 13)
    linea_tab = "2026-09-08\t09:17:31\tADS3202\tCH1\tFREQ\t1.001000E+03\n"
    med_tab, mot_tab = analizar_linea(linea_tab)
    assert mot_tab is None, "La línea con tabulaciones debe aceptarse como dato válido"
    assert med_tab["valor"] == 1001.0

    # Líneas a IGNORAR (ambos componentes del par deben ser None)
    assert analizar_linea("") == (None, None), "Línea vacía debe ignorarse"
    assert analizar_linea("   \n") == (None, None), "Línea de solo espacios debe ignorarse"
    assert analizar_linea("# Encabezado informativo") == (None, None), "Línea de comentario debe ignorarse"

    # Líneas a RECHAZAR por regla:
    # Cantidad de campos incorrecta
    _, mot1 = analizar_linea("2026-09-08 09:14:31 ADS3202 CH1 FREQ ERROR: comando desconocido")
    assert mot1 == "No tiene exactamente seis campos"

    # Hora imposible (25:61:00)
    _, mot2 = analizar_linea("2026-09-08 25:61:00 ADS3202 CH2 FREQ 2.500000E+03")
    assert mot2 == "Hora imposible"

    # Canal que no es CH1 ni CH2 (CH3)
    _, mot3 = analizar_linea("2026-09-08 09:16:31 ADS3202 CH3 FREQ 1.000000E+03")
    assert mot3 == "Canal que no es CH1 ni CH2"

    # Magnitud que no es FREQ, PKPK ni CYCRMS (TEMP)
    _, mot4 = analizar_linea("2026-09-08 09:17:01 ADS3202 CH1 TEMP 3.150000E+02")
    assert mot4 == "Magnitud que no es FREQ, PKPK ni CYCRMS"

    # Valor no convertible a número (coma decimal en lugar de punto)
    _, mot5 = analizar_linea("2026-09-08 09:15:31 ADS3202 CH1 PKPK 2,003812")
    assert mot5 == "Valor que no se puede convertir a número"

    # Valor NaN (Línea 65 del archivo real)
    _, mot6 = analizar_linea("2026-09-08 09:16:01 ADS3202 CH2 CYCRMS NaN")
    assert mot6 == "Valor que no se puede convertir a número"

    # 2. Pruebas de integración sobre el archivo real 'mediciones.log'
    if os.path.exists("mediciones.log"):
        series, rechazadas = leer_log("mediciones.log")

        # Debe contener las 6 series esperadas (2 canales x 3 magnitudes)
        assert ("ADS3202", "CH1", "FREQ") in series
        assert ("ADS3202", "CH1", "PKPK") in series
        assert ("ADS3202", "CH1", "CYCRMS") in series
        assert ("ADS3202", "CH2", "FREQ") in series
        assert ("ADS3202", "CH2", "PKPK") in series
        assert ("ADS3202", "CH2", "CYCRMS") in series

        # En mediciones.log existen exactamente 8 líneas con anomalías
        assert len(rechazadas) == 8, f"Se esperaban 8 líneas rechazadas, se obtuvieron {len(rechazadas)}"

        # Confirmación de que la línea 105 (tabulada) no fue descartada
        lineas_rechazadas_nums = [r["linea"] for r in rechazadas]
        assert 105 not in lineas_rechazadas_nums, "La línea con tabulaciones no debe estar en rechazadas"

    print("08_log.py: Todas las pruebas pasaron correctamente (OK).")
