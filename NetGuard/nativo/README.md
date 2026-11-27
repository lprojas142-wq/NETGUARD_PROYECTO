# Backend de código objeto para Linux x86-64 — NetGuard

NetGuard traduce cuádruplos optimizados a ensamblador `.asm` Intel/GNU as para **Linux x86-64**, enlazable con `gcc` y `nativo/runtime.c`. Los ejemplos factorial, Fibonacci, recursión, estructuras y los 5,000 registros simulados se verifican contra la máquina virtual Python.

## Requisitos

- Ubuntu/Linux **x86-64** o Windows con **WSL Ubuntu** sobre x86-64.
- Python 3.8+, Bash y GCC; en Ubuntu `sudo apt update && sudo apt install -y gcc`.
- PLY incluido en el ZIP, sin necesidad de `pip install`.

## Pasos de demostración

```bash
cd NetGuard
python3 pruebas.py
python3 pruebas_rubrica.py
python3 pruebas_final.py
python3 netguard.py ejemplos/reglas.ng --asm salida_netguard.asm --no-ejecutar
bash nativo/compilar_linux.sh salida_netguard.asm nativo/netguard_nativo
./nativo/netguard_nativo
```

Para mostrar recursión real compilada a CPU:

```bash
python3 netguard.py tests/execution/recursion.ng --asm salida_recursion.asm --no-ejecutar
bash nativo/compilar_linux.sh salida_recursion.asm nativo/recursion_nativo
./nativo/recursion_nativo
```

Para estructuras:

```bash
python3 netguard.py tests/execution/estructuras.ng --asm salida_estructuras.asm --no-ejecutar
bash nativo/compilar_linux.sh salida_estructuras.asm nativo/estructuras_nativo
./nativo/estructuras_nativo
```

Para analizar un registro simulado grande:

```bash
python3 netguard.py ejemplos/reglas.ng ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log --asm salida_5000.asm --no-ejecutar
bash nativo/compilar_linux.sh salida_5000.asm nativo/5000_nativo
./nativo/5000_nativo | tail -1
```

## CPU y memoria

- `.rodata`: cadenas, nombres de campos, rutas LOG; `.data`: variables globales; `.text`: instrucciones de CPU.
- `RAX/RDX`: operaciones enteras; `XMM0/XMM1`: flotantes; `RDI, RSI, RDX, RCX, R8, R9`: argumentos hasta seis.
- Pila (stack frames): variables locales, parámetros, temporales y scratch. **Cada llamada recursiva tiene marco propio**, con `push rbp`, `sub rsp,N` y `leave; ret`.
- `compilador/register_alloc.py`: asignador local y determinístico; los valores se guardan en memoria entre instrucciones; no utiliza análisis global de liveness.
- `runtime.c`: lectura de LOG, estructuras dinámicas y emisión de alertas; las operaciones numéricas y saltos son ensamblador real.

## Límites y advertencias

No produce un EXE de Windows. No implementa arreglos genéricos ni estructuras anidadas; funciones máximo seis argumentos y retorno final. Las estructuras se almacenan dinámicamente; el runtime académico no está diseñado para servicios de larga duración ni liberación exhaustiva de todos los objetos asignados. En registros LOG malformados el intérprete Python genera advertencias que el runtime C puede omitir. **No atribuir diferencias de tiempos a la optimización sin medir en el mismo entorno.**
