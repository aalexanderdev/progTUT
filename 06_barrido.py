"""
Ejercicio 6 — El barrido
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA
Materia: Programación

Consigna:
Escribir la función barrer(instrumento, canales) que realiza un barrido de las
tres magnitudes físicas de cada canal especificado:
- FREQuency? (Frecuencia en Hz)
- PKPK?      (Tensión pico a pico en Volts)
- CYCRms?    (Tensión eficaz / RMS en Volts)

Para dos canales ('CH1' y 'CH2'), devuelve una lista con 6 diccionarios de medición.
Si el instrumento contesta con un error, el valor numérico queda en None,
pero el texto crudo se guarda obligatoriamente para trazabilidad.
"""

# Importamos la función de conversión numérica desarrollada en el Ejercicio 2
a_numero = __import__("02_magnitudes").a_numero

# Lista de tuplas con las 3 magnitudes reglamentarias por canal:
# (Identificador_Magnitud, Sufijo_Comando_SCPI, Unidad_Física)
MAGNITUDES = [
    ("FREQ", "FREQuency?", "Hz"),
    ("PKPK", "PKPK?", "V"),
    ("CYCRMS", "CYCRms?", "V"),
]


def barrer(instrumento, canales):
    """
    Ejecuta el barrido sistemático de mediciones solicitando frecuencia, Vpp y Vrms.

    Parámetros:
        instrumento: Objeto que expone el método 'preguntar(comando)'. Puede ser una
                     instancia real de la clase Instrumento o un objeto simulado (Mock).
        canales (iterable): Colección con los nombres de canal a barrer (ej. ['CH1', 'CH2']).

    Retorna:
        list: Lista de diccionarios, donde cada diccionario representa una medición:
              {
                  'canal': str,       # Nombre del canal analógico ('CH1', 'CH2')
                  'magnitud': str,    # Nombre estándar de la magnitud ('FREQ', 'PKPK', 'CYCRMS')
                  'unidad': str,      # Unidad física de medida ('Hz', 'V')
                  'texto_crudo': str, # Cadena devuelta literalmente por el equipo
                  'valor': float|None # Valor convertido a número, o None si hubo error
              }

    Justificación arquitectónica:
        barrer() recibe el instrumento por parámetro (inyección de dependencias).
        Esto permite desacoplar la lógica de adquisición del transporte de red, haciendo
        posible probarla con un mock determinista sin depender de sockets ni sufrir el
        ruido aleatorio ("temblor") del instrumento real o virtual.
    """
    if not canales:
        return []

    mediciones = []

    for canal in canales:
        for nombre_mag, comando_sufijo, unidad in MAGNITUDES:
            comando = f":MEASUrement:{canal}:{comando_sufijo}"
            # Se envía la consulta SCPI al instrumento
            texto_crudo = instrumento.preguntar(comando)
            # Se intenta convertir la respuesta a float con la función del ejercicio 2
            valor_num = a_numero(texto_crudo)

            # Si el instrumento respondió un error (ej. "ERROR: comando desconocido"),
            # valor_num será None, pero se almacena el texto crudo intacto
            mediciones.append({
                "canal": canal,
                "magnitud": nombre_mag,
                "unidad": unidad,
                "texto_crudo": texto_crudo,
                "valor": valor_num,
            })

    return mediciones


# -----------------------------------------------------------------------------
# Bloque de Pruebas Unitarias (asserts)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Clase simulada (Mock) según la recomendación pedagógica de la consigna (pág. 11):
    # Permite verificar el comportamiento de barrer sin abrir sockets ni depender de la red.
    class InstrumentoMock:
        def __init__(self, respuestas=None):
            # Respuestas estáticas y predecibles para las consultas esperadas
            self.respuestas = respuestas or {
                ":MEASUrement:CH1:FREQuency?": "1.000000E+03",
                ":MEASUrement:CH1:PKPK?": "2.000000E+00",
                ":MEASUrement:CH1:CYCRms?": "7.071068E-01",
                ":MEASUrement:CH2:FREQuency?": "2.500000E+03",
                ":MEASUrement:CH2:PKPK?": "8.000000E-01",
                ":MEASUrement:CH2:CYCRms?": "2.828427E-01",
            }
            self.comandos_recibidos = []

        def preguntar(self, comando):
            self.comandos_recibidos.append(comando)
            return self.respuestas.get(comando, "ERROR: comando desconocido")

    # 1. Prueba normal de barrido completo con dos canales (3 magnitudes x 2 canales = 6 mediciones)
    mock = InstrumentoMock()
    resultado = barrer(mock, ["CH1", "CH2"])
    assert len(resultado) == 6, f"Se esperaban 6 mediciones, pero se obtuvieron {len(resultado)}"

    # Verificación de la primera medición (CH1 FREQ)
    assert resultado[0]["canal"] == "CH1"
    assert resultado[0]["magnitud"] == "FREQ"
    assert resultado[0]["unidad"] == "Hz"
    assert resultado[0]["texto_crudo"] == "1.000000E+03"
    assert resultado[0]["valor"] == 1000.0, "La frecuencia no fue convertida a 1000.0 Hz"

    # Verificación de la segunda medición (CH1 PKPK)
    assert resultado[1]["canal"] == "CH1"
    assert resultado[1]["magnitud"] == "PKPK"
    assert resultado[1]["unidad"] == "V"
    assert resultado[1]["valor"] == 2.0, "La tensión pico a pico no fue convertida a 2.0 V"

    # Verificación de la tercera medición (CH1 CYCRMS)
    assert resultado[2]["canal"] == "CH1"
    assert resultado[2]["magnitud"] == "CYCRMS"
    assert resultado[2]["unidad"] == "V"
    assert abs(resultado[2]["valor"] - 0.7071068) < 1e-6, "El valor RMS no coincide con el esperado"

    # 2. Caso raro: El instrumento responde con un error SCPI en una de las mediciones
    # Regla: valor debe ser None, pero texto_crudo debe registrar el mensaje de error textual
    mock_error = InstrumentoMock(respuestas={
        ":MEASUrement:CH1:FREQuency?": "1.000000E+03",
        ":MEASUrement:CH1:PKPK?": "ERROR: comando desconocido",
        ":MEASUrement:CH1:CYCRms?": "7.071068E-01",
    })
    res_err = barrer(mock_error, ["CH1"])
    assert len(res_err) == 3
    assert res_err[1]["magnitud"] == "PKPK"
    assert res_err[1]["valor"] is None, "El valor con error debe ser None"
    assert res_err[1]["texto_crudo"] == "ERROR: comando desconocido", "El texto crudo de error debe preservarse"

    # 3. Caso raro: Lista de canales vacía
    res_vacia = barrer(mock, [])
    assert res_vacia == [], "Barrer una lista vacía de canales debe retornar una lista vacía"

    print("06_barrido.py: Todas las pruebas pasaron correctamente (OK).")
