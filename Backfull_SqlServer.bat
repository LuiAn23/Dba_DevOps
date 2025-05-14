@echo off
SET SQL_SERVER=COCLOCCCPRD07\SQLEXPRESS
SET BASE_BACKUP_DIR=\\192.168.30.18\F\Diario\Laserfiche

:: Obtener la fecha y hora actual en formato YYYYMMDD y HHMM
FOR /F %%I IN ('powershell -NoProfile -Command "Get-Date -Format yyyyMMddHHmm"') DO SET datetime=%%I
SET DATE_FOLDER=%datetime:~0,8%
SET TIME_NOW=%datetime:~8,4%

:: Crear la carpeta de backup con la fecha actual
SET BACKUP_DIR=%BASE_BACKUP_DIR%\%DATE_FOLDER%
IF NOT EXIST "%BACKUP_DIR%" (
    echo Creando carpeta de backups: %BACKUP_DIR%
    mkdir "%BACKUP_DIR%"
) else (
    echo La carpeta de backups ya existe: %BACKUP_DIR%
)

:: Script SQL para realizar el backup
SET SQL_SCRIPT=%TEMP%\backup_full_script.sql

:: Crear el script SQL para realizar el backup de todas las bases de datos
echo DECLARE @name VARCHAR(50), @path VARCHAR(500), @backfile VARCHAR(500) > %SQL_SCRIPT%
echo DECLARE db_cursor CURSOR FOR >> %SQL_SCRIPT%
echo SELECT name >> %SQL_SCRIPT%
echo FROM sys.databases >> %SQL_SCRIPT%
echo WHERE name NOT IN ('master', 'model', 'msdb', 'tempdb') >> %SQL_SCRIPT%
echo OPEN db_cursor >> %SQL_SCRIPT%
echo FETCH NEXT FROM db_cursor INTO @name >> %SQL_SCRIPT%
echo WHILE @@FETCH_STATUS = 0 >> %SQL_SCRIPT%
echo BEGIN >> %SQL_SCRIPT%
echo SET @path = '%BACKUP_DIR%\%DATE_FOLDER%_%TIME_NOW%_' + @name + '_FULL.bak' >> %SQL_SCRIPT%
echo SET @backfile = 'BACKUP DATABASE [' + @name + '] TO DISK = ''' + @path + ''' WITH INIT' >> %SQL_SCRIPT%
echo EXEC(@backfile) >> %SQL_SCRIPT%
echo FETCH NEXT FROM db_cursor INTO @name >> %SQL_SCRIPT%
echo END >> %SQL_SCRIPT%
echo CLOSE db_cursor >> %SQL_SCRIPT%
echo DEALLOCATE db_cursor >> %SQL_SCRIPT%

:: Ejecutar el script SQL utilizando sqlcmd (Autenticación integrada de Windows)
echo Ejecutando el script de backup completo en SQL Server...
sqlcmd -S %SQL_SERVER% -E -i %SQL_SCRIPT% > "%BACKUP_DIR%\backup_log.txt" 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error al ejecutar el script de backup. Verifique el archivo de log para más detalles: %BACKUP_DIR%\backup_log.txt
    del %SQL_SCRIPT%
    exit /b %ERRORLEVEL%
) ELSE (
    echo El script de backup se ejecutó correctamente.
)

:: Limpiar el archivo temporal
del %SQL_SCRIPT%

:: Comprimir la carpeta de backup
echo Comprimiendo la carpeta de backups...
powershell -Command "Compress-Archive -Path '%BACKUP_DIR%\*' -DestinationPath '%BACKUP_DIR%.zip'"

:: Verificar si la compresión se realizó correctamente
IF %ERRORLEVEL% NEQ 0 (
    echo Error al comprimir la carpeta de backups.
    exit /b %ERRORLEVEL%
) else (
    echo Carpeta de backups comprimida exitosamente.
)

:: Copiar el archivo comprimido al servidor remoto
echo Copiando el archivo comprimido al servidor remoto...
copy "%BACKUP_DIR%.zip" "%BASE_BACKUP_DIR%\%DATE_FOLDER%.zip"
IF %ERRORLEVEL% NEQ 0 (
    echo Error al copiar el archivo comprimido al servidor remoto.
    exit /b %ERRORLEVEL%
) else (
    echo Archivo comprimido copiado exitosamente al servidor remoto.
)