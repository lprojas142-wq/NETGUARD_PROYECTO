# Guía de exposición y defensa — NetGuard (8 a 12 minutos)

## 1. Presentación del problema

«NetGuard es un compilador educativo para un lenguaje propio `.ng`, orientado a analizar archivos de registros de eventos de red. El usuario escribe reglas; el compilador las valida, genera cuádruplas, las optimiza y las ejecuta mediante una máquina virtual Python o un backend de ensamblador Linux x86-64. La entrada son logs almacenados o simulados: no hacemos captura de red en vivo».

## 2. Mostrar `ejemplos/reglas.ng`

Explicar `LIMIT`, `LOAD EVENTS`, `FOR EACH`, `IF/ELSE`, `ALERT` y `MARK`. Identificar que `failedAttempts >= maxAttempts OR trafficMB > trafficLimit` genera una alerta cuando al menos una de las dos condiciones es verdadera.

## 3. Mostrar las tres capas

- **Front-End:** `lexer.py` reconoce tokens; `parser.py` reconoce la GLC y ejecuta acciones semánticas; `semantic.py` verifica tipos y construye árboles/pilas; `symtable.py` administra símbolos y direcciones.
- **Middle-End:** `codegen.py` genera exclusivamente cuádruplas; `optimizer.py` aplica las pasadas de optimización.
- **Back-End:** `vm.py` interpreta cuádruplas; `asm_codegen.py` produce ensamblador x86-64 y `runtime.c` resuelve E/S de logs y estructuras.

## 4. Ejecutar la demostración Python

```powershell
py pruebas.py
py pruebas_rubrica.py
py pruebas_final.py --sin-asm
py netguard.py ejemplos/reglas.ng --todo
```

En Windows, las pruebas nativas se omiten con `--sin-asm`; para compilar/ejecutar el ensamblador se requiere Linux x86-64 o WSL Ubuntu con GCC.

## 5. Explicar las evidencias

- `--tokens`: clasificación léxica.
- `--arbol`: AST, prefija y postfija.
- `--traza`: POper, PTipos, POptr, PSaltos.
- `--tabla`: variables, constantes, ámbitos y direcciones.
- `--cuadruplos`: cuatro campos `(op, arg1, arg2, resultado)`.
- `--optimizado --comparar`: técnicas aplicadas, menor cantidad de instrucciones y misma salida.
- `--registros`: política local de RAX/RDX, XMM y registros de argumentos.
- `--asm salida.asm --no-ejecutar`: generación de código objeto fuente.

## 6. Demostrar funciones, estructuras y código objeto

```powershell
py netguard.py tests/execution/recursion.ng --comparar
py netguard.py tests/execution/estructuras.ng --arbol --cuadruplos
py netguard.py tests/execution/factorial.ng --asm factorial.asm --no-ejecutar
```

Para ejecutar `factorial.asm`, abrir una terminal WSL/Ubuntu, ubicarse en la carpeta del proyecto y ejecutar:

```bash
bash nativo/compilar_linux.sh factorial.asm nativo/factorial_nativo
./nativo/factorial_nativo
```

## 7. Resultados y limitaciones

En la prueba con 5,000 eventos simulados se obtienen 626 alertas y 4,374 marcas normales. Con `--comparar`, las versiones original y optimizada producen el mismo reporte y ejecutan 46,259 y 40,005 cuádruplas, respectivamente. La paridad entre intérprete y ensamblador se comprueba en los casos representativos de la suite nativa. La política de registros es local, el análisis de optimización de ciclos es acotado a patrones `FOR EACH`, y el backend nativo es Linux x86-64.

## 8. Cierre

«El proyecto integra análisis léxico, sintáctico y semántico; árboles y pilas; tabla de símbolos; representación intermedia con cuádruplas; optimización; máquina virtual y generación de ensamblador. Las suites de prueba verifican el comportamiento de esas etapas y las limitaciones del prototipo están documentadas».
