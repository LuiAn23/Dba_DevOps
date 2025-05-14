@echo off
:inicio
REM Mostrar el menú de opciones
echo Seleccione la ruta de busqueda del archivo:
echo 1. \\192.168.202.115\pdf\rues\formularios\8
echo 2. \\192.168.202.115\pdf\rues\formularios\08
echo 3. \\192.168.202.115\pdf\rues\soporte\08
echo 4. \\192.168.202.115\pdfcew\CE\certificados\08
echo 5. \\192.168.202.115\pdf\rues\recibos
echo X. Salir

set /p option="Ingrese el numero de la opcion: "
REM Verificar si el usuario desea salir
if /i "%option%"=="X" (
    exit /b
)

REM Establecer la ruta de búsqueda según la opción seleccionada
if "%option%"=="1" (
    set sourcePath="\\192.168.202.115\pdf\rues\formularios\8"
) else if "%option%"=="2" (
    set sourcePath="\\192.168.202.115\pdf\rues\formularios\08"
) else if "%option%"=="3" (
    set sourcePath="\\192.168.202.115\pdf\rues\soportes\08"
) else if "%option%"=="4" (
    set sourcePath="\\192.168.202.115\pdfcew\CE\certificados\08"
) else if "%option%"=="5" (
    set sourcePath="\\192.168.202.115\pdf\rues\recibos"
) else (
    echo Opción no válida.
    pause
    goto inicio
)

REM Solicitar el nombre del archivo
set /p fileName="Ingrese el nombre del archivo (PDF): "
set destination="C:\Users\Analis15\Documents"

REM Construir la ruta completa del archivo fuente
set source=%sourcePath%\%fileName%

REM Imprimir las rutas para verificación
echo Ruta del archivo fuente: %source%
echo Ruta de destino: %destination%

REM Verificar si el archivo existe y copiarlo
if exist "%source%" (
    copy "%source%" "%destination%"
    echo Archivo copiado exitosamente.
) else (
    echo Archivo no encontrado.
)
pause
goto inicio