[sisadmin@coclocccprdl16 Monitoring]$ cat main.py 
import sys
import os

# Añadir el directorio actual al PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SERVERS, LOG_FILE
from utils import check_service, check_url, check_cpu_load, check_memory, check_filesystem, get_cpu_count, send_email
from validate_ip import check_url_with_certificate

# Vaciar los archivos de logs al inicio de cada ejecución
open(LOG_FILE, 'w').close()

def check_url(url, label):
    if not url:
        return "No URL"
    if label in ["REGISTRO - MOVIL", "Produccion Glassfish RUE", "Balanceador Servicios", "Balanceador -REGISTRO", "Balanceador -CAE"]:
        return "Amarillo"
    return check_url_with_certificate(url)

def generate_report():
    report = "<html><body><table border='1'><tr><th>ETIQUETA</th><th>SERVIDOR</th><th>FILESYSTEM</th><th>CPU</th><th>MEMORIA</th><th>SERVICIOS</th><th>URL</th></tr>"
    for server in SERVERS:
        label = server["label"]
        server_ip = server["ip"]
        url = server["url"]
        require_pdf = server.get("require_pdf", False)
        services_status = [check_service(server_ip, service) for service in server["services"]]
        url_status = check_url(url, label)
        
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
                fs_html = f"<td style='background-color: red'>{fs['filesystem']} {fs['u
                
                se%']}</td>"
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
                services_status_html = "<td style='background-color: yellow'>Warning</td>"
            else:
                services_status_html = "<td style='background-color: yellow'>Warning</td>"
        
        url_status_html = f"<td style='background-color: {'yellow' if url_status in ['Amarillo', 'No URL'] else 'green' if url_status == 'Exitoso' else 'red'}'>{'No URL' if url_status == 'No URL' else 'Warning' if url_status == 'Amarillo' else url_status}</td>"
        
        # Determine row color based on all services status
        row_color = 'green' if all_services_successful and url_status == "Exitoso" else 'yellow' if any_service_yellow else 'yellow'
        
        report += f"<tr><td>{label}</td><td>{server_ip}</td>{''.join(filesystem_html_list)}{cpu_load_html}{mem_usage_html}{services_status_html}{url_status_html}</tr>"
    
    report += "</table></body></html>"
    return report

# Generar el informe y enviar el correo electrónico
report = generate_report()
send_email(report)

