# config.py
# Configuraciones de las instancias de Oracle

instancias = [
    {
        "nombre": "REGISTRO",
        "username": "system",
        "password": "txDHUT*5W5w2M",
        "dsn": "192.168.202.4:1521/REGISTRO", 
    },
    {
        "nombre": "DOCUNET",
        "username": "system",
        "password": "sOthOa**RgUerdBA4br1l",
        "dsn": "192.168.202.2:1521/DOCUNET",  
    },
    {
        "nombre": "ERP",
        "username": "system",
        "password": "sOthOa**RgUerdBA4br1l",
        "dsn": "192.168.202.3:1641/ERP",  
    },
]

intervalo_monitoreo = 10  # Intervalo de monitoreo en segundos

MAIL_CONFIG = {
    'subject_no_certificates': 'No se evidencia Certificados represados',
    'subject_warning': 'Warning se evidencian algunos Certificados represados',
    'subject_alert': 'Alerta se evidencian algunos Certificados represados',
    'subject_report': 'Reporte de Monitoreo de Bases de Datos',
    'to': 'luis.orobio@sisa.com.co',
    'cc': ''
}
