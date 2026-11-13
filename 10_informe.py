"""
Ejercicio 10 — El informe
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA
Materia: Programación

Consigna:
Escribir la función armar_informe(idn, series, verificaciones) que devuelve
el informe completo como una sola cadena de texto:
- El instrumento identificado.
- Una línea por cada serie con su n, su promedio, su mínimo y su máximo
  formateados con unidades legibles (con_unidad).
- El resultado de cada verificación realizada sobre los canales.

Requisito fundamental de diseño (pág. 13):
armar_informe es una FUNCIÓN PURA: no imprime nada por pantalla (no usa print)
ni abre ningún archivo. Recibe toda la información por parámetro y devuelve texto.
Esto permite probarla de forma determinista mediante asserts. El print lo realiza
quien la llama al final del programa.
"""

# Importamos las piezas desarrolladas en los módulos precedentes
parsear_idn = __import__("01_identificacion").parsear_idn
con_unidad = __import__("02_magnitudes").con_unidad
Instrumento = __import__("05_cliente").Instrumento
barrer = __import__("06_barrido").barrer
verificar_canal = __import__("07_verificacion").verificar_canal
leer_log = __import__("08_log").leer_log
resumen = __import__("09_estadistica").resumen


def _obtener_unidad_magnitud(magnitud):
    """
    Función auxiliar interna que asocia la unidad física base según la magnitud.
    """
    if magnitud == "FREQ":
        return "Hz"
    elif magnitud in ("PKPK", "CYCRMS", "CYCRms"):
        return "V"
    return ""


def armar_informe(idn, series, verificaciones):
    """
    Construye y formatea el reporte textual consolidado del banco de mediciones.

    Parámetros:
        idn (dict): Diccionario de identificación retornado por parsear_idn().
                    Contiene 'fabricante', 'modelo', 'serie' y 'version'.
        series (dict): Diccionario con series históricas del log:
                       {(equipo, canal, magnitud): [valores]}.
        verificaciones (list): Lista de diccionarios de verificación física
                               producidos por verificar_canal().

    Retorna:
        str: Cadena de texto formateada con el informe completo listo para ser
             mostrado en consola o archivado.
    """
    lineas = []
    lineas.append("=" * 64)
    lineas.append(" BANCO DE MEDICIONES AUTOMATIZADO — INFORME FINAL")
    lineas.append("=" * 64)
    lineas.append("")

    # -------------------------------------------------------------------------
    # Sección 1: Identificación del instrumento
    # -------------------------------------------------------------------------
    lineas.append("1. INSTRUMENTO IDENTIFICADO")
    lineas.append("-" * 64)
    if idn and isinstance(idn, dict):
        lineas.append(f"  Fabricante : {idn.get('fabricante', 'N/A')}")
        lineas.append(f"  Modelo     : {idn.get('modelo', 'N/A')}")
        lineas.append(f"  Nro. Serie : {idn.get('serie', 'N/A')}")
        lineas.append(f"  Firmware   : {idn.get('version', 'N/A')}")
    else:
        lineas.append("  [Instrumento no identificado o datos no disponibles]")
    lineas.append("")

    # -------------------------------------------------------------------------
    # Sección 2: Verificación de señales senoidales en tiempo real
    # -------------------------------------------------------------------------
    lineas.append("2. VERIFICACIÓN DE SEÑALES SENOIDALES EN VIVO")
    lineas.append("-" * 64)
    if verificaciones:
        for v in verificaciones:
            ch = v.get("canal", "?")
            coincide = v.get("coincide", False)
            estado_str = "COINCIDE (OK)" if coincide else "NO COINCIDE (FALLO)"

            vpp = v.get("vpp_medido")
            vrms_med = v.get("vrms_medido")
            vrms_teo = v.get("vrms_teorico")
            err = v.get("error_relativo")

            # Formateo de las magnitudes con sus unidades legibles (con_unidad)
            vpp_fmt = con_unidad(vpp, "V") if vpp is not None else "N/A"
            vrms_med_fmt = con_unidad(vrms_med, "V") if vrms_med is not None else "N/A"
            vrms_teo_fmt = con_unidad(vrms_teo, "V") if vrms_teo is not None else "N/A"
            err_fmt = f"{err * 100:.2f} %" if err is not None else "N/A"

            lineas.append(f"  Canal {ch}: {estado_str}")
            lineas.append(f"    Vpp medido     : {vpp_fmt}")
            lineas.append(f"    Vrms medido    : {vrms_med_fmt}")
            lineas.append(f"    Vrms teórico   : {vrms_teo_fmt}")
            lineas.append(f"    Error relativo : {err_fmt}")
    else:
        lineas.append("  [Sin verificaciones registradas]")
    lineas.append("")

    # -------------------------------------------------------------------------
    # Sección 3: Resumen estadístico de las series del log
    # -------------------------------------------------------------------------
    lineas.append("3. SERIES DE REGISTRO HISTÓRICO")
    lineas.append("-" * 64)
    if series:
        for clave, valores in sorted(series.items(), key=lambda x: str(x[0])):
            if isinstance(clave, tuple) and len(clave) == 3:
                eq, ch, mag = clave
                nombre_serie = f"{eq} {ch} {mag}"
                unidad = _obtener_unidad_magnitud(mag)
            else:
                nombre_serie = str(clave)
                unidad = ""

            est = resumen(valores)
            if est:
                n = est["n"]
                # Formateo con prefijos SI de cada estadístico
                prom_fmt = con_unidad(est["promedio"], unidad)
                min_fmt = con_unidad(est["minimo"], unidad)
                max_fmt = con_unidad(est["maximo"], unidad)
                desv_fmt = con_unidad(est["desvio"], unidad)
                lineas.append(
                    f"  * {nombre_serie:<20} (n={n:>2}): "
                    f"prom = {prom_fmt:<10} | min = {min_fmt:<10} | "
                    f"max = {max_fmt:<10} | desv = {desv_fmt}"
                )
            else:
                lineas.append(f"  * {nombre_serie}: [Serie vacía]")
    else:
        lineas.append("  [No hay series cargadas]")

    lineas.append("")
    lineas.append("=" * 64)
    return "\n".join(lineas)


# -----------------------------------------------------------------------------
# Bloque de Pruebas Unitarias y Ejecución Integrada del Banco de Mediciones
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    import time

    # ---- 1. Pruebas unitarias de la función pura armar_informe ----
    mock_idn = {
        "fabricante": "OWON",
        "modelo": "ADS3202",
        "serie": "25470803",
        "version": "V1.2.0",
    }
    mock_series = {
        ("ADS3202", "CH1", "FREQ"): [1000.0, 1000.5, 999.5],
        ("ADS3202", "CH1", "PKPK"): [2.0, 2.01, 1.99],
    }
    mock_verif = [
        {
            "canal": "CH1",
            "coincide": True,
            "vpp_medido": 2.0,
            "vrms_medido": 0.707,
            "vrms_teorico": 0.7071,
            "error_relativo": 0.0001,
        }
    ]

    informe_mock = armar_informe(mock_idn, mock_series, mock_verif)

    # Asserts sobre el contenido textual puro
    assert isinstance(informe_mock, str), "El informe debe ser una cadena de texto"
    assert "OWON" in informe_mock and "ADS3202" in informe_mock, "Debe contener los datos del equipo"
    assert "CH1" in informe_mock and "COINCIDE (OK)" in informe_mock, "Debe indicar la verificación"
    assert "1 kHz" in informe_mock or "1000 Hz" in informe_mock, "Debe formatear las magnitudes con unidades"

    # Caso raro: Parámetros vacíos o nulos
    informe_vacio = armar_informe(None, {}, [])
    assert isinstance(informe_vacio, str)
    assert "Sin verificaciones" in informe_vacio

    print("Pruebas unitarias de 10_informe.py pasaron correctamente (OK).\n")

    # ---- 2. Flujo completo integrado: El banco de mediciones terminado ----
    # Conectamos con el osciloscopio virtual (puerto 5555)
    try:
        inst = Instrumento("127.0.0.1", 5555)
    except ConnectionRefusedError:
        import threading
        import instrumento_virtual

        hilo_ads = threading.Thread(
            target=instrumento_virtual.servir,
            args=(5555, instrumento_virtual.responder_ads, "ADS3202"),
            daemon=True,
        )
        hilo_ads.start()
        time.sleep(0.3)
        inst = Instrumento("127.0.0.1", 5555)

    try:
        # a) Identificar el instrumento conectado
        resp_idn = inst.preguntar("*IDN?")
        datos_idn = parsear_idn(resp_idn)

        # b) Realizar el barrido de los canales CH1 y CH2 en vivo
        mediciones_vivas = barrer(inst, ["CH1", "CH2"])

        # c) Verificar físicamente cada canal
        verif_ch1 = verificar_canal(mediciones_vivas, "CH1")
        verif_ch2 = verificar_canal(mediciones_vivas, "CH2")
        verificaciones_vivas = [verif_ch1, verif_ch2]
    finally:
        inst.cerrar()

    # d) Leer las series históricas del archivo de log de laboratorio
    ruta_log = "mediciones.log"
    if os.path.exists(ruta_log):
        series_log, _ = leer_log(ruta_log)
    else:
        series_log = {}

    # e) Construir y presentar el informe final en pantalla
    informe_completo = armar_informe(datos_idn, series_log, verificaciones_vivas)
    print(informe_completo)
