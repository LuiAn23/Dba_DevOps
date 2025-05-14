import os

DB_CONFIG = {
    'user': os.getenv("ORACLE_USER", "system"),
    'password': os.getenv("ORACLE_PASSWORD", "ZSbooyioUkE1tlFT3NY2"),
    'dsn': f"{os.getenv('ORACLE_HOST', '192.168.202.4')}:{os.getenv('ORACLE_PORT', '1521')}/{os.getenv('ORACLE_SERVICE_NAME', 'REGISTRO')}",
    'encoding': 'UTF-8'
}

MAIL_CONFIG = {
    'subject_no_certificates': 'No se evidencia Certificados represados',
    'subject_warning': 'Warning se evidencian algunos Certificados represados',
    'subject_alert': 'Alerta se evidencian algunos Certificados represados',
    'to': 'luis.orobio@sisa.com.co',
    'cc': 'fjaramillo@ccc.org.co, practop@ccc.org.co',
    'body': 'Se adjunta el reporte de certificados represados.'
}
