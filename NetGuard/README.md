# NetGuard — compilador de lenguaje prototipado para análisis de registros de red

**Proyecto integrador · Lenguajes y Autómatas II · Ingeniería en Sistemas Computacionales · Instituto Tecnológico de Oaxaca**

> Proyecto académico: interpreta archivos `.log` guardados o simulados. **No** es un IDS en tiempo real ni bloquea conexiones de red.

NetGuard implementa un lenguaje específico de dominio (`.ng`) construido con **Python + PLY**. Incluye análisis léxico, sintáctico y semántico; tablas de símbolos y direcciones; árboles y pilas; cuádruplas como única representación intermedia; optimización; máquina virtual; y un backend **x86-64 Linux** que genera ensamblador `.asm` enlazable con un pequeño *runtime* C. Esta edición añade **funciones con parámetros y retorno (también recursivas), estructuras `STRUCT`, casts explícitos, `WHILE`, mapeo de registros y pruebas nativas**.

## 1. Inicio rápido: Windows / VS Code

Abre **esta carpeta `NetGuard`**, no la carpeta superior del ZIP, en VS Code. En Terminal → Nueva terminal ejecuta:

```powershell
py --version
py pruebas.py
py pruebas_rubrica.py
py pruebas_final.py --sin-asm
py netguard.py ejemplos/reglas.ng --presentacion
```

Si tu equipo reconoce `python` en lugar de `py`, usa `python`. **No necesitas pip**: PLY está incluido en `ply/`. El comando `--presentacion` avanza por etapas con **Enter** si la terminal es interactiva.

## 2. Demostraciones importantes

```powershell
py netguard.py ejemplos/reglas.ng --todo
py netguard.py ejemplos/reglas.ng --registros --no-ejecutar
py netguard.py tests/execution/funciones.ng --comparar
py netguard.py tests/execution/recursion.ng --comparar
py netguard.py tests/execution/estructuras.ng --comparar
py netguard.py tests/intermediate/ciclos_anidados.ng --comparar
py netguard.py ejemplos/errores/P01_sintaxis.ng
py netguard.py tests/semantic/S11_funcion_no_definida.ng
py netguard.py ejemplos/reglas.ng ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log --reporte reporte_5000.txt
```

`P01` y `S11` terminan con código de salida distinto de cero **a propósito**: son pruebas negativas.

## 3. Comparación de LOG correcto e incorrecto

El lector espera seis campos CSV por evento, en este orden:

```text
sourceIP,eventType,port,failedAttempts,trafficMB,status
```

El proyecto incluye dos archivos emparejados de **500 eventos** para una demostración rápida:

- `ejemplos/registro_correcto_500.log`: 500 filas válidas; debe procesar los 500 eventos sin advertencias R02.
- `ejemplos/registro_incorrecto_500.log`: conserva 500 filas, pero seis contienen errores intencionales. NetGuard debe emitir seis advertencias `R02`, ignorar esas filas y procesar 494 eventos válidos.

Ejecuta en PowerShell, desde la carpeta `NetGuard`:

```powershell
py netguard.py ejemplos/reglas.ng ejemplos/registro_correcto_500.log --reporte reporte_correcto_500.txt
py netguard.py ejemplos/reglas.ng ejemplos/registro_incorrecto_500.log --reporte reporte_incorrecto_500.txt
```

Resultados esperados con `ejemplos/reglas.ng`:

| Archivo | Eventos analizados | Alertas | Marcados normales | Advertencias R02 |
|---|---:|---:|---:|---:|
| Correcto (500) | 500 | 69 | 431 | 0 |
| Incorrecto (500) | 494 | 66 | 428 | 6 |

Los seis errores intencionales son: IPv4 inválida, puerto no entero, `failedAttempts` no entero, `trafficMB` no numérico, una fila con cinco campos y otra con siete campos. El lector no detiene todo el análisis: informa `R02` y omite solamente la fila inválida.

También se conserva el conjunto grande de 5,000 eventos `ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log` y se incluye su contraparte con seis filas dañadas `ejemplos/registro_incorrecto_5000.log` (4,994 eventos aceptados):

```powershell
py netguard.py ejemplos/reglas.ng ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log --reporte reporte_correcto_5000.txt
py netguard.py ejemplos/reglas.ng ejemplos/registro_incorrecto_5000.log --reporte reporte_incorrecto_5000.txt
```

**Importante:** un LOG incorrecto no es un programa `.ng` con error de sintaxis. El programa de reglas compila normalmente; las advertencias `R02` aparecen al leer las filas malformadas del LOG.

## 4. Generación y ejecución nativa (Ubuntu / WSL, arquitectura x86-64)

Requiere `python3`, `bash` y `gcc` (en Ubuntu: `sudo apt update && sudo apt install -y gcc`). Dentro de **NetGuard**:

```bash
python3 pruebas.py
python3 pruebas_rubrica.py
python3 pruebas_final.py
python3 netguard.py ejemplos/reglas.ng --asm salida_netguard.asm --no-ejecutar
bash nativo/compilar_linux.sh salida_netguard.asm nativo/netguard_nativo
./nativo/netguard_nativo
```

Para generar el ejecutable recursivo:

```bash
python3 netguard.py tests/execution/recursion.ng --asm recursion.asm --no-ejecutar
bash nativo/compilar_linux.sh recursion.asm nativo/recursion_nativo
./nativo/recursion_nativo
```

**Importante:** el archivo `.asm` usa la sintaxis Intel de **GNU as** bajo Linux. No se ejecuta directamente desde PowerShell ni es un `.exe` de Windows. Consulta `nativo/README.md` y `documentacion/MANUAL_USUARIO.md`.

## 5. Estructura del repositorio

```text
NetGuard/
├── netguard.py                 CLI y presentación por fases
├── compilador/                lexer, parser, semántica, tabla, IR,
│   ├── optimizer.py           optimización de cuádruplos
│   ├── vm.py                  máquina virtual
│   ├── asm_codegen.py         traductor x86-64
│   └── register_alloc.py      política local de registros
├── ply/                       biblioteca externa PLY incluida
├── nativo/                    runtime C y compilador GCC
├── ejemplos/                  reglas y archivos .log simulados
├── tests/                     semantic/, intermediate/, execution/
├── herramientas/              benchmarks y análisis de costos
├── documentacion/             informe, GLC, manuales, matriz y glosario
├── evidencias/                salidas verificadas y ASM representativo
├── pruebas.py                 suite original
├── pruebas_rubrica.py         suite anterior por temas
├── pruebas_final.py           validación integral + paridad nativa
├── INSTRUCCIONES_GITHUB.md    publicación paso a paso
└── .github/workflows/ci.yml   automatización de pruebas en GitHub
```

## 6. Lenguaje NetGuard de ejemplo

```text
STRUCT Metrica
    intentos : int
END
FUNCTION doble(x : int) : int
    RETURN x * 2
END
LOAD EVENTS FROM "red_laboratorio.log" AS traffic
LET m : Metrica = NEW Metrica
m.intentos = doble(2)
FOR EACH event IN traffic
    IF event.failedAttempts >= m.intentos
        ALERT "Actividad sospechosa" FROM event.sourceIP
    ELSE
        MARK event AS "normal"
    END
END
```

Tipos básicos: `int`, `float`, `string`, `boolean`, `ip`; tipos especiales `event[]`, `event` y estructuras `STRUCT`. Se admite `int(expr)`, `float(expr)`, promoción `int` a `float`, `IF/ELSE`, `WHILE`, `FOR EACH`, `FUNCTION`, `RETURN`, `NEW` y campo de registro `registro.campo`.

**Restricciones intencionales:** máximo seis parámetros por función; las funciones se declaran antes de `LOAD`; una función solo puede invocar funciones ya declaradas o llamarse recursivamente; `RETURN` al final del cuerpo; campos de `STRUCT` de tipos básicos, sin arreglos dinámicos. El backend realiza **asignación local y determinística de registros**, con almacenamiento en pila, no asignación global por intervalos de vida.

## 7. Evidencia comprobable

Las tres suites se reportan por separado porque algunas verificaciones se solapan: **41/41 pruebas base, 21/21 adicionales de rúbrica y 38/38 verificaciones integrales**, sin fallos en el entorno Linux x86-64 de revisión. En la prueba Python con 5,000 registros simulados se obtuvieron **626 alertas y 4,374 marcas normales**; `--comparar` confirmó que el reporte original y el optimizado son iguales y redujo las instrucciones ejecutadas de 46,259 a 40,005 (13.5%). La equivalencia entre intérprete y ensamblador se comprueba aparte en casos representativos de la suite nativa. Los LOG son **simulados**, no tráfico real.

## 8. Reporte académico y alcance

Empieza por `documentacion/INFORME_TECNICO_FINAL.md` y `documentacion/MATRIZ_CUMPLIMIENTO_FINAL.md`. Consulta `documentacion/GLOSARIO.md` (también disponible en DOCX y PDF) para los conceptos. Para exposición: `documentacion/GUIA_DEFENSA.md`.

La matriz distingue entre **implementado y probado**, **implementación limitada** y **evidencia que el estudiante debe completar** (capturas, repositorio propio y valoración docente). No se afirma un compilador universal ni compatibilidad nativa con Windows.
