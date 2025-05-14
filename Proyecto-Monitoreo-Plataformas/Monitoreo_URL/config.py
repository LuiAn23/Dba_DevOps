SERVERS = [
    {"ip": "192.168.202.101", "url": "https://192.168.202.101:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "Web Services"},
    {"ip": "192.168.202.102", "url": "https://192.168.202.102:4848/common/applications/fileChooser.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "REGISTRO - MOVIL"},
    {"ip": "192.168.202.103", "url": "", "services": ["nginx", "snmpd", "firewalld"], "require_pdf": False, "label": "Balanceador Servicios"},
    {"ip": "192.168.202.106", "url": "", "services": ["nginx", "firewalld"], "require_pdf": False, "label": "Balanceador -REGISTRO"},
    {"ip": "192.168.202.107", "url": "", "services": ["nginx", "firewalld"], "require_pdf": False, "label": "Balanceador -CAE"},
    {"ip": "192.168.202.108", "url": "http://192.168.202.108:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Producción"},
    {"ip": "192.168.202.109", "url": "http://192.168.202.109:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Producción"},
    {"ip": "192.168.202.110", "url": "http://192.168.202.110:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Producción"},
    {"ip": "192.168.202.118", "url": "http://192.168.202.118:7001/console/login/LoginForm.jsp", "services": ["weblogic"], "require_pdf": True, "label": "Producción"},
    {"ip": "192.168.202.115", "url": "https://192.168.202.115:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "PDFs de REGISTRO -Glassfish - Apps - Producción"},
    {"ip": "192.168.202.116", "url": "https://192.168.202.116:4848/common/index.jsf", "services": ["glassfish", "nginx", "java", "firewalld"], "require_pdf": True, "label": "PDFs de REGISTRO -Glassfish - Apps - Producción"},
    {"ip": "192.168.202.141", "url": "https://192.168.202.141:4848/common/index.jsf", "services": ["glassfish"], "require_pdf": True, "label": "Produccion Glassfish RUE"},
    {"ip": "192.168.202.148", "url": "http://192.168.202.148:5050/svi/08/inicio", "services": ["glassfish"], "require_pdf": True, "label": "Producción"},
    {"ip": "192.168.202.149", "url": "http://192.168.202.149:5050/svi/08/inicio", "services": ["glassfish"], "require_pdf": True, "label": "Producción"}
]

LOG_FILE = "cron.log"

MAIL_SUBJECT = "Estado de Salud de los servicios de App Produccion"
MAIL_TO = "luis.orobio@sisa.com.co,mgonzale@ccc.org.co,ajojoa@ccc.org.co,jsantacr@ccc.org.co"
MAIL_CC = "wimunoz@ccc.org.co,fjaramillo@ccc.org.co,jcmendez@ccc.org.co,practop@ccc.org.co"
MAIL_BODY = "La validación del servicio y las URL se ha realizado. Adjunto se encuentran los logs con los detalles."
