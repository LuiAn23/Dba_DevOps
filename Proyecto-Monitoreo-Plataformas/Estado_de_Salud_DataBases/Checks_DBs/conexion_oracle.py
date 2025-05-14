# conexion_oracle.py
import cx_Oracle
from config import instancias  # Importar la lista de instancias desde config.py

def conectar_oracle(instancia):
    """
    Establece una conexión a la base de datos Oracle.
    """
    try:
        connection = cx_Oracle.connect(
            instancia["username"], instancia["password"], instancia["dsn"]
        )
        print(f"Conexión a {instancia['nombre']} establecida con éxito.")
        return connection
    except cx_Oracle.Error as error:
        print(f"Error al conectar a {instancia['nombre']}: {error}")
        return None

def cerrar_conexion(connection):
    """
    Cierra la conexión a la base de datos Oracle.
    """
    if connection:
        try:
            connection.close()
            print("Conexión a Oracle cerrada.")
        except cx_Oracle.Error as error:
            print("Error al cerrar la conexión:", error)
