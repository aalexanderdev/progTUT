# Trabajo Final Integrador — Programación
**Tecnicatura Universitaria en Telecomunicaciones (TUT)**  
**Universidad Tecnológica Nacional — Facultad Regional Buenos Aires (UTN FRBA)**  
**Ciclo lectivo:** 2026  
**Docentes:** Prof. Pablo E. Hernández, Prof. Candela Fernández Ibáñez  

---

## Integrantes:

* **Nombre y Apellido:** Richard Martin Lagos
* **Nombre y Apellido:** Esteban Balbiani
* **Nombre y Apellido:** Leonardo Omar Galiano
* **Nombre y Apellido:** Alexander Arrua

---

## Descripción del Proyecto

El proyecto implementa un **banco de mediciones automatizado en Python** capaz de:
1. Comunicarse con instrumentos de laboratorio (Osciloscopio OWON ADS3202 y Multímetro OWON XDM1041) mediante comandos estándar **SCPI** sobre una conexión de red TCP/IP (LAN).
2. Configurar canales, verificar sintaxis de órdenes/consultas y realizar barridos de mediciones de magnitudes en tiempo real (frecuencia, tensión pico a pico y tensión RMS).
3. Contrastar y verificar las mediciones en vivo contra las predicciones de la física (relación $V_{rms} = \frac{V_{pp}}{2\sqrt{2}}$ para ondas senoidales puras) considerando tolerancias relativas de medición.
4. Procesar y filtrar registros históricos de sesiones (`mediciones.log`), rechazando datos anómalos o corruptos y contemplando formatos con tabulaciones.
5. Calcular estadísticas descriptivas completas (media, desvío estándar muestral, máximos y mínimos) y generar un informe final formateado y legible para operadores humanos mediante funciones puras.

---

## Estructura del Repositorio

El repositorio sigue estrictamente la convención de nombres requerida por la cátedra:

```text
.
├── README.md                 <- Información institucional, integrantes y documentación
├── bitacora-ia.md            <- Registro detallado de interacción y verificación con IA
├── instrumento_virtual.py    <- Emulador SCPI provisto por la cátedra (no modificado)
├── mediciones.log            <- Archivo de registro histórico de laboratorio (no modificado)
├── 01_identificacion.py      <- Ejercicio 1: Parseo de respuesta al comando *IDN?
├── 02_magnitudes.py          <- Ejercicio 2: Conversión numérica y formato con prefijos SI
├── 03_comandos.py            <- Ejercicio 3: Validación sintáctica de comandos SCPI
├── 04_configurar.py          <- Ejercicio 4: Generación de secuencia de configuración de canal
├── 05_cliente.py             <- Ejercicio 5: Cliente socket TCP para comunicación SCPI
├── 06_barrido.py             <- Ejercicio 6: Barrido automático de mediciones por canal
├── 07_verificacion.py        <- Ejercicio 7: Verificación teórica vs experimental ($V_{rms}$)
├── 08_log.py                 <- Ejercicio 8: Procesamiento y saneamiento de registros de sesión
├── 09_estadistica.py         <- Ejercicio 9: Cálculo de media, desvío muestral y rango
└── 10_informe.py             <- Ejercicio 10: Armado del informe final y ejecución integrada
```

---

## Requisitos y Ejecución

* **Python 3.8+** (se utiliza exclusivamente la biblioteca estándar: `socket`, `math`, `sys`, `os`, `time`, etc.). No requiere instalar dependencias adicionales vía `pip`.

### 1. Ejecución del emulador (Instrumento Virtual)
En una terminal independiente, ejecutar:
```bash
python3 instrumento_virtual.py
```
El instrumento quedará a la escucha en `127.0.0.1:5555` (Osciloscopio ADS3202) y `127.0.0.1:5556` (Multímetro XDM1041). Para detenerlo presionar `Ctrl + C`.

### 2. Ejecución individual de ejercicios
Cada archivo `.py` es completamente autónomo y contiene su propio bloque de pruebas con `assert`:

```bash
python3 01_identificacion.py
python3 02_magnitudes.py
python3 03_comandos.py
python3 04_configurar.py
python3 05_cliente.py
python3 06_barrido.py
python3 07_verificacion.py
python3 08_log.py
python3 09_estadistica.py
python3 10_informe.py
```

*Nota:* Los ejercicios `05_cliente.py` y `10_informe.py` se conectan al instrumento virtual si ya está en ejecución, o levantan automáticamente una instancia local en un hilo si se corren de forma aislada para garantizar que las pruebas pasen sin fallas.
