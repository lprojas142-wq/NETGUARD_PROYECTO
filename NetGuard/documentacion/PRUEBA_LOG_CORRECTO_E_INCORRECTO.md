# Práctica: comparar un LOG correcto y uno incorrecto

## Objetivo

Demostrar que el lector de registros de NetGuard valida la estructura de cada fila, informa errores de formato con `R02`, omite las filas defectuosas y continúa procesando las filas válidas.

## Formato esperado

Cada evento debe tener exactamente seis campos separados por comas:

```text
sourceIP,eventType,port,failedAttempts,trafficMB,status
```

El lector valida la dirección IPv4, que `port` y `failedAttempts` sean enteros, que `trafficMB` sea numérico y que existan exactamente seis campos. También ignora encabezados, líneas vacías y comentarios que comienzan con `#`.

## Archivos de 500 eventos

- `ejemplos/registro_correcto_500.log`: encabezado + 500 eventos válidos.
- `ejemplos/registro_incorrecto_500.log`: encabezado + 500 filas, seis de ellas con errores intencionales.

Los errores de las filas incorrectas son:

| Línea del archivo | Campo | Valor incorrecto | Motivo |
|---:|---|---|---|
| 26 | `sourceIP` | `192.0.2.999` | No es IPv4 válida. |
| 51 | `port` | `veintidos` | Debe ser entero. |
| 76 | `failedAttempts` | `muchos` | Debe ser entero. |
| 101 | `trafficMB` | `mucho` | Debe ser numérico. |
| 126 | Número de campos | 5 campos | Faltó `status`. |
| 151 | Número de campos | 7 campos | Hay un campo adicional. |

## Comandos para PowerShell / terminal de VS Code

Ejecuta desde la carpeta que contiene `netguard.py`:

```powershell
py netguard.py ejemplos/reglas.ng ejemplos/registro_correcto_500.log --reporte reporte_correcto_500.txt
py netguard.py ejemplos/reglas.ng ejemplos/registro_incorrecto_500.log --reporte reporte_incorrecto_500.txt
```

## Resultados esperados

Con `ejemplos/reglas.ng`:

| Métrica | Correcto | Incorrecto |
|---|---:|---:|
| Filas de datos en el LOG | 500 | 500 |
| Eventos aceptados/analizados | 500 | 494 |
| Alertas | 69 | 66 |
| Marcados normales | 431 | 428 |
| Advertencias `R02` | 0 | 6 |

Las seis filas malformadas se excluyen. Las otras 494 se procesan con normalidad. El programa no debe detenerse por esos errores de formato.

## Conjunto adicional de 5,000 eventos

El repositorio ya incluye `ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log`, que tiene 5,000 filas de datos (5,001 líneas contando el encabezado). Para contrastarlo con un archivo grande malformado se agregó `ejemplos/registro_incorrecto_5000.log`, que tiene 5,000 filas de datos y seis defectuosas.

```powershell
py netguard.py ejemplos/reglas.ng ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log --reporte reporte_correcto_5000.txt
py netguard.py ejemplos/reglas.ng ejemplos/registro_incorrecto_5000.log --reporte reporte_incorrecto_5000.txt
```

Resultado esperado para el incorrecto: 4,994 eventos analizados, 623 alertas, 4,371 marcados normales y seis advertencias `R02`.

## Cómo explicarlo en la defensa

> Primero ejecuto el LOG correcto. Tiene 500 registros que cumplen el formato, por eso los 500 se procesan sin advertencias. Después ejecuto el LOG incorrecto: conserva 500 filas, pero seis tienen datos inválidos. El lector detecta cada problema, informa `R02` y descarta solo esa fila. Por eso analiza 494 eventos y continúa trabajando. Esto demuestra la validación del formato de entrada y la tolerancia a errores de registros.

**Distinción:** `R02` es una advertencia de una fila del archivo `.log`. No es un error léxico, sintáctico ni semántico del programa de reglas `.ng`.
