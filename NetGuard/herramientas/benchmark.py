# -*- coding: utf-8 -*-
"""Medición orientativa del intérprete, antes/después de optimización.

Tiempo wall-clock medido dentro de Python y pico de memoria asignada
observado con tracemalloc. NO son ciclos de CPU ni uso de registros físicos.
"""
import argparse
import gc
import os
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compilador import compilar, optimizar, MaquinaVirtual, ManejadorErrores


def evaluar(cuads, ruta, registro, rep):
    tiempos=[]
    lineas=None
    for _ in range(rep):
        gc.collect()
        vm=MaquinaVirtual(cuads, ManejadorErrores(), base_dir=str(Path(ruta).resolve().parent),
                          registro=registro, salida=lambda _texto: None)
        t=time.perf_counter()
        vm.ejecutar()
        tiempos.append((time.perf_counter()-t)*1000)
        if lineas is None:
            lineas=vm.lineas
    gc.collect()
    tracemalloc.start()
    m=MaquinaVirtual(cuads, ManejadorErrores(), base_dir=str(Path(ruta).resolve().parent),
                     registro=registro, salida=lambda _texto: None)
    m.ejecutar()
    _, peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return statistics.median(tiempos),peak/(1024*1024),m.ejecutados,lineas


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('programa', nargs='?', default='ejemplos/reglas.ng')
    ap.add_argument('registro', nargs='?', default='ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log')
    ap.add_argument('--repeticiones', type=int, default=3)
    args=ap.parse_args()
    r=compilar(Path(args.programa).read_text(encoding='utf-8'))
    if r.errores.hay_errores():
        r.errores.imprimir(); return 1
    opt,_=optimizar(r.cuadruplos,r.tabla)
    ruta_log=os.path.abspath(args.registro) if args.registro else None
    antes=evaluar(r.cuadruplos,args.programa,ruta_log,args.repeticiones)
    despues=evaluar(opt,args.programa,ruta_log,args.repeticiones)
    print('NETGUARD: BENCHMARK DEL INTÉRPRETE PYTHON')
    print('Se mide tiempo de pared (mediana) y memoria asignada en Python (tracemalloc).')
    print('Tipo           Cuádruplos  Instrucciones   Tiempo (ms)   Memoria pico (MiB)')
    for n,qs,res in [('Original',r.cuadruplos,antes),('Optimizado',opt,despues)]:
        print(f'{n:14} {len(qs):>7} {res[2]:>14} {res[0]:>13.2f} {res[1]:>19.2f}')
    print('Resultados iguales:', 'SÍ' if antes[3]==despues[3] else 'NO')
    print('Nota: estos tiempos dependen de la carga y hardware; no equivalen a una')
    print('medición de los registros de CPU ni de la asignación de memoria nativa.')
    return 0 if antes[3]==despues[3] else 1


if __name__=='__main__':
    sys.exit(main())
