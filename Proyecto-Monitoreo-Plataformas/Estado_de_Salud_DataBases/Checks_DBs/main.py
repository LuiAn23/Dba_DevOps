# main.py
import time
from config import instancias, intervalo_monitoreo
from monitoreo import monitorear_instancia

def main():
    """
    Función principal para ejecutar el monitoreo de las instancias de Oracle.
    """
    print("Iniciando el monitoreo de instancias de Oracle...")
    while True:
        for instancia in instancias:
            monitorear_instancia(instancia)
        print(f"Esperando {intervalo_monitoreo} segundos para la siguiente verificación...")
        time.sleep(intervalo_monitoreo)

if __name__ == "__main__":
    main()
