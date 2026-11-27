# NETGUARD — Informe técnico final del proyecto integrador

**Tecnológico Nacional de México**  
**Instituto Tecnológico de Oaxaca**  
**Ingeniería en Sistemas Computacionales**  
**Asignatura:** Lenguajes y Autómatas II  
**Proyecto integrador:** Diseño e implementación de un compilador para un lenguaje prototipado.  
**Sistema propuesto:** NetGuard — Lenguaje para análisis de registros de red.  
**Fecha:** noviembre de 2026.  
**Autores:** Completar nombres de los integrantes.  
**Docente:** Completar nombre de la docente.

---

## Índice del informe

1. Resumen y palabras clave.
2. Introducción, problemática, justificación y objetivos.
3. Marco teórico y conceptual.
4. Diagnóstico y contextualización.
5. Especificación formal del lenguaje.
6. Diseño de arquitectura del compilador.
7. Tema 1: análisis semántico.
8. Tema 2: código intermedio.
9. Tema 3: optimización.
10. Tema 4: generación de código objeto.
11. Pruebas y evaluación de resultados.
12. Manual de uso resumido.
13. Limitaciones, conclusiones y trabajo futuro.
14. Referencias y anexos.

## 1. Resumen

NetGuard es un compilador educativo para un lenguaje específico de dominio orientado a analizar archivos de eventos de red. Se diseñó una sintaxis propia con archivos `.ng`, declaraciones tipadas, condiciones, ciclos, funciones con parámetros y retorno, estructuras de datos, y acciones de alerta. Su arquitectura incluye análisis léxico y sintáctico con PLY, análisis semántico basado en tablas de tipos, pilas, árboles de expresiones y tabla de símbolos; generación de cuádruplas como única representación intermedia; optimizaciones; y dos rutas de ejecución: una máquina virtual escrita en Python y un generador de ensamblador x86-64 para Linux que trabaja junto con un runtime C. La evaluación incluye suites de regresión, pruebas negativas, algoritmos como factorial y Fibonacci, comparación optimizada/no optimizada y un caso con 5,000 eventos simulados. El proyecto permite estudiar de forma observable todas las etapas requeridas para un compilador prototipado, sin afirmar capacidades de captura de tráfico en tiempo real.

**Palabras clave:** compiladores, gramática libre de contexto, análisis semántico, código intermedio, optimización, ensamblador, registros de red, PLY.

## 2. Introducción y planteamiento

### 2.1 Problemática

Los registros de eventos de red reúnen información de accesos y tráfico; analizarlos manualmente es repetitivo y dificulta revisar reglas de comportamiento. En el contexto académico, también existe el reto de visualizar las etapas de compilación de forma integrada, desde tokens hasta instrucciones ejecutables. NetGuard aborda ambos problemas mediante un lenguaje de reglas pequeño, verificable y con código objeto demostrable.

### 2.2 Justificación

El proyecto integra conceptos de Lenguajes y Autómatas II con una aplicación relacionada con la carrera de Ingeniería en Sistemas Computacionales. El uso de logs simulados permite evaluar reglas de forma reproducible y segura, mientras que la arquitectura modular hace posible identificar cada fase y sus productos intermedios.

### 2.3 Objetivo general

Diseñar e implementar un compilador para un lenguaje prototipado que procese reglas sobre registros de eventos de red y exhiba sus etapas de análisis, generación de código intermedio, optimización y traducción a ensamblador x86-64.

### 2.4 Objetivos específicos

- Definir la gramática libre de contexto, reglas de tipo y semántica del lenguaje `.ng`.
- Implementar análisis léxico, sintáctico y semántico con reportes de errores.
- Construir árboles, pilas semánticas, tablas de símbolos y direcciones virtuales.
- Generar y optimizar código intermedio exclusivamente en cuádruplas.
- Aplicar y evaluar técnicas locales, globales, de ciclos y de mirilla.
- Traducir instrucciones a ensamblador y ejecutar casos de estudio sobre Linux x86-64.
- Probar el sistema con datos simulados y documentar los resultados y limitaciones.

## 3. Marco teórico y conceptual

### 3.1 Gramática libre de contexto

Una GLC define producciones con las que se reconocen estructuras de instrucciones válidas. En NetGuard, las funciones `p_...` del módulo `parser.py` constituyen las reglas de la gramática utilizada por PLY yacc. La semántica se asocia a acciones realizadas durante la reducción de producciones.

### 3.2 Análisis semántico

Una construcción puede ser léxica y sintácticamente válida, pero incompatible en significado. Por ello se comprueban tipos, existencia de identificadores, ámbitos, firmas de funciones y campos de estructuras. El compilador mantiene una tabla dinámica de símbolos y cuatro pilas auxiliares para operandos, tipos, operadores y saltos.

### 3.3 Árboles, notaciones y código intermedio

El árbol de expresión preserva la prioridad de operadores. Su preorden produce notación prefija y su postorden produce postfija. NetGuard utiliza exclusivamente cuádruplas `(operador, argumento1, argumento2, resultado)` como representación intermedia, elegida entre las alternativas permitidas por la rúbrica.

### 3.4 Optimización de código

La optimización transforma código intermedio para reducir operaciones redundantes sin alterar su comportamiento esperado. NetGuard realiza plegado de constantes, propagación de constantes, simplificación algebraica, reducción de fuerza, subexpresiones comunes, eliminación de instrucciones muertas, mejoras de saltos y movimientos de invariantes de bucles `FOR EACH`. El desempeño real puede variar por el equipo y la carga.

### 3.5 Arquitectura de microprocesadores y memoria

En x86-64, registros como `RAX`, `RDX`, `RDI`, `RSI`, `RCX`, `R8`, `R9` y `XMM0`/`XMM1` se utilizan para operaciones, parámetros y retornos. El ensamblador contiene segmentos `.rodata` (literales), `.data` (globales) y `.text` (instrucciones). Cada función requiere una pila de llamadas con marco propio y puntero base `rbp`.

### 3.6 Marco contextual y legal

Los LOG incluidos son **simulados**, y el proyecto no intercepta comunicaciones de terceros ni realiza análisis de redes en vivo. Se debe evitar subir a GitHub archivos privados, credenciales o datos de tráfico reales sin autorización. El uso de la biblioteca PLY y GNU GCC se realiza como herramientas de desarrollo académico; deben respetarse sus licencias correspondientes. El proyecto no sustituye políticas institucionales de seguridad.

## 4. Diagnóstico y contextualización

### 4.1 Alcance del prototipo

NetGuard admite tipos `int`, `float`, `string`, `boolean` e `ip`, estructuras `STRUCT` de campos básicos y colecciones `event[]` provenientes de `.log`. Permite `LIMIT`, `LET`, asignación, operaciones aritméticas y lógicas, `IF/ELSE`, `WHILE`, `FOR EACH`, `FUNCTION`, `RETURN`, llamadas con hasta seis argumentos, recursión, casts explícitos `int()` y `float()`, `ALERT` y `MARK`. Los ámbitos son globales y locales por bloque/función; se detectan redeclaraciones.

### 4.2 Arquitectura de destino

Se seleccionó Linux x86-64 como destino nativo por permitir generar `.asm` con GNU as, ensamblar y enlazar con GCC y ejecutar el binario sobre una CPU real. En Windows se usa Python para la compilación y máquina virtual; la ejecución nativa se efectúa mediante WSL/Ubuntu.

## 5. Especificación formal del lenguaje

La especificación completa se encuentra en `ESPECIFICACION_GLC.md`, que incluye terminales, producciones BNF/EBNF, reglas semánticas y tabla de tipos. La fuente normativa del parser es `compilador/parser.py`.

**Ejemplo:**

```text
LIMIT maxAttempts : int = 5
LIMIT trafficLimit : float = 500.0
LOAD EVENTS FROM "red_laboratorio.log" AS traffic
FOR EACH event IN traffic
    IF event.failedAttempts >= maxAttempts OR event.trafficMB > trafficLimit
        ALERT "Evento sospechoso" FROM event.sourceIP
    ELSE
        MARK event AS "normal"
    END
END
```

La primera condición dispara la alerta a partir de **cinco o más intentos fallidos**; la segunda cuando el tráfico **supera 500 MB**. La lógica está escrita en `.ng`, no codificada directamente dentro del lector de LOG.

## 6. Arquitectura general e integración

El flujo es: **`.ng` → lexer/PLY → parser/GLC y semántica → tabla de símbolos/direcciones y AST → cuádruplos → optimizador → VM o backend x86-64 → salida/reporte`**. `compilador/__init__.py` orquesta las primeras fases; `netguard.py` expone los comandos CLI. Para información completa de los módulos y el diagrama de bloques consultar `ARQUITECTURA_IMPLEMENTACION.md`.

## 7. Tema 1: análisis semántico

Las acciones semánticas se ejecutan dentro de las producciones PLY al reconocer declaraciones, expresiones y estructuras. Para la expresión `intentos >= 5`, se comprueba que los operandos sean numéricos y que el resultado sea booleano. `PilaSemantica` organiza los operandos y operadores; `PSaltos` guarda direcciones de salto pendientes; `TablaSimbolos` gestiona ámbitos y direcciones virtuales.

La conversión **implícita** permite asignar un `int` a `float`; la **explícita** permite transformar valores numéricos con `int(expr)` y `float(expr)`. Los casos de error comprueban variables no declaradas, colisiones de nombres, incompatibilidad de tipos, funciones desconocidas, número de argumentos, retornos incompatibles y campos inexistentes.

## 8. Tema 2: generación de código intermedio

Se generan cuádruplos a medida que se reducen expresiones. Ejemplo:

| Nº | Operador | Argumento 1 | Argumento 2 | Resultado |
|---|---|---|---|---|
| 1 | `>=` | `event.failedAttempts` | `5` | `t1` |
| 2 | `GOTOF` | `t1` | — | `L_else` |
| 3 | `ALERT` | `"Evento sospechoso"` | `event.sourceIP` | — |

Los saltos son rellenados mediante *backpatching* una vez que se conoce su destino. El lenguaje genera cuádruplos para `WHILE`, `FOR EACH`, `IF/ELSE`, y para `FUNC`, `PARAM`, `CALL`, `RET` en funciones de usuario. El operador `NEWSTRUCT` crea estructuras dinámicas; sus campos forman parte de los operandos de lectura/escritura.

**Caso adicional:** `tests/execution/recursion.ng` implementa factorial recursivo con parámetros y un retorno de tipo `int`.

## 9. Tema 3: optimización

Se aplican pasadas consecutivas de folding, propagación, simplificación, subexpresiones comunes, eliminación de código muerto, optimizaciones de saltos y reducción de fuerza. Para ciclos se incorporó movimiento de invariantes de `FOR EACH`; en `WHILE` operan las mejoras generales, sin afirmar una optimización universal de invariantes.

La opción `--comparar` ejecuta el original y el optimizado y compara las líneas generadas, además de las instrucciones intermedias ejecutadas. La herramienta `herramientas/benchmark.py` informa tiempo y memoria asignada observada en Python; `herramientas/perfil_codigo_objeto.py` describe registros y stack frames nativos. Un ahorro en cuádruplos no garantiza una mejora de tiempo en todo escenario.

## 10. Tema 4: generación de código objeto

El módulo `asm_codegen.py` transforma cuádruplos optimizados en ensamblador x86-64, almacenado en un archivo `.asm`. `register_alloc.py` establece la asignación local de registros físicos y su política de derrames a memoria. Se emplean `RAX/RDX` para enteros, `XMM0/XMM1` para flotantes y registros de parámetros al realizar llamadas; se respeta alineación de marcos de pila y uso de `call/ret`.

El ensamblador contiene `.rodata`, `.data` y `.text`. Las rutinas auxiliares de C, en `nativo/runtime.c`, permiten cargar LOG, leer campos, generar alertas y administrar instancias `STRUCT`. Factorial, Fibonacci, recursión y estructuras han sido probados en ejecutables Linux x86-64, sin confundir esa generación con la máquina virtual Python.

## 11. Validación experimental y resultados

### 11.1 Suites

El paquete incluye tres suites que se reportan por separado porque algunas verificaciones se solapan: **41/41 pruebas base**, **21/21 pruebas adicionales de rúbrica** y **38/38 verificaciones integrales finales**, todas correctas en el entorno de construcción Linux x86-64. La suite final exige que las líneas del intérprete original, el optimizado y el binario generado coincidan en casos representativos. Estos resultados deben volver a verificarse en la computadora donde se expondrá.

### 11.2 Prueba principal con 5,000 eventos

El archivo simulado `ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log` se procesó mediante las reglas de NetGuard.

| Indicador | Resultado |
|---|---:|
| Registros válidos procesados | 5,000 |
| Alertas emitidas | 626 |
| Eventos marcados como normales | 4,374 |
| Comparación original/optimizada | Reportes iguales; 46,259 → 40,005 instrucciones ejecutadas (13.5% menos) |

El conteo deriva del archivo de simulación proporcionado para pruebas, no de capturas de una red real. Se anexan resultados de consola reproducibles en `evidencias/RESULTADOS_PRUEBAS.txt`.

### 11.3 Pruebas negativas

Se diseñaron programas con errores léxicos, sintácticos y semánticos deliberados (`L`, `P`, `S`) para comprobar la detección temprana y evitar ejecución de entradas incorrectas. También se comprueba un error de ejecución por división entre cero (`R03`). El éxito de una prueba negativa significa **obtener el error esperado**.

## 12. Manual resumido

Con Python instalado y desde la carpeta `NetGuard`:

```bash
python3 pruebas.py
python3 pruebas_rubrica.py
python3 pruebas_final.py
python3 netguard.py ejemplos/reglas.ng --presentacion
python3 netguard.py ejemplos/reglas.ng --asm salida_netguard.asm --no-ejecutar
bash nativo/compilar_linux.sh salida_netguard.asm nativo/netguard_nativo
./nativo/netguard_nativo
```

En Windows se usa `py` para los comandos Python. GCC y Bash requieren Linux x86-64 o WSL para la ejecución nativa. Consultar `MANUAL_USUARIO.md` para todas las banderas y problemas frecuentes.

## 13. Limitaciones, conclusiones y trabajo futuro

### Limitaciones

Se trata de un lenguaje educativo y de dominio, no de propósito general. Se admiten hasta seis argumentos por función, declaraciones de función previas a su uso, un retorno final obligatorio, estructuras de campos primitivos, acceso a eventos offline y backend nativo Linux x86-64. La política de registros es **local y determinística**, no un asignador global optimizado por análisis de vida. El lector de LOG en C no refleja todas las advertencias detalladas del lector Python sobre registros malformados. Las pruebas no sustituyen una verificación formal ni pruebas en todo procesador/OS posible.

### Conclusiones

El proyecto integra las etapas centrales de un compilador prototipado y demuestra el tránsito real de un lenguaje fuente hasta un archivo `.asm` enlazado y ejecutable, además de la ruta de intérprete original. La separación modular permite estudiar y depurar cada etapa con comandos reproducibles. Las pruebas de simulación muestran coincidencia de resultados entre las rutas Python y nativa para los casos evaluados.

### Trabajo futuro

Se podrían añadir arreglos de usuario, campos de estructuras anidadas, funciones adelantadas y procedimientos sin retorno, asignación global por análisis de vida útil, análisis de flujo más avanzado para bucles `WHILE`, perfiles nativos de uso de memoria y soporte de código objeto Windows/otras arquitecturas. Ninguna de estas extensiones se presenta como ya desarrollada.

## 14. Referencias y anexos

**Fuente institucional:** Tecnológico Nacional de México, Instituto Tecnológico de Oaxaca. (2026). *Proyecto integrador: Diseño e implementación de un compilador completo para un lenguaje prototipado* [Rúbrica de la asignatura Lenguajes y Autómatas II].

**Bibliografía técnica de consulta:**

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, techniques, and tools* (2nd ed.). Addison-Wesley.
- Cooper, K. D., & Torczon, L. (2012). *Engineering a compiler* (2nd ed.). Morgan Kaufmann.
- Free Software Foundation. (s. f.). *Using the GNU Compiler Collection (GCC)* [Documentación técnica].
- System V ABI Working Group. (s. f.). *System V application binary interface: AMD64 architecture processor supplement* [Especificación técnica].

**Anexos en el ZIP:** `ESPECIFICACION_GLC.md`, `ARQUITECTURA_IMPLEMENTACION.md`, `MANUAL_USUARIO.md`, `GUIA_DEFENSA.md`, `MATRIZ_CUMPLIMIENTO_FINAL.md`, `PORTAFOLIO_EVIDENCIAS.md`, `GLOSARIO.md/.docx/.pdf`, la rúbrica en PDF, código fuente, suites de pruebas y archivos de evidencia verificados.
