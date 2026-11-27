#!/usr/bin/env bash
# Compila el .asm generado en un ejecutable nativo para Linux x86-64.
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo 'Uso: bash nativo/compilar_linux.sh archivo.asm [salida]' >&2
  exit 2
fi
SRC="$1"; DEST="${2:-nativo/netguard_nativo}"
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIR="$(mktemp -d)"
trap 'rm -rf "$DIR"' EXIT
gcc -c -x assembler "$SRC" -o "$DIR/programa.o"
gcc -std=c11 -O2 -Wall -Wextra -c "$BASE/runtime.c" -o "$DIR/runtime.o"
gcc -no-pie "$DIR/programa.o" "$DIR/runtime.o" -o "$DEST"
echo "Ejecutable listo: $DEST"
