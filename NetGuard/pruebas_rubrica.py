# -*- coding: utf-8 -*-
"""Pruebas adicionales para la rúbrica final de Lenguajes y Autómatas II."""
import os
import sys
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

from compilador import compilar, optimizar, MaquinaVirtual, ManejadorErrores
from compilador.asm_codegen import generar_asm

RAIZ = Path(__file__).resolve().parent
aprobadas = 0
fallidas = 0


def prueba(titulo, condicion, detalle=''):
    global aprobadas, fallidas
    if condicion:
        aprobadas += 1
        print('  [OK] ' + titulo)
    else:
        fallidas += 1
        print('  [FALLO] ' + titulo + (': ' + str(detalle) if detalle else ''))


def preparar(archivo):
    ruta = RAIZ / archivo
    r = compilar(ruta.read_text(encoding='utf-8'))
    return ruta, r


def correr(ruta, codigo):
    e = ManejadorErrores()
    vm = MaquinaVirtual(codigo, e, base_dir=str(ruta.parent), salida=lambda _: None)
    vm.ejecutar()
    return vm.lineas


print('PRUEBAS EXTRA DE LA RÚBRICA NETGUARD')
for fuente, mensaje in [
    ('ejemplos/while_cast.ng', 'WHILE y conversión explícita'),
    ('tests/execution/factorial.ng', 'factorial nativo'),
    ('tests/execution/fibonacci.ng', 'fibonacci nativo'),
    ('ejemplos/reglas.ng', 'reglas de NetGuard'),
]:
    ruta, r = preparar(fuente)
    prueba(mensaje + ': análisis semántico', not r.errores.hay_errores())
    if r.errores.hay_errores():
        continue
    opt, _ = optimizar(r.cuadruplos, r.tabla)
    antes, despues = correr(ruta, r.cuadruplos), correr(ruta, opt)
    prueba(mensaje + ': salida original = optimizada', antes == despues)
    if 'factorial' in fuente or 'fibonacci' in fuente:
        prueba(mensaje + ': algoritmo correcto', len(antes) == 2 and 'correcto' in antes[0])
    if 'while_cast' in fuente:
        prueba('WHILE: tres iteraciones correctas', len(antes) == 4 and 'Alertas: 3' in antes[-1])
        nodos = [n for _texto, _linea, n in r.pila.arboles]
        prueba('Notaciones prefija y postfija implementadas', all(n.preorden() and n.postorden() for n in nodos))
    asm = generar_asm(opt, r.tabla, str(ruta))
    prueba(mensaje + ': ASM x86-64 generado', '.intel_syntax noprefix' in asm and 'main:' in asm)

for fuente, codigo in [
    ('tests/semantic/S10_cast_invalido.ng', 'S10'),
    ('tests/semantic/S05_while_no_boolean.ng', 'S05'),
]:
    _ruta, r = preparar(fuente)
    prueba(f'Error semántico {codigo} detectado', r.errores.hay_errores() and
           any(e[0] == codigo for e in r.errores.errores))

# Verificación directa de binarios reales en Linux x86-64 con GCC disponible.
if platform.system() == 'Linux' and platform.machine() in ('x86_64', 'AMD64') and shutil.which('gcc'):
    with tempfile.TemporaryDirectory() as td:
        directorio = Path(td)
        runtime = RAIZ / 'nativo/runtime.c'
        for nombre in ('factorial', 'fibonacci', 'reglas'):
            fuente = 'tests/execution/' + nombre + '.ng' if nombre != 'reglas' else 'ejemplos/reglas.ng'
            ruta, r = preparar(fuente)
            opt, _ = optimizar(r.cuadruplos, r.tabla)
            asm_path = directorio / (nombre + '.asm')
            asm_path.write_text(generar_asm(opt, r.tabla, str(ruta)), encoding='utf-8')
            objeto, rt_obj, ejecutable = directorio/(nombre+'.o'), directorio/'runtime.o', directorio/nombre
            try:
                subprocess.run(['gcc','-c','-x','assembler',str(asm_path),'-o',str(objeto)],check=True,capture_output=True)
                subprocess.run(['gcc','-c','-std=c11','-O2',str(runtime),'-o',str(rt_obj)],check=True,capture_output=True)
                subprocess.run(['gcc','-no-pie',str(objeto),str(rt_obj),'-o',str(ejecutable)],check=True,capture_output=True)
                resultado = subprocess.run([str(ejecutable)], check=True, capture_output=True, text=True)
                esperado = correr(ruta, opt)
                prueba(nombre + ': .asm ensamblado, enlazado y ejecutado', resultado.stdout.splitlines() == esperado)
            except subprocess.CalledProcessError as e:
                prueba(nombre + ': prueba de objeto nativo', False, e.stderr.decode() if isinstance(e.stderr,bytes) else e.stderr)
else:
    print('  [NOTA] Pruebas nativas omitidas: requieren Linux x86-64 y GCC (ej. WSL).')

print(f'\nRESULTADO: {aprobadas} correctas, {fallidas} fallidas')
sys.exit(1 if fallidas else 0)
