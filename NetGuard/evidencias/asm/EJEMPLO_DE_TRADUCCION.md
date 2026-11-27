# Fragmento representativo de generación x86-64

Para generar archivos `.asm` **ejecutables en TU equipo**, utiliza:

```bash
python3 netguard.py tests/execution/recursion.ng --asm salida_recursion.asm --no-ejecutar
bash nativo/compilar_linux.sh salida_recursion.asm nativo/recursion_nativo
./nativo/recursion_nativo
```

Ejemplos de mapeo instrucción intermedia → x86-64 (sintaxis Intel):

```asm
# Cuádruplo suma de enteros: (+, a, b, temporal)
mov rax, QWORD PTR [rbp - 8]
mov rdx, QWORD PTR [rbp - 16]
add rax, rdx
mov QWORD PTR [rbp - 24], rax

# Salto condicional (GOTOF, t1, —, L10)
mov rax, QWORD PTR [rbp - 32]
test rax, rax
jz L10

# Esquema de función recursiva (FUNC/RET)
push rbp
mov rbp, rsp
sub rsp, 128
# ... instrucciones ...
leave
ret
```

**Este archivo es solo un fragmento explicativo**: no es un programa completo ni se debe ensamblar directamente. Los `.asm` funcionales se generan mediante `--asm` con rutas correctas de tu computadora.
