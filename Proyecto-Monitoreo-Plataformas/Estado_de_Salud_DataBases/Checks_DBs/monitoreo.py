# monitoreo.py
from conexion_oracle import conectar_oracle, cerrar_conexion
import os
import cx_Oracle  # Importar cx_Oracle

def ejecutar_query_desde_archivo(cursor, archivo_sql):
    """
    Ejecuta un query SQL desde un archivo.
    """
    try:
        with open(archivo_sql, "r") as f:
            query = f.read()
        cursor.execute(query)
        return cursor.fetchall()  # Obtener todos los resultados
    except Exception as e:
        print(f"Error al ejecutar el query desde {archivo_sql}: {e}")
        return None

def monitorear_instancia(instancia):
    """
    Monitorea el estado de una instancia de Oracle y ejecuta queries desde archivos SQL.
    """
    connection = conectar_oracle(instancia)
    if connection:
        try:
            cursor = connection.cursor()
            directorio_sql = "Sql"  # Directorio donde están los archivos SQL
            for archivo_sql in os.listdir(directorio_sql):
                if archivo_sql.endswith(".sql"):
                    ruta_completa = os.path.join(directorio_sql, archivo_sql)
                    resultados = ejecutar_query_desde_archivo(cursor, ruta_completa)
                    if resultados:
                        print(f"Instancia {instancia['nombre']}: Resultados de {archivo_sql}:")
                        for fila in resultados:
                            print(fila)
                    else:
                        print(f"Instancia {instancia['nombre']}: No se obtuvieron resultados de {archivo_sql}")
        except cx_Oracle.Error as error:
            print(f"Error al monitorear {instancia['nombre']}: {error}")
        finally:
            cerrar_conexion(connection)
