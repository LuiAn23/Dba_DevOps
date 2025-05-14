# email_utils.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import MAIL_CONFIG

def send_email(subject, body):
    """
    Envía un correo electrónico usando smtplib.
    """
    msg = MIMEMultipart()
    msg['From'] = MAIL_CONFIG['to']  # Usar 'to' como remitente
    msg['To'] = MAIL_CONFIG['to']  # Usar 'to' como destinatario
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('localhost', 587)  # Usar 'localhost' y el puerto 587
        # server.starttls()  # Encriptar la conexión usando TLS (opcional)
        # server.login(MAIL_CONFIG['to'], MAIL_CONFIG['password'])  # Autenticarse (opcional)
        recipients = MAIL_CONFIG['to'].split(',') + MAIL_CONFIG.get('cc', '').split(',')  # Obtener destinatarios y CC
        server.sendmail(MAIL_CONFIG['to'], recipients, msg.as_string())
        print("Correo electrónico enviado con éxito.")
    except Exception as e:
        print(f"Error al enviar el correo electrónico: {e}")
    finally:
        server.quit()
