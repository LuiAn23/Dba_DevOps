
Scripts:


set line 180;
column 00 format a4
column 01 format a4
column 02 format a4
column 03 format a4
column 04 format a4
column 05 format a4
column 06 format a4
column 07 format a4
column 08 format a4
column 09 format a4
column 10 format a4
column 11 format a4
column 12 format a4
column 13 format a4
column 14 format a4
column 15 format a4
column 16 format a4
column 17 format a4
column 18 format a4
column 19 format a4
column 20 format a4
column 21 format a4
column 22 format a4
column 23 format a4

COLUMN DAY FORMAT A10

SELECT SUBSTR(first_time,1,9) DAY,
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'00',1,0)),'999') "00",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'01',1,0)),'999') "01",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'02',1,0)),'999') "02",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'03',1,0)),'999') "03",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'04',1,0)),'999') "04",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'05',1,0)),'999') "05",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'06',1,0)),'999') "06",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'07',1,0)),'999') "07",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'08',1,0)),'999') "08",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'09',1,0)),'999') "09",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'10',1,0)),'999') "10",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'11',1,0)),'999') "11",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'12',1,0)),'999') "12",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'13',1,0)),'999') "13",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'14',1,0)),'999') "14",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'15',1,0)),'999') "15",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'16',1,0)),'999') "16",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'17',1,0)),'999') "17",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'18',1,0)),'999') "18",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'19',1,0)),'999') "19",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'20',1,0)),'999') "20",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'21',1,0)),'999') "21",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'22',1,0)),'999') "22",
TO_CHAR(SUM(DECODE(SUBSTR(TO_CHAR(first_time,'DD-MM-YY HH24:MI:SS'),10,2),'23',1,0)),'999') "23" ,
count(*) "Total"
FROM v$log_history
WHERE SUBSTR(first_time,1,9) LIKE '%&MONTH%'
GROUP BY SUBSTR(first_time,1,9)
ORDER BY SUBSTR(DAY,7,9),SUBSTR(DAY,1,6),SUBSTR(DAY,1,2)
;
/


Notas:

Asegúrate de ajustar el query en get_redo_count según tus necesidades específicas.
Configura las variables de entorno para las credenciales de la base de datos y otros parámetros necesarios.
Verifica que el servidor SMTP esté correctamente configurado para enviar correos.
Con esta estructura, el sistema validará la cantidad de redos y enviará un correo si se supera el umbral especificado.




vi config.py

DB_CONFIG = {
    'user': os.getenv("ORACLE_USER", "system"),
    'password': os.getenv("ORACLE_PASSWORD", "ZSbooyioUkE1tlFT3NY2"),
    'dsn': f"{os.getenv('ORACLE_HOST', '192.168.202.4')}:{os.getenv('ORACLE_PORT', '1521')}/{os.getenv('ORACLE_SERVICE_NAME', 'REGISTRO')}",
    'encoding': 'UTF-8'
}

MAIL_CONFIG = {
    'subject_no_redos': 'No se evidencia Redos',
    'subject_warning': 'Warning se evidencian algunos Redos',
    'subject_alert': 'Alerta se evidencian muchos Redos',
    'to': 'luis.orobio@sisa.com.co',
    'cc': '',
    'body': 'Se adjunta el reporte de redos.'
}




vi main.py

import cx_Oracle
from utils import send_email
from config import DB_CONFIG, MAIL_CONFIG

def get_redo_count():
    query = """
    SELECT COUNT(*) AS count
    FROM v$log_history
    WHERE SUBSTR(first_time,1,9) LIKE '%&MONTH%'
    """
    connection = cx_Oracle.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result[0]

def generate_report(count):
    if count == 0:
        return  # No enviar correo si no hay redos
    elif 8 <= count <= 12:
        subject = MAIL_CONFIG['subject_warning']
        color = 'yellow'
    elif count > 13:
        subject = MAIL_CONFIG['subject_alert']
        color = 'red'
    else:
        return  # No enviar correo si el conteo no está en los rangos especificados

    body = f"""
    <html>
    <body>
        <table border='1'>
            <tr><th>Cantidad de Redos</th><th>Número de Redos</th><th>Estado</th></tr>
            <tr style='background-color: {color};'><td>{count}</td><td>{count}</td><td>{subject}</td></tr>
        </table>
    </body>
    </html>
    """
    send_email(subject, body)

if __name__ == "__main__":
    count = get_redo_count()
    generate_report(count)
	
	
vi utils.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import MAIL_CONFIG

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = MAIL_CONFIG['to']
    msg['To'] = MAIL_CONFIG['to']
    msg['Cc'] = MAIL_CONFIG['cc']
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP('localhost')
    recipients = MAIL_CONFIG['to'].split(',') + MAIL_CONFIG['cc'].split(',')
    server.sendmail(MAIL_CONFIG['to'], recipients, msg.as_string())
    server.quit()
	
	
	
	
	
vi config.sh

#!/bin/bash

# Configuración de la base de datos
export ORACLE_USER="system"
export ORACLE_PASSWORD="ZSbooyioUkE1tlFT3NY2"
export ORACLE_HOST="192.168.202.4"
export ORACLE_PORT="1521"
export ORACLE_SERVICE_NAME="REGISTRO"

# Configuración del correo
MAIL_TO="luis.orobio@sisa.com.co"
MAIL_CC=""
SUBJECT_WARNING="Warning se evidencian algunos Redos"
SUBJECT_ALERT="Alerta se evidencian muchos Redos"



vi main.sh

#!/bin/bash

# Cargar la configuración
source ./config.sh

# Obtener el mes actual en el formato adecuado (ej. MAR)
MONTH=$(date +%b | tr '[:lower:]' '[:upper:]')

# Obtener la cantidad de redos
REDO_COUNT=$(sqlplus -s ${ORACLE_USER}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME} <<EOF
SET HEAD OFF
SET FEEDBACK OFF
SET PAGESIZE 0
SELECT COUNT(*) FROM v\$log_history WHERE SUBSTR(first_time,1,9) LIKE '%${MONTH}%';
EXIT;
EOF
)

# Limpiar el resultado para obtener solo el número
REDO_COUNT=$(echo $REDO_COUNT | xargs)

# Generar el reporte y enviar el correo
generate_report() {
    local count=$1
    local subject=$2
    local color=$3

    local body="<html><body><table border='1'><tr><th>Cantidad de Redos</th><th>Número de Redos</th><th>Estado</th></tr><tr style='background-color: ${color};'><td>${count}</td><td>${count}</td><td>${subject}</td></tr></table></body></html>"

    echo -e "Subject: ${subject}\nTo: ${MAIL_TO}\nCc: ${MAIL_CC}\nContent-Type: text/html\n\n${body}" | sendmail -t
}

if [ "$REDO_COUNT" -eq 0 ]; then
    exit 0  # No enviar correo si no hay redos
elif [ "$REDO_COUNT" -ge 8 ] && [ "$REDO_COUNT" -le 12 ]; then
    generate_report "$REDO_COUNT" "$SUBJECT_WARNING" "yellow"
elif [ "$REDO_COUNT" -gt 13 ]; then
    generate_report "$REDO_COUNT" "$SUBJECT_ALERT" "red"
fi