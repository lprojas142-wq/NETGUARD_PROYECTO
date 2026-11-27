# Manual de arquitectura e implementación — NetGuard

## 1. Arquitectura por etapas

```text
Archivo .ng
    |
    v
lexer.py (PLY lex) --> tokens --> parser.py (PLY yacc / GLC)
                                  |             |
                                  v             v
                          semantic.py       symtable.py
                      tipos/árboles/pilas  símbolos/direcciones
                                  \             /
                                   v           v
                                  codegen.py
                             cuádruplas (única representación intermedia)
                                      |
                                      v
                                 optimizer.py
                            local / global / bucles / mirilla
                                      |
                         +------------+-------------+
                         |                          |
                         v                          v
                       vm.py               asm_codegen.py
                  intérprete Python           .asm x86-64
                  informe .txt                    |
                                                GCC
                                                  |
                                          ejecutable Linux
                                                  |
                                    runtime.c (LOG, ALERT, STRUCT)
```

## 2. Tabla de símbolos y de direcciones

`TablaSimbolos` mantiene una **pila de diccionarios** por ámbito; `todos` permite conservar las entradas para su visualización aunque un ámbito ya se haya cerrado. Un símbolo guarda `nombre`, `categoria`, `tipo`, `ambito`, `nivel`, `dir`, `modificable`, `valor_inicial` y `linea`. Se asignan direcciones virtuales numéricas al crear símbolos y temporales.

| Rango virtual | Uso |
|---|---|
| 1000 en adelante | Variables globales (LIMIT). |
| 2000 en adelante | Variables locales, variables de ciclo y parámetros. |
| 3000 en adelante | Temporales. |
| 4000 en adelante | Constantes. |
| 5000 en adelante | Colecciones de eventos. |
| 6000 en adelante | Referencias de funciones para la tabla de símbolos. |

La dirección virtual **no equivale a la dirección física** de RAM. El backend la mapea a variables en `.data` o desplazamientos desde `rbp` en la pila. Cada llamada a función tiene un **marco de pila propio** para soportar recursión; los parámetros se pasan según la convención descrita abajo.

## 3. Pila semántica y árboles

La clase `PilaSemantica` administra `POper` (operandos), `PTipos` (tipos), `POptr` (operadores) y `PSaltos` (destinos pendientes). Al reducir una operación, consulta la regla de tipos (`resultado`), crea un temporal, genera su cuádruplo y crea un nodo del árbol de expresión. `Nodo.preorden()` y `Nodo.postorden()` muestran notación prefija y postfija. Los ámbitos se abren y cierran para IF, ELSE, WHILE, FOR y FUNCTION.

## 4. Gestión de errores

`errors.py` centraliza códigos, líneas y mensajes; `lexer.py`, `parser.py`, `semantic.py` y `vm.py` detectan errores según su etapa. Si hay errores de compilación, la CLI **no** ejecuta el programa. Los casos negativos se incluyen en `tests/semantic/` y `ejemplos/errores/`.

## 5. Optimización del código intermedio

`optimizer.py` transforma cuádruplos manteniendo una bitácora, reconstruye destinos de salto y compara el resultado antes/después usando `--comparar`.

| Familia | Implementación concreta |
|---|---|
| Local | Folding, propagación de constantes, simplificación algebraica, subexpresiones comunes. |
| Global | Eliminación de código muerto/inalcanzable, análisis básico del flujo por saltos. |
| Ciclos | Movimiento de expresiones invariantes en `FOR EACH`; otras pasadas locales también operan en cuerpos `WHILE`. |
| Mirilla | Simplificación de saltos consecutivos y saltos a la siguiente instrucción. |
| Reducción de fuerza | Algunas multiplicaciones por 2 se transforman en suma y divisiones reales por constante en multiplicación por recíproco. |

Las llamadas `CALL` y las operaciones de estructuras son puntos de efectos secundarios para no mover expresiones indebidamente. La optimización **no es una demostración formal de equivalencia en todos los programas posibles**; se verifica mediante regresiones y comparación de resultados.

## 6. Mapeo de cuádruplas a x86-64

La salida de `asm_codegen.py` usa **GNU as con sintaxis Intel**, arquitectura Linux x86-64, ABI System V. `register_alloc.py` formaliza una estrategia de asignación **local por instrucción**: carga operandos en registros temporales, ejecuta la operación y vuelca el resultado a la ubicación virtual mapeada en memoria.

| Cuádruplo | Código máquina representativo | Uso de registros |
|---|---|---|
| `=, x, —, y` | `mov`, `movsd` | `RAX` / `XMM0`. |
| `+, a, b, t1` | `add` / `addsd` | `RAX`, `RDX` o `XMM0`, `XMM1`. |
| `>, a, b, t1` | `cmp`, `setg` / `ucomisd`, `seta` | Registros generales o XMM. |
| `GOTOF, cond, —, n` | `test rax, rax` + `jz Ln` | `RAX`. |
| `GOTO, —, —, n` | `jmp Ln` | Sin registro dedicado. |
| `PARAM` | Guarda argumento de 64 bits en una ranura del marco | Ranura de pila temporal. |
| `CALL` | Carga hasta seis argumentos en `RDI`–`R9`; `call Lfuncion` | Convención de llamada propia para `.ng` numérica/punteros. |
| `RET` | Recupera el resultado de retorno, `leave`, `ret` | `RAX` o `XMM0`. |
| `NEWSTRUCT` | `call ng_struct_new` | Puntero en `RAX`. |
| `LOAD` / `ALERT` / `MARK` | `call ng_load` / `ng_alert` / `ng_mark` | ABI System V hacia C. |

Los argumentos `float` de funciones `.ng` se transfieren como sus **bits de 64** en registros enteros de argumento y se reconstruyen como dobles en la ranura de pila del receptor. El retorno `float` se devuelve en `XMM0`. Las llamadas a `runtime.c` obedecen el ABI de C; no deben confundirse ambas convenciones.

## 7. Segmentos y organización de memoria

```text
.section .rodata   Cadenas, mensajes, nombres de campos, rutas de entrada
.section .data     Constantes de arranque de variables globales (bloques .quad)
.section .text     main, FUNC, cálculo, control de flujo, CALL/RET
Stack frame       [rbp - offset] variables locales, parámetros, temporales,
                  scratch1, scratch2 y seis ranuras para argumentos
Heap (runtime C)  Colecciones dinámicas .log y estructuras definidas con NEW
```

El prólogo de cada función utiliza `push rbp`, `mov rbp, rsp`, `sub rsp, frame_alineado`; el epílogo `leave`, `ret`. El marco está **alineado a 16 bytes** para llamadas ABI System V. Las variables globales permanecen en `.data` y los locales/temporales se aíslan por marco de pila para soportar recursión. `--registros` imprime el mapeo de registros físicos y su estrategia de desbordamiento a pila.

**Límites explícitos:** no se aplican coloración de grafos ni asignación global por vida útil; en vez de eso se adopta un asignador local, con resultados escritos en memoria al terminar cada cuádruplo. Tampoco se generan binarios nativos de Windows ni se pretende reemplazar el sistema operativo para leer LOG.

## 8. Medición de recursos y equivalencia

- **Instrucciones:** `--comparar` cuenta cuádruplos ejecutados antes y después.
- **Tiempo y memoria de Python:** `herramientas/benchmark.py` mide mediana de tiempo wall-clock y pico de asignaciones observadas por `tracemalloc`. No equivale al RSS nativo.
- **Costo estático nativo:** `herramientas/perfil_codigo_objeto.py` informa tamaño de marco de pila, cuádruplos y líneas del `.asm`. La memoria real depende de la cantidad de eventos y estructuras.
- **Equivalencia:** `pruebas_final.py` coteja todas las líneas de salida del intérprete original, optimizado y binario nativo en casos representativos.

Un menor número de cuádruplos no **garantiza** menor tiempo en cualquier equipo. Las medidas deben interpretarse en conjunto con la carga, GCC y el entorno.

## 9. Casos de estudio

`tests/execution/`: factorial iterativo, Fibonacci, llamadas con parámetros, factorial recursivo, estructuras, promoción de tipos. `tests/intermediate/`: casts/WHILE y ciclos anidados. `tests/semantic/`: errores deliberados de tipos, funciones, casting, campos y definición de estructuras. `ejemplos/reglas.ng` + `ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log` validan el escenario principal de detección de eventos.
