"""
Ejercicio 5 — El cliente
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA
Materia: Programación

Consigna:
Implementar la clase Instrumento para comunicarse por red TCP/IP con un instrumento SCPI.
Métodos requeridos:
- enviar(comando): Envía una orden (no espera respuesta).
- preguntar(comando): Envía una consulta y retorna la respuesta devuelta por el equipo.
- cerrar(): Finaliza la conexión de red liberando recursos.
Valores por defecto del constructor: IP 127.0.0.1 y puerto 5555.
Cada comando debe enviarse finalizado en '\n', y cada respuesta recibida finaliza en '\n'.
"""

import socket


class Instrumento:
    """
    Cliente TCP orientado a objetos para comunicación con instrumentos SCPI sobre LAN.

    Atributos:
        direccion (str): Dirección IP del equipo (por defecto "127.0.0.1").
        puerto (int): Puerto TCP del servicio SCPI (5555 para osciloscopio, 5556 para multímetro).
        sock (socket.socket): Descriptor de socket TCP para el transporte de bytes.
        archivo (file-like): Envoltorio缓冲 creado con makefile() para facilitar la lectura
                             línea por línea terminada en '\n'.
    """

    def __init__(self, direccion="127.0.0.1", puerto=5555):
        """
        Inicializa el cliente y establece inmediatamente la conexión TCP con el instrumento.
        """
        self.direccion = direccion
        self.puerto = puerto
        # Creación del socket TCP IPv4 (AF_INET, SOCK_STREAM)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.direccion, self.puerto))
        # makefile("r") permite leer respuestas basadas en texto mediante readline()
        # evitando problemas de fragmentación típicos de recv() crudo en TCP
        self.archivo = self.sock.makefile("r", encoding="utf-8")

    def enviar(self, comando):
        """
        Envía una orden de control o configuración (ENVIAR) sin esperar respuesta.

        Garantiza que el comando termine estrictamente con el carácter salto de línea '\\n',
        el cual actúa como delimitador de fin de mensaje en el protocolo SCPI.
        """
        if not comando.endswith("\n"):
            comando = comando + "\n"
        self.sock.sendall(comando.encode("utf-8"))

    def preguntar(self, comando):
        """
        Envía una consulta (QUERY) y aguarda la línea de respuesta correspondiente.

        Retorna:
            str: El texto de respuesta devuelto por el instrumento, eliminando el
                 delimitador final '\\r\\n' o '\\n'.
        """
        self.enviar(comando)
        respuesta = self.archivo.readline()
        return respuesta.rstrip("\r\n")

    def cerrar(self):
        """
        Cierra de manera prolija el archivo de lectura y la conexión de socket subyacente.
        """
        try:
            self.archivo.close()
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass


# -----------------------------------------------------------------------------
# Bloque de Pruebas Unitarias (asserts)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import time
    parsear_idn = __import__("01_identificacion").parsear_idn

    # Intentamos conectar con el osciloscopio virtual en localhost:5555.
    # Si el instrumento no está corriendo en otra terminal, para cumplir con el requisito
    # de que "Cada archivo .py tiene que poder ejecutarse solo con python3 05_cliente.py",
    # levantamos automáticamente el instrumento virtual en hilos daemon en segundo plano.
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
        hilo_xdm = threading.Thread(
            target=instrumento_virtual.servir,
            args=(5556, instrumento_virtual.responder_xdm, "XDM1041"),
            daemon=True,
        )
        hilo_ads.start()
        hilo_xdm.start()
        time.sleep(0.3)  # Pausa breve para permitir el bind del socket servidor
        inst = Instrumento("127.0.0.1", 5555)

    # 1. Prueba mínima de consigna: *IDN?
    # Se consulta la identificación y se parsea utilizando la función del Ejercicio 1.
    resp_idn = inst.preguntar("*IDN?")
    assert resp_idn == "OWON,ADS3202,25470803,V1.2.0", f"Respuesta IDN inesperada: {resp_idn}"

    datos_idn = parsear_idn(resp_idn)
    assert datos_idn is not None, "El parseo de la respuesta IDN no debe ser None"
    assert datos_idn["modelo"] == "ADS3202", "El modelo identificado debe ser ADS3202"

    # 2. Prueba de alternancia entre orden (enviar) y consulta (preguntar):
    # Verificamos estado inicial, lo cambiamos a OFF y lo restablecemos a ON.
    estado_orig = inst.preguntar(":CH1:DISPlay?")
    assert estado_orig in ("ON", "OFF"), "El estado de display debe ser ON u OFF"

    inst.enviar(":CH1:DISPlay OFF")
    assert inst.preguntar(":CH1:DISPlay?") == "OFF", "El instrumento no aplicó la orden :CH1:DISPlay OFF"
    inst.enviar(":CH1:DISPlay ON")
    assert inst.preguntar(":CH1:DISPlay?") == "ON", "El instrumento no restableció la orden a ON"

    # 3. Caso raro: Consulta de comando no contemplado en el árbol SCPI del osciloscopio
    resp_error = inst.preguntar(":COMANDO:INVENTADO?")
    assert resp_error == "ERROR: comando desconocido", f"Respuesta de error inesperada: {resp_error}"

    # 4. Caso adicional: Conexión con el multímetro XDM1041 en el puerto alternativo 5556
    multimetro = Instrumento("127.0.0.1", 5556)
    resp_multi = multimetro.preguntar("*IDN?")
    assert resp_multi == "OWON,XDM1041,25470803,V4.4.0,3"
    datos_multi = parsear_idn(resp_multi)
    assert datos_multi["modelo"] == "XDM1041", "El modelo del multímetro debe ser XDM1041"
    multimetro.cerrar()

    # Cierre de conexión con el osciloscopio
    inst.cerrar()

    print("05_cliente.py: Todas las pruebas pasaron correctamente (OK).")
