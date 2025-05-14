import cx_Oracle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def fetch_data_from_db():
    # Database connection details
    dsn_tns = cx_Oracle.makedsn('coclocccprdb01', '1521', service_name='REGISTRO')
    connection = cx_Oracle.connect(user='system', password='ZSbooyioUkE1tlFT3NY2', dsn=dsn_tns)

    # Query to fetch data
    query = """
    SELECT *
    FROM CE_SOLICITUD
    WHERE TRUNC(SOLI_FECSOL) >= TO_DATE(TO_CHAR(SYSDATE, 'dd/mm/yyyy'), 'dd/mm/yyyy') - 10
    AND SOLI_ESTADO IN (6, 7)
    ORDER BY SOLI_FECSOL DESC
    """

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return rows

def count_estado_6(rows):
    return sum(1 for row in rows if row[10] == 6)

def send_email(count_estado_6):
    if count_estado_6 > 3:
        # Email details
        sender_email = "your_email@example.com"
        receiver_email = "luis.orobio@sisa.com.co,mgonzale@ccc.org.co,ajojoa@ccc.org.co,jsantacr@ccc.org.co"
        cc_email = "wimunoz@ccc.org.co,fjaramillo@ccc.org.co,jcmendez@ccc.org.co,practop@ccc.org.co"
        subject = "Estado de Salud de los servicios y URL"
        body = f"La validación del servicio y las URL se ha realizado. Adjunto se encuentran los logs con los detalles. The count of rows with SOLI_ESTADO = 6 is {count_estado_6}, which is greater than 3."

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Cc'] = cc_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Attach log files
        log_files = ["/home/sisadmin/sta.log", "/home/sisadmin/service_status.log"]
        for log_file in log_files:
            with open(log_file, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(log_file)}",
                )
                msg.attach(part)

        # Send the email
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login(sender_email, 'your_password')
            server.sendmail(sender_email, receiver_email.split(",") + cc_email.split(","), msg.as_string())

def main():
    rows = fetch_data_from_db()
    count = count_estado_6(rows)
    send_email(count)

if __name__ == "__main__":
    main()