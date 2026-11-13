"""
Ejercicio 4 — Configurar un canal
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA
Materia: Programación

Consigna:
Escribir la función comandos_de_canal(canal, display, acoplamiento, sonda, escala)
que devuelve una lista con las cuatro órdenes SCPI requeridas para configurar
completamente un canal del osciloscopio:
1. DISPlay
2. COUPling
3. PROBe
4. SCALe
Si el canal especificado no es 'CH1' ni 'CH2', la función debe retornar None.
"""


def comandos_de_canal(canal, display, acoplamiento, sonda, escala):
    """
    Genera la secuencia ordenada de 4 comandos SCPI para parametrizar un canal del osciloscopio.

    Parámetros:
        canal (str): Identificador del canal analógico ('CH1' o 'CH2').
        display (str): Estado de visualización ('ON' u 'OFF').
        acoplamiento (str): Tipo de acoplamiento de entrada ('DC', 'AC', 'GND').
        sonda (str): Factor de atenuación de la punta de prueba ('1X', '10X').
        escala (str): Sensibilidad vertical por división (ej. '1v', '500mv').

    Retorna:
        list: Lista de 4 cadenas con las órdenes formateadas en el orden exigido:
              [":<canal>:DISPlay <display>",
               ":<canal>:COUPling <acoplamiento>",
               ":<canal>:PROBe <sonda>",
               ":<canal>:SCALe <escala>"]
        None: Si el canal no es exactamente 'CH1' ni 'CH2'.

    Detalles de diseño:
        Se valida estrictamente que el canal pertenezca a la tupla ('CH1', 'CH2').
        No se permiten minúsculas ('ch1') ni otros canales inexistentes en el modelo ADS3202.
    """
    if canal not in ("CH1", "CH2"):
        return None

    return [
        f":{canal}:DISPlay {display}",
        f":{canal}:COUPling {acoplamiento}",
        f":{canal}:PROBe {sonda}",
        f":{canal}:SCALe {escala}",
    ]


# -----------------------------------------------------------------------------
# Bloque de Pruebas Unitarias (asserts)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Importamos dinámicamente la función validar del Ejercicio 3
    validar = __import__("03_comandos").validar

    # 1. Caso de prueba especificado en la consigna para el canal 1 (CH1)
    esperado_ch1 = [
        ":CH1:DISPlay ON",
        ":CH1:COUPling DC",
        ":CH1:PROBe 10X",
        ":CH1:SCALe 1v",
    ]
    resultado_ch1 = comandos_de_canal("CH1", "ON", "DC", "10X", "1v")
    assert resultado_ch1 == esperado_ch1, "La secuencia de órdenes para CH1 no coincide con la consigna"

    # 2. Caso de prueba para el canal 2 (CH2)
    esperado_ch2 = [
        ":CH2:DISPlay OFF",
        ":CH2:COUPling AC",
        ":CH2:PROBe 1X",
        ":CH2:SCALe 500mv",
    ]
    resultado_ch2 = comandos_de_canal("CH2", "OFF", "AC", "1X", "500mv")
    assert resultado_ch2 == esperado_ch2, "La secuencia de órdenes para CH2 no coincide"

    # 3. "LA PRUEBA QUE VALE POR DIEZ" (consigna pág. 10):
    # En lugar de solo comparar contra cadenas fijas, se verifica que absolutamente
    # todos los comandos producidos sean válidos según el analizador sintáctico del ejercicio 3.
    for cmd in resultado_ch1:
        assert validar(cmd) is None, f"El comando generado '{cmd}' no supera la validación sintáctica SCPI"
    for cmd in resultado_ch2:
        assert validar(cmd) is None, f"El comando generado '{cmd}' no supera la validación sintáctica SCPI"

    # 4. Casos raros / valores inválidos: canales no soportados
    assert comandos_de_canal("CH3", "ON", "DC", "10X", "1v") is None, "CH3 no existe en el ADS3202"
    assert comandos_de_canal("ch1", "ON", "DC", "10X", "1v") is None, "El canal en minúscula debe rechazarse"
    assert comandos_de_canal("", "ON", "DC", "10X", "1v") is None, "Canal vacío debe retornar None"
    assert comandos_de_canal(None, "ON", "DC", "10X", "1v") is None, "Canal None debe retornar None"

    print("04_configurar.py: Todas las pruebas pasaron correctamente (OK).")
