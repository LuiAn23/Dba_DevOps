import cx_Oracle
import smtplib
import json
import os
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from configparser import ConfigParser
from prettytable import PrettyTable

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("oracle_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("OracleMonitor")

class ServerStatus:
    SUCCESS = "EXITOSO"
    WARNING = "WARNING"
    ALERT = "ALERTADO"

class OracleMonitor:
    def __init__(self, config_file="config.json"):
        """
        Inicializa el monitor de Oracle con la configuración desde un archivo
        """
        self.config_file = config_file
        self.load_config()
        self.init_email_config()
        self.check_queries = self.load_check_queries()

    def load_config(self):
        """
        Carga la configuración desde el archivo JSON
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as file:
                    self.config = json.load(file)
                logger.info(f"Configuración cargada desde {self.config_file}")
            else:
                # Configuración inicial basada en los datos proporcionados
                self.config = {
                    "source_server": {
                        "host": "192.168.202.116",
                        "port": 1521,
                        "user": "system",
                        "password": "ZSbooyioUkE1tlFT3NY2",
                        "service_name": "ORCL"
                    },
                    "destination_servers": [
                        {
                            "host": "192.168.202.2",
                            "port": 1522,
                            "user": "system",
                            "password": "ZSbooyioUkE1tlFT3NY2",
                            "service_name": "ORCL"
                        },
                        {
                            "host": "192.168.202.3",
                            "port": 1523,
                            "user": "system",
                            "password": "ZSbooyioUkE1tlFT3NY2",
                            "service_name": "ORCL"
                        },
                        {
                            "host": "192.168.202.4",
                            "port": 1524,
                            "user": "system",
                            "password": "ZSbooyioUkE1tlFT3NY2",
                            "service_name": "ORCL"
                        }
                    ],
                    "email_config": {
                        "smtp_server": "smtp.yourcompany.com",
                        "smtp_port": 587,
                        "sender_email": "oracle.monitor@yourcompany.com",
                        "sender_password": "your_password",
                        "recipients": ["admin@yourcompany.com", "dba@yourcompany.com"]
                    },
                    "monitor_interval": 300  # en segundos
                }
                self.save_config()
                logger.info("Configuración inicial creada")
        except Exception as e:
            logger.error(f"Error al cargar la configuración: {str(e)}")
            raise

    def save_config(self):
        """
        Guarda la configuración en el archivo JSON
        """
        try:
            with open(self.config_file, 'w') as file:
                json.dump(self.config, file, indent=2)
            logger.info(f"Configuración guardada en {self.config_file}")
        except Exception as e:
            logger.error(f"Error al guardar la configuración: {str(e)}")

    def init_email_config(self):
        """
        Asegura que exista la configuración de correo electrónico
        """
        if 'email_config' not in self.config:
            self.config['email_config'] = {
                "smtp_server": "smtp.yourcompany.com",
                "smtp_port": 587,
                "sender_email": "oracle.monitor@yourcompany.com",
                "sender_password": "your_password",
                "recipients": ["admin@yourcompany.com"]
            }
            self.save_config()

    def load_check_queries(self):
        """
        Carga las consultas para verificar el estado de las bases de datos
        """
        # Archivo de definición de consultas
        queries_file = "check_queries.json"
        default_queries = {
            "tablespace_usage": {
                "query": """
                    SELECT 
                        tablespace_name, 
                        ROUND(used_percent, 2) as used_percent
                    FROM 
                        (SELECT tablespace_name, 
                         100 * (1 - (bytes_free / bytes_total)) as used_percent
                        FROM 
                         (SELECT a.tablespace_name, 
                          SUM(a.bytes) as bytes_total, 
                          SUM(NVL(b.bytes, 0)) as bytes_free
                         FROM dba_data_files a, 
                              dba_free_space b
                         WHERE a.tablespace_name = b.tablespace_name (+)
                         GROUP BY a.tablespace_name))
                    WHERE used_percent > 75
                    ORDER BY used_percent DESC
                """,
                "warning_threshold": 85,
                "alert_threshold": 95,
                "description": "Uso de Tablespace"
            },
            "locked_sessions": {
                "query": """
                    SELECT 
                        s1.username || ' (' || s1.sid || ')' as locking_user,
                        s2.username || ' (' || s2.sid || ')' as waiting_user,
                        l.ctime/60 as lock_time_minutes
                    FROM 
                        gv$lock l, gv$session s1, gv$session s2
                    WHERE 
                        l.block = 1 AND
                        s1.sid = l.sid AND
                        s2.sid = l.id2
                """,
                "warning_threshold": 1,
                "alert_threshold": 3,
                "description": "Sesiones Bloqueadas"
            },
            "database_status": {
                "query": """
                    SELECT 
                        instance_name, 
                        status, 
                        database_status
                    FROM 
                        v$instance
                """,
                "status_check": "status = 'OPEN' AND database_status = 'ACTIVE'",
                "description": "Estado de la Base de Datos"
            },
            "invalid_objects": {
                "query": """
                    SELECT 
                        owner, 
                        object_type, 
                        COUNT(*) as count
                    FROM 
                        dba_objects
                    WHERE 
                        status = 'INVALID'
                    GROUP BY 
                        owner, object_type
                    ORDER BY 
                        count DESC
                """,
                "warning_threshold": 10,
                "alert_threshold": 50,
                "description": "Objetos Inválidos"
            },
            "archivelog_status": {
                "query": """
                    SELECT 
                        ROUND((A.SPACE_LIMIT - A.SPACE_USED)/1024/1024) as free_mb,
                        ROUND(A.SPACE_USED/1024/1024) as used_mb,
                        ROUND(A.SPACE_LIMIT/1024/1024) as limit_mb,
                        ROUND(A.SPACE_USED/A.SPACE_LIMIT * 100, 2) as used_pct
                    FROM 
                        V$RECOVERY_FILE_DEST A
                """,
                "warning_threshold": 80,
                "alert_threshold": 90,
                "description": "Uso de Archivelog Area"
            }
        }

        try:
            if os.path.exists(queries_file):
                with open(queries_file, 'r') as file:
                    return json.load(file)
            else:
                # Crear archivo de consultas con valores por defecto
                with open(queries_file, 'w') as file:
                    json.dump(default_queries, file, indent=2)
                logger.info(f"Archivo de consultas creado: {queries_file}")
                return default_queries
        except Exception as e:
            logger.error(f"Error al manejar archivo de consultas: {str(e)}")
            return default_queries

    def add_server(self, server_type, server_info):
        """
        Agrega un nuevo servidor a la configuración
        
        Args:
            server_type (str): "source" o "destination"
            server_info (dict): Información del servidor a agregar
        """
        if server_type == "source":
            self.config["source_server"] = server_info
        elif server_type == "destination":
            self.config["destination_servers"].append(server_info)
        self.save_config()
        logger.info(f"Servidor {server_info['host']} agregado como {server_type}")

    def remove_server(self, server_type, host):
        """
        Elimina un servidor de la configuración
        
        Args:
            server_type (str): "source" o "destination"
            host (str): Host del servidor a eliminar
        """
        if server_type == "source" and self.config["source_server"]["host"] == host:
            logger.error("No se puede eliminar el servidor fuente principal")
            return False
        
        if server_type == "destination":
            self.config["destination_servers"] = [
                server for server in self.config["destination_servers"] 
                if server["host"] != host
            ]
            self.save_config()
            logger.info(f"Servidor {host} eliminado de {server_type}")
            return True
        return False

    def get_connection_string(self, server):
        """
        Genera la cadena de conexión para cx_Oracle
        
        Args:
            server (dict): Configuración del servidor
        
        Returns:
            str: Cadena de conexión
        """
        service_name = server.get("service_name", "ORCL")
        return f"{server['user']}/{server['password']}@{server['host']}:{server['port']}/{service_name}"

    def connect_to_database(self, server):
        """
        Establece conexión con la base de datos
        
        Args:
            server (dict): Configuración del servidor
        
        Returns:
            cx_Oracle.Connection: Conexión a la base de datos o None si falla
        """
        try:
            connection_string = self.get_connection_string(server)
            connection = cx_Oracle.connect(connection_string)
            return connection
        except Exception as e:
            logger.error(f"Error al conectar a {server['host']}: {str(e)}")
            return None

    def execute_query(self, connection, query):
        """
        Ejecuta una consulta en la base de datos
        
        Args:
            connection (cx_Oracle.Connection): Conexión a la base de datos
            query (str): Consulta SQL a ejecutar
        
        Returns:
            list: Lista de resultados o None si falla
        """
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Error al ejecutar consulta: {str(e)}")
            return None

    def check_server_health(self, server):
        """
        Verifica el estado de salud de un servidor
        
        Args:
            server (dict): Configuración del servidor
        
        Returns:
            dict: Resultados de las verificaciones con su estado
        """
        results = {
            "server": f"{server['host']}:{server['port']}",
            "status": ServerStatus.SUCCESS,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "checks": []
        }
        
        connection = self.connect_to_database(server)
        if not connection:
            results["status"] = ServerStatus.ALERT
            results["checks"].append({
                "name": "Conexión",
                "status": ServerStatus.ALERT,
                "message": "No se pudo establecer conexión con el servidor"
            })
            return results
        
        # Ejecutar cada consulta de verificación
        for check_name, check_info in self.check_queries.items():
            try:
                query_results = self.execute_query(connection, check_info["query"])
                
                check_result = {
                    "name": check_info["description"],
                    "status": ServerStatus.SUCCESS,
                    "data": query_results
                }
                
                # Analizar resultados según el tipo de verificación
                if query_results:
                    if "status_check" in check_info:
                        # Verificación por condición de estado
                        status_ok = True
                        for row in query_results:
                            exec_context = {key: value for key, value in row.items()}
                            if not eval(check_info["status_check"], {"__builtins__": {}}, exec_context):
                                status_ok = False
                                break
                        
                        if not status_ok:
                            check_result["status"] = ServerStatus.ALERT
                            check_result["message"] = f"Estado incorrecto en {check_info['description']}"
                            results["status"] = ServerStatus.ALERT
                    
                    elif "warning_threshold" in check_info and "alert_threshold" in check_info:
                        # Verificación por umbrales
                        max_value = 0
                        for row in query_results:
                            # Buscar un valor numérico en el resultado para comparar
                            for key, value in row.items():
                                if isinstance(value, (int, float)) and value > max_value:
                                    max_value = value
                        
                        if max_value >= check_info["alert_threshold"]:
                            check_result["status"] = ServerStatus.ALERT
                            check_result["message"] = f"{check_info['description']} - Valor {max_value} excede umbral de alerta ({check_info['alert_threshold']})"
                            results["status"] = ServerStatus.ALERT
                        elif max_value >= check_info["warning_threshold"]:
                            check_result["status"] = ServerStatus.WARNING
                            check_result["message"] = f"{check_info['description']} - Valor {max_value} excede umbral de advertencia ({check_info['warning_threshold']})"
                            if results["status"] != ServerStatus.ALERT:
                                results["status"] = ServerStatus.WARNING
                    
                    elif len(query_results) > 0:
                        # Si solo importa si hay resultados o no
                        check_result["status"] = ServerStatus.WARNING
                        check_result["message"] = f"Se encontraron {len(query_results)} registros en {check_info['description']}"
                        if results["status"] == ServerStatus.SUCCESS:
                            results["status"] = ServerStatus.WARNING
                
                results["checks"].append(check_result)
                
            except Exception as e:
                logger.error(f"Error en verificación {check_name}: {str(e)}")
                check_result = {
                    "name": check_info["description"],
                    "status": ServerStatus.ALERT,
                    "message": f"Error al ejecutar verificación: {str(e)}",
                    "data": []
                }
                results["checks"].append(check_result)
                results["status"] = ServerStatus.ALERT
        
        connection.close()
        return results

    def send_email_alert(self, server_results):
        """
        Envía una alerta por correo electrónico con los resultados del monitoreo
        
        Args:
            server_results (list): Lista de resultados de los servidores
        """
        try:
            email_config = self.config.get("email_config", {})
            
            if not email_config or not email_config.get("recipients"):
                logger.warning("Configuración de correo no definida o sin destinatarios")
                return
            
            # Preparar el mensaje
            msg = MIMEMultipart()
            
            # Determinar el estado general
            overall_status = ServerStatus.SUCCESS
            for result in server_results:
                if result["status"] == ServerStatus.ALERT:
                    overall_status = ServerStatus.ALERT
                    break
                elif result["status"] == ServerStatus.WARNING and overall_status != ServerStatus.ALERT:
                    overall_status = ServerStatus.WARNING
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Establecer el asunto según el estado general
            status_emoji = "✅" if overall_status == ServerStatus.SUCCESS else "⚠️" if overall_status == ServerStatus.WARNING else "🚨"
            msg['Subject'] = f"{status_emoji} [Oracle Monitor] Estado de Servidores: {overall_status} - {timestamp}"
            msg['From'] = email_config.get("sender_email", "oracle.monitor@yourcompany.com")
            msg['To'] = ", ".join(email_config.get("recipients", []))
            
            # Contenido HTML del correo
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .server {{ margin-bottom: 20px; padding: 10px; border-radius: 5px; }}
                    .success {{ background-color: #d4edda; }}
                    .warning {{ background-color: #fff3cd; }}
                    .alert {{ background-color: #f8d7da; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h2>Reporte de Estado de Servidores Oracle</h2>
                <p>Fecha: {timestamp}</p>
            """
            
            # Agregar cada servidor al contenido
            for result in server_results:
                status_class = "success" if result["status"] == ServerStatus.SUCCESS else "warning" if result["status"] == ServerStatus.WARNING else "alert"
                
                html_content += f"""
                <div class="server {status_class}">
                    <h3>Servidor: {result["server"]} - Estado: {result["status"]}</h3>
                    <table>
                        <tr>
                            <th>Verificación</th>
                            <th>Estado</th>
                            <th>Mensaje</th>
                        </tr>
                """
                
                for check in result["checks"]:
                    check_class = "success" if check["status"] == ServerStatus.SUCCESS else "warning" if check["status"] == ServerStatus.WARNING else "alert"
                    message = check.get("message", "OK" if check["status"] == ServerStatus.SUCCESS else "")
                    
                    html_content += f"""
                        <tr class="{check_class}">
                            <td>{check["name"]}</td>
                            <td>{check["status"]}</td>
                            <td>{message}</td>
                        </tr>
                    """
                    
                    # Si hay datos y no está en estado SUCCESS, mostrarlos
                    if check.get("data") and check["status"] != ServerStatus.SUCCESS:
                        html_content += f"""
                        <tr>
                            <td colspan="3">
                                <table>
                                    <tr>
                        """
                        
                        # Encabezados de columnas
                        if check["data"]:
                            for col in check["data"][0].keys():
                                html_content += f"<th>{col}</th>"
                            
                            html_content += "</tr>"
                            
                            # Filas de datos (limitando a 10 para no hacer el correo muy grande)
                            for row in check["data"][:10]:
                                html_content += "<tr>"
                                for col, val in row.items():
                                    html_content += f"<td>{val}</td>"
                                html_content += "</tr>"
                            
                            if len(check["data"]) > 10:
                                html_content += f"""
                                <tr>
                                    <td colspan="{len(check['data'][0])}" style="text-align:center;">
                                        <i>Mostrando 10 de {len(check["data"])} registros...</i>
                                    </td>
                                </tr>
                                """
                        
                        html_content += """
                                </table>
                            </td>
                        </tr>
                        """
                
                html_content += """
                    </table>
                </div>
                """
            
            html_content += """
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Enviar el correo
            with smtplib.SMTP(email_config.get("smtp_server", "localhost"), email_config.get("smtp_port", 25)) as server:
                if email_config.get("smtp_use_tls", True):
                    server.starttls()
                
                if email_config.get("sender_password"):
                    server.login(email_config.get("sender_email"), email_config.get("sender_password"))
                
                server.send_message(msg)
            
            logger.info(f"Correo de alerta enviado a {', '.join(email_config.get('recipients', []))}")
            
        except Exception as e:
            logger.error(f"Error al enviar correo: {str(e)}")

    def run_monitoring_cycle(self):
        """
        Ejecuta un ciclo completo de monitoreo en todos los servidores
        """
        logger.info("Iniciando ciclo de monitoreo")
        all_results = []
        
        # Verificar servidor fuente
        source_results = self.check_server_health(self.config["source_server"])
        all_results.append(source_results)
        logger.info(f"Servidor fuente {self.config['source_server']['host']} verificado - Estado: {source_results['status']}")
        
        # Verificar servidores destino
        for server in self.config["destination_servers"]:
            result = self.check_server_health(server)
            all_results.append(result)
            logger.info(f"Servidor destino {server['host']} verificado - Estado: {result['status']}")
        
        # Enviar alertas por correo si hay algún problema
        has_issues = any(result["status"] != ServerStatus.SUCCESS for result in all_results)
        always_send = self.config.get("always_send_email", False)
        
        if has_issues or always_send:
            self.send_email_alert(all_results)
        
        return all_results

    def run_monitor(self):
        """
        Ejecuta el monitor en un bucle continuo
        """
        interval = self.config.get("monitor_interval", 300)  # Por defecto, cada 5 minutos
        
        logger.info(f"Iniciando monitor con intervalo de {interval} segundos")
        
        try:
            while True:
                self.run_monitoring_cycle()
                logger.info(f"Ciclo completado, esperando {interval} segundos")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Monitor detenido por el usuario")
        except Exception as e:
            logger.error(f"Error en ciclo de monitoreo: {str(e)}")

    def add_check_query(self, name, query, description, warning_threshold=None, alert_threshold=None, status_check=None):
        """
        Agrega una nueva consulta de verificación
        
        Args:
            name (str): Nombre de la verificación
            query (str): Consulta SQL
            description (str): Descripción de la verificación
            warning_threshold (float, optional): Umbral de advertencia
            alert_threshold (float, optional): Umbral de alerta
            status_check (str, optional): Condición de verificación de estado
        """
        new_check = {
            "query": query,
            "description": description
        }
        
        if warning_threshold is not None and alert_threshold is not None:
            new_check["warning_threshold"] = warning_threshold
            new_check["alert_threshold"] = alert_threshold
        elif status_check:
            new_check["status_check"] = status_check
        
        self.check_queries[name] = new_check
        
        # Guardar las consultas actualizadas
        with open("check_queries.json", 'w') as file:
            json.dump(self.check_queries, file, indent=2)
        
        logger.info(f"Nueva consulta de verificación agregada: {name}")

def main():
    """
    Función principal para ejecutar el monitor
    """
    print("="*50)
    print("Sistema de Monitoreo de Oracle")
    print("="*50)
    
    monitor = OracleMonitor()
    
    if len(os.sys.argv) > 1:
        # Modo de línea de comandos
        command = os.sys.argv[1]
        
        if command == "run":
            monitor.run_monitor()
        elif command == "check":
            results = monitor.run_monitoring_cycle()
            
            # Mostrar resultados en consola
            for result in results:
                print(f"\nServidor: {result['server']} - Estado: {result['status']}")
                for check in result["checks"]:
                    print(f"  - {check['name']}: {check['status']}")
                    if check.get("message"):
                        print(f"    {check['message']}")
                    
                    if check.get("data") and check["status"] != ServerStatus.SUCCESS:
                        if check["data"]:
                            table = PrettyTable(list(check["data"][0].keys()))
                            for row in check["data"][:10]:
                                table.add_row(list(row.values()))
                            print(table)
                            if len(check["data"]) > 10:
                                print(f"    (Mostrando 10 de {len(check['data'])} registros)")
        
        elif command == "add-server":
            if len(os.sys.argv) < 4:
                print("Uso: python oracle_monitor.py add-server [source|destination] [host:port:user:password:service]")
                return
            
            server_type = os.sys.argv[2]
            server_info = os.sys.argv[3].split(":")
            
            if len(server_info) < 5:
                print("Formato incorrecto. Use: host:port:user:password:service")
                return
            
            new_server = {
                "host": server_info[0],
                "port": int(server_info[1]),
                "user": server_info[2],
                "password": server_info[3],
                "service_name": server_info[4] if len(server_info) > 4 else "ORCL"
            }
            
            monitor.add_server(server_type, new_server)
            print(f"Servidor agregado: {new_server['host']}:{new_server['port']}")
        
        elif command == "add-query":
            # Ejemplo: python oracle_monitor.py add-query nombre_consulta "SELECT..." "Descripción" warning alert
            if len(os.sys.argv) < 5:
                print("Uso: python oracle_monitor.py add-query [nombre] [query] [descripción] [warning] [alert]")
                return
            
            name = os.sys.argv[2]
            query = os.sys.argv[3]
            description = os.sys.argv[4]
            
            if len(os.sys.argv) > 6:
                # Con umbrales
                warning = float(os.sys.argv[5])
                alert = float(os.sys.argv[6])
                monitor.add_check_query(name, query, description, warning, alert)
            elif len(os.sys.argv) > 5:
                # Con verificación de estado
                status_check = os.sys.argv[5]
                monitor.add_check_query(name, query, description, status_check=status_check)
            else:
                # Sin umbrales ni verificación, solo si hay resultados
                monitor.add_check_query(name, query, description)
            
            print(f"Consulta agregada: {name}")
        
        else:
            print("Comando no reconocido. Opciones válidas: run, check, add-server, add-query")
    else:
        # Modo interactivo
        print("\nModo interactivo. Seleccione una opción:")
        print("1. Ejecutar monitoreo (continuo)")
        print("2. Verificar servidores (una vez)")
        print("3. Agregar servidor")
        print("4. Agregar consulta de verificación")
        print("5. Salir")
        
        option = input("Opción: ")
        
        if option == "1":
            monitor.run_monitor()
        elif option == "2":
            monitor.run_monitoring_cycle()
        elif option == "3":
            server_type = input("Tipo de servidor (source/destination): ")
            host = input("Host: ")
            port = int(input("Puerto: "))
            user = input("Usuario: ")
            password = input("Contraseña: ")
            service = input("Nombre del servicio (o Enter para ORCL): ") or "ORCL"
            
            new_server = {
                "host": host,
                "port": port,
                "user": user,
                "password": password,
                "service_name": service
            }
            
            monitor.add_server(server_type, new_server)
            print(f"Servidor agregado: {host}:{port}")
        elif option == "4":
            name = input("Nombre de la consulta: ")
            query = input("Consulta SQL: ")
            description = input("Descripción: ")
            
            threshold_type = input("Tipo de verificación (threshold/status/count): ")
            
            if threshold_type == "threshold":
                warning = float(input("Umbral de advertencia: "))
                alert = float(input("Umbral de alerta: "))
                monitor.add_check_query(name, query, description, warning, alert)
            elif threshold_type == "status":
                status_check = input("Condición de verificación (ej: status = 'OPEN'): ")
                monitor.ad