oracle@coclocccprdb01 Monitoring]$ cat Validar_Certificados.sh
#!/bin/bash

# Variables de entorno
ORACLE_HOST="coclocccprdb01"
ORACLE_PORT="1521"
ORACLE_SERVICE_NAME="REGISTRO"
ORACLE_USER="system"
ORACLE_PASSWORD="ZSbooyioUkE1tlFT3NY2"
SMTP_SERVER="smtp.example.com"
SMTP_PORT="587"
SMTP_USER="your_email@example.com"
SMTP_PASSWORD="your_password"
RECEIVER_EMAIL="luis.orobio@sisa.com.co"
CC_EMAIL="luis.orobio@sisa.com.co"
SUBJECT="Estado Certificados"

# Consulta SQL
QUERY="SELECT * FROM CE_SOLICITUD WHERE TRUNC(SOLI_FECSOL) >= TO_DATE(TO_CHAR(SYSDATE, 'dd/mm/yyyy'), 'dd/mm/yyyy') - 10 AND SOLI_ESTADO IN (6, 7) ORDER BY SOLI_FECSOL DESC;"

# Ejecutar la consulta y guardar el resultado en un archivo
sqlplus -s ${ORACLE_USER}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME} <<EOF > resultado.txt
SET PAGESIZE 50000
SET LINESIZE 32767
SET FEEDBACK OFF
SET ECHO OFF
${QUERY}
EXIT;
EOF

# Contar el número de registros con SOLI_ESTADO = 6
COUNT_ESTADO_6=$(grep -c "6" resultado.txt)

# Generar el cuerpo del correo electrónico
BODY="Estado Actual de los certificados"

# Enviar el correo electrónico si COUNT_ESTADO_6 es mayor o igual a 2
if [ ${COUNT_ESTADO_6} -ge 2 ]; then
    echo "${BODY}" | mail -s "${SUBJECT}" -a resultado.txt -c "${CC_EMAIL}" "${RECEIVER_EMAIL}"
fi

# Limpiar archivos temporales
rm resultado.txt
