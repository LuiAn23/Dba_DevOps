#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filepath: check_weblogic_status.py

import paramiko
import smtplib
import datetime
from email.mime.text import MIMEText

# Configuración de los servidores WebLogic
servers = [
    {
        'host': '192.168.202.108',
        'so_username': 'sisadmin',
        'wl_username': 'weblogic',
        'wl_password': 'wl_password'  # Reemplaza con la contraseña real
    },
    {
        'host': '192.168.202.109',
        'so_username': 'sisadmin',
        'wl_username': 'weblogic',
        'wl_password': 'wl_password'  # Reemplaza con la contraseña real
    }
]

# Configuración de correo electrónico para alertas
mail_server = 'smtp.example.com'
mail_port = 25
mail_from = 'weblogic-monitor@example.com'
mail_to = ['admin@example.com']  # Actualiza con correos reales

# Función para verificar el estado de los servidores WebLogic
def check_server_status(server):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server['host'], username=server['so_username'])

        # Comando para verificar el estado de los manejados
        command = """
        . /u01/oracle/app/oracle/product/14.1.1/wlserver/server/bin/setWLSEnv.sh
        java weblogic.WLST <<EOF
        connect('%s', '%s', 't3://%s:7001')
        domainRuntime()
        cd('/ServerLifeCycleRuntimes')
        servers = ls(returnMap='true')
        for server in servers:
            cd('/ServerLifeCycleRuntimes/' + server)
            state = cmo.getState()
            print('Servidor: ' + server + ' Estado: ' + state)
        disconnect()
        exit()
        EOF
        """ % (server['wl_username'], server['wl_password'], server['host'])

        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        errors = stderr.read().decode()

        ssh.close()

        if errors:
            print(f"Errores en {server['host']}: {errors}")
            return None
        else:
            return output

    except Exception as e:
        print(f"Error al conectar con {server['host']}: {str(e)}")
        return None

# Enviar correo electrónico de alerta
def send_alert(message_content):
    msg = MIMEText(message_content)
    msg['Subject'] = 'ALERTA: Estado de servidores WebLogic'
    msg['From'] = mail_from
    msg['To'] = ', '.join(mail_to)

    try:
        smtp = smtplib.SMTP(mail_server, mail_port)
        smtp.sendmail(mail_from, mail_to, msg.as_string())
        smtp.quit()
        print('Alerta enviada correctamente')
    except Exception as e:
        print('Error al enviar la alerta: ' + str(e))

# Función principal
def main():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message_content = f"Monitoreo de servidores WebLogic - {timestamp}\n\n"

    for server in servers:
        status = check_server_status(server)
        if status:
            message_content += f"Servidor {server['host']}:\n{status}\n"
        else:
            message_content += f"Servidor {server['host']}: No se pudo obtener el estado\n"

    send_alert(message_content)

# Ejecutar el script
if __name__ == '__main__':
    main()