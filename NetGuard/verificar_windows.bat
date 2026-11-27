@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === NETGUARD: PRUEBAS EN WINDOWS (SIN ASM NATIVO) ===
py pruebas.py || exit /b 1
py pruebas_rubrica.py || exit /b 1
py pruebas_final.py --sin-asm || exit /b 1
echo Todas las pruebas Python terminaron correctamente.
