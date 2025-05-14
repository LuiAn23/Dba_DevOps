@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

SET LOCAL_BACKUP_DIR=G:\Backups_Full
SET REMOTE_BACKUP_DIR=\\WINVMWAPPRD90\Laserfiche
SET LOG_DIR=%LOCAL_BACKUP_DIR%\Logs

REM Obtener la fecha y hora actual en formato YYYYMMDD_HHMMSS
FOR /F "tokens=1-4 delims=/ " %%A IN ('date /t') DO SET DATE=%%D%%B%%C
FOR /F "tokens=1-2 delims=: " %%A IN ('time /t') DO SET TIME=%%A%%B
SET LOG_FILE=%LOG_DIR%\execution_log_%DATE%_%TIME%.log

IF NOT EXIST %LOG_DIR% (
    mkdir %LOG_DIR%
)

echo LOCAL_BACKUP_DIR=%LOCAL_BACKUP_DIR% > %LOG_FILE%
echo REMOTE_BACKUP_DIR=%REMOTE_BACKUP_DIR% >> %LOG_FILE%

REM Obtener la última carpeta en el directorio de backups, excluyendo la carpeta Logs
FOR /F "delims=" %%I IN ('dir "%LOCAL_BACKUP_DIR%\*" /b /ad /o-d /t:w ^| findstr /v /i "Logs"') DO SET LAST_FOLDER=%%I & GOTO :FOUND_FOLDER

:FOUND_FOLDER
IF NOT DEFINED LAST_FOLDER (
    echo No se encontró ninguna carpeta en %LOCAL_BACKUP_DIR%. >> %LOG_FILE%
    exit /b 1
)

echo LAST_FOLDER=%LAST_FOLDER% >> %LOG_FILE%

REM Comprimir la última carpeta
SET LAST_ZIP_FILE=%LAST_FOLDER%.zip
echo Comprimiendo la carpeta %LAST_FOLDER%... >> %LOG_FILE%
7z a "%LOCAL_BACKUP_DIR%\%LAST_ZIP_FILE%" "%LOCAL_BACKUP_DIR%\%LAST_FOLDER%\*" >> %LOG_FILE% 2>&1
IF ERRORLEVEL 1 (
    echo Error al comprimir la carpeta %LAST_FOLDER%. >> %LOG_FILE%
    exit /b %ERRORLEVEL%
) else (
    echo Carpeta comprimida exitosamente. >> %LOG_FILE%
)

echo LAST_ZIP_FILE=%LAST_ZIP_FILE% >> %LOG_FILE%

REM Enviar el archivo comprimido al servidor remoto
echo Enviando el archivo comprimido al servidor remoto... >> %LOG_FILE%
copy "%LOCAL_BACKUP_DIR%\%LAST_ZIP_FILE%" "%REMOTE_BACKUP_DIR%\%LAST_ZIP_FILE%"
IF ERRORLEVEL 1 (
    echo Error al enviar el archivo comprimido al servidor remoto. >> %LOG_FILE%
    exit /b %ERRORLEVEL%
) else (
    echo Archivo comprimido enviado exitosamente al servidor remoto. >> %LOG_FILE%
)

REM Borrar archivos .zip de más de 2 días
echo Borrando archivos .zip de más de 2 días... >> %LOG_FILE%
forfiles /p "%LOCAL_BACKUP_DIR%" /s /m *.zip /d -2 /c "cmd /c del @path"
IF ERRORLEVEL 1 (
    echo Error al borrar archivos .zip antiguos. >> %LOG_FILE%
    exit /b %ERRORLEVEL%
) else (
    echo Archivos .zip antiguos borrados exitosamente. >> %LOG_FILE%
)

echo El archivo de log se ha guardado en %LOG_FILE%
pause