import cx_Oracle
from utils import send_email
from config import DB_CONFIG, MAIL_CONFIG

def get_certificate_count():
    query = """
    SELECT COUNT(*) AS count
    FROM CE_SOLICITUD
    WHERE TRUNC(SOLI_FECSOL) >= TO_DATE(TO_CHAR(SYSDATE, 'dd/mm/yyyy'), 'dd/mm/yyyy') - 10
    AND SOLI_ESTADO = 6
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
        return  # No enviar correo si no hay certificados
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
            <tr><th>Cantidad de Registros</th><th>Número de Registros</th><th>Estado</th></tr>
            <tr style='background-color: {color};'><td>{count}</td><td>{count}</td><td>{subject}</td></tr>
        </table>
    </body>
    </html>
    """
    send_email(subject, body)

if __name__ == "__main__":
    count = get_certificate_count()
    generate_report(count)