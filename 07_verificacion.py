"""
Ejercicio 7 — La verificación
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA
Materia: Programación

Consigna:
Este es el ejercicio central del trabajo práctico.
Escribir:
a) vrms_teorico(vpp): Calcula el Vrms teórico para una senoide a partir de Vpp.
   Retorna None si el dato no tiene sentido físico (negativo, nulo o no numérico).
b) coincide(medido, teorico, tolerancia=0.02): Retorna True si el valor medido
   cae dentro de la tolerancia relativa respecto al teórico (2% por defecto).
   Error relativo = |medido - teorico| / |teorico|
c) verificar_canal(filas, canal): Busca PKPK y CYCRMS en el resultado del barrido
   y retorna un diccionario indicando si coinciden físicamente.

Atención: "La prueba que demuestra que la prueba sirve" (pág. 12):
Para una señal cuadrada de 2 Vpp, el Vrms es 1 V (no 707 mV). Debe dar que NO coincide.
"""

import math


def vrms_teorico(vpp):
    """
    Calcula el valor RMS (tensión eficaz) teórico correspondiente a una onda senoidal pura.

    Fundamento físico:
        Para una señal senoidal pura simétrica:
            Vp = Vpp / 2               (Tensión pico)
            Vrms = Vp / sqrt(2)        (Tensión eficaz)
            Vrms = Vpp / (2 * sqrt(2))

    Parámetros:
        vpp (float, int): Tensión pico a pico en Volts.

    Retorna:
        float: El valor de Vrms teórico predicho por las ecuaciones de la física.
        None: Si vpp no es numérico, es nulo o es <= 0 (un valor pico a pico no puede
              ser nulo ni negativo en una señal física real).
    """
    if vpp is None or not isinstance(vpp, (int, float)):
        return None
    if vpp <= 0:
        return None
    return (vpp / 2.0) / math.sqrt(2)


def coincide(medido, teorico, tolerancia=0.02):
    """
    Determina si un valor medido experimentalmente coincide con el valor teórico
    dentro de un margen de tolerancia relativa porcentual.

    Fórmula del error relativo:
        error = |medido - teorico| / |teorico|

    Parámetros:
        medido (float): Valor numérico medido por el instrumento.
        teorico (float): Valor numérico de referencia esperado teóricamente.
        tolerancia (float): Margen de error relativo admisible (0.02 = 2% por defecto).

    Retorna:
        bool: True si error <= tolerancia, False en caso contrario o si los datos son inválidos.

    Nota de laboratorio:
        En metrología no se utiliza el operador de igualdad estricta (==) sobre mediciones
        experimentales, dado que todo instrumento presenta incertidumbre de medición y ruido.
    """
    if medido is None or teorico is None or tolerancia is None:
        return False
    if not isinstance(medido, (int, float)) or not isinstance(teorico, (int, float)):
        return False
    # Protección ante división por cero si el valor teórico es 0
    if teorico == 0:
        return medido == 0

    error_relativo = abs(medido - teorico) / abs(teorico)
    return error_relativo <= tolerancia


def verificar_canal(filas, canal):
    """
    Localiza las lecturas de PKPK y CYCRMS correspondientes a un canal en la lista
    del barrido y dictamina si la señal es compatible con una senoide pura.

    Parámetros:
        filas (list): Lista de diccionarios de mediciones generada por barrer().
        canal (str): Canal analógico a auditar ('CH1' o 'CH2').

    Retorna:
        dict: Diccionario descriptivo con los resultados de la verificación:
              {
                  'canal': str,              # Canal verificado
                  'coincide': bool,          # True si la senoide verifica al 2%, False si no
                  'vpp_medido': float|None,  # Tensión pico a pico medida
                  'vrms_medido': float|None, # Tensión RMS medida por el equipo
                  'vrms_teorico': float|None,# Tensión RMS teórica calculada
                  'error_relativo': float|None # Discrepancia relativa fraccional
              }
    """
    if not isinstance(filas, list):
        return {
            "canal": canal,
            "coincide": False,
            "vpp_medido": None,
            "vrms_medido": None,
            "vrms_teorico": None,
            "error_relativo": None,
        }

    vpp = None
    vrms = None

    # Búsqueda de las magnitudes PKPK y CYCRMS del canal indicado
    for fila in filas:
        if fila.get("canal") == canal:
            mag = fila.get("magnitud")
            if mag == "PKPK":
                vpp = fila.get("valor")
            elif mag in ("CYCRMS", "CYCRms"):
                vrms = fila.get("valor")

    # Cálculo del valor teórico esperado según la física senoidal
    vrms_teor = vrms_teorico(vpp)

    # Si falta algún dato o hubo error en el instrumento, no se puede verificar
    if vpp is None or vrms is None or vrms_teor is None:
        return {
            "canal": canal,
            "coincide": False,
            "vpp_medido": vpp,
            "vrms_medido": vrms,
            "vrms_teorico": vrms_teor,
            "error_relativo": None,
        }

    # Cálculo del error relativo porcentual y evaluación de tolerancia (2%)
    error_rel = abs(vrms - vrms_teor) / abs(vrms_teor)
    coinciden = coincide(vrms, vrms_teor, 0.02)

    return {
        "canal": canal,
        "coincide": coinciden,
        "vpp_medido": vpp,
        "vrms_medido": vrms,
        "vrms_teorico": vrms_teor,
        "error_relativo": error_rel,
    }


# -----------------------------------------------------------------------------
# Bloque de Pruebas Unitarias (asserts)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Pruebas de cálculo de vrms_teorico
    # Para Vpp = 2 V -> Vp = 1 V -> Vrms = 1 / sqrt(2) ≈ 0.70710678 V
    vrms_2v = vrms_teorico(2.0)
    assert abs(vrms_2v - 0.70710678) < 1e-6, "Vrms teórico para 2 Vpp incorrecto"

    # Para Vpp = 0.8 V -> Vp = 0.4 V -> Vrms = 0.4 / sqrt(2) ≈ 0.28284271 V
    vrms_08v = vrms_teorico(0.8)
    assert abs(vrms_08v - 0.28284271) < 1e-6, "Vrms teórico para 0.8 Vpp incorrecto"

    # Casos raros / datos sin sentido físico
    assert vrms_teorico(0) is None, "Tensión cero no debe calcular Vrms"
    assert vrms_teorico(-2.0) is None, "Tensión negativa no debe calcular Vrms"
    assert vrms_teorico(None) is None, "None no debe calcular Vrms"
    assert vrms_teorico("dos") is None, "Cadenas de texto deben devolver None"

    # 2. Pruebas de la función coincide
    # Lectura con ruido experimental menor al 2% (709 mV vs 707.1 mV -> 0.27% de error)
    assert coincide(0.709, 0.70710678, 0.02) is True, "Debe coincidir con error del 0.27%"
    # Lectura con error mayor al 2% (730 mV vs 707.1 mV -> 3.2% de error)
    assert coincide(0.730, 0.70710678, 0.02) is False, "Debe rechazar con error del 3.2%"

    # 3. Caso normal de verificar_canal con señal senoidal (CH1 nominal)
    barrido_seno = [
        {"canal": "CH1", "magnitud": "FREQ", "valor": 1000.0},
        {"canal": "CH1", "magnitud": "PKPK", "valor": 2.0},
        {"canal": "CH1", "magnitud": "CYCRMS", "valor": 0.708},
    ]
    res_ch1 = verificar_canal(barrido_seno, "CH1")
    assert res_ch1["coincide"] is True, "Una señal senoidal válida debe coincidir"
    assert res_ch1["canal"] == "CH1"

    # 4. LA PRUEBA QUE DEMUESTRA QUE LA PRUEBA SIRVE (consigna pág. 12):
    # Una onda cuadrada de 2 Vpp tiene Vrms = 1 V, no 707 mV.
    # Si la función dijera que sí también en este caso, la prueba no serviría para nada.
    barrido_cuadrada = [
        {"canal": "CH1", "magnitud": "FREQ", "valor": 1000.0},
        {"canal": "CH1", "magnitud": "PKPK", "valor": 2.0},
        {"canal": "CH1", "magnitud": "CYCRMS", "valor": 1.0},
    ]
    res_cuadrada = verificar_canal(barrido_cuadrada, "CH1")
    assert res_cuadrada["coincide"] is False, "La onda cuadrada NO debe coincidir con la fórmula senoidal"

    # 5. Casos raros / borde: mediciones incompletas o erróneas en el instrumento
    barrido_incompleto = [
        {"canal": "CH1", "magnitud": "PKPK", "valor": 2.0},
        # Falta CYCRMS en el barrido
    ]
    assert verificar_canal(barrido_incompleto, "CH1")["coincide"] is False

    barrido_con_error = [
        {"canal": "CH1", "magnitud": "PKPK", "valor": None},
        {"canal": "CH1", "magnitud": "CYCRMS", "valor": 0.707},
    ]
    assert verificar_canal(barrido_con_error, "CH1")["coincide"] is False

    # Canal inexistente o lista vacía
    assert verificar_canal([], "CH1")["coincide"] is False

    print("07_verificacion.py: Todas las pruebas pasaron correctamente (OK).")
