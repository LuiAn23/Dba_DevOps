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
