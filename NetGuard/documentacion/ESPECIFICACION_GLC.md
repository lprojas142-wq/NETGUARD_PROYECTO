# Especificación formal del lenguaje NetGuard

## 1. Identidad y dominio

**Extensión:** `.ng`. **Implementación:** Python y PLY (lexer `lex`, parser `yacc` LALR). **Objetivo:** evaluar reglas de seguridad sobre eventos provenientes de registros `.log` estructurados. El lenguaje permite programación numérica elemental como demostración de los requisitos del compilador. No captura tráfico en vivo.

## 2. Terminales y categorías léxicas

- Tipos básicos: `int`, `float`, `string`, `boolean`, `ip`.
- Declaraciones y dominio: `STRUCT`, `NEW`, `LIMIT`, `LET`, `LOAD`, `EVENTS`, `FROM`, `AS`, `ALERT`, `MARK`.
- Control y funciones: `IF`, `ELSE`, `END`, `WHILE`, `FOR`, `EACH`, `IN`, `FUNCTION`, `RETURN`.
- Literales: `INT_LIT`, `FLOAT_LIT`, `STRING_LIT`, `IP_LIT`, `true`, `false`.
- Comparación: `<`, `<=`, `>`, `>=`, `==`, `!=`; lógica `AND`, `OR`, `NOT`; aritmética `+`, `-`, `*`, `/`.
- Símbolos auxiliares: `=`, `:`, `.`, `(`, `)`, `,`; identificadores `ID`; comentarios desde `#` al final de línea.

## 3. GLC abreviada (BNF/EBNF legible)

El archivo **`compilador/parser.py` es la fuente normativa de producciones PLY**; el siguiente esquema representa sus categorías principales. `*` denota cero o más, `+` uno o más, `?` opcional.

```text
<programa>       ::= <estructura>* <limit>* <funcion>* <carga>+ <sentencia>+
<estructura>     ::= STRUCT ID <campo_estructura>+ END
<campo_estructura> ::= ID ':' <tipo_basico>
<tipo>           ::= int | float | string | boolean | ip | ID_de_estructura
<limit>          ::= LIMIT ID ':' <tipo> '=' <expresion>
<funcion>        ::= FUNCTION ID '(' <parametros>? ')' ':' <tipo>
                     <sentencia>* RETURN <expresion> END
<parametros>     ::= ID ':' <tipo> (',' ID ':' <tipo>)*
<carga>          ::= LOAD EVENTS FROM STRING_LIT AS ID
<sentencia>      ::= LET ID ':' <tipo> '=' <expresion>
                   | <destino> '=' <expresion>
                   | IF <expresion> <sentencia>* [ELSE <sentencia>*] END
                   | WHILE <expresion> <sentencia>* END
                   | FOR EACH ID IN ID <sentencia>* END
                   | ALERT <expresion> FROM <expresion>
                   | MARK ID AS <expresion>
                   | <llamada>
<destino>        ::= ID | ID '.' ID
<llamada>        ::= ID '(' <expresion> (',' <expresion>)* ')'
<expresion>      ::= expresiones aritméticas, lógicas y relacionales
                   | NOT <expresion> | '-' <expresion>
                   | '(' <expresion> ')' | int '(' <expresion> ')'
                   | float '(' <expresion> ')' | NEW ID
                   | ID '.' ID | <llamada> | <literal>
```

La precedencia aplicada mediante no terminales en `parser.py` es: `OR` menor que `AND`, luego `NOT`, relaciones, sumas/restas, multiplicación/división, unarios y factores. Las acciones de `p_...` en el parser realizan semántica y generan cuádruplos durante la reducción de reglas.

**Alcances:** funciones después de `LIMIT` y antes de `LOAD`; no se admiten declaraciones de función anidadas ni referencias adelantadas a funciones no definidas. Las funciones admiten entre 0 y 6 parámetros y tienen un `RETURN` final obligatorio; pueden llamarse recursivamente. Estructuras `STRUCT` incluyen exclusivamente campos de tipos básicos (sin anidamiento de estructuras).

## 4. Reglas semánticas dirigidas por sintaxis (resumen)

| Producción conceptual | Acción al reducir | Comprobación o efecto |
|---|---|---|
| `LIMIT id : tipo = expr` | Busca nombre, crea símbolo global, cuádruplo `=` | Error `S02` si duplicado; `S03` si tipos incompatibles. |
| `LET id : tipo = expr` | Crea símbolo local y dirección, cuádruplo `=` | Regla `asignable(tipo, expr.tipo)`. |
| `expr op expr` | Saca operandos, consulta tabla de tipos, construye `Nodo` y temporal | Error `S04` en tipos incompatibles. |
| `IF expr` | Genera `GOTOF` con destino pendiente; apila salto | `S05` si condición no booleana. |
| `ELSE`/`END` | Inserta `GOTO` y rellena destinos pendientes | Pila `PSaltos`. |
| `WHILE expr` | Marca comienzo, comprueba condición y genera salto | `GOTO` de retorno y `GOTOF` de salida. |
| `FUNCTION` | Inserta símbolo y parámetros en ámbito propio; cuádruplo `FUNC` | Parámetros tipados, máximo seis. |
| `RETURN expr` | Contrasta tipo de retorno y genera `RET` | Error `S13` por incompatibilidad. |
| `f(args)` | Comprueba firma, genera `PARAM` por argumento y `CALL` | Errores `S11`, `S12`, `S03`. |
| `STRUCT` | Registra nombre y tipos de campos | Error `S02` por definición duplicada. |
| `NEW Struct` | Genera `NEWSTRUCT` en temporal | Error `S14` si la estructura no existe. |
| `obj.campo` | Busca estructura y comprueba campo | Error `S07` si campo inexistente. |
| `int(expr)` y `float(expr)` | Genera `CAST_INT` o `CAST_FLOAT` | Error `S10` si origen no numérico. |

## 5. Tabla de tipos

| Operación | Tipos admitidos | Resultado |
|---|---|---|
| `+`, `-`, `*` | `int`/`float` | `int` si ambos son `int`; si no `float`. |
| `/` | Numéricos | `float`; `R03` al dividir entre cero. |
| `<`, `<=`, `>`, `>=` | Numéricos | `boolean`. |
| `==`, `!=` | Numéricos o ambos `string`/`boolean`/`ip` | `boolean`. |
| `AND`, `OR`, `NOT` | `boolean` | `boolean`. |
| Asignación y parámetros | Igual tipo o `int → float` | Promoción implícita si corresponde. |
| `int(float)` | Numérico | Truncamiento hacia cero. |
| `float(int)` | Numérico | Doble precisión. |

## 6. Registro de errores

- **L**: léxicos (`L01` carácter inválido, `L02` cadena sin cerrar).
- **P**: sintácticos (`P01` símbolo inesperado, `P02` final prematuro).
- **S**: semánticos (`S01` no declarada, `S02` duplicada, `S03` tipo incompatible, `S05` condición inválida, `S07` campo desconocido, `S10` cast inválido, `S11` función ausente, `S12` argumentos, `S13` retorno, `S14` estructura no definida).
- **R**: ejecución (`R01` LOG inexistente, `R02` registro inválido, `R03` división entre cero / límite de ejecución).

Los archivos `ejemplos/errores/` y `tests/semantic/` contienen casos negativos deliberados para demostrar las detecciones.

## 7. Notaciones y representación intermedia

Expresión fuente: `(a + 2) * b`.

- **Infija:** `(a + 2) * b`.
- **Prefija:** `* + a 2 b` (preorden del árbol de expresión).
- **Postfija:** `a 2 + b *` (postorden del árbol de expresión).
- **Cuádruplos:** `(+ , a, 2, t1)` seguido de `(*, t1, b, t2)`.
NetGuard utiliza **exclusivamente cuádruplas** como representación intermedia. La rúbrica permite elegir una representación; el equipo seleccionó cuádruplas porque hacen explícitos el operador, los dos argumentos y el destino del resultado, lo que facilita temporales, direcciones virtuales, optimización y saltos.

## 8. Cuádruplos disponibles

| Grupo | Operadores principales |
|---|---|
| Asignación y cálculo | `=`, `+`, `-`, `*`, `/`, `NEG`, `NOT`, `AND`, `OR`, `<`, `<=`, `>`, `>=`, `==`, `!=` |
| Conversión | `CAST_INT`, `CAST_FLOAT` |
| Control | `GOTO`, `GOTOF`, `END` |
| Eventos | `LOAD`, `FE_INIT`, `FE_NEXT`, `ALERT`, `MARK` |
| Funciones | `FUNC`, `PARAM`, `CALL`, `RET` |
| Estructuras | `NEWSTRUCT`, lectura/escritura de campos como operandos con clase `structcampo` |

El backend traduce los cuádruplos a x86-64 y se apoya en funciones auxiliares C solo para E/S de registros y estructuras; las operaciones aritméticas, condiciones y saltos se codifican directamente en ensamblador.
