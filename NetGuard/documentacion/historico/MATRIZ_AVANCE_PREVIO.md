# NetGuard — matriz de cumplimiento de la rúbrica final

**Materia:** Lenguajes y Autómatas II · Instituto Tecnológico de Oaxaca  
**Documento base:** `Proyecto Integrador_Automatas 2.pdf`, apartados 1 a 4 y entregables.  
**Fecha del avance:** noviembre de 2026.  
**Naturaleza:** revisión técnica del ZIP de NetGuard y de su extensión de código objeto.

**Leyenda:** ✅ Evidencia implementada y ejecutable · 🟨 Implementado parcialmente o documentación pendiente · ⬜ Pendiente.

## Tema 1. Análisis semántico

| Criterio de la rúbrica | Estado | Evidencia y observaciones |
|---|---|---|
| Acciones semánticas dirigidas por sintaxis | ✅ | `compilador/parser.py` ejecuta acciones en producciones PLY |
| Árboles de expresiones | ✅ | `compilador/semantic.py`, función `dibujar_arbol`; `--arbol` |
| Pila semántica | ✅ | `semantic.py` con `POper`, `PTipos`, `POptr`, `PSaltos`; `--traza` |
| Comprobación de tipos | ✅ | `semantic.py` con `resultado()` y `asignable()` |
| Conversiones implícitas y explícitas | 🟨 | `int → float` implícita; casts `int(expr)` y `float(expr)` implementados para numéricos, no conversión universal |
| Tabla dinámica de símbolos y direcciones | ✅ | `symtable.py` con ámbitos y direcciones virtuales |
| Registro de errores semánticos | ✅ | `errors.py` y ejemplos `S01` a `S10`; nuevos tests `tests/semantic/` |

## Tema 2. Código intermedio

| Criterio | Estado | Evidencia y observaciones |
|---|---|---|
| Infija, prefija y postfija | ✅ | Árboles `Nodo.preorden()` y `Nodo.postorden()`; imprimir en `--arbol` |
| Representación en cuádruplos / triplos | ✅ | `codegen.py`, `--cuadruplos`, `--tripletas` |
| Declaraciones, asignaciones y expresiones | ✅ | `parser.py`, `semantic.py`, `codegen.py` |
| IF-ELSE, WHILE y FOR EACH con saltos | ✅ | Se añadieron `WHILE` y sus backpatchings en `parser.py`; ejemplo `ejemplos/while_cast.ng` |
| Invocación de funciones definidas por usuario | ⬜ | Falta definir gramática, alcance, parámetros, pila de llamadas y cuádruplos CALL/RET |
| Declaración de estructuras | 🟨 | El tipo de dominio `event` tiene campos fijos; falta sintaxis para estructuras nuevas del usuario |

## Tema 3. Optimización

| Criterio | Estado | Evidencia y observaciones |
|---|---|---|
| Local | ✅ | Folding, propagación de constantes, simplificación algebraica, reducción de fuerza, subexpresiones comunes |
| Global | ✅ | Eliminación de código muerto y de código inalcanzable |
| Ciclos | 🟨 | Movimiento de invariantes de `FOR EACH`; ampliar evaluación en ciclos `WHILE` |
| Mirilla | ✅ | Saltos a saltos, saltos inmediatos, eliminación de inalcanzable |
| Análisis de flujo y costos | 🟨 | `--comparar` mide instrucciones ejecutadas; `herramientas/benchmark.py` mide tiempo y memoria del intérprete; falta un análisis de registros/pila y experimentos repetidos formalizados |

## Tema 4. Código objeto

| Criterio | Estado | Evidencia y observaciones |
|---|---|---|
| Traducción de cuádruplos a `.asm` | ✅ | `compilador/asm_codegen.py`; bandera `--asm`; genera x86-64 GNU as con sintaxis Intel |
| Asignación de registros físicos | 🟨 | Asignación fija de `RAX`, `RDX`, `RDI`, `RSI`, `XMM0`, `XMM1` con derrames a pila; no hay un asignador completo por análisis de vida |
| Segmentos datos / código / pila | 🟨 | `.rodata` literales, `.data` globales, `.text` ejecutable, marco de pila en `main`; falta desarrollar marcos de pila de funciones definidas por el usuario |
| Ejecución ensamblada sobre el destino | ✅ | Linux x86-64 con `gcc` + `nativo/runtime.c`; ver `nativo/README.md` |
| Ejemplos clásicos en código objeto | ✅ | `tests/execution/factorial.ng`, `fibonacci.ng`; ver `pruebas_rubrica.py` |
| Equivalencia con el intérprete | ✅ | Probados 5,000 LOG: 626 alertas y 4,374 normales; además 21 pruebas adicionales correctas |

## Entregables del reporte y evidencia

| Entregable | Estado | Qué preparar o actualizar |
|---|---|---|
| Marco teórico: GLC, notaciones, optimización, CPU | 🟨 | Existe `NetGuard_Fases1y2_Proyecto_Integrador.pdf`, pero hay que integrar los cambios posteriores |
| Especificación de GLC + acciones semánticas | 🟨 | Actualizar producciones nuevas `WHILE`, `tipo_cast` y funciones cuando existan |
| Manual de arquitectura | 🟨 | Añadir el backend `.asm`, la interacción con `runtime.c` y el mapeo de registros |
| Manual de usuario y CLI | ✅ | `GUIA_PASO_A_PASO.txt` y `nativo/README.md`; explicar extensión `--asm` |
| Suite semántica, intermedia, ejecución | ✅ | `pruebas.py`, `pruebas_rubrica.py`, `tests/{semantic,intermediate,execution}/` |
| Presentación de traducción en vivo | 🟨 | Ensayo de `--presentacion`, `--asm`, compilación por `gcc` y ejecución nativa |
| GitHub/GitLab y control de versiones | ⬜ | No se incluye repositorio remoto verificable; crear y subir la versión final |
| Matriz de valoración / lista de cotejo | 🟨 | Este documento sirve de lista de cotejo, pero hay que adaptarlo al formato de evaluación de la profesora |

## Orden recomendado de cierre

1. **Crítico:** implementar funciones de usuario y definir `CALL/RET`, semántica de parámetros y stack frames; revisar estructuras para cubrir exactamente la gramática requerida.
2. **Crítico:** actualizar el reporte final para eliminar contradicciones con la Fase 2 (antes excluía `WHILE`, casts y código objeto) e incluir gramática y diagramas de la ruta `.asm`.
3. **Alto:** reforzar el backend con una política explícita de asignación de registros y pruebas de comportamiento de errores; registrar limitaciones de la versión Linux.
4. **Alto:** adjuntar resultados de benchmark y capturas de ejecución de `factorial.ng`, `fibonacci.ng` y los 5,000 eventos.
5. **Alto:** crear el repositorio Git y subir fuentes, documentación y evidencia, excluyendo binarios y `__pycache__`.
6. **Final:** ensayo de demostración en vivo y captura de resultados con la máquina en que se expondrá.

## Comandos de verificación

```bash
python pruebas.py
python pruebas_rubrica.py
python netguard.py ejemplos/reglas.ng --presentacion
python netguard.py ejemplos/while_cast.ng --arbol --cuadruplos --comparar
python herramientas/benchmark.py
python netguard.py ejemplos/reglas.ng --asm salida_netguard.asm --no-ejecutar
bash nativo/compilar_linux.sh salida_netguard.asm nativo/netguard_nativo
./nativo/netguard_nativo
```

> La generación y ejecución nativas requieren Linux x86-64 o WSL con GCC. En Windows puro, pueden ejecutarse el compilador Python y las pruebas no nativas.

**Criterio de honestidad académica:** los estados ✅ describen funciones realmente presentes; los 🟨 y ⬜ no deben presentarse como si ya estuvieran terminados.
