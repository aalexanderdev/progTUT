#!/usr/bin/env python3
"""
Instrumento virtual SCPI — TFI de Programacion
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA

Este programa hace de cuenta que es el osciloscopio ADS3202 y el
multimetro XDM1041 del laboratorio. Responde los mismos comandos SCPI
que responden los equipos reales, descriptos en el documento
"Protocolo SCPI aplicado a la instrumentacion OWON integrada V16".

No hay que instalar nada. Se abre una terminal y se escribe:

    python3 instrumento_virtual.py

y el programa queda escuchando. Desde OTRA terminal se corre el
programa del TFI, que se conecta a 127.0.0.1 en el puerto 5555
(osciloscopio) o 5556 (multimetro).

Para cortarlo: Ctrl+C.

NO HAY QUE MODIFICAR ESTE ARCHIVO. Es el instrumento; el instrumento
no se toca, se mide.
"""

import math
import random
import socket
import threading

PUERTO_ADS3202 = 5555
PUERTO_XDM1041 = 5556

# Semilla fija: el instrumento tiembla siempre igual, asi dos alumnos
# que corren el mismo programa ven exactamente los mismos numeros.
# Cada equipo tiene su propio generador para que el temblor de uno no
# dependa de cuantas veces se consulto el otro.
AZAR_ADS = random.Random(202004)
AZAR_XDM = random.Random(1041)

# La senal que el generador XDG3252 le esta inyectando al CH1.
# Son los valores del ejemplo de la pagina 14 del documento de catedra.
FRECUENCIA_CH1 = 1000.0            # hertz
VPP_CH1 = 2.0                      # volt pico a pico

# En CH2 hay una senal distinta, para que el barrido de los dos
# canales no devuelva dos veces lo mismo.
FRECUENCIA_CH2 = 2500.0
VPP_CH2 = 0.8

RUIDO = 0.005                      # +-0,5 % de temblor en cada lectura


def temblar(valor, azar):
    """Un instrumento real nunca devuelve dos veces el mismo numero."""
    return valor * (1 + azar.uniform(-RUIDO, RUIDO))


def cientifica(valor):
    """Formato en que los equipos OWON devuelven los numeros."""
    return "%E" % valor


# --------------------------------------------------------------------
# Osciloscopio ADS3202
# --------------------------------------------------------------------

ESTADO_ADS = {
    ":CH1:DISPlay": "ON",
    ":CH2:DISPlay": "OFF",
    ":CH1:COUPling": "DC",
    ":CH2:COUPling": "DC",
    ":CH1:PROBe": "10X",
    ":CH2:PROBe": "10X",
    ":CH1:SCALe": "1v",
    ":CH2:SCALe": "500mv",
    ":HORIzontal:SCALe": "1ms",
    ":TRIGger:TYPE": "SINGle",
    ":TRIGger:STATUS": "TRIG",
    ":RUNning": "RUN",
}

MEDICIONES_ADS = {
    ":MEASUrement:CH1:FREQuency": FRECUENCIA_CH1,
    ":MEASUrement:CH1:PKPK": VPP_CH1,
    ":MEASUrement:CH1:CYCRms": VPP_CH1 / 2 / math.sqrt(2),
    ":MEASUrement:CH2:FREQuency": FRECUENCIA_CH2,
    ":MEASUrement:CH2:PKPK": VPP_CH2,
    ":MEASUrement:CH2:CYCRms": VPP_CH2 / 2 / math.sqrt(2),
}


def responder_ads(comando):
    """Devuelve el texto de la respuesta, o None si era una orden."""
    comando = comando.strip()
    if comando == "":
        return None

    if comando == "*IDN?":
        return "OWON,ADS3202,25470803,V1.2.0"

    if comando.endswith("?"):
        clave = comando[:-1]
        if clave in MEDICIONES_ADS:
            return cientifica(temblar(MEDICIONES_ADS[clave], AZAR_ADS))
        if clave in ESTADO_ADS:
            return ESTADO_ADS[clave]
        return "ERROR: comando desconocido"

    # Es una orden: viene como ":CH1:DISPlay ON"
    partes = comando.split(" ", 1)
    if len(partes) == 2 and partes[0] in ESTADO_ADS:
        ESTADO_ADS[partes[0]] = partes[1].strip()
    return None


# --------------------------------------------------------------------
# Multimetro XDM1041
# --------------------------------------------------------------------

ESTADO_XDM = {
    "FUNC1": "VOLT:DC",
    "AUTO": "1",
    "RANGE": "AUTO",
    "RATE": "M",
}

# Lo que mide el multimetro segun como este configurado.
VALORES_XDM = {
    "VOLT:DC": 12.04,
    "VOLT:AC": 0.707,
    "RES": 50.0,
    "FREQ": 1000.0,
}


def responder_xdm(comando):
    comando = comando.strip()
    if comando == "":
        return None

    if comando == "*IDN?":
        return "OWON,XDM1041,25470803,V4.4.0,3"

    if comando == "MEAS1?":
        funcion = ESTADO_XDM["FUNC1"]
        return cientifica(temblar(VALORES_XDM.get(funcion, 0.0), AZAR_XDM))

    if comando.endswith("?"):
        return ESTADO_XDM.get(comando[:-1], "ERROR: comando desconocido")

    if comando.startswith("CONF:"):
        ESTADO_XDM["FUNC1"] = comando[5:].replace(" AUTO", "").strip()
        return None

    return None


# --------------------------------------------------------------------
# El servidor
# --------------------------------------------------------------------

def atender(conexion, responder):
    with conexion:
        archivo = conexion.makefile("r")
        for linea in archivo:
            salida = responder(linea)
            if salida is not None:
                conexion.sendall((salida + "\n").encode())


def servir(puerto, responder, nombre):
    servidor = socket.socket()
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("127.0.0.1", puerto))
    servidor.listen(5)
    print("%-8s escuchando en 127.0.0.1:%d" % (nombre, puerto))
    while True:
        conexion, _ = servidor.accept()
        hilo = threading.Thread(target=atender,
                                args=(conexion, responder),
                                daemon=True)
        hilo.start()


def main():
    hilo = threading.Thread(
        target=servir,
        args=(PUERTO_XDM1041, responder_xdm, "XDM1041"),
        daemon=True)
    hilo.start()
    try:
        servir(PUERTO_ADS3202, responder_ads, "ADS3202")
    except KeyboardInterrupt:
        print("\nInstrumento apagado.")


if __name__ == "__main__":
    main()
