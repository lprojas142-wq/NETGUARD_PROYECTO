# Glosario técnico de NetGuard

Este glosario reúne los términos que aparecen en el código, la documentación y la rúbrica del proyecto. Las definiciones describen cómo se usan en esta implementación.

| Término | Definición aplicada a NetGuard |
|---|---|
| Acción semántica | Código Python asociado a una producción de la gramática y ejecutado cuando el parser reconoce esa regla. |
| Ámbito (scope) | Región en la que una variable está visible; NetGuard administra ámbitos globales, de bloque y de función. |
| Análisis léxico | Primera etapa: reconoce lexemas y los clasifica como tokens. |
| Análisis sintáctico | Comprueba que la secuencia de tokens cumple la gramática libre de contexto. |
| Análisis semántico | Verifica declaraciones, tipos, compatibilidad de operaciones, ámbitos y uso válido de estructuras. |
| AST / árbol de expresión | Estructura jerárquica que representa operandos y operadores respetando la precedencia. |
| Back-End | Parte que ejecuta la representación intermedia o la traduce a ensamblador. |
| Backpatching | Técnica para completar posteriormente el destino de saltos cuyo número aún no se conoce al generarlos. |
| Benchmark | Medición repetida de rendimiento bajo una carga de prueba definida. |
| Bloque básico | Secuencia de instrucciones intermedias con una sola entrada y sin saltos internos, salvo al final. |
| Casting / conversión explícita | Cambio solicitado por el programador, por ejemplo `int(x)` o `float(x)`. |
| Código intermedio (IR) | Representación entre el lenguaje fuente y la ejecución. En este proyecto son exclusivamente cuádruplas. |
| Código objeto | Código destinado a una arquitectura; aquí se genera fuente ensamblador `.asm` para GNU as en Linux x86-64. |
| Código muerto | Instrucción cuyo resultado no afecta la salida ni el comportamiento observable y que puede eliminarse de forma segura. |
| Código inalcanzable | Instrucción a la que no existe un camino de control desde la entrada del programa o función. |
| Compilador | Programa que analiza un lenguaje fuente y lo traduce a otra representación. |
| Constante | Valor que no cambia durante la ejecución; NetGuard la registra en la tabla de constantes. |
| Cuádrupla | Instrucción intermedia de cuatro campos: operador, argumento 1, argumento 2 y resultado. |
| Dirección virtual | Identificador lógico usado para ubicar una variable/constante en la memoria administrada por el compilador; no es una dirección física de RAM. |
| DSL | *Domain Specific Language*: lenguaje especializado para un dominio. NetGuard usa `.ng` para reglas sobre logs. |
| EBNF / BNF | Notaciones para expresar formalmente las producciones de una gramática. |
| Ensamblador | Representación textual de instrucciones de una arquitectura, que después puede ensamblarse. |
| Expresión infija | Notación habitual con operadores entre operandos, por ejemplo `a + b`. |
| Expresión prefija | Notación con el operador antes de sus operandos, por ejemplo `+ a b`; en NetGuard se obtiene por preorden del árbol. |
| Expresión postfija | Notación con el operador después de sus operandos, por ejemplo `a b +`; se obtiene por postorden del árbol. |
| FE_INIT | Cuádrupla que inicializa el recorrido de una colección de eventos. |
| FE_NEXT | Cuádrupla que intenta obtener el siguiente evento de la colección. |
| Front-End | Capa de análisis del lenguaje: lexer, parser, semántica y tabla de símbolos. |
| Función recursiva | Función que se llama a sí misma; NetGuard admite recursión dentro de sus restricciones. |
| GLC | Gramática Libre de Contexto que define las instrucciones válidas del lenguaje. |
| GCC | GNU Compiler Collection; se usa para ensamblar/enlazar el backend nativo con `runtime.c`. |
| Generador de código | Módulo que convierte acciones semánticas y expresiones en cuádruplas. |
| Heap | Memoria dinámica; el runtime C la utiliza para colecciones de eventos y estructuras. |
| Identificador | Nombre definido por el usuario, por ejemplo `maxAttempts` o `traffic`. |
| Intérprete | Programa que ejecuta instrucciones de una representación; `vm.py` interpreta cuádruplas. |
| Lexer | Analizador léxico implementado con PLY Lex. |
| LALR(1) | Técnica de análisis sintáctico ascendente con un símbolo de anticipación; PLY Yacc la utiliza para construir el parser. |
| Lexema | Secuencia de caracteres concreta que coincide con un patrón de token, como `LIMIT` o `500`. |
| Literal | Valor escrito directamente en el fuente, como `5`, `500.0`, `true` o `"alerta"`. |
| Log / registro | Archivo de eventos guardados; contiene IP, tipo, puerto, intentos fallidos, tráfico y estado. |
| Middle-End | Capa que genera y optimiza el código intermedio. |
| Máquina virtual (VM) | Intérprete de cuádruplas escrito en Python que ejecuta la lógica de NetGuard. |
| Memoria virtual del compilador | Organización lógica de direcciones para globales, locales, temporales, constantes, colecciones y funciones. |
| Mirilla (peephole) | Optimización sobre una pequeña ventana de instrucciones, por ejemplo simplificar saltos consecutivos. |
| Optimizador | Módulo que transforma cuádruplas intentando reducir trabajo sin cambiar el resultado observable. |
| Operando | Valor o referencia utilizada por una instrucción; puede ser variable, constante, temporal, campo o función. |
| Parser | Analizador sintáctico construido con PLY Yacc. |
| Pila | Estructura LIFO: el último elemento insertado es el primero en salir. |
| Pila semántica | Conjunto de pilas que ayuda a procesar operandos, tipos, operadores y saltos durante el análisis. |
| POper | Pila de operandos usada por `PilaSemantica`. |
| PTipos | Pila paralela que guarda el tipo de cada operando. |
| POptr | Pila de operadores pendientes. |
| PSaltos | Pila de posiciones de cuádruplas de salto y regreso pendientes. |
| PLY | Biblioteca Python que proporciona Lex y Yacc para construir analizadores léxicos y sintácticos. |
| Promoción implícita | Conversión automática permitida por las reglas de tipos, como `int` a `float`. |
| Propagación de constantes | Sustituir usos de una variable por su valor conocido cuando es seguro. |
| Reducción de fuerza | Sustituir una operación por otra equivalente más simple en patrones concretos. |
| Registro físico | Registro de CPU como RAX, RDX o XMM0. El backend de NetGuard utiliza una política local y determinista. |
| Runtime | Código auxiliar de ejecución; `nativo/runtime.c` carga logs, expone campos y produce alertas/marcas. |
| Salto condicional (GOTOF) | Cuádrupla que cambia el flujo si la condición es falsa. |
| Salto incondicional (GOTO) | Cuádrupla que transfiere el control siempre a otro destino. |
| Segmento `.data` | Área del ensamblador destinada a datos globales inicializados/reservados. |
| Segmento `.rodata` | Área para datos de solo lectura, como cadenas y literales de texto. |
| Segmento `.text` | Área que contiene las instrucciones ejecutables. |
| Semántica dirigida por sintaxis | Enfoque en el que las reglas gramaticales ejecutan acciones semánticas al reconocerse. |
| Stack frame / marco de pila | Espacio reservado por una llamada a función para parámetros, locales y temporales. |
| Tabla de símbolos | Estructura que registra identificadores, categoría, tipo, ámbito, dirección y propiedades. |
| Temporal | Variable auxiliar generada por el compilador para guardar un resultado intermedio. |
| Token | Categoría léxica reconocida por el lexer. `ID`, `INT_LIT` y `IF` son ejemplos. |
| Tipo | Clasificación de valor, como `int`, `float`, `string`, `boolean`, `ip` o `event`. |
| Verificación de tipos | Comprobación de que operadores, argumentos, asignaciones y retornos usan tipos compatibles. |
| x86-64 | Arquitectura de 64 bits elegida como destino del backend de ensamblador. |

## Cómo explicar la cadena completa en una frase

El lexer convierte el `.ng` en tokens; el parser reconoce la GLC y ejecuta acciones semánticas; la tabla de símbolos y la pila validan nombres/tipos y construyen árboles; `codegen.py` produce cuádruplas; `optimizer.py` las mejora; `vm.py` las interpreta o `asm_codegen.py` las traduce a ensamblador x86-64 para Linux.

## Límites que no deben confundirse con errores

- La notación prefija y postfija se obtiene del AST; no existe un conversor independiente de cadenas de expresiones.
- Las direcciones virtuales no son direcciones reales de RAM.
- El asignador de registros es local por instrucción, no global por análisis de vida útil.
- El backend `.asm` se dirige a Linux x86-64, no a Windows PE.
- Los logs de demostración son archivos de entrada simulados; no son capturas de tráfico vivo.
