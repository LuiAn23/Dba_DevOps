# Herramienta de Copia de Archivos - GUI de Escritorio


## Descripción


Aplicación de escritorio con interfaz gráfica para copiar archivos desde ubicaciones de red predefinidas hacia directorios locales. Construida con Python Tkinter incluyendo seguimiento de progreso y manejo de errores.


## Características

GUI Intuitiva: Interfaz moderna con selección por radio buttons
Gestión de Rutas de Red: Ubicaciones predefinidas + rutas personalizadas
Visualización de Progreso: Barra de progreso en tiempo real
Copia Optimizada: Transferencia por bloques (chunks de 1MB)
Manejo de Errores: Validación y mensajes de estado amigables

##	Stack Técnico

Python 3.8+
Tkinter + ttk (GUI)
Librerías estándar (shutil, os)

##	Uso

python file_copy_tool.py

Seleccionar ruta de red (predefinida o personalizada)
Ingresar nombre del archivo
Hacer clic en "Descargar Archivo"
Monitorear el progreso

##	Beneficios Clave

Elimina la navegación manual por redes
Retroalimentación visual del progreso
Manejo robusto de errores
Amigable para personal no técnico


📌 Código Limpio (sin rutas sensibles)
python# Rutas de ejemplo - reemplazar con ubicaciones reales
self.options = [
    r"\\file-server\documents\forms\folder1",
    r"\\file-server\documents\forms\folder2", 
    r"\\file-server\documents\support\main",
    r"\\file-server\documents\receipts",
    r"\\file-server\documents\mutations\forms"
]  






