"""
Ejercicio 3 — Órdenes y consultas
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA
Materia: Programación

Consigna:
Escribir dos funciones:
a) es_consulta(comando): Retorna True si el comando termina con el signo '?',
   indicando que se trata de una consulta SCPI (QUERY).
b) validar(comando): Evalúa la sintaxis del comando SCPI según 7 reglas estrictas.
   Retorna None si el comando está correctamente formado, o el mensaje de error
   correspondiente si rompe alguna regla.
"""

# Constantes con los mensajes de error asociados a cada una de las 7 reglas
ERROR_VACIO = "El comando no puede estar vacio"
ERROR_PREFIJO = "El comando debe empezar con : o con *"
ERROR_ESPACIOS_SEGUIDOS = "El comando no puede tener dos espacios seguidos"
ERROR_MULTIPLES_CONSULTAS = "El comando puede tener a lo sumo un ?"
ERROR_SIGNO_NO_AL_FINAL = "El signo ? debe ir al final del comando"
ERROR_ORDEN_ARGUMENTOS = "Una orden lleva un solo argumento"
ERROR_CONSULTA_CON_ARGUMENTO = "Una consulta no lleva argumento"


def es_consulta(comando):
    """
    Determina si un comando SCPI corresponde a una consulta (query).

    En el estándar SCPI, toda consulta se distingue por finalizar con un signo
    de interrogación '?'. Si no finaliza con '?', se trata de una orden (comando
    de configuración o ejecución).

    Parámetros:
        comando (str): Cadena de comando a evaluar.

    Retorna:
        bool: True si termina en '?', False en cualquier otro caso.
    """
    if not isinstance(comando, str):
        return False
    return comando.endswith("?")


def validar(comando):
    """
    Valida la sintaxis de un comando SCPI verificando el cumplimiento de las 7 reglas
    definidas por la cátedra:

    Regla 1: No puede estar vacío (ejemplo que la rompe: "").
    Regla 2: Debe empezar con ':' o con '*' (ejemplo: "CH1:DISPlay ON").
    Regla 3: No puede contener dos espacios seguidos (ejemplo: ":CH1:DISPlay  ON").
    Regla 4: Puede tener a lo sumo un solo '?' (ejemplo: ":CH1:DISPlay??").
    Regla 5: El '?' debe ubicarse estrictamente al final (ejemplo: ":CH1:DIS?Play").
    Regla 6: Una orden lleva exactamente un argumento (ejemplo: ":CH1:SCALe 1 v").
    Regla 7: Una consulta no lleva argumentos (ejemplo: ":CH1:DISPlay ON?").

    Parámetros:
        comando (str): Cadena de texto con el comando a validar.

    Retorna:
        None: Si el comando cumple con todas las reglas (es válido).
        str: Cadena de texto con la descripción del error si viola alguna regla.
    """
    # Regla 1: No puede ser nulo ni una cadena vacía
    if not isinstance(comando, str) or len(comando) == 0:
        return ERROR_VACIO

    # Regla 2: Los comandos SCPI jerárquicos inician con ':' y los comunes IEEE 488.2 con '*'
    if not (comando.startswith(":") or comando.startswith("*")):
        return ERROR_PREFIJO

    # Regla 3: No se permiten espacios dobles accidentales
    if "  " in comando:
        return ERROR_ESPACIOS_SEGUIDOS

    # Regla 4: No puede contener más de un signo de interrogación
    if comando.count("?") > 1:
        return ERROR_MULTIPLES_CONSULTAS

    # Regla 5: Si contiene '?', debe ser exclusivamente el último carácter
    if "?" in comando and not comando.endswith("?"):
        return ERROR_SIGNO_NO_AL_FINAL

    # Reglas 6 y 7: Distinción de estructura según sea consulta u orden
    if es_consulta(comando):
        # Una consulta SCPI pura no debe llevar espacios ni argumentos
        if " " in comando:
            return ERROR_CONSULTA_CON_ARGUMENTO
    else:
        # Una orden de configuración debe estructurarse como: COMANDO VALOR
        # Por lo tanto, al separar por espacios simples, deben existir exactamente 2 partes
        partes = comando.split(" ")
        if len(partes) != 2:
            return ERROR_ORDEN_ARGUMENTOS

    # Si superó todas las verificaciones, el comando está bien formado
    return None


# -----------------------------------------------------------------------------
# Bloque de Pruebas Unitarias (asserts)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # --- Verificación de es_consulta ---
    assert es_consulta("*IDN?") is True, "*IDN? debe reconocerse como consulta"
    assert es_consulta(":MEASUrement:CH1:FREQuency?") is True, "Comando con '?' final es consulta"
    assert es_consulta(":CH1:DISPlay ON") is False, "Comando sin '?' es una orden"
    assert es_consulta("") is False, "Cadena vacía no es consulta"
    assert es_consulta(None) is False, "None no es consulta"

    # --- Verificación de validar con los ejemplos exactos de la consigna (pág. 9) ---
    assert validar("") == ERROR_VACIO, "Rompe Regla 1: comando vacío"
    assert validar("CH1:DISPlay ON") == ERROR_PREFIJO, "Rompe Regla 2: no inicia con : ni *"
    assert validar(":CH1:DISPlay  ON") == ERROR_ESPACIOS_SEGUIDOS, "Rompe Regla 3: dos espacios seguidos"
    assert validar(":CH1:DISPlay??") == ERROR_MULTIPLES_CONSULTAS, "Rompe Regla 4: múltiples signos ?"
    assert validar(":CH1:DIS?Play") == ERROR_SIGNO_NO_AL_FINAL, "Rompe Regla 5: signo ? intercalado"
    assert validar(":CH1:SCALe 1 v") == ERROR_ORDEN_ARGUMENTOS, "Rompe Regla 6: orden con 2 argumentos ('1' y 'v')"
    assert validar(":CH1:DISPlay ON?") == ERROR_CONSULTA_CON_ARGUMENTO, "Rompe Regla 7: consulta con argumento"

    # --- Comandos válidos en el protocolo SCPI del laboratorio ---
    assert validar("*IDN?") is None, "*IDN? es válido"
    assert validar(":CH1:DISPlay ON") is None, "Encendido de canal es válido"
    assert validar(":CH1:COUPling DC") is None, "Acoplamiento es válido"
    assert validar(":CH1:PROBe 10X") is None, "Atenuación de punta es válida"
    assert validar(":CH1:SCALe 1v") is None, "Escala con unidad compactada ('1v') es válida"
    assert validar(":MEASUrement:CH1:FREQuency?") is None, "Consulta de frecuencia es válida"
    assert validar(":MEASUrement:CH2:PKPK?") is None, "Consulta de Vpp es válida"

    # --- Casos raros / borde adicionales ---
    assert validar(None) == ERROR_VACIO, "None debe reportarse como vacío"
    assert validar(":CH1:DISPlay") == ERROR_ORDEN_ARGUMENTOS, "Orden sin argumento debe rechazarse"
    assert validar(" :CH1:DISPlay ON") == ERROR_PREFIJO, "Espacio inicial rompe regla de prefijo"

    print("03_comandos.py: Todas las pruebas pasaron correctamente (OK).")
