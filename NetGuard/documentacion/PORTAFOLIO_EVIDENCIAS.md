# Portafolio digital de evidencias — NetGuard

Este documento es una lista de capturas y artefactos que el equipo debe completar durante su demostración. No se deben insertar capturas simuladas ni afirmar que el repositorio está publicado si no se ha subido.

| Evidencia | Archivo o comando | Qué debe mostrar la captura |
|---|---|---|
| Estructura del proyecto | VS Code, carpetas `compilador`, `ply`, `nativo`, `tests` | Archivos del proyecto y módulos organizados. |
| Análisis léxico | `--tokens` | Tokens, lexemas, líneas y categorías. |
| Árboles y notaciones | `--arbol` | Árbol, prefija y postfija derivadas del AST. |
| Pila semántica | `--traza` | POper, PTipos, POptr y PSaltos. |
| Tabla de símbolos/direcciones | `--tabla --direcciones` | Tipos, ámbitos y direcciones virtuales. |
| Código intermedio | `--cuadruplos` | Única representación intermedia: cuádruplas. |
| Optimización | `--optimizado --comparar` | Cuádruplas originales/optimizadas, bitácora y equivalencia de resultados. |
| Funciones/recursión/estructuras | `tests/execution/recursion.ng`, `estructuras.ng` | `FUNC`, `CALL`, `RET`, `NEWSTRUCT` y campos. |
| Registros físicos | `--registros` | RAX, RDX, XMM0/XMM1, registros de argumentos y política local. |
| Generación de ASM | `--asm salida_netguard.asm --no-ejecutar` | Archivo `.asm` y segmentos `.rodata`, `.data`, `.text`. |
| Ejecución nativa | `nativo/compilar_linux.sh` y el binario | Resultado del ejecutable Linux x86-64. |
| Pruebas | `pruebas.py`, `pruebas_rubrica.py`, `pruebas_final.py` | Resúmenes de las tres suites. |
| 5,000 eventos | `--reporte reporte_5000.txt` | 5,000 procesados, 626 alertas y 4,374 marcas del log simulado. |
| LOG correcto/incorrecto | `registro_correcto_500.log` y `registro_incorrecto_500.log` | Comparación: 500 aceptados sin R02 frente a 494 aceptados y seis advertencias R02. |
| Repositorio | GitHub/GitLab publicado | URL real, historial de commits y CI. |

## Autoevaluación del equipo

| Competencia | Evidencia | Nivel / límite |
|---|---|---|
| Análisis semántico | `semantic.py`, `symtable.py`, `tests/semantic/` | Implementado y probado para los tipos/errores soportados. |
| Código intermedio | `codegen.py`, `--cuadruplos` | Cuádruplas solamente. Prefija/postfija se muestran desde el AST. |
| Optimización | `optimizer.py`, `--comparar`, benchmark | Implementada con análisis global y de ciclos de alcance acotado. |
| Código objeto | `asm_codegen.py`, `runtime.c`, suite x86-64 | Probado en Linux x86-64 con GCC; no es backend Windows. |
| Registros | `register_alloc.py`, `--registros` | Política local; no asignación global por vida útil. |
| Documentación | Informe, GLC, arquitectura, manual y glosario | Incluida; completar datos del equipo y docente. |
| Capturas | Evidencias de la PC de presentación | Pendiente del equipo. |
| Repositorio/versiones | GitHub/GitLab y CI | Pendiente de publicación desde la cuenta del equipo. |

## Lista de cotejo para la entrega

- [ ] Completar autores, grupo y docente en el informe.
- [ ] Ejecutar las suites en la computadora de exposición.
- [ ] Capturar tokens, árboles, pila, tabla de símbolos, cuádruplas y optimización.
- [ ] Generar un `.asm` y, desde Linux/WSL, compilarlo y ejecutarlo.
- [ ] Capturar pruebas positivas y errores intencionales.
- [ ] Publicar el repositorio y verificar la acción de CI.
- [ ] Añadir capturas y valoración docente al portafolio.
