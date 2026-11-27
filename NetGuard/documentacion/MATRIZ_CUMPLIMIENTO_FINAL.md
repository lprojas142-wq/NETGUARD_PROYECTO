# Matriz de cumplimiento y lista de cotejo — NetGuard

**Documento rector:** `documentacion/Rubrica_Proyecto_Integrador.pdf` (Lenguajes y Autómatas II). **Edición revisada:** 22 de noviembre de 2026.

**Estados:** ✅ implementado y comprobado en las pruebas incluidas; ◐ implementado con alcance limitado; □ requiere una acción/evidencia del equipo o una plataforma externa. La matriz evalúa el código real; no convierte una característica futura en una característica terminada.

## Tema 1 — Análisis semántico

| Requisito | Estado | Evidencia y alcance |
|---|---|---|
| Acciones semánticas dirigidas por sintaxis | ✅ | Las producciones `p_...` de `compilador/parser.py` ejecutan acciones de `semantic.py`, `symtable.py` y `codegen.py`. |
| Árboles de expresiones y pila semántica | ✅ | `Nodo`, preorden/postorden y `PilaSemantica` con POper, PTipos, POptr y PSaltos; opciones `--arbol` y `--traza`. |
| Comprobación de tipos | ✅ | `resultado()` y `asignable()` cubren aritmética, lógica, relaciones y asignaciones. |
| Conversiones implícitas y explícitas | ✅ | Promoción `int` → `float`; casts `int(expr)` y `float(expr)` mediante `CAST_INT` / `CAST_FLOAT`; pruebas de `while_cast.ng`, promociones y error S10. |
| Tabla dinámica de símbolos y direcciones | ✅ | `TablaSimbolos` administra ámbitos y asigna direcciones virtuales a globales, locales, temporales, constantes, colecciones y referencias de función. |
| Detección/gestión de errores semánticos | ✅ | `errors.py`; pruebas S01–S14 presentes para variables, tipos, funciones, parámetros, retornos, campos y estructuras. |

## Tema 2 — Generación de código intermedio

| Requisito | Estado | Evidencia y alcance |
|---|---|---|
| Infija a prefija y postfija | ✅ | `Nodo.preorden()` y `Nodo.postorden()` producen notaciones desde el árbol de expresión; se muestran con `--arbol`. No es un conversor independiente de cadenas arbitrarias. |
| Representación intermedia | ✅ | **Solo cuádruplas** `(op, arg1, arg2, resultado)`, en `codegen.py`; esta es la única representación intermedia que genera y consume el compilador. |
| Declaración, expresión y asignación | ✅ | `LIMIT`, `LET`, asignaciones y operaciones aritméticas/lógicas en `parser.py` y `codegen.py`. |
| Estructuras de control | ✅ | `IF/ELSE`, `WHILE` y `FOR EACH`, con `GOTO`, `GOTOF`, `FE_INIT` y `FE_NEXT`; incluye ciclos anidados. |
| Funciones y llamadas | ✅ | `FUNCTION`, parámetros, `RETURN`, `PARAM`, `CALL`, `RET` y recursión. Restricciones: hasta seis parámetros, declaración previa al uso y retorno final obligatorio. |
| Estructuras definidas por el usuario | ✅ | `STRUCT`, `NEW`, lectura/escritura de campos básicos; sin estructuras anidadas ni arreglos dinámicos de usuario. |

## Tema 3 — Optimización

| Requisito | Estado | Evidencia y alcance |
|---|---|---|
| Optimización local | ✅ | Plegado de constantes, propagación, simplificación algebraica y subexpresiones comunes en `optimizer.py`. |
| Optimización global / flujo de control | ◐ | Eliminación de código muerto e inalcanzable y análisis de saltos; no es un análisis global completo de vivacidad/flujo de datos sobre todo CFG. |
| Optimización de ciclos | ◐ | Movimiento de invariantes implementado para el patrón `FOR EACH`; las pasadas locales también se aplican en cuerpos `WHILE`, pero no hay LICM general para todos los bucles. |
| Optimización de mirilla | ✅ | Simplificación de saltos a saltos y eliminación de saltos a la instrucción siguiente; limpieza de código inalcanzable. |
| Eliminación de código muerto, propagación, álgebra y reducción de fuerza | ✅ | Pasadas identificables y casos de prueba en `ejemplos/optimizacion.ng`. La reducción de fuerza incluye patrones concretos como multiplicar por 2 y dividir reales por constante. |
| Evaluación de recursos antes/después | ◐ | `--comparar` mide cuádruplas ejecutadas; `herramientas/benchmark.py` mide mediana de tiempo de pared y pico de memoria Python con `tracemalloc`; `perfil_codigo_objeto.py` informa tamaño estático de stack frame, ranuras, líneas ASM y política de registros. No mide ciclos de CPU, RSS nativo ni trazas de uso real de registros. |

## Tema 4 — Generación de código objeto

| Requisito | Estado | Evidencia y alcance |
|---|---|---|
| Asignación a registros físicos | ◐ | `register_alloc.py` y `--registros` describen el mapeo local por instrucción: RAX/RDX, XMM0/XMM1 y registros de argumentos. Los resultados se derraman a memoria; no hay asignación global por intervalos de vida ni coloración de grafos. |
| Traducción a ensamblador `.asm` | ✅ | `asm_codegen.py` traduce cuádruplas optimizadas a GNU as, sintaxis Intel, Linux x86-64. |
| Ensamblado, enlace y ejecución | ✅ en Linux x86-64 | `nativo/compilar_linux.sh`, `runtime.c`, GCC y `pruebas_final.py` comprueban ejecutables nativos. En Windows se requiere WSL/Ubuntu para esta parte. |
| Segmentos de código/datos/texto y stack frame | ✅ | Secciones `.text`, `.data`, `.rodata`; prólogo/epílogo con RBP y pila alineada; el runtime C gestiona heap de colecciones y estructuras. |
| Suite de código objeto | ✅ | `tests/execution/` incluye factorial, Fibonacci, recursión, funciones y estructuras; la suite final compara salidas ASM frente a VM. |

## Entregables de documentación y evaluación

| Entregable | Estado | Acción o ubicación |
|---|---|---|
| Especificación formal de GLC y acciones semánticas | ✅ | `ESPECIFICACION_GLC.md`, contrastada con `compilador/parser.py`. |
| Manual de arquitectura e implementación | ✅ | `ARQUITECTURA_IMPLEMENTACION.md`; incluye capas, tablas, pilas, memoria, cuádruplas y backend. |
| Manual de usuario e instalación | ✅ | `MANUAL_USUARIO.md` y `README.md`; comandos para Windows y Linux/WSL. |
| Suite `/tests/semantic/` | ✅ | Casos intencionales de tipos, variables, casts, funciones y estructuras. |
| Suite `/tests/intermediate/` | ✅ | Ciclos anidados y WHILE/casting. |
| Suite `/tests/execution/` | ✅ | Factorial, Fibonacci, funciones, recursión, promociones y estructuras. |
| Informe técnico final | ◐ | `INFORME_TECNICO_FINAL.md/.docx/.pdf`; el equipo debe completar nombres de integrantes y docente y revisar el formato solicitado por su profesora. |
| Demostración en vivo y capturas | □ | Ejecutar los comandos en la PC de exposición y capturar salidas reales de VS Code/terminal. |
| Repositorio GitHub/GitLab y control de versiones | □ | Publicar desde una cuenta del equipo; `INSTRUCCIONES_GITHUB.md` orienta el proceso. No se inventa una URL de repositorio publicado. |
| Portafolio con evidencias y lista de cotejo | ◐ | `PORTAFOLIO_EVIDENCIAS.md`; faltan capturas del equipo y valoración docente. |

## Validación reproducida en Linux x86-64

Las tres suites se ejecutaron en el entorno de revisión:

- `python pruebas.py`: **41/41**.
- `python pruebas_rubrica.py`: **21/21**.
- `python pruebas_final.py`: **38/38**, incluyendo ensamblado y ejecución nativa con GCC.

Las suites se solapan en algunas capacidades; no deben sumarse como si fueran 100 pruebas independientes. Con el archivo de práctica simulado de 5,000 eventos, `reglas.ng` produce **626 alertas y 4,374 marcas normales**.

## Restricciones que deben declararse en la defensa

- NetGuard procesa archivos LOG offline; no captura tráfico de red en tiempo real.
- El backend de objeto es GNU as / Intel para Linux x86-64; no produce `.exe` nativo de Windows.
- La asignación de registros es local y determinista, no un asignador global avanzado.
- El optimizador usa análisis de flujo simplificado; la LICM se limita a patrones de `FOR EACH`.
- Las métricas de benchmark son orientativas y dependen del equipo y del entorno.
- Las funciones admiten como máximo seis parámetros; estructuras de campos primitivos, sin arreglos dinámicos ni anidamiento.
