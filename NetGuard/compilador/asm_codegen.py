# -*- coding: utf-8 -*-
"""Backend x86-64 Linux (GNU as, sintaxis Intel) para los cuádruplos NetGuard.

Genera ensamblador real con instrucciones de CPU para expresiones y control de
flujo. Las operaciones de dominio (leer registros LOG, alertar, marcar eventos)
utilizan un runtime C enlazado. Target: Linux x86-64, ABI System V.
"""
import os
import struct
from .register_alloc import AsignadorRegistros


class GeneracionASMError(Exception):
    pass


class BackendASM:
    def __init__(self, cuads, tabla, programa, registro=None):
        self.q = cuads
        self.registros = AsignadorRegistros()
        self.tabla = tabla
        self.programa = programa
        self.registro = registro
        self.lineas = []
        self.strings = {}
        self.globales = {s.dir for s in tabla.todos if s.categoria == 'Global'}
        dirs = set()
        for q in cuads:
            for op in (q.a1, q.a2, q.res):
                if op is not None and not isinstance(op, int):
                    if op.clase in ('var', 'temp') and op.dir not in self.globales:
                        dirs.add(op.dir)
                    if op.clase in ('campo', 'structcampo') and op.simbolo.dir not in self.globales:
                        dirs.add(op.simbolo.dir)
        self.slot = {d: (i + 1) * 8 for i, d in enumerate(sorted(dirs))}
        self.scratch1 = (len(dirs) + 1) * 8
        self.scratch2 = (len(dirs) + 2) * 8
        self.arg_slots = [(len(dirs) + 3 + i) * 8 for i in range(6)]
        self.frame = ((self.arg_slots[-1] + 15) // 16) * 16

    def e(self, line):
        self.lineas.append('    ' + line)

    def pos(self, op):
        d = op if isinstance(op, int) else op.dir
        if d in self.globales:
            return f'QWORD PTR [rip + g_{d}]'
        if d not in self.slot:
            raise GeneracionASMError(f'Dirección sin reservar: {d}')
        return f'QWORD PTR [rbp - {self.slot[d]}]'

    def sp(self, idx):
        return f'QWORD PTR [rbp - {idx}]'

    def cadena(self, valor):
        if valor not in self.strings:
            self.strings[valor] = 'ng_str_' + str(len(self.strings))
        return self.strings[valor]

    def cargar(self, o, como=None):
        if o is None:
            raise GeneracionASMError('Operando sin definir')
        destino = como or o.tipo
        if o.clase == 'structcampo':
            self.e(f'mov rdi, {self.pos(o.simbolo.dir)}')
            lab = self.cadena(o.campo)
            self.e(f'lea rsi, [rip + {lab}]')
            metodo = ('float' if o.tipo == 'float' else
                      'text' if o.tipo in ('string', 'ip') else 'int')
            self.e('call ng_struct_get_' + metodo)
        elif o.clase == 'campo':
            self.e(f'mov rdi, {self.pos(o.simbolo.dir)}')
            self.e(f'mov esi, {o.desplazamiento}')
            if o.tipo == 'float':
                self.e('call ng_get_float')
            elif o.tipo in ('string', 'ip'):
                self.e('call ng_get_text')
            else:
                self.e('call ng_get_int')
        elif o.clase == 'const':
            if o.tipo == 'float':
                bits = struct.unpack('<Q', struct.pack('<d', float(o.valor)))[0]
                self.e(f'movabs rax, {bits}')
                self.e('movq xmm0, rax')
            elif o.tipo in ('string', 'ip'):
                lab = self.cadena(str(o.valor))
                self.e(f'lea rax, [rip + {lab}]')
            elif o.tipo == 'boolean':
                self.e(f'mov rax, {1 if o.valor else 0}')
            elif o.tipo == 'int':
                self.e(f'mov rax, {int(o.valor)}')
            else:
                raise GeneracionASMError(f'Tipo constante sin backend: {o.tipo}')
        else:
            if o.tipo == 'float':
                self.e(f'movsd xmm0, {self.pos(o)}')
            else:
                self.e(f'mov rax, {self.pos(o)}')
        if o.tipo == 'int' and destino == 'float':
            self.e('cvtsi2sd xmm0, rax')
        elif o.tipo == 'float' and destino == 'int':
            self.e('cvttsd2si rax, xmm0')
        return destino

    def guardar(self, o, tipo):
        if o.clase == 'structcampo':
            if o.tipo == 'float':
                if tipo == 'int':
                    self.e('cvtsi2sd xmm0, rax')
                self.e(f'mov rdi, {self.pos(o.simbolo.dir)}')
                lab = self.cadena(o.campo)
                self.e(f'lea rsi, [rip + {lab}]')
                self.e('call ng_struct_set_float')
            else:
                self.e('mov rdx, rax')
                self.e(f'mov rdi, {self.pos(o.simbolo.dir)}')
                lab = self.cadena(o.campo)
                self.e(f'lea rsi, [rip + {lab}]')
                metodo = 'text' if o.tipo in ('string', 'ip') else 'int'
                self.e('call ng_struct_set_' + metodo)
            return
        if o.tipo == 'float':
            if tipo != 'float':
                self.e('cvtsi2sd xmm0, rax')
            self.e(f'movsd {self.pos(o)}, xmm0')
        else:
            if tipo == 'float':
                self.e('cvttsd2si rax, xmm0')
            self.e(f'mov {self.pos(o)}, rax')

    def operandos(self, a, b, como):
        self.cargar(a, como)
        if como == 'float':
            self.e(f'movsd {self.sp(self.scratch1)}, xmm0')
        else:
            self.e(f'mov {self.sp(self.scratch1)}, rax')
        self.cargar(b, como)
        if como == 'float':
            self.e(f'movsd {self.sp(self.scratch2)}, xmm0')
            self.e(f'movsd xmm0, {self.sp(self.scratch1)}')
            self.e(f'movsd xmm1, {self.sp(self.scratch2)}')
        else:
            self.e(f'mov {self.sp(self.scratch2)}, rax')
            self.e(f'mov rax, {self.sp(self.scratch1)}')
            self.e(f'mov rdx, {self.sp(self.scratch2)}')

    def quad(self, q, i):
        op = q.op
        self.lineas.append(f'L{i}:')
        self.e(f'# {i}: {q}')
        if op == 'END':
            self.e('call ng_summary')
            self.e('xor eax, eax')
            self.e('leave')
            self.e('ret')
        elif op == 'NEWSTRUCT':
            self.e('call ng_struct_new')
            self.guardar(q.res, 'struct')
        elif op == 'FUNC':
            self.e('push rbp')
            self.e('mov rbp, rsp')
            self.e(f'sub rsp, {self.frame}')
            for n in sorted(self.slot):
                self.e(f'mov {self.pos(n)}, 0')
            for param, reg in zip(q.funcion_params, ('rdi','rsi','rdx','rcx','r8','r9')):
                self.e(f'mov {self.pos(param)}, {reg}')
        elif op == 'RET':
            self.cargar(q.a1, getattr(q, 'tipo_retorno', q.a1.tipo))
            self.e('leave')
            self.e('ret')
        elif op == 'PARAM':
            tipo = getattr(q, 'param_tipo', q.a1.tipo)
            self.cargar(q.a1, tipo)
            if tipo == 'float':
                self.e('movq rax, xmm0')
            self.e(f'mov {self.sp(self.arg_slots[q.a2])}, rax')
        elif op == 'CALL':
            if q.a2 > 6:
                raise GeneracionASMError('Se admiten hasta 6 argumentos')
            for i, reg in enumerate(self.registros.parametros(q.a2)):
                self.e(f'mov {reg}, {self.sp(self.arg_slots[i])}')
            self.e(f'call L{q.a1.dir}')
            self.guardar(q.res, q.res.tipo)
        elif op == '=':
            self.cargar(q.a1)
            self.guardar(q.res, q.a1.tipo)
        elif op in ('CAST_INT', 'CAST_FLOAT'):
            tipo = 'int' if op == 'CAST_INT' else 'float'
            self.cargar(q.a1, tipo)
            self.guardar(q.res, tipo)
        elif op in ('+', '-', '*', '/'):
            tipo = q.res.tipo
            self.operandos(q.a1, q.a2, tipo)
            if tipo == 'float':
                if op == '/':
                    self.e('pxor xmm2, xmm2')
                    self.e('ucomisd xmm1, xmm2')
                    self.e(f'jne .Ldiv_ok_{i}')
                    self.e('call ng_div_zero')
                    self.lineas.append(f'.Ldiv_ok_{i}:')
                self.e({'+':'addsd xmm0, xmm1','-':'subsd xmm0, xmm1',
                        '*':'mulsd xmm0, xmm1','/':'divsd xmm0, xmm1'}[op])
            else:
                if op == '+': self.e('add rax, rdx')
                elif op == '-': self.e('sub rax, rdx')
                elif op == '*': self.e('imul rax, rdx')
                else: raise GeneracionASMError('División entera sin resultado float')
            self.guardar(q.res, tipo)
        elif op in ('NEG', 'NOT'):
            self.cargar(q.a1)
            if op == 'NOT':
                self.e('test rax, rax')
                self.e('sete al')
                self.e('movzx rax, al')
            elif q.a1.tipo == 'float':
                self.e('pxor xmm1, xmm1')
                self.e('subsd xmm1, xmm0')
                self.e('movapd xmm0, xmm1')
            else: self.e('neg rax')
            self.guardar(q.res, q.res.tipo)
        elif op in ('AND', 'OR'):
            self.operandos(q.a1, q.a2, 'boolean')
            self.e('and rax, rdx' if op == 'AND' else 'or rax, rdx')
            self.e('test rax, rax')
            self.e('setne al')
            self.e('movzx rax, al')
            self.guardar(q.res, 'boolean')
        elif op in ('<', '<=', '>', '>=', '==', '!='):
            if q.a1.tipo in ('string', 'ip') and q.a2.tipo in ('string', 'ip'):
                if op not in ('==','!='):
                    raise GeneracionASMError('Comparación de cadenas inválida')
                self.cargar(q.a1)
                self.e(f'mov {self.sp(self.scratch1)}, rax')
                self.cargar(q.a2)
                self.e('mov rsi, rax')
                self.e(f'mov rdi, {self.sp(self.scratch1)}')
                self.e('call ng_text_eq')
                if op == '!=': self.e('xor eax, 1')
            else:
                es_float = q.a1.tipo == 'float' or q.a2.tipo == 'float'
                self.operandos(q.a1, q.a2, 'float' if es_float else 'int')
                if es_float:
                    self.e('ucomisd xmm0, xmm1')
                    instruccion = {'<':'setb','<=':'setbe','>':'seta','>=':'setae','==':'sete','!=':'setne'}[op]
                else:
                    self.e('cmp rax, rdx')
                    instruccion = {'<':'setl','<=':'setle','>':'setg','>=':'setge','==':'sete','!=':'setne'}[op]
                self.e(f'{instruccion} al')
                self.e('movzx rax, al')
            self.guardar(q.res, 'boolean')
        elif op == 'GOTO':
            self.e(f'jmp L{q.res}')
        elif op == 'GOTOF':
            self.cargar(q.a1)
            self.e('test rax, rax')
            self.e(f'jz L{q.res}')
        elif op == 'LOAD':
            if self.registro:
                ruta = os.path.abspath(self.registro)
            else:
                base = os.path.dirname(os.path.abspath(self.programa))
                ruta = os.path.join(base, q.a1.valor)
            lab = self.cadena(ruta)
            self.e(f'lea rdi, [rip + {lab}]')
            self.e('call ng_load')
            self.guardar(q.res, 'event[]')
        elif op == 'FE_INIT':
            self.cargar(q.a1)
            self.e('mov rdi, rax')
            self.e('call ng_init')
        elif op == 'FE_NEXT':
            self.cargar(q.a1)
            self.e('mov rdi, rax')
            self.e('call ng_next')
            self.e(f'mov {self.pos(q.a2)}, rax')
            self.e('test rax, rax')
            self.e('setne al')
            self.e('movzx rax, al')
            self.guardar(q.res, 'boolean')
        elif op == 'ALERT':
            self.cargar(q.a1)
            self.e(f'mov {self.sp(self.scratch1)}, rax')
            self.cargar(q.a2)
            self.e('mov rsi, rax')
            self.e(f'mov rdi, {self.sp(self.scratch1)}')
            self.e('call ng_alert')
        elif op == 'MARK':
            self.cargar(q.a1)
            self.e(f'mov {self.sp(self.scratch1)}, rax')
            self.cargar(q.a2)
            self.e('mov rsi, rax')
            self.e(f'mov rdi, {self.sp(self.scratch1)}')
            self.e('call ng_mark')
        else:
            raise GeneracionASMError(f'Operación de NetGuard sin traducción nativa: {op}')

    def generar(self):
        for i,q in enumerate(self.q,1):
            self.quad(q,i)
        prologo = ['.intel_syntax noprefix', '.section .rodata']
        for valor,lab in self.strings.items():
            bb = (valor.encode('utf-8') + b'\x00')
            prologo.append(f'{lab}:')
            prologo.append('    .byte ' + ', '.join(str(x) for x in bb))
        prologo.append('.section .data')
        for d in sorted(self.globales):
            prologo.append(f'g_{d}: .quad 0')
        prologo.extend(['.section .text', '.globl main', '.type main, @function', 'main:',
                        '    push rbp', '    mov rbp, rsp', f'    sub rsp, {self.frame}'])
        # Inicializa todas las ranuras, incluidos punteros y temporales
        for n in sorted(self.slot):
            prologo.append(f'    mov {self.pos(n)}, 0')
        return '\n'.join(prologo + self.lineas + ['.section .note.GNU-stack,"",@progbits', ''])


def generar_asm(cuadruplos, tabla, programa, registro=None):
    return BackendASM(cuadruplos, tabla, programa, registro).generar()
