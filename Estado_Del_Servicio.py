import cx_Oracle
import os
from datetime import datetime

# Configuración de conexión
config = {
    'host': 'coclocccprdb01',
    'port': 1521,
    'sid': 'REGISTRO',
    'username': 'SYS',
    'password': 'fvSXIaFGGs'
}

class DatabaseHealthCheck:
    def __init__(self, config):
        self.config = config
        self.connection = None

    # Conectar a la base de datos Oracle
    def connect(self):
        try:
            dsn_tns = cx_Oracle.makedsn(self.config['host'], self.config['port'], service_name=self.config['sid'])
            self.connection = cx_Oracle.connect(self.config['username'], self.config['password'], dsn_tns)
            print("Conexión exitosa a Oracle.")
        except cx_Oracle.DatabaseError as e:
            print(f"Error al conectar a la base de datos: {e}")
            raise

    # Desconectar de la base de datos Oracle
    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Desconectado de Oracle.")

    # Revisión de sesiones inactivas
    def check_inactive_sessions(self):
        cursor = self.connection.cursor()
        query = """
        SELECT username, sid, serial#, status, last_call_et
        FROM v$session
        WHERE status = 'INACTIVE'
        AND last_call_et > 300;  -- Sesiones inactivas por más de 5 minutos
        """
        cursor.execute(query)
        sessions = cursor.fetchall()
        print("Sesiones inactivas:")
        for row in sessions:
            print(f"Usuario: {row[0]}, SID: {row[1]}, Serial: {row[2]}, Estado: {row[3]}, Tiempo de inactividad (segundos): {row[4]}")
        cursor.close()

    # Revisión de logs de backups
    def check_backup_logs(self):
        cursor = self.connection.cursor()
        query = """
        SELECT BACKUP_TYPE, STATUS, COMPLETION_TIME
        FROM V$BACKUP
        WHERE COMPLETION_TIME > SYSDATE - 30  -- Últimos 30 días
        """
        cursor.execute(query)
        backups = cursor.fetchall()
        print("Logs de backups recientes:")
        for row in backups:
            print(f"Tipo de Backup: {row[0]}, Estado: {row[1]}, Fecha de finalización: {row[2]}")
        cursor.close()

    # Revisión de logs de la base de datos
    def check_db_logs(self, log_dir='/path/to/oracle/logs'):
        if not os.path.exists(log_dir):
            print(f"El directorio de logs no existe: {log_dir}")
            return

        print("Revisión de logs de la base de datos:")
        for log_file in os.listdir(log_dir):
            if log_file.endswith('.log'):
                log_path = os.path.join(log_dir, log_file)
                with open(log_path, 'r') as log:
                    logs = log.readlines()
                    print(f"Contenido del archivo de log {log_file}:")
                    for line in logs[-10:]:  # Muestra las últimas 10 líneas
                        print(line.strip())

    # Revisión de espacio en tablespaces
    def check_tablespace(self):
        cursor = self.connection.cursor()
        query = """
        SELECT tablespace_name, ROUND(SUM(bytes) / 1024 / 1024, 2) AS total_mb,
               ROUND(SUM(bytes) / 1024 / 1024 / 1024, 2) AS total_gb
        FROM dba_data_files
        GROUP BY tablespace_name
        """
        cursor.execute(query)
        tablespaces = cursor.fetchall()
        print("Espacio en tablespace:")
        for row in tablespaces:
            print(f"Tablespace: {row[0]}, Tamaño Total: {row[1]} MB ({row[2]} GB)")
        cursor.close()

    # Revisión de espacio en disco del servidor
    def check_disk_space(self):
        disk = os.popen("df -h").read()
        print("Espacio en disco del servidor:")
        print(disk)

    # Agregar nuevas tareas (funciones adicionales)
    def add_custom_check(self, query, description):
        cursor = self.connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Resultado de la revisión: {description}")
        for row in results:
            print(row)
        cursor.close()

    # Función que ejecuta todas las tareas de revisión
    def run_all_checks(self):
        self.check_inactive_sessions()
        self.check_backup_logs()
        self.check_db_logs()
        self.check_tablespace()
        self.check_disk_space()

# Función principal que ejecuta todo el proceso
def main():
    db_check = DatabaseHealthCheck(config)
    
    # Conectar a Oracle
    db_check.connect()

    try:
        # Ejecutar todas las tareas por defecto
        db_check.run_all_checks()

        # Si quieres agregar una revisión personalizada, puedes hacerlo de esta forma:
        # Ejemplo de consulta personalizada:
        custom_query = """
        SELECT username, count(*) FROM v$session GROUP BY username;
        """
        db_check.add_custom_check(custom_query, "Revisión de número de sesiones por usuario")
    
    finally:
        # Desconectar de Oracle
        db_check.disconnect()

if __name__ == "__main__":
    main()
