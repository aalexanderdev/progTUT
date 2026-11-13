"""
Ejercicio 2 — Magnitudes
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA
Materia: Programación

Consigna:
1. a_numero(texto): Convierte números en notación científica enviados por los
   equipos OWON (ej: "1.000000E+03") a tipo float (1000.0). Retorna None si el
   texto no representa un número válido.
2. con_unidad(valor, unidad): Hace el camino inverso, formateando el valor con
   prefijos del Sistema Internacional (p, n, u, m, ninguno, k, M, G) de forma
   que el número quede comprendido entre 1 y 999.
   Atención a la trampa de redondeo: con_unidad(999.9999, "Hz") debe dar "1 kHz".
"""


def a_numero(texto):
    """
    Convierte una cadena de texto en notación científica o decimal a float.

    Parámetros:
        texto (str): Texto a convertir (ej. "1.000000E+03", "2.5", "-0.04").

    Retorna:
        float: El número representado como punto flotante en Python.
        None: Si la cadena no puede interpretarse como un número real válido
              o si el argumento es nulo / vacío.

    Detalles de diseño:
        Se limpia la cadena con strip() para eliminar espacios o saltos de línea.
        Se utiliza un bloque try-except para capturar excepciones de conversión
        (ValueError, TypeError, AttributeError) retornando None de manera segura.
    """
    if texto is None:
        return None
    try:
        return float(str(texto).strip())
    except (ValueError, TypeError, AttributeError):
        return None


def con_unidad(valor, unidad):
    """
    Formatea un valor numérico agregando el prefijo del Sistema Internacional (SI)
    más adecuado para que la cifra resultante quede en el rango [1, 999].

    Prefijos del Sistema Internacional soportados:
        - pico  (p) : 10^-12
        - nano  (n) : 10^-9
        - micro (u) : 10^-6  (usamos 'u' en texto plano ASCII)
        - mili  (m) : 10^-3
        - base  ("") : 10^0   (sin prefijo)
        - kilo  (k) : 10^3
        - Mega  (M) : 10^6
        - Giga  (G) : 10^9

    Parámetros:
        valor (int, float): Magnitud física a representar (ej. 1000.0, 0.707).
        unidad (str): Símbolo de la unidad física (ej. "Hz", "V", "s", "F").

    Retorna:
        str: Texto legible para humanos (ej. "1 kHz", "707 mV", "0 V").
        None: Si el valor recibido no es de tipo numérico.

    Resolución de la trampa de redondeo:
        Si tenemos 999.9999 Hz, antes de redondear está en [1, 999] con prefijo base ("").
        Pero al redondear a 3 decimales se convierte en 1000.0, saliéndose del rango [1, 999].
        La función verifica si el valor redondeado es >= 1000.0 y, si existe un prefijo
        mayor en la tabla, lo escala dividiendo por 1000 y avanza al siguiente prefijo ("k").
    """
    if valor is None or not isinstance(valor, (int, float)):
        return None

    # Caso especial: valor cero exacto se reporta con la unidad sin prefijo
    if valor == 0:
        return f"0 {unidad}"

    # Preservamos el signo negativo si corresponde y trabajamos con el valor absoluto
    signo = "-" if valor < 0 else ""
    abs_val = abs(valor)

    # Tabla de escalas ordenadas por exponente de 10 ascendente
    escalas = [
        (-12, "p"),
        (-9, "n"),
        (-6, "u"),
        (-3, "m"),
        (0, ""),
        (3, "k"),
        (6, "M"),
        (9, "G"),
    ]

    # Determinamos el índice de la escala buscando el rango [10^exp, 10^(exp+3))
    indice = 0
    for i, (exp, _) in enumerate(escalas):
        limite_superior = 10 ** (exp + 3)
        if abs_val < limite_superior or i == len(escalas) - 1:
            indice = i
            break

    exp, prefijo = escalas[indice]
    escalado = abs_val / (10 ** exp)

    # Redondeamos el número a un máximo de 3 decimales
    escalado_redondeado = round(escalado, 3)

    # Control de la trampa de redondeo: si al redondear llega a 1000 y hay un prefijo mayor
    if escalado_redondeado >= 1000.0 and indice + 1 < len(escalas):
        indice += 1
        exp, prefijo = escalas[indice]
        escalado_redondeado = round(abs_val / (10 ** exp), 3)

    # Formateo estético de número:
    # Si es entero exacto (ej. 2.0 o 707.0) se muestra sin punto decimal ("2", "707").
    # Si tiene parte decimal (ej. 2.500) se eliminan los ceros a la derecha ("2.5").
    if escalado_redondeado == int(escalado_redondeado):
        num_str = str(int(escalado_redondeado))
    else:
        num_str = f"{escalado_redondeado:.3f}".rstrip("0").rstrip(".")

    return f"{signo}{num_str} {prefijo}{unidad}"


# -----------------------------------------------------------------------------
# Bloque de Pruebas Unitarias (asserts)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # --- Pruebas de la función a_numero ---
    # Casos válidos con notación científica y decimales estándar
    assert a_numero("1.000000E+03") == 1000.0, "Fallo al convertir notación exponencial estándar"
    assert a_numero("2.5e-3") == 0.0025, "Fallo al convertir exponencial negativa"
    assert a_numero("-12.5") == -12.5, "Fallo al convertir número negativo"
    assert a_numero("0") == 0.0, "Fallo al convertir cero"
    assert a_numero("  3.14 \n") == 3.14, "Fallo al limpiar espacios y salto de línea"

    # Casos raros / inválidos para a_numero
    assert a_numero("invalido") is None, "Texto arbitrario debe devolver None"
    assert a_numero("") is None, "Cadena vacía debe devolver None"
    assert a_numero("   ") is None, "Cadena de espacios debe devolver None"
    assert a_numero(None) is None, "None debe devolver None"
    assert a_numero("ERROR: comando desconocido") is None, "Error de instrumento debe devolver None"

    # --- Pruebas de la función con_unidad ---
    # Casos especificados en la tabla de la consigna (pág. 8)
    assert con_unidad(1000.0, "Hz") == "1 kHz", "1000 Hz debe convertirse en 1 kHz"
    assert con_unidad(2500.0, "Hz") == "2.5 kHz", "2500 Hz debe convertirse en 2.5 kHz"
    assert con_unidad(2.0, "V") == "2 V", "2.0 V debe mostrarse como '2 V' (sin .0)"
    assert con_unidad(0.707, "V") == "707 mV", "0.707 V debe mostrarse como 707 mV"
    assert con_unidad(0.0005, "s") == "500 us", "0.0005 s debe mostrarse como 500 us"
    assert con_unidad(0.0, "V") == "0 V", "0.0 V debe mostrarse como 0 V"

    # Caso trampa de la consigna (pág. 9):
    # 999.9999 Hz al redondearse a 3 decimales no debe quedar en '1000 Hz', sino en '1 kHz'
    assert con_unidad(999.9999, "Hz") == "1 kHz", "Falló la resolución del caso trampa de redondeo"

    # Casos raros / borde adicionales:
    # Números negativos
    assert con_unidad(-2.0, "V") == "-2 V", "Debe soportar tensiones negativas"
    assert con_unidad(-0.0005, "s") == "-500 us", "Debe soportar submúltiplos negativos"

    # Prefijos extremos soportados (p, n, M, G)
    assert con_unidad(1.5e-12, "F") == "1.5 pF", "Debe soportar picofaradios (p)"
    assert con_unidad(2.2e-9, "F") == "2.2 nF", "Debe soportar nanofaradios (n)"
    assert con_unidad(1.2e6, "Hz") == "1.2 MHz", "Debe soportar Megahertz (M)"
    assert con_unidad(2.4e9, "Hz") == "2.4 GHz", "Debe soportar Gigahertz (G)"

    # Entradas inválidas
    assert con_unidad(None, "V") is None, "Valor nulo debe devolver None"
    assert con_unidad("texto", "V") is None, "Valor de tipo texto no numérico debe devolver None"

    print("02_magnitudes.py: Todas las pruebas pasaron correctamente (OK).")
