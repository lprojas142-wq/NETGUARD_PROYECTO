#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo '=== NETGUARD: PRUEBAS ==='
python3 pruebas.py
python3 pruebas_rubrica.py
python3 pruebas_final.py
echo '=== NETGUARD: CÓDIGO OBJETO DEMO ==='
python3 netguard.py tests/execution/recursion.ng --asm salida_recursion.asm --no-ejecutar
bash nativo/compilar_linux.sh salida_recursion.asm nativo/recursion_nativo
./nativo/recursion_nativo
