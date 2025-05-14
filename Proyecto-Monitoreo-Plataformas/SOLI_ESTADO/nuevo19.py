
############### Solicitud de estado 6 > 10, noticar, Actividad Pendiente ########################################

select  * 
from  CE_SOLICITUD  
WHERE  trunc(SOLI_FECSOL) >= to_date(to_char(SYSDATE,'dd/mm/yyyy') ,'dd/mm/yyyy') -10
and soli_estado in (6,7) 
order by SOLI_FECSOL desc;


################################################################################################################


192.168.202.115
192.168.202.116
192.168.202.101
192.168.202.102
192.168.202.103
192.168.202.106
192.168.202.107
192.168.202.109
192.168.202.108
192.168.202.110
192.168.202.118
192.168.202.148
192.168.202.149
192.168.202.141
192.168.202.4
192.168.202.2
192.168.202.3

##############  crear realaccion de confianza entre servidores ####################################

Contraseña: S1S4_adm1n$#
            S1S4_adm1n##
			S1S4_adm1n$#
			S1S4_adm1n**
			S1S4_adm1n*#




-------------- Origen 

ssh sisadmin@192.168.202.108
ssh sisadmin@192.168.202.109
cat ~/.ssh/authorized_keys
ssh-keygen -t rsa -b 2048
cat ~/.ssh/authorized_keys
ssh-keygen -t rsa -b 2048
cat ~/.ssh/authorized_keys
ssh-copy-id sisadmin@192.168.202.108
ssh-copy-id sisadmin@192.168.202.118
ssh sisadmin@192.168.202.148
ssh sisadmin@192.168.202.106


ssh-copy-id sisadmin@192.168.202.103

---------- Destino

ssh-keygen -t rsa -b 2048
ssh-copy-id sisadmin@192.168.202.116

ssh-keygen -t rsa -b 2048
ssh-copy-id user@192.168.202.116
ssh-copy-id sisadmin@192.168.202.116
ssh user@192.168.202.116
ssh sisadmin@192.168.202.116


ssh-keygen -t rsa -b 2048
ssh-copy-id sisadmin@192.168.202.116
ssh sisadmin@192.168.202.116

S1S4_adm1n*#

192.168.202.103


{"ip": "192.168.202.110", "url": "http://192.168.202.110:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True},

{"ip": "192.168.202.103", "url": "", "services": ["nginx", "snmpd", "firewalld"]},
{"ip": "192.168.202.102", "url": "https://192.168.202.102:4848/common/applications/fileChooser.jsf", "services": ["glassfish", "nginx", "java", "firewalld"]},


{"ip": "192.168.202.107", "url": "", "services": ["nginx", "firewalld"], "require_pdf": False},




######################################################################


####################################

Nueva Version. #######################

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import subprocess
from validate_ip import check_url_with_certificate

# Configuración de los servidores y servicios a verificar
SERVERS = [
    {"ip": "192.168.202.101", "url": "https://192.168.202.101:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "Servidor 1"},
    {"ip": "192.168.202.102", "url": "https://192.168.202.102:4848/common/applications/fileChooser.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "Servidor 2"},
    {"ip": "192.168.202.103", "url": "", "services": ["nginx", "snmpd", "firewalld"], "require_pdf": False, "label": "Servidor 3"},
    {"ip": "192.168.202.108", "url": "http://192.168.202.108:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Servidor 4"},
    {"ip": "192.168.202.109", "url": "http://192.168.202.109:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Servidor 5"},
    {"ip": "192.168.202.115", "url": "https://192.168.202.115:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "Servidor 6"},
    {"ip": "192.168.202.116", "url": "https://192.168.202.116:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "Servidor 7"},
    {"ip": "192.168.202.149", "url": "http://192.168.202.149:5050/svi/08/inicio", "services": ["glassfish"], "require_pdf": True, "label": "Servidor 8"},
    {"ip": "192.168.202.149", "url": "http://192.168.202.149:5050/svi/08/inicio", "services": ["glassfish"], "require_pdf": True, "label": "Servidor 9"}
]
LOG_FILE = "/home/sisadmin/sta.log"
SERVICE_STATUS_LOG = "/home/sisadmin/service_status.log"
MAIL_SUBJECT = "Estado de Salud de los servicios y URL"
MAIL_TO = "luis.orobio@sisa.com.co"
MAIL_CC = ""
MAIL_BODY = "La validación del servicio y las URL se ha realizado. Adjunto se encuentran los logs con los detalles."

# Definir errores conocidos
KNOWN_ERRORS = {
    "nginx": ["nginx: [emerg]"],
    "firewalld": ["firewalld: [error]"],
    "snmpd": ["snmpd: [error]"]  # Asegúrate de incluir errores conocidos para snmpd si es necesario
}

# Vaciar los archivos de logs al inicio de cada ejecución
open(LOG_FILE, 'w').close()
open(SERVICE_STATUS_LOG, 'w').close()

def check_service(server_ip, service_name):
    try:
        if service_name == "nginx":
            result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "systemctl status nginx"], capture_output=True, text=True)
            if "active (running)" in result.stdout:
                status = "Exitoso"
            elif any(error in result.stdout for error in KNOWN_ERRORS["nginx"]):
                status = "Amarillo"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Known error detected for {service_name} on {server_ip}. Response: {result.stdout}\n")
            else:
                status = "Fallido"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Service check failed for {service_name} on {server_ip}. Response: {result.stdout}\n")
        elif service_name == "snmpd":
            result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "systemctl status snmpd"], capture_output=True, text=True)
            if "active (running)" in result.stdout:
                status = "Exitoso"
            elif any(error in result.stdout for error in KNOWN_ERRORS["snmpd"]):
                status = "Amarillo"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Known error detected for {service_name} on {server_ip}. Response: {result.stdout}\n")
            else:
                status = "Fallido"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Service check failed for {service_name} on {server_ip}. Response: {result.stdout}\n")
        elif service_name == "firewalld":
            result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "systemctl status firewalld"], capture_output=True, text=True)
            if "inactive (dead)" in result.stdout:
                status = "Exitoso"
            elif any(error in result.stdout for error in KNOWN_ERRORS["firewalld"]):
                status = "Amarillo"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Known error detected for {service_name} on {server_ip}. Response: {result.stdout}\n")
            else:
                status = "Fallido"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Service check failed for {service_name} on {server_ip}. Response: {result.stdout}\n")
        else:
            result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, f"ps -fea | grep -v grep | grep {service_name}"], capture_output=True, text=True)
            if result.returncode == 0:
                status = "Exitoso"
            else:
                status = "Fallido"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Service check failed for {service_name} on {server_ip}. Response: {result.stdout}\n")
        return status
    except Exception as e:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Exception occurred while checking service {service_name} on {server_ip}: {str(e)}\n")
        return "Fallido"

def check_url(url):
    if not url:
        return "No URL"
    return check_url_with_certificate(url)

def check_cpu_load(server_ip):
    try:
        result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "uptime"], capture_output=True, text=True)
        load_average = result.stdout.split()[-3:]
        load_average = [float(load.strip(',').replace(',', '.')) for load in load_average]
        return load_average
    except Exception as e:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Exception occurred while checking CPU load on {server_ip}: {str(e)}\n")
        return [0.0, 0.0, 0.0]

def check_memory(server_ip):
    try:
        result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "free -m"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        mem_line = lines[1].split()
        total_mem = int(mem_line[1])
        used_mem = int(mem_line[2])
        mem_usage_percent = (used_mem / total_mem) * 100
        return mem_usage_percent
    except Exception as e:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Exception occurred while checking memory on {server_ip}: {str(e)}\n")
        return 0.0

def check_filesystem(server_ip, require_pdf):
    try:
        result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "df -h"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        filesystem_status = []
        for line in lines[1:]:
            parts = line.split()
            if len(parts) > 5 and parts[5] == '/pdf':
                filesystem_status.append({
                    'filesystem': parts[0],
                    'size': parts[1],
                    'used': parts[2],
                    'avail': parts[3],
                    'use%': parts[4],
                    'mounted_on': parts[5]
                })
        if not filesystem_status and not require_pdf:
            filesystem_status.append({
                'filesystem': 'N/A',
                'size': 'N/A',
                'used': 'N/A',
                'avail': 'N/A',
                'use%': 'N/A',
                'mounted_on': 'N/A'
            })
        return filesystem_status
    except Exception as e:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Exception occurred while checking filesystem on {server_ip}: {str(e)}\n")
        return [{
            'filesystem': 'N/A',
            'size': 'N/A',
            'used': 'N/A',
            'avail': 'N/A',
            'use%': 'N/A',
            'mounted_on': 'N/A'
        }]

def get_cpu_count(server_ip):
    try:
        result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "nproc"], capture_output=True, text=True)
        return int(result.stdout.strip())
    except Exception as e:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Exception occurred while getting CPU count on {server_ip}: {str(e)}\n")
        return 0

def generate_report():
    report = "<html><body><table border='1'><tr><th>ETIQUETA</th><th>SERVIDOR</th><th>FILESYSTEM</th><th>CPU</th><th>MEMORIA</th><th>SERVICIOS</th><th>URL</th></tr>"
    for server in SERVERS:
        label = server["label"]
        server_ip = server["ip"]
        url = server["url"]
        require_pdf = server.get("require_pdf", False)
        services_status = [check_service(server_ip, service) for service in server["services"]]
        url_status = check_url(url)
        
        # Check CPU load average
        cpu_load = check_cpu_load(server_ip)
        cpu_count = get_cpu_count(server_ip)
        cpu_load_html = f"<td style='background-color: {'red' if cpu_load[2] > cpu_count else 'green'}'>{cpu_load[2]}</td>"
        
        # Check memory usage
        mem_usage_percent = check_memory(server_ip)
        mem_usage_html = f"<td style='background-color: {'red' if mem_usage_percent > 90 else 'green'}'>{mem_usage_percent:.2f}%</td>"
        
        # Check filesystem usage for /pdf only
        filesystem_status_list = check_filesystem(server_ip, require_pdf)
        filesystem_html_list = []
        for fs in filesystem_status_list:
            if fs['filesystem'] == 'N/A':
                fs_html = f"<td style='background-color: yellow'>N/A</td>"
            elif fs['use%'] > '95%':
                fs_html = f"<td style='background-color: red'>{fs['filesystem']} {fs['use%']}</td>"
            else:
                fs_html = f"<td style='background-color: green'>{fs['filesystem']} {fs['use%']}</td>"
            filesystem_html_list.append(fs_html)
        
        # Check if all services are successful
        if not services_status:
            services_status_html = "<td style='background-color: yellow'>N/A</td>"
        else:
            all_services_successful = all(status == "Exitoso" for status in services_status)
            any_service_yellow = any(status == "Amarillo" for status in services_status)
            if all_services_successful:
                services_status_html = "<td style='background-color: green'>Exitoso</td>"
            elif any_service_yellow:
                services_status_html = "<td style='background-color: yellow'>Amarillo</td>"
            else:
                services_status_html = "<td style='background-color: red'>Fallido</td>"
        
        url_status_html = f"<td style='background-color: {'yellow' if url_status == 'No URL' else 'green' if url_status == 'Exitoso' else 'red'}'>{url_status}</td>"
        
        # Determine row color based on all services status
        if all_services_successful and url_status == "Exitoso":
            row_color = 'green'
        elif any_service_yellow:
            row_color = 'yellow'
        else:
            row_color = 'red'
        
        report += f"<tr style='background-color: {row_color}'><td>{label}</td><td>{server_ip}</td>{''.join(filesystem_html_list)}{cpu_load_html}{mem_usage_html}{services_status_html}{url_status_html}</tr>"
    
    report += "</table></body></html>"
    return report

def send_email(report):
    msg = MIMEMultipart()
    msg['From'] = MAIL_TO
    msg['To'] = MAIL_TO
    if MAIL_CC:
        msg['Cc'] = MAIL_CC
    msg['Subject'] = MAIL_SUBJECT
    
    # Cuerpo del correo con la tabla
    body = f"{MAIL_BODY}<br><br>{report}"
    msg.attach(MIMEText(body, 'html'))
    
    # Adjuntar el archivo de log
    attachment = open(LOG_FILE, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(LOG_FILE)}")
    
    msg.attach(part)
    
    # Enviar el correo
    server = smtplib.SMTP('localhost')
    text = msg.as_string()
    recipients = [MAIL_TO] + (MAIL_CC.split(',') if MAIL_CC else [])
    server.sendmail(MAIL_TO, recipients, text)
    server.quit()

# Generate the report and send the email
report = generate_report()
send_email(report)


####################   vi validate_ip.py   ###############################

import subprocess

def check_url_with_certificate(url):
    try:
        result = subprocess.run(["curl", "-s", "--head", "--insecure", url], capture_output=True, text=True)
        if "HTTP/1." in result.stdout and " 200 " in result.stdout:
            status = "Exitoso"
        elif "SSL certificate problem" in result.stderr:
            status = "Amarillo"
            with open("/home/sisadmin/sta.log", 'a') as log_file:
                log_file.write(f"Certificate error detected for {url}. Response: {result.stderr}\n")
        else:
            status = "Fallido"
            with open("/home/sisadmin/sta.log", 'a') as log_file:
                log_file.write(f"URL check failed for {url}. Response: {result.stdout}\n")
        return status
    except Exception as e:
        with open("/home/sisadmin/sta.log", 'a') as log_file:
            log_file.write(f"Exception occurred while checking URL {url}: {str(e)}\n")
        return "Fallido"






# Configuración de los servidores y servicios a verificar
SERVERS = [
    {"ip": "192.168.202.101", "url": "https://192.168.202.101:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "Web Services"},
    {"ip": "192.168.202.102", "url": "https://192.168.202.102:4848/common/applications/fileChooser.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "REGISTRO - MOVIL"},
    {"ip": "192.168.202.103", "url": "", "services": ["nginx", "snmpd", "firewalld"], "require_pdf": False, "label": "Balanceador Servicios"},
    {"ip": "192.168.202.106", "url": "", "services": ["nginx", "firewalld"], "require_pdf": False, "label": "Balanceador -REGISTRO"},
    {"ip": "192.168.202.107", "url": "", "services": ["nginx", "firewalld"], "require_pdf": False, "label": "Balanceador -CAE"},
    {"ip": "192.168.202.108", "url": "http://192.168.202.108:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Weblogic 14"},
    {"ip": "192.168.202.109", "url": "http://192.168.202.109:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Weblogic 14"},
    {"ip": "192.168.202.110", "url": "http://192.168.202.110:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Produccion Weblogic 12"},
    {"ip": "192.168.202.118", "url": "http://192.168.202.118:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Produccion Weblogic 12"},
    {"ip": "192.168.202.115", "url": "https://192.168.202.115:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "PDFs de REGISTRO -Glassfish - Apps - Produccion"},
    {"ip": "192.168.202.116", "url": "https://192.168.202.116:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "PDFs de REGISTRO -Glassfish - Apps - Produccion"},
    {"ip": "192.168.202.141", "url": "https://192.168.202.141:4848/common/index.jsf", "services": ["glassfish"], "require_pdf": True, "label": "Produccion Glassfish RUE"},
    {"ip": "192.168.202.148", "url": "http://192.168.202.148:5050/svi/08/inicio", "services": ["glassfish"], "require_pdf": True, "label": "Produccion Glassfish Servicios"},
    {"ip": "192.168.202.149", "url": "http://192.168.202.149:5050/svi/08/inicio", "services": ["glassfish"], "require_pdf": True, "label": "Produccion Glassfish Servicios"}
]


















Pasos para Ejecutar el Script
Activa el entorno virtual (si no está ya activado):

source venv/bin/activate
Ejecuta el script main.py:

python main.py
Esto debería ejecutar el script y enviar el correo con la tabla de información de los servidores en el cuerpo del correo, mostrando solo el valor de cpu_load[2] en la columna de CPU, además del log adjunto.

Si necesitas más ayuda o ajustes adicionales, ¡házmelo saber!


Editar en Pages




El contenido generado por inteligencia artificial puede ser incorrecto
Copilot said:
Copilot
Puede encontrar la página aquí: 
La validación del servicio y
. Si desea agregarle otras respuestas, haga clic en "Editar en Pages".


Hoy
You said:

perfecto el script esta funcionando como necesito 
Copilot said:
Copilot
¡Genial! Me alegra saber que el script está funcionando como necesitas. Si en algún momento necesitas más ayuda, ajustes adicionales o tienes nuevas ideas para implementar, no dudes en decírmelo. ¡Estoy aquí para ayudarte! 🚀

¡Buena suerte con el monitoreo de tus servidores! 😊


Editar en Pages




El contenido generado por inteligencia artificial puede ser incorrecto
You said:

pregunta, si quiero agregar mas servidores como seria el proceso. 
Copilot said:
Copilot
Agregar más servidores al script es bastante sencillo. Solo necesitas seguir estos pasos:

1. Editar la Lista de Servidores
Abre el archivo main.py y localiza la sección donde se define la lista de servidores. Añade los nuevos servidores a la lista SERVERS con su dirección IP, URL y servicios que deseas monitorear.

Ejemplo
Supongamos que quieres agregar dos nuevos servidores con las siguientes configuraciones:

Servidor 1: IP 192.168.202.150, URL http://192.168.202.150:5050/svi/08/inicio, servicios nginx
Servidor 2: IP 192.168.202.151, URL http://192.168.202.151:5050/svi/08/inicio, servicios tomcat
Código Actualizado
# Configuración de los servidores y servicios a verificar
SERVERS = [
    {"ip": "192.168.202.148", "url": "http://192.168.202.148:5050/svi/08/inicio", "services": ["glassfish"]},
    {"ip": "192.168.202.149", "url": "http://192.168.202.149:5050/svi/08/inicio", "services": ["glassfish"]},
    {"ip": "192.168.202.150", "url": "http://192.168.202.150:5050/svi/08/inicio", "services": ["nginx"]},
    {"ip": "192.168.202.151", "url": "http://192.168.202.151:5050/svi/08/inicio", "services": ["tomcat"]}
]
2. Guardar los Cambios
Guarda los cambios en el archivo main.py.

3. Ejecutar el Script
Ejecuta el script como lo haces normalmente:

python main.py
Resumen
Edita la lista SERVERS en el archivo main.py para incluir los nuevos servidores.
Guarda los cambios en el archivo.
Ejecuta el script para verificar que los nuevos servidores se están monitoreando correctamente.


########################################################


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import subprocess
from validate_ip import check_url_with_certificate

# Configuración de los servidores y servicios a verificar
SERVERS = [
    {"ip": "192.168.202.101", "url": "https://192.168.202.101:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "Web Services"},
    {"ip": "192.168.202.102", "url": "https://192.168.202.102:4848/common/applications/fileChooser.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "REGISTRO - MOVIL"},
    {"ip": "192.168.202.103", "url": "", "services": ["nginx", "snmpd", "firewalld"], "require_pdf": False, "label": "Balanceador Servicios"},
    {"ip": "192.168.202.106", "url": "", "services": ["nginx", "firewalld"], "require_pdf": False, "label": "Balanceador -REGISTRO"},
    {"ip": "192.168.202.107", "url": "", "services": ["nginx", "firewalld"], "require_pdf": False, "label": "Balanceador -CAE"},
    {"ip": "192.168.202.108", "url": "http://192.168.202.108:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Weblogic 14"},
    {"ip": "192.168.202.109", "url": "http://192.168.202.109:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Weblogic 14"},
    {"ip": "192.168.202.110", "url": "http://192.168.202.110:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Produccion Weblogic 12"},
    {"ip": "192.168.202.118", "url": "http://192.168.202.118:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Produccion Weblogic 12"},
    {"ip": "192.168.202.115", "url": "https://192.168.202.115:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "PDFs de REGISTRO -Glassfish - Apps - Produccion"},
    {"ip": "192.168.202.116", "url": "https://192.168.202.116:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "PDFs de REGISTRO -Glassfish - Apps - Produccion"},
    {"ip": "192.168.202.141", "url": "https://192.168.202.141:4848/common/index.jsf", "services": ["glassfish"], "require_pdf": True, "label": "Produccion Glassfish RUE"},
    {"ip": "192.168.202.148", "url": "http://192.168.202.148:5050/svi/08/inicio", "services": ["glassfish"], "require_pdf": True, "label": "Produccion Glassfish Servicios"},
    {"ip": "192.168.202.149", "url": "http://192.168.202.149:5050/svi/08/inicio", "services": ["glassfish"], "require_pdf": True, "label": "Produccion Glassfish Servicios"}
]

LOG_FILE = "/home/sisadmin/sta.log"
SERVICE_STATUS_LOG = "/home/sisadmin/service_status.log"
MAIL_SUBJECT = "Estado de Salud de los servicios y URL"
MAIL_TO = "luis.orobio@sisa.com.co,mgonzale@ccc.org.co,ajojoa@ccc.org.co,jsantacr@ccc.org.co"
MAIL_CC = "wimunoz@ccc.org.co,fjaramillo@ccc.org.co,jcmendez@ccc.org.co,practop@ccc.org.co"
MAIL_BODY = "La validación del servicio y las URL se ha realizado. Adjunto se encuentran los logs con los detalles."

# Definir errores conocidos
KNOWN_ERRORS = {
    "nginx": ["nginx: [emerg]"],
    "firewalld": ["firewalld: [error]"],
    "snmpd": ["snmpd: [error]"]  # Asegúrate de incluir errores conocidos para snmpd si es necesario
}

# Vaciar los archivos de logs al inicio de cada ejecución
open(LOG_FILE, 'w').close()
open(SERVICE_STATUS_LOG, 'w').close()

def check_service(server_ip, service_name):
    try:
        if service_name == "nginx":
            result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "systemctl status nginx"], capture_output=True, text=True)
            if "active (running)" in result.stdout:
                status = "Exitoso"
            elif any(error in result.stdout for error in KNOWN_ERRORS["nginx"]):
                status = "Amarillo"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Known error detected for {service_name} on {server_ip}. Response: {result.stdout}\n")
            else:
                status = "Fallido"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Service check failed for {service_name} on {server_ip}. Response: {result.stdout}\n")
        elif service_name == "snmpd":
            result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "systemctl status snmpd"], capture_output=True, text=True)
            if "active (running)" in result.stdout:
                status = "Exitoso"
            elif any(error in result.stdout for error in KNOWN_ERRORS["snmpd"]):
                status = "Amarillo"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Known error detected for {service_name} on {server_ip}. Response: {result.stdout}\n")
            else:
                status = "Fallido"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Service check failed for {service_name} on {server_ip}. Response: {result.stdout}\n")
        elif service_name == "firewalld":
            result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "systemctl status firewalld"], capture_output=True, text=True)
            if "inactive (dead)" in result.stdout:
                status = "Exitoso"
            elif any(error in result.stdout for error in KNOWN_ERRORS["firewalld"]):
                status = "Amarillo"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Known error detected for {service_name} on {server_ip}. Response: {result.stdout}\n")
            else:
                status = "Fallido"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Service check failed for {service_name} on {server_ip}. Response: {result.stdout}\n")
        else:
            result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, f"ps -fea | grep -v grep | grep {service_name}"], capture_output=True, text=True)
            if result.returncode == 0:
                status = "Exitoso"
            else:
                status = "Fallido"
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f"Service check failed for {service_name} on {server_ip}. Response: {result.stdout}\n")
        return status
    except Exception as e:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Exception occurred while checking service {service_name} on {server_ip}: {str(e)}\n")
        return "Fallido"

def check_url(url):
    if not url:
        return "No URL"
    return check_url_with_certificate(url)

def check_cpu_load(server_ip):
    try:
        result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "uptime"], capture_output=True, text=True)
        load_average = result.stdout.split()[-3:]
        load_average = [float(load.strip(',').replace(',', '.')) for load in load_average]
        return load_average
    except Exception as e:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Exception occurred while checking CPU load on {server_ip}: {str(e)}\n")
        return [0.0, 0.0, 0.0]

def check_memory(server_ip):
    try:
        result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "free -m"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        mem_line = lines[1].split()
        total_mem = int(mem_line[1])
        used_mem = int(mem_line[2])
        mem_usage_percent = (used_mem / total_mem) * 100
        return mem_usage_percent
    except Exception as e:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Exception occurred while checking memory on {server_ip}: {str(e)}\n")
        return 0.0

def check_filesystem(server_ip, require_pdf):
    try:
        result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "df -h"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        filesystem_status = []
        for line in lines[1:]:
            parts = line.split()
            if len(parts) > 5 and parts[5] == '/pdf':
                filesystem_status.append({
                    'filesystem': parts[0],
                    'size': parts[1],
                    'used': parts[2],
                    'avail': parts[3],
                    'use%': parts[4],
                    'mounted_on': parts[5]
                })
        if not filesystem_status and not require_pdf:
            filesystem_status.append({
                'filesystem': 'N/A',
                'size': 'N/A',
                'used': 'N/A',
                'avail': 'N/A',
                'use%': 'N/A',
                'mounted_on': 'N/A'
            })
        return filesystem_status
    except Exception as e:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Exception occurred while checking filesystem on {server_ip}: {str(e)}\n")
        return [{
            'filesystem': 'N/A',
            'size': 'N/A',
            'used': 'N/A',
            'avail': 'N/A',
            'use%': 'N/A',
            'mounted_on': 'N/A'
        }]

def get_cpu_count(server_ip):
    try:
        result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "nproc"], capture_output=True, text=True)
        return int(result.stdout.strip())
    except Exception as e:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Exception occurred while getting CPU count on {server_ip}: {str(e)}\n")
        return 0

def generate_report():
    report = "<html><body><table border='1'><tr><th>ETIQUETA</th><th>SERVIDOR</th><th>FILESYSTEM</th><th>CPU</th><th>MEMORIA</th><th>SERVICIOS</th><th>URL</th></tr>"
    for server in SERVERS:
        label = server["label"]
        server_ip = server["ip"]
        url = server["url"]
        require_pdf = server.get("require_pdf", False)
        services_status = [check_service(server_ip, service) for service in server["services"]]
        url_status = check_url(url)
        
        # Check CPU load average
        cpu_load = check_cpu_load(server_ip)
        cpu_count = get_cpu_count(server_ip)
        cpu_load_html = f"<td style='background-color: {'red' if cpu_load[2] > cpu_count else 'green'}'>{cpu_load[2]}</td>"
        
        # Check memory usage
        mem_usage_percent = check_memory(server_ip)
        mem_usage_html = f"<td style='background-color: {'red' if mem_usage_percent > 90 else 'green'}'>{mem_usage_percent:.2f}%</td>"
        
        # Check filesystem usage for /pdf only
        filesystem_status_list = check_filesystem(server_ip, require_pdf)
        filesystem_html_list = []
        for fs in filesystem_status_list:
            if fs['filesystem'] == 'N/A':
                fs_html = f"<td style='background-color: yellow'>N/A</td>"
            elif fs['use%'] > '95%':
                fs_html = f"<td style='background-color: red'>{fs['filesystem']} {fs['use%']}</td>"
            else:
                fs_html = f"<td style='background-color: green'>{fs['filesystem']} {fs['use%']}</td>"
            filesystem_html_list.append(fs_html)
        
        # Check if all services are successful
        if not services_status:
            services_status_html = "<td style='background-color: yellow'>N/A</td>"
        else:
            all_services_successful = all(status == "Exitoso" for status in services_status)
            any_service_yellow = any(status == "Amarillo" for status in services_status)
            if all_services_successful:
                services_status_html = "<td style='background-color: green'>Exitoso</td>"
            elif any_service_yellow:
                services_status_html = "<td style='background-color: yellow'>Amarillo</td>"
            else:
                services_status_html = "<td style='background-color: red'>Fallido</td>"
        
        url_status_html = f"<td style='background-color: {'yellow' if url_status == 'No URL' else 'green' if url_status == 'Exitoso' else 'red'}'>{url_status}</td>"
        
        # Determine row color based on all services status
        row_color = 'green' if all_services_successful and url_status == "Exitoso" else 'yellow' if any_service_yellow else 'red'
        
        report += f"<tr><td>{label}</td><td>{server_ip}</td>{''.join(filesystem_html_list)}{cpu_load_html}{mem_usage_html}{services_status_html}{url_status_html}</tr>"
    
    report += "</table></body></html>"
    return report

def send_email(report):
    msg = MIMEMultipart()
    msg['From'] = MAIL_TO.split(',')[0]  # El primer correo en MAIL_TO será el remitente
    msg['To'] = MAIL_TO
    msg['Cc'] = MAIL_CC
    msg['Subject'] = MAIL_SUBJECT
    
    # Cuerpo del correo con la tabla
    body = f"{MAIL_BODY}<br><br>{report}"
    msg.attach(MIMEText(body, 'html'))
    
    # Adjuntar el archivo de log
    attachment = open(LOG_FILE, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(LOG_FILE)}")
    
    msg.attach(part)
    
    # Enviar el correo
    server = smtplib.SMTP('localhost')
    text = msg.as_string()
    recipients = MAIL_TO.split(',') + MAIL_CC.split(',')
    server.sendmail(MAIL_TO.split(',')[0], recipients, text)
    server.quit()

# Generate the report and send the email
report = generate_report()
send_email(report)