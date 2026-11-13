# Bitácora de Uso de Inteligencia Artificial

**Materia:** Programación — Tecnicatura Universitaria en Telecomunicaciones (UTN FRBA)  
**Trabajo Final Integrador:** Banco de mediciones automatizado en Python  

En este documento dejamos registrado cómo y para qué usamos el modelo de lenguaje en el desarrollo del trabajo práctico, detallando qué le pedimos, qué nos devolvió, qué cosas tuvimos que corregirle o adaptar para que cumpla con la consigna, y cómo lo pusimos a prueba con nuestros propios asserts.

---

## Ejercicio 1 — Identificación del equipo (`01_identificacion.py`)

### 1. El prompt
```text
Escribí en Python la función parsear_idn(respuesta) para el TFI de Telecomunicaciones UTN FRBA.
Recibe la respuesta a *IDN? y devuelve un diccionario con 'fabricante', 'modelo', 'serie' y 'version',
o None si no sirve. Debe soportar respuestas de 4 campos (osciloscopio ADS3202: OWON,ADS3202,25470803,V1.2.0)
y de 5 campos (multímetro XDM1041: OWON,XDM1041,25470803,V4.4.0,3 descartando el quinto campo).
Debe manejar campos con espacios alrededor, cadenas vacías y respuestas como 'ERROR: comando desconocido'.
```

### 2. Qué contestó
Nos dio una función básica que separaba el texto con comas usando `split(",")` y guardaba los primeros cuatro elementos en un diccionario. Si la lista tenía menos de 4 elementos, devolvía `None`.

### 3. Qué cambiaste
* El código que dio fallaba si le pasabas algo que no fuera un texto (como `None` o un número), así que le agregamos una validación inicial de tipo.
* Si el instrumento devuelve un mensaje de error (por ejemplo `"ERROR: comando desconocido"`), la IA no lo filtraba bien si venía con comas. Le pusimos un filtro directo para que cualquier respuesta que empiece con `"ERROR"` devuelva `None`.
* Le aplicamos `.strip()` a cada campo por separado, porque si el instrumento manda espacios (ej: `" OWON , ADS3202 "`), los espacios quedaban adentro del diccionario.
* Agregamos un control para que si algún campo queda vacío (por ejemplo `"OWON,,123,V1.0"`), también se considere inválido.

### 4. Cómo lo verificaste
Escribimos pruebas con `assert` comprobando:
* Que lea bien tanto la respuesta de 4 campos del osciloscopio como la de 5 del multímetro (descartando el último número).
* Que limpie los espacios y saltos de línea (`\n`).
* Varios casos raros: pasarle texto vacío, `None`, menos de 4 campos, campos vacíos en el medio y la respuesta de error `"ERROR: comando desconocido"`.

---

## Ejercicio 2 — Magnitudes (`02_magnitudes.py`)

### 1. El prompt
```text
Escribí dos funciones en Python:
a) a_numero(texto): convierte notación científica OWON (ej. '1.000000E+03') a float 1000.0, o None si no es número.
b) con_unidad(valor, unidad): devuelve texto legible para humanos usando prefijos SI (p, n, u, m, ninguno, k, M, G)
para dejar el número entre 1 y 999. Ejemplos: 1000 Hz -> '1 kHz', 2500 Hz -> '2.5 kHz', 2 V -> '2 V',
0.707 V -> '707 mV', 0.0005 s -> '500 us', 0 V -> '0 V'.
Ojo con el caso trampa: con_unidad(999.9999, 'Hz') debe dar '1 kHz' y no '1000 Hz'.
```

### 2. Qué contestó
Propuso usar logaritmos (`math.log10`) para calcular la potencia de 10 y elegir el prefijo, y después formateaba con `round()`.

### 3. Qué cambiaste
* Descartamos el logaritmo porque si el valor es 0 o negativo da error matemático en Python. En su lugar armamos una lista ordenada con las escalas fijas: `p`, `n`, `u`, `m`, sin prefijo, `k`, `M` y `G`.
* Manejamos el caso especial de `0 V` directo con un `if valor == 0`.
* Corregimos la **trampa del redondeo**: si tenés `999.9999 Hz`, al redondearlo a 3 decimales pasa a ser `1000.0` y se sale del rango de 1 a 999. Le agregamos una condición para que si el número redondeado llega a 1000, lo divida por 1000 y salte al siguiente prefijo (`k`).
* Cuidamos el formato visual: si el número es entero (como `2.0` o `707.0`) mostramos `"2 V"` y `"707 mV"` sin decimales feos, pero si tiene decimales reales (como `2.5`) los dejamos como `"2.5 kHz"`.

### 4. Cómo lo verificaste
Pusimos asserts con todos los ejemplos que estaban en la tabla de la consigna (`1000 Hz`, `2500 Hz`, `2 V`, `0.707 V`, `0.0005 s`, `0 V`). Verificamos especialmente que `con_unidad(999.9999, "Hz")` devuelva exactamente `"1 kHz"`, y probamos con números negativos y prefijos chicos y grandes (`pF`, `GHz`).

---

## Ejercicio 3 — Órdenes y consultas (`03_comandos.py`)

### 1. El prompt
```text
Escribí en Python es_consulta(comando) y validar(comando).
validar debe devolver None si está bien o un mensaje de error si viola alguna de estas 7 reglas:
1. No vacío
2. Empieza con : o con *
3. No hay dos espacios seguidos
4. Hay a lo sumo un ?
5. El ? va al final
6. Una orden lleva un solo argumento (:CH1:SCALe 1 v la rompe)
7. Una consulta no lleva argumento (:CH1:DISPlay ON? la rompe)
```

### 2. Qué contestó
Una serie de condiciones `if` chequeando cada punto y devolviendo distintos textos explicativos.

### 3. Qué cambiaste
* Guardamos los textos de error en constantes arriba de todo (tipo `ERROR_VACIO`, `ERROR_PREFIJO`, etc.) para no equivocarnos al compararlos en las pruebas.
* Nos aseguramos de que las órdenes (las que no tienen `?`) tengan exactamente un comando y un parámetro separados por un solo espacio (`len(partes) == 2`). Así detecta tanto si le faltan argumentos como si le sobran (como el caso de `:CH1:SCALe 1 v` que tiene dos).
* Para las consultas, nos aseguramos de que no tengan ningún espacio en el medio (`" " in comando`), porque una consulta no tiene que llevar parámetros.

### 4. Cómo lo verificaste
Hicimos un assert para cada uno de los 7 ejemplos que la consigna decía que rompían las reglas, verificando que devuelva el mensaje de error esperado. Además probamos comandos válidos reales del osciloscopio (`*IDN?`, `:CH1:DISPlay ON`, etc.) comprobando que devuelvan `None`.

---

## Ejercicio 4 — Configurar un canal (`04_configurar.py`)

### 1. El prompt
```text
Escribí comandos_de_canal(canal, display, acoplamiento, sonda, escala) en Python.
Devuelve la lista con los 4 comandos en este orden:
:CH1:DISPlay <display>, :CH1:COUPling <acoplamiento>, :CH1:PROBe <sonda>, :CH1:SCALe <escala>.
Si el canal no es CH1 ni CH2 devuelve None.
```

### 2. Qué contestó
La función simple que revisa el canal y arma la lista de cadenas con f-strings.

### 3. Qué cambiaste
* La función era directa, pero le sumamos la verificación estricta de que si le pasan el canal en minúscula (`"ch1"`) o cualquier otra cosa devuelva `None`.
* En la parte de pruebas agregamos la **"prueba que vale por diez"** que pide la consigna: importamos la función `validar` del ejercicio 3 y pasamos cada uno de los 4 comandos generados por esa función para confirmar que cumplen todas las reglas de formato.

### 4. Cómo lo verificaste
* Comparamos la lista devuelta contra la que pedía el PDF para CH1 y CH2.
* Hicimos un bucle con `assert validar(cmd) is None` para cada comando generado.
* Probamos con canales inválidos (`"CH3"`, `"ch1"`, `""`, `None`) esperando `None`.

---

## Ejercicio 5 — El cliente (`05_cliente.py`)

### 1. El prompt
```text
Escribí una clase Instrumento en Python usando socket para hablarle por TCP a un equipo SCPI.
Métodos: __init__(direccion="127.0.0.1", puerto=5555), enviar(comando), preguntar(comando), cerrar().
Cada comando debe enviarse terminado en '\n' y cada respuesta recibida termina en '\n'.
```

### 2. Qué contestó
Una clase que creaba un socket en el constructor y usaba `socket.sendall()` y `socket.recv(1024)`.

### 3. Qué cambiaste
* Cambiamos el `recv(1024)` crudo por `self.sock.makefile("r")` y `readline()`. En TCP los mensajes pueden llegar en pedazos o acumularse; con `readline()` te asegurás de leer exactamente una línea entera hasta el `\n`.
* Aseguramos que `enviar()` siempre agregue el `\n` al final si el usuario no lo puso, para que el instrumento no se quede colgado esperando.
* En el bloque `__main__`, como la consigna pide que el archivo se pueda probar solo, agregamos un bloque `try/except ConnectionRefusedError` que levanta el instrumento virtual en un hilo secundario si no estaba prendido de antes. Así las pruebas pasan solas sin dar error de conexión.

### 4. Cómo lo verificaste
* Le preguntamos `*IDN?` y verificamos que responda `"OWON,ADS3202,25470803,V1.2.0"`.
* Probamos mandar una orden para apagar el canal (`:CH1:DISPlay OFF`), consultamos si cambió, y lo volvimos a encender.
* Probamos un comando inventado para ver que devuelva `"ERROR: comando desconocido"`.
* Nos conectamos también al puerto 5556 para comprobar que hable con el multímetro (`XDM1041`).

---

## Ejercicio 6 — El barrido (`06_barrido.py`)

### 1. El prompt
```text
Escribí barrer(instrumento, canales) que pide las 3 magnitudes de cada canal:
:MEASUrement:<canal>:FREQuency?
:MEASUrement:<canal>:PKPK?
:MEASUrement:<canal>:CYCRms?
Devuelve una lista de diccionarios con canal, magnitud, unidad, texto_crudo y valor (float o None si hubo error).
```

### 2. Qué contestó
La función con dos bucles (uno para canales y otro para las 3 magnitudes), llamando a `instrumento.preguntar()`.

### 3. Qué cambiaste
* Usamos nuestra función `a_numero()` del ejercicio 2 para convertir lo que responde el equipo a float.
* Cuidamos una regla importante que remarcaba el apunte: si el equipo contesta con error, en el diccionario el campo `valor` tiene que quedar en `None`, pero en `texto_crudo` hay que guardar el mensaje tal cual vino para saber qué pasó.
* Siguiendo el consejo del apunte ("Cómo probar esto sin prender el instrumento"), armamos una clase simulada `InstrumentoMock` en las pruebas. Esta clase tiene su propio método `preguntar()` que devuelve valores fijos sin red.

### 4. Cómo lo verificaste
* Con el mock verificamos que al barrer CH1 y CH2 devuelva exactamente 6 diccionarios con los campos y valores esperados.
* Simulamos una respuesta con error para ver que `valor` quede en `None` y `texto_crudo` guarde `"ERROR: comando desconocido"`.
* Probamos pasarle una lista vacía de canales y comprobamos que devuelva `[]`.

---

## Ejercicio 7 — La verificación (`07_verificacion.py`)

### 1. El prompt
```text
Escribí en Python:
a) vrms_teorico(vpp): devuelve Vrms para senoide (Vpp / 2 / sqrt(2)), o None si no tiene sentido físico.
b) coincide(medido, teorico, tolerancia=0.02): True si |medido - teorico| / |teorico| <= tolerancia.
c) verificar_canal(filas, canal): busca PKPK y CYCRMS del canal en el barrido y devuelve un diccionario con el resultado.
```

### 2. Qué contestó
Escribió las 3 funciones aplicando las fórmulas de física y comparando el error relativo contra el 2%.

### 3. Qué cambiaste
* En `vrms_teorico` agregamos que si la tensión es menor o igual a cero, o si no es un número, devuelva `None`, porque físicamente una tensión pico a pico no puede ser negativa ni nula en una señal real.
* En `verificar_canal` hicimos que devuelva un diccionario bien claro con el canal, si coincide o no (`True`/`False`), los valores medidos, el teórico y el porcentaje de error.
* Agregamos la prueba clave que pedía el apunte: **la prueba de la onda cuadrada**. Para una onda cuadrada de 2 Vpp, el Vrms es 1 V y no 0.707 V. Le pasamos esos datos a la función para confirmar que devuelve `coincide == False`.

### 4. Cómo lo verificaste
* Probamos las fórmulas matemáticas para 2 V y 0.8 V.
* Probamos `coincide` con una medición con poco ruido (0.27% de error -> da True) y con una corrida (3.2% de error -> da False).
* Probamos la onda cuadrada confirmando que da False.
* Probamos con barridos donde faltaban datos o donde hubo error en la lectura.

---

## Ejercicio 8 — El registro de la sesión (`08_log.py`)

### 1. El prompt
```text
Escribí analizar_linea(linea) y leer_log(ruta).
Ignorar: línea vacía y que empieza con #.
Rechazar: no tiene 6 campos, hora imposible (ej. 25:61:00), canal que no es CH1 ni CH2,
magnitud que no es FREQ, PKPK ni CYCRMS, valor no convertible a número.
Ojo con la línea con tabulaciones.
```

### 2. Qué contestó
Un parser que separaba con `split()` y validaba los campos con condiciones y conversiones.

### 3. Qué cambiaste
* Nos aseguramos de usar `linea.split()` sin ningún argumento entre los paréntesis. Como explicaba el apunte, si usás `split(" ")` perdés la línea 105 del log que está separada con tabulaciones (`\t`).
* Validamos la hora partiendo por los dos puntos (`hora.split(":")`) y revisando que las horas estén entre 0 y 23, y los minutos y segundos entre 0 y 59.
* Al revisar el archivo real `mediciones.log`, descubrimos que la línea 65 tenía el texto `"NaN"`. En Python `float("NaN")` no tira error pero no es un número válido de laboratorio, así que agregamos `math.isnan(valor)` para rechazarla correctamente.
* La función `analizar_linea` devuelve `(None, None)` si la línea se ignora (comentarios o en blanco), `(None, motivo)` si se rechaza, y `(medicion, None)` si es válida.

### 4. Cómo lo verificaste
* Probamos líneas de prueba para cada una de las causas de rechazo (hora imposible, canal raro, etc.).
* Corrimos `leer_log` directamente sobre el archivo `mediciones.log` que nos dio la cátedra y verificamos que encuentre las 6 series y detecte exactamente las 8 líneas que tenían errores, sin perder la línea que tenía tabulaciones.

---

## Ejercicio 9 — Estadística de una serie (`09_estadistica.py`)

### 1. El prompt
```text
Escribí resumen(valores) y fuera_de_rango(valores, minimo, maximo) en Python.
resumen devuelve diccionario con n, minimo, maximo, promedio, desvio (muestral dividido por n - 1),
o None si está vacía. Con n=1 desvío es 0.0.
fuera_de_rango devuelve posiciones de valores fuera del rango (extremos cuentan adentro).
```

### 2. Qué contestó
Las fórmulas de promedio y desvío estándar, y una comprensión de lista para buscar los índices fuera de rango.

### 3. Qué cambiaste
* Verificamos que si la lista viene vacía o con `None` devuelva `None`.
* Revisamos que el cálculo del desvío divida por `n - 1` (desvío muestral) y no por `n`, y controlamos que si `n == 1` devuelva `0.0` para no dividir por cero.
* En `fuera_de_rango` nos aseguramos de que la condición sea `v < minimo or v > maximo`, para que los valores que caen justo en los bordes se consideren adentro.

### 4. Cómo lo verificaste
* Hicimos una prueba manual con 8 números conocidos para chequear que la cuenta dé exacta.
* Probamos con un solo número para ver que el desvío dé `0.0`.
* Corrimos el control que pedía la consigna: calcular el resumen de la serie de frecuencias de CH1 del log real y verificar que el promedio dé a menos del 0.5% de 1000 Hz (dio 999.26 Hz, o sea 0.07% de error) y el desvío sea menor a 5 Hz (dio 2.74 Hz).

---

## Ejercicio 10 — El informe (`10_informe.py`)

### 1. El prompt
```text
Escribí armar_informe(idn, series, verificaciones) que devuelve el informe completo como un string puro,
sin hacer print ni abrir archivos.
Debe mostrar el instrumento identificado, una línea por serie con n, promedio, mínimo y máximo
formateados con con_unidad, y el resultado de las verificaciones.
Al ejecutarse el archivo como main, debe realizar el barrido en vivo, verificar los canales, leer el log y mostrar el informe.
```

### 2. Qué contestó
Un esqueleto que armaba el texto juntando líneas en una lista y haciendo `"\n".join(lineas)`.

### 3. Qué cambiaste
* Conectamos todo el programa usando las funciones de los 9 ejercicios anteriores.
* Mejoramos el diseño del texto para que quede prolijo, encolumnado y fácil de leer, mostrando las unidades con `con_unidad` (Hz, kHz, V, mV, uV).
* Respetamos la consigna de que `armar_informe` sea una **función pura**: no hace `print()` ni abre archivos, solo recibe los datos calculados y devuelve el texto. El `print()` se hace recién al final de todo en el bloque principal.

### 4. Cómo lo verificaste
* Probamos `armar_informe` pasándole datos de prueba fijos y usando `assert` sobre el texto devuelto.
* Corrimos el archivo completo de punta a punta: se conecta al osciloscopio virtual, hace el barrido de CH1 y CH2, verifica que sean senoides, lee el historial de `mediciones.log` e imprime el informe final completo en la pantalla.

---

## Preguntas para la Defensa Oral

Respuestas directas y claras para las preguntas típicas de los profesores:

1. **¿Por qué en el ejercicio 7 no se puede usar `==` para comparar una medición?**  
   Porque en la realidad los instrumentos tienen ruido e incertidumbre (el instrumento virtual le agrega a propósito un temblor aleatorio de $\pm 0.5\%$). Dos lecturas casi nunca van a ser idénticas a nivel de decimales. Por eso se define una tolerancia (en este caso el 2%) y se comprueba si el valor medido cae dentro de esa franja alrededor del teórico.

2. **Mostrame una prueba tuya y explicame qué error estaría detectando.**  
   En `07_verificacion.py`, la prueba de la onda cuadrada. Le pasamos una señal con $V_{pp} = 2\text{ V}$ y $V_{rms} = 1\text{ V}$. Si el programa estuviera mal hecho y aceptara cualquier cosa diciendo que siempre coincide, esa prueba fallaría. La prueba confirma que nuestro código sabe distinguir una senoide de una cuadrada y dice que no coincide.

3. **Si borro esta línea de tu código, ¿qué prueba tuya se pone en rojo?**  
   * Si en `02_magnitudes.py` borrás el control del redondeo (`if escalado_redondeado >= 1000.0:`), la prueba de `con_unidad(999.9999, "Hz")` falla porque devolvería `"1000 Hz"` en vez de `"1 kHz"`.
   * Si en `08_log.py` cambiás `linea.split()` por `linea.split(" ")`, la prueba de la línea 105 (que tiene tabulaciones) falla y salta la aserción de que no debe estar en la lista de rechazadas.

4. **¿Qué hace `split()` sin argumentos que no hace `split(" ")`?**  
   `split(" ")` busca únicamente el espacio común. Si hay dos espacios seguidos genera elementos vacíos, y si hay tabulaciones (`\t`) no las separa. En cambio, `split()` sin argumentos junta cualquier grupo de espacios, tabulaciones o saltos de línea y los toma como un solo separador, limpiando además los espacios de las puntas.

5. **¿Por qué `barrer` recibe el instrumento por parámetro en vez de crearlo adentro?**  
   Para poder probar la función sin necesidad de tener el instrumento prendido ni usar la red. Como lo recibe por parámetro, en las pruebas le podemos pasar un objeto "de mentira" (*mock*) que conteste siempre lo mismo. Eso hace que las pruebas sean rápidas, no dependan de la red y no fallen por el temblor aleatorio.

6. **Esta parte la escribió un modelo. ¿Cómo comprobaste que estaba bien?**  
   No nos quedamos con lo primero que devolvió el modelo. Revisamos el código línea por línea, le agregamos manejo de casos raros (como campos vacíos o valores `NaN`), y armamos pruebas con `assert` tanto para casos normales como para los casos límite que marcaba el enunciado. Además, comparamos los resultados del log contra los valores esperados que daba la cátedra.
