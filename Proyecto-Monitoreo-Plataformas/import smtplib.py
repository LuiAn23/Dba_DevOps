import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import subprocess

# Configuración de los servidores y servicios a verificar
SERVERS = [
    {"ip": "192.168.202.108", "url": "http://192.168.202.108:7001/console/login/LoginForm.jsp", "services": ["weblogic"]},
    {"ip": "192.168.202.109", "url": "http://192.168.202.109:7001/console/login/LoginForm.jsp", "services": ["weblogic"]},
    {"ip": "192.168.202.115", "url": "https://192.168.202.115:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"]},
    {"ip": "192.168.202.149", "url": "http://192.168.202.149:5050/svi/08/inicio", "services": ["glassfish"]},
    {"ip": "192.168.202.149", "url": "http://192.168.202.149:5050/svi/08/inicio", "services": ["glassfish"]}
]
LOG_FILE = "/home/sisadmin/sta.log"
SERVICE_STATUS_LOG = "/home/sisadmin/service_status.log"
MAIL_SUBJECT = "Estado de Salud de los servicios y URL"
MAIL_TO = "luis.orobio@sisa.com.co"
MAIL_CC = "mgonzale@ccc.org.co"
MAIL_BODY = "La validación del servicio y las URL se ha realizado. Adjunto se encuentran los logs con los detalles."

# Vaciar los archivos de logs al inicio de cada ejecución
open(LOG_FILE, 'w').close()
open(SERVICE_STATUS_LOG, 'w').close()

def check_service(server_ip, service_name):
    if service_name == "nginx":
        result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "systemctl status nginx"], capture_output=True, text=True)
        if "active (running)" in result.stdout:
            status = "Exitoso"
        else:
            status = "Fallido"
            with open(LOG_FILE, 'a') as log_file:
                log_file.write(f"Service check failed for {service_name} on {server_ip}. Response: {result.stdout}\n")
    elif service_name == "firewalld":
        result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "systemctl status firewalld"], capture_output=True, text=True)
        if "inactive (dead)" in result.stdout:
            status = "Exitoso"
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

def check_url(url):
    result = subprocess.run(["curl", "-s", "--head", url], capture_output=True, text=True)
    if "HTTP/1." in result.stdout and " 200 " in result.stdout:
        status = "Exitoso"
    else:
        status = "Fallido"
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"URL check failed for {url}. Response: {result.stdout}\n")
    return status

def check_cpu_load(server_ip):
    result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "uptime"], capture_output=True, text=True)
    load_average = result.stdout.split()[-3:]
    load_average = [float(load.strip(',').replace(',', '.')) for load in load_average]
    return load_average

def check_memory(server_ip):
    result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "free -m"], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    mem_line = lines[1].split()
    total_mem = int(mem_line[1])
    used_mem = int(mem_line[2])
    mem_usage_percent = (used_mem / total_mem) * 100
    return mem_usage_percent

def check_filesystem(server_ip):
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
    return filesystem_status

def get_cpu_count(server_ip):
    result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", server_ip, "nproc"], capture_output=True, text=True)
    return int(result.stdout.strip())

def generate_report():
    report = "<html><body><table border='1'><tr><th>SERVIDOR</th><th>FILESYSTEM</th><th>CPU</th><th>MEMORIA</th><th>SERVICIOS</th><th>URL</th></tr>"
    for server in SERVERS:
        server_ip = server["ip"]
        url = server["url"]
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
        filesystem_status_list = check_filesystem(server_ip)
        filesystem_html_list = []
        for fs in filesystem_status_list:
            if fs['use%'] > '95%':
                fs_html = f"<td style='background-color: red'>{fs['filesystem']} {fs['use%']}</td>"
            else:
                fs_html = f"<td style='background-color: green'>{fs['filesystem']} {fs['use%']}</td>"
            filesystem_html_list.append(fs_html)
        
        # Check if all services are successful
        all_services_successful = all(status == "Exitoso" for status in services_status)
        services_status_html = f"<td style='background-color: {'green' if all_services_successful else 'red'}'>{'Exitoso' if all_services_successful else 'Fallido'}</td>"
        url_status_html = f"<td style='background-color: {'green' if url_status == 'Exitoso' else 'red'}'>{url_status}</td>"
        
        # Determine row color based on all services status
        row_color = 'green' if all_services_successful and url_status == "Exitoso" else 'red'
        
        report += f"<tr style='background-color: {row_color}'><td>{server_ip}</td>{''.join(filesystem_html_list)}{cpu_load_html}{mem_usage_html}{services_status_html}{url_status_html}</tr>"
    
    report += "</table></body></html>"
    return report

def send_email(report):
    msg = MIMEMultipart()
    msg['From'] = MAIL_TO
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
    server.sendmail(MAIL_TO, [MAIL_TO] + MAIL_CC.split(','), text)
    server.quit()

# Generate the report and send the email
report = generate_report()
send_email(report)