"""
Ejercicio 1 — Identificación del equipo
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA
Materia: Programación

Consigna:
Escribir la función parsear_idn(respuesta) que recibe la cadena de texto
devuelta por la consulta SCPI '*IDN?' y retorna un diccionario con las claves:
'fabricante', 'modelo', 'serie' y 'version'. Si la respuesta no es válida,
debe retornar None.
"""


def parsear_idn(respuesta):
    """
    Parsea la respuesta al comando SCPI de identificación '*IDN?'.

    Parámetros:
        respuesta (str): Cadena de texto recibida desde el instrumento.
                         Ejemplo osciloscopio: "OWON,ADS3202,25470803,V1.2.0"
                         Ejemplo multímetro:   "OWON,XDM1041,25470803,V4.4.0,3"

    Retorna:
        dict: Diccionario con las claves 'fabricante', 'modelo', 'serie' y 'version'.
        None: Si la respuesta es inválida, está vacía, contiene un mensaje de error
              o no posee los campos mínimos requeridos.

    Detalles de diseño:
        1. Se valida que la entrada sea de tipo cadena (str) y no esté vacía tras
           eliminar espacios en blanco o saltos de línea con strip().
        2. Si el instrumento no reconoció el comando, suele responder cadenas que
           inician con 'ERROR' (ej: 'ERROR: comando desconocido'). Se detecta y descarta.
        3. El protocolo SCPI separa los campos con comas. Se divide la cadena y se
           limpia el espacio sobrante alrededor de cada campo.
        4. Regla del trabajo práctico: El osciloscopio responde con 4 campos y el
           multímetro con 5. Ambos son válidos, descartando el quinto campo del multímetro.
           Por lo tanto, se exige tener al menos 4 campos.
        5. Se verifica que ninguno de los primeros 4 campos obligatorios haya quedado vacío.
    """
    # 1. Validación de tipo y contenido no vacío
    if not isinstance(respuesta, str):
        return None

    texto = respuesta.strip()
    if not texto:
        return None

    # 2. Descarte de mensajes de error devueltos por el instrumento
    if texto.startswith("ERROR"):
        return None

    # 3. Separación por comas y limpieza de espacios en cada campo
    partes = [campo.strip() for campo in texto.split(",")]

    # 4. Deben existir al menos 4 campos (fabricante, modelo, serie, version)
    if len(partes) < 4:
        return None

    # 5. Ningún campo obligatorio puede ser una cadena vacía (ej: "OWON,,123,V1")
    if any(len(campo) == 0 for campo in partes[:4]):
        return None

    # Se toman los primeros 4 campos; si hay un 5to campo (multímetro), se ignora
    return {
        "fabricante": partes[0],
        "modelo": partes[1],
        "serie": partes[2],
        "version": partes[3],
    }


# -----------------------------------------------------------------------------
# Bloque de Pruebas Unitarias (asserts)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Prueba 1: Respuesta típica de 4 campos correspondiente al Osciloscopio ADS3202
    resp_osc = "OWON,ADS3202,25470803,V1.2.0"
    res1 = parsear_idn(resp_osc)
    assert res1 == {
        "fabricante": "OWON",
        "modelo": "ADS3202",
        "serie": "25470803",
        "version": "V1.2.0",
    }, "Error en parseo estándar de osciloscopio (4 campos)"

    # Prueba 2: Respuesta de 5 campos del Multímetro XDM1041 (debe ignorar el 5to campo '3')
    resp_multi = "OWON,XDM1041,25470803,V4.4.0,3"
    res2 = parsear_idn(resp_multi)
    assert res2 == {
        "fabricante": "OWON",
        "modelo": "XDM1041",
        "serie": "25470803",
        "version": "V4.4.0",
    }, "Error al descartar el 5to campo del multímetro"

    # Prueba 3: Tolerancia a espacios en blanco accidentales y caracteres newline '\n'
    resp_espacios = "  OWON , ADS3202 , 25470803 , V1.2.0 \r\n"
    res3 = parsear_idn(resp_espacios)
    assert res3 == {
        "fabricante": "OWON",
        "modelo": "ADS3202",
        "serie": "25470803",
        "version": "V1.2.0",
    }, "Error: la función debe limpiar espacios sobrantes alrededor de cada campo"

    # Prueba 4 (Caso raro): Cadena vacía o formada únicamente por espacios
    assert parsear_idn("") is None, "Una cadena vacía debe devolver None"
    assert parsear_idn("   \t  ") is None, "Una cadena de solo espacios debe devolver None"

    # Prueba 5 (Caso raro): Menos de cuatro campos suministrados
    assert parsear_idn("OWON,ADS3202,25470803") is None, "Menos de 4 campos debe devolver None"

    # Prueba 6 (Caso raro): Mensaje de error retornado por comando SCPI no reconocido
    assert parsear_idn("ERROR: comando desconocido") is None, "Respuestas de error deben devolver None"

    # Prueba 7 (Caso raro): Campos vacíos intercalados entre comas
    assert parsear_idn("OWON,,25470803,V1.2.0") is None, "Campos vacíos deben invalidar la respuesta"

    # Prueba 8 (Caso raro): Tipos de datos no válidos (None, enteros)
    assert parsear_idn(None) is None, "Pasar None debe ser manejado retornando None"
    assert parsear_idn(12345) is None, "Pasar un tipo numérico debe retornar None"

    print("01_identificacion.py: Todas las pruebas pasaron correctamente (OK).")
