# -*- coding: utf-8 -*-
"""Política verificable de asignación de registros del backend Linux x86-64.

Asignación LOCAL por instrucción: los valores permanentes viven en memoria;
cada cuádruplo carga sus operandos a registros de trabajo, guarda el resultado
y por ello no mantiene temporales vivos entre instrucciones de máquina.

La política prioriza robustez y transparencia, no eficiencia óptima.
"""

class AsignadorRegistros:
    GENERAL = ('rax', 'rdx')
    REALES = ('xmm0', 'xmm1')
    ARGUMENTOS = ('rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9')
    PUNTERO_PILA = 'rbp'

    def entradas(self, tipo):
        return self.REALES if tipo == 'float' else self.GENERAL

    def resultado(self, tipo):
        return 'xmm0' if tipo == 'float' else 'rax'

    def parametros(self, cantidad):
        if cantidad > 6:
            raise ValueError('El backend admite máximo seis parámetros')
        return self.ARGUMENTOS[:cantidad]

    @staticmethod
    def estrategia():
        return [
            ('Enteros y booleanos', 'RAX / RDX', 'Carga, calcula y derrama a memoria'),
            ('Reales de doble precisión', 'XMM0 / XMM1', 'Aritmética SSE2, resultados a pila'),
            ('Dirección de eventos y cadenas', 'RDI / RSI', 'Argumentos de runtime C (ABI System V)'),
            ('Funciones de usuario', 'RDI, RSI, RDX, RCX, R8, R9', 'Hasta 6 parámetros de 64 bits'),
            ('Memoria de locales/temporales', 'RBP - desplazamiento', 'Ranuras de 8 bytes en stack frame'),
            ('Variables globales', 'RIP + g_dirección', 'Segmento .data'),
        ]


asignador = AsignadorRegistros()
