# Manual de usuario, instalación y compilación — NetGuard

## Requisitos

- **Intérprete y compilador:** Python 3.8 o superior, Windows/Linux/macOS. La biblioteca PLY se incluye en la carpeta `ply/` y no requiere instalación adicional.
- **Generación de código:** se puede generar `.asm` en cualquier sistema con Python, pero **para ensamblar, enlazar y ejecutar** se requiere Linux x86-64 (o WSL Ubuntu en Windows), Bash y GCC.
- VS Code es opcional, pero facilita abrir archivos y depurar.

## Arranque desde la carpeta NetGuard

En VS Code abre `Terminal → Nueva terminal`. Comienza con `py --version` (Windows) o `python3 --version` (Ubuntu). Si el comando de Python no funciona, instala Python o selecciona el intérprete correcto.

**Windows / PowerShell**

```powershell
py pruebas.py
py pruebas_rubrica.py
py pruebas_final.py --sin-asm
py netguard.py ejemplos/reglas.ng --presentacion
```

**Linux o WSL**

```bash
python3 pruebas.py
python3 pruebas_rubrica.py
python3 pruebas_final.py
python3 netguard.py ejemplos/reglas.ng --presentacion
```

## Sintaxis de la línea de comandos

```text
python netguard.py PROGRAMA.ng [REGISTRO.log] [OPCIONES]
```

| Opción | Función |
|---|---|
| `--tokens` | Tabla léxica de tokens. |
| `--arbol` | Árbol de expresiones; notación prefija y postfija. |
| `--traza` | Pilas semánticas y acciones. |
| `--tabla` | Tabla de símbolos, constantes y direcciones virtuales. |
| `--cuadruplos` | Código intermedio de cuatro campos. |
| `--optimizado` | Cuádruplos optimizados y bitácora. |
| `--direcciones` | Mostrar direcciones virtuales junto a los operandos. |
| `--registros` | Política de mapeo a registros físicos x86-64. |
| `--todo` | Todas las fases y comparación de resultados. |
| `--presentacion` | Demostración por etapas, con pausas si hay terminal interactiva. |
| `--comparar` | Ejecuta sin optimizar y optimizado y comprueba resultados. |
| `--sin-optimizar` | Utiliza los cuádruplos originales para ejecutar. |
| `--no-ejecutar` | Compila, pero no ejecuta la máquina virtual. |
| `--asm archivo.asm` | Genera ensamblador GNU as/Intel Linux x86-64 optimizado. |
| `--reporte ruta.txt` | Cambia el archivo de salida del reporte. |

## Ejemplos orientados a la defensa

**1. Demostrar funcionamiento general:**

```bash
python3 netguard.py ejemplos/reglas.ng --presentacion
```

**2. Revisar un caso de error de sintaxis y uno semántico:**

```bash
python3 netguard.py ejemplos/errores/P01_sintaxis.ng
python3 netguard.py tests/semantic/S11_funcion_no_definida.ng
```

Estos comandos **deben** indicar errores; no son fallas accidentales.

**3. Analizar 5,000 eventos simulados:**

```bash
python3 netguard.py ejemplos/reglas.ng ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log --reporte reporte_5000.txt
```

**4. Mostrar funciones, recursión y estructuras:**

```bash
python3 netguard.py tests/execution/funciones.ng --comparar
python3 netguard.py tests/execution/recursion.ng --comparar
python3 netguard.py tests/execution/estructuras.ng --arbol --cuadruplos
```

**5. Generar el ensamblador y compilar a binario:**

```bash
python3 netguard.py tests/execution/recursion.ng --asm salida_recursion.asm --no-ejecutar
bash nativo/compilar_linux.sh salida_recursion.asm nativo/recursion_nativo
./nativo/recursion_nativo
```

## Demostración: LOG correcto y LOG incorrecto

NetGuard procesa cada evento como una fila CSV con seis campos separados por comas:

```text
sourceIP,eventType,port,failedAttempts,trafficMB,status
```

En el paquete se incluyen dos archivos de 500 eventos para comparar:

| Archivo | Filas de datos | Resultado esperado |
|---|---:|---|
| `ejemplos/registro_correcto_500.log` | 500 válidas | 500 eventos analizados y cero advertencias `R02`. |
| `ejemplos/registro_incorrecto_500.log` | 494 válidas + 6 malformadas | 494 eventos analizados y seis advertencias `R02`. |

Ejecuta desde la carpeta raíz `NetGuard`:

```powershell
py netguard.py ejemplos/reglas.ng ejemplos/registro_correcto_500.log --reporte reporte_correcto_500.txt
py netguard.py ejemplos/reglas.ng ejemplos/registro_incorrecto_500.log --reporte reporte_incorrecto_500.txt
```

Con las reglas del ejemplo `reglas.ng`, se esperan estos resultados reproducibles:

| Resultado | LOG correcto | LOG incorrecto |
|---|---:|---:|
| Eventos analizados | 500 | 494 |
| Alertas | 69 | 66 |
| Marcados normales | 431 | 428 |
| Advertencias `R02` | 0 | 6 |

El LOG incorrecto contiene deliberadamente: una IPv4 inválida (`192.0.2.999`), un puerto no entero (`veintidos`), intentos fallidos no enteros (`muchos`), tráfico no numérico (`mucho`), una fila con cinco campos y una fila con siete campos. El lector registra una advertencia `R02` por cada caso e ignora únicamente esa fila; continúa procesando las demás.

Para comparar el conjunto de 5,000 eventos que ya incluye el proyecto, utiliza el archivo correcto `ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log` y su contraparte `ejemplos/registro_incorrecto_5000.log`:

```powershell
py netguard.py ejemplos/reglas.ng ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log --reporte reporte_correcto_5000.txt
py netguard.py ejemplos/reglas.ng ejemplos/registro_incorrecto_5000.log --reporte reporte_incorrecto_5000.txt
```

El segundo debe analizar 4,994 eventos e informar seis advertencias `R02`. Estos son errores del **archivo LOG**, no errores léxicos, sintácticos o semánticos del programa `.ng`.

## Resolución de errores frecuentes

| Error | Solución |
|---|---|
| `python/py no reconocido` | Verifica instalación e intérprete; en PowerShell prueba `py`, en Ubuntu `python3`. |
| `No se encuentra netguard.py` | Abre la terminal dentro de la **carpeta NetGuard**. |
| `[R01] No existe archivo LOG` | Usa una ruta real; en los tests, las rutas relativas parten del `.ng`. |
| Error `P01` / `Sxx` | Revisa la línea que imprime el compilador y corrige el `.ng`. |
| `gcc: command not found` | En Ubuntu: `sudo apt install gcc`; en Windows usa WSL. |
| `.asm` no abre en Windows | `.asm` es **código fuente ensamblador Linux**, no un ejecutable de Windows. |
| `--presentacion` no espera Enter | Las pausas solo funcionan en una terminal interactiva; no dentro de una redirección a archivo. |
| Archivos `reporte*.txt` generados | Son salidas locales; Git los excluye para evitar ensuciar el repositorio. |

## Formato del LOG

Se aceptan líneas de seis campos separados por coma:

```text
sourceIP,eventType,port,failedAttempts,trafficMB,status
192.168.1.10,LOGIN,443,7,600.50,pending
```

Se ignoran encabezados, líneas vacías y comentarios. El lector de Python reporta advertencias en registros malformados y el lector nativo los omite; por esta diferencia no se promete equivalencia literal de advertencias para datos inválidos. Un log es un archivo **de entrada**; NetGuard no captura paquetes en vivo.
