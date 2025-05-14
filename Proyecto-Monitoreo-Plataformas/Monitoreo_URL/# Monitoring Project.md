# Monitoring Project

Este proyecto se encarga de monitorear varios servidores y servicios, generando un informe en formato HTML y enviándolo por correo electrónico.

## Estructura del Proyecto

- `main.py`: Archivo principal que ejecuta el monitoreo y genera el informe.
- `config.py`: Archivo de configuración que contiene la lista de servidores y otros parámetros de configuración.
- `utils.py`: Archivo que contiene funciones auxiliares para verificar servicios, URLs, carga de CPU, memoria, sistema de archivos y envío de correos electrónicos.

## Dependencias

- Python 3.x
- Librerías adicionales (si las hay)

## Configuración

Asegúrate de que el archivo `config.py` contenga la configuración correcta de los servidores y otros parámetros necesarios.

## Ejecución

Para ejecutar el proyecto, simplemente corre el archivo `main.py`:

```bash
python main.py
```

## Funciones Principales

### `check_service(server_ip, service)`

Verifica el estado de un servicio en un servidor dado.

### `check_url(url, label)`

Verifica el estado de una URL, considerando etiquetas específicas.

### `check_cpu_load(server_ip)`

Verifica la carga de CPU de un servidor.

### `check_memory(server_ip)`

Verifica el uso de memoria de un servidor.

### `check_filesystem(server_ip, require_pdf)`

Verifica el uso del sistema de archivos de un servidor.

### `send_email(report)`

Envía el informe generado por correo electrónico.

## Generación del Informe

El informe se genera en formato HTML y contiene la siguiente información para cada servidor:

- Etiqueta
- IP del servidor
- Uso del sistema de archivos
- Carga de CPU
- Uso de memoria
- Estado de los servicios
- Estado de la URL

## Contacto

Para más información, contacta al equipo de desarrollo.
