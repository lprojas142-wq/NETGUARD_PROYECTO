# -*- coding: utf-8 -*-
"""Pruebas de aceptación del cierre NetGuard: intérprete, semántica y Linux x86-64.

    python pruebas_final.py           # pruebas generales; nativas si hay gcc
    python pruebas_final.py --sin-asm # solo Python (Windows sin WSL)
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

from compilador import compilar, optimizar, MaquinaVirtual, ManejadorErrores, ErrorNetGuard
from compilador.asm_codegen import generar_asm

ROOT = Path(__file__).resolve().parent
OK = 0
FALLOS = []


def comprobar(condicion, etiqueta, detalle=''):
    global OK
    if condicion:
        OK += 1
        print(f' [OK] {etiqueta}')
    else:
        FALLOS.append(f'{etiqueta}: {detalle}')
        print(f' [FALLÓ] {etiqueta}: {detalle}')


def probar_archivo(nombre, registro=None):
    ruta = ROOT / nombre
    res = compilar(ruta.read_text(encoding='utf8'))
    if res.errores.hay_errores():
        return None, None, None, str(res.errores)
    opt, _ = optimizar(res.cuadruplos, res.tabla)
    salidas = []
    for qs in (res.cuadruplos, opt):
        vm = MaquinaVirtual(qs, ManejadorErrores(), base_dir=str(ruta.parent),
                           registro=str(ROOT / registro) if registro else None,
                           salida=lambda x: None)
        vm.ejecutar()
        salidas.append(vm)
    return res, opt, salidas, None


def ejecutar_nativo(nombre, res, opt, registro=None):
    with tempfile.TemporaryDirectory(prefix='netguard_pruebas_') as d:
        asm = Path(d) / 'prueba.asm'
        exe = Path(d) / 'prueba'
        asm.write_text(generar_asm(opt, res.tabla, str(ROOT / nombre),
                                   str(ROOT / registro) if registro else None), encoding='utf8')
        cmd = ['bash', str(ROOT / 'nativo/compilar_linux.sh'), str(asm), str(exe)]
        c = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if c.returncode:
            raise RuntimeError('gcc: ' + c.stderr[:1000])
        r = subprocess.run([str(exe)], capture_output=True, text=True, cwd=ROOT, timeout=60)
        if r.returncode:
            raise RuntimeError('programa nativo: ' + r.stderr[:1000])
        return [x for x in r.stdout.splitlines() if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sin-asm', action='store_true', help='omite pruebas x86-64 nativas')
    opts = ap.parse_args()
    positivos = [
        ('ejemplos/reglas.ng', 'Eventos analizados: 3 | Alertas: 2 | Marcados: 1', None),
        ('ejemplos/while_cast.ng', 'Eventos analizados:', None),
        ('tests/execution/factorial.ng', 'Factorial de 5 correcto: 120', None),
        ('tests/execution/fibonacci.ng', 'Fibonacci', None),
        ('tests/execution/funciones.ng', 'Eventos analizados: 3 | Alertas: 2 | Marcados: 1', None),
        ('tests/execution/recursion.ng', 'Factorial recursivo 120', None),
        ('tests/execution/promocion_funciones.ng', 'Promocion de funciones correcta', None),
        ('tests/execution/estructuras.ng', 'Eventos analizados: 3 | Alertas: 2 | Marcados: 1', None),
        ('tests/intermediate/ciclos_anidados.ng', 'Ciclos anidados 6', None),
        ('ejemplos/reglas.ng', 'Eventos analizados: 5000 | Alertas: 626 | Marcados: 4374',
         'ejemplos/NetGuard_Log_Practica_5000_Eventos_SIMULADO.log'),
    ]
    codigo = {}
    print('\nNETGUARD | VALIDACIÓN INTEGRAL (Python)')
    for nombre, esperado, log in positivos:
        res, opt, vs, err = probar_archivo(nombre, log)
        if err:
            comprobar(False, nombre, err)
            continue
        mensaje = '\n'.join(vs[1].lineas)
        comprobar(esperado in mensaje, nombre + ' · resultado', f'se esperaba: {esperado}; obtenido: {mensaje[-200:]}')
        comprobar(vs[0].lineas == vs[1].lineas, nombre + ' · equivalencia original/optimizado')
        codigo[(nombre, log)] = (res, opt, vs[1])
    for nombre, error in [
        ('tests/semantic/S11_funcion_no_definida.ng', 'S11'),
        ('tests/semantic/S12_cantidad_argumentos.ng', 'S12'),
        ('tests/semantic/S13_retorno_incompatible.ng', 'S13'),
        ('tests/semantic/S14_estructura_desconocida.ng', 'S14'),
        ('tests/semantic/S07_campo_estructura.ng', 'S07'),
        ('tests/semantic/S03_parametro_incorrecto.ng', 'S03'),
    ]:
        res = compilar((ROOT / nombre).read_text(encoding='utf8'))
        codes = [x[0] for x in res.errores.errores]
        comprobar(error in codes, nombre + ' · rechazo semántico', 'códigos recibidos: ' + repr(codes))

    # La división entre cero debe producir R03 y detener la VM.
    nombre_error = 'ejemplos/errores/R03_division_cero.ng'
    r = compilar((ROOT / nombre_error).read_text(encoding='utf8'))
    opt_error, _ = optimizar(r.cuadruplos, r.tabla)
    try:
        vm = MaquinaVirtual(opt_error, ManejadorErrores(),
                           base_dir=str((ROOT / nombre_error).parent), salida=lambda _: None)
        vm.ejecutar()
        comprobar(False, 'División entre cero · VM', 'no se recibió R03')
    except ErrorNetGuard as e:
        comprobar(e.codigo == 'R03', 'División entre cero · VM', str(e))

    nativo = platform.system() == 'Linux' and platform.machine() in ('x86_64', 'AMD64') and shutil.which('gcc')
    if not opts.sin_asm and nativo:
        print('\nNETGUARD | PRUEBAS NATIVAS x86-64 CON GCC')
        for nombre, _, registro in positivos:
            if (nombre, registro) not in codigo:
                continue
            res, opt, vm = codigo[(nombre, registro)]
            try:
                salida = ejecutar_nativo(nombre, res, opt, registro)
                comprobar(salida == vm.lineas, nombre + ' · ASM vs VM',
                          f'ASM {salida[-4:]}; VM {vm.lineas[-4:]}')
            except Exception as e:
                comprobar(False, nombre + ' · ASM vs VM', str(e))
        # El ejecutable nativo también debe detenerse con R03.
        try:
            with tempfile.TemporaryDirectory(prefix='netguard_r03_') as d:
                asm = Path(d)/'r03.asm'; exe = Path(d)/'r03'
                asm.write_text(generar_asm(opt_error, r.tabla, str(ROOT/nombre_error)), encoding='utf8')
                c = subprocess.run(['bash', str(ROOT/'nativo/compilar_linux.sh'), str(asm), str(exe)],
                                   capture_output=True, text=True, cwd=ROOT)
                if c.returncode:
                    raise RuntimeError(c.stderr)
                c = subprocess.run([str(exe)], capture_output=True, text=True, cwd=ROOT, timeout=30)
                comprobar(c.returncode != 0 and '[R03]' in c.stderr,
                          'División entre cero · ASM', c.stderr)
        except Exception as e:
            comprobar(False, 'División entre cero · ASM', str(e))
    else:
        print('\nPruebas nativas omitidas (se requiere Linux x86-64 y GCC; Windows: usar WSL).')
    print(f'\nRESULTADO FINAL: {OK} verificaciones correctas; {len(FALLOS)} fallidas.')
    if FALLOS:
        print('\n'.join(FALLOS))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
