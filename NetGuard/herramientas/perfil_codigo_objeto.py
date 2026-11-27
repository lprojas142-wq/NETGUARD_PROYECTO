# -*- coding: utf-8 -*-
"""Costos estáticos del ensamblador original y optimizado (Linux x86-64)."""
import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from compilador import compilar, optimizar
from compilador.asm_codegen import BackendASM
from compilador.register_alloc import AsignadorRegistros


def main():
    p = argparse.ArgumentParser(description='Perfil estático de marcos de pila, registros y tamaño de ensamblador')
    p.add_argument('programa', nargs='?', default=str(RAIZ/'ejemplos/reglas.ng'))
    a = p.parse_args()
    archivo = Path(a.programa)
    r = compilar(archivo.read_text(encoding='utf8'))
    if r.errores.hay_errores():
        print(r.errores)
        return 1
    opt, _ = optimizar(r.cuadruplos, r.tabla)
    print('NETGUARD | PERFIL ESTÁTICO x86-64 (no es RSS real ni tiempo de CPU)')
    print(f'Archivo fuente: {archivo}')
    for etiqueta, qs in [('Original', r.cuadruplos), ('Optimizado', opt)]:
        backend = BackendASM(qs, r.tabla, str(archivo))
        asm = backend.generar()
        instrucciones = [x for x in asm.splitlines() if x.startswith('    ') and not x.lstrip().startswith(('#','.'))]
        print(f'{etiqueta:<12} cuádruplos={len(qs):<5} marcos_de_pila={backend.frame} bytes '
              f'ranuras={len(backend.slot):<4} líneas_asm={len(instrucciones)}')
    print('Registros físicos usados por la política de asignación local:')
    for uso, registros, _ in AsignadorRegistros.estrategia():
        print(f'  - {uso}: {registros}')
    print('Nota: más/menos líneas de ensamblador no asegura mayor/menor tiempo real.')
    print('Pila informada: tamaño máximo reservado por llamada en el generador, '
          'sin sumar profundidad recursiva ni heap del runtime.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
