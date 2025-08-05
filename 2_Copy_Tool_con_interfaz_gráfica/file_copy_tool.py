import tkinter as tk
from tkinter import ttk
import shutil
import os

class FileCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Copy")
        self.root.geometry("550x580")
        self.root.configure(bg="#f0f0f0")  # Color de fondo general

        # Centrar la ventana en la pantalla
        self.center_window(500, 580)

        # Crear un estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Tema más moderno

        self.style.configure("TLabel", font=("Arial", 11, "bold"), foreground="#4CAF50", background="#f0f0f0")
        self.style.configure("TButton", font=("Arial", 10, "bold"), background="#4CAF50", foreground="white")
        self.style.configure("TEntry", font=("Arial", 10), padding=5)
        self.style.configure("TRadiobutton", font=("Arial", 10), foreground="black", background="#f0f0f0", padding=5)  # Estilo con relleno

        # Configurar el estilo de la barra de progreso
        self.style.configure("TProgressbar", troughcolor="#f0f0f0", background="#4CAF50")

        # Etiqueta para seleccionar la ruta de búsqueda
        self.label = ttk.Label(root, text="Seleccione la ruta del archivo:", style="TLabel")
        self.label.pack(pady=10)

        # Frame para alinear los checkboxes y el textbox de "Otro"
        self.options_frame = tk.Frame(root, bg="#f0f0f0")
        self.options_frame.pack(pady=6)

        # Opciones de checkbox
       # Rutas de ejemplo - reemplazar con ubicaciones reales
        self.options = [
            r"\\file-server\documents\forms\folder1",
            r"\\file-server\documents\forms\folder2", 
            r"\\file-server\documents\support\main",
            r"\\file-server\documents\receipts",
            r"\\file-server\documents\mutations\forms"
        ]

        self.selected_option = tk.StringVar(value="")  # Solo una opción a la vez

        for option in self.options:
            check_button = ttk.Radiobutton(self.options_frame, text=option, variable=self.selected_option, value=option, style="TRadiobutton", command=self.select_options)
            check_button.pack(anchor="w", pady=3, padx=20)

        # Checkbox "Otro"
        self.other_check = ttk.Radiobutton(self.options_frame, text="Otra", variable=self.selected_option, value="Otra", style="TRadiobutton", command=self.select_options)
        self.other_check.pack(anchor="w", pady=3, padx=20)

        # Etiqueta para el campo de entrada de "Otra"
        self.other_label = ttk.Label(self.options_frame, text="Colocar Ruta Nueva:", style="TLabel")
        self.other_label.pack(pady=5, padx=20)
        self.other_label.pack_forget()  # Ocultar por defecto

        # Entry oculto para ingresar otra ruta
        self.other_entry = ttk.Entry(self.options_frame, width=60, style="TEntry")
        self.other_entry.pack(pady=5, padx=20)
        self.other_entry.pack_forget()  # Ocultar por defecto

        # Evento para monitorizar cambios en el campo "Otro"
        self.other_entry.bind("<KeyRelease>", self.update_custom_path)

        # Campo de entrada para el nombre del archivo
        self.fileLabel = ttk.Label(root, text="Ingrese el nombre del archivo (PDF):", style="TLabel")
        self.fileLabel.pack(pady=10)

        self.fileNameField = ttk.Entry(root, width=60, style="TEntry")
        self.fileNameField.pack(pady=10)

        # Frame para alinear los botones en una línea
        self.button_frame = tk.Frame(root, bg="#f0f0f0")
        self.button_frame.pack(pady=10)

        # Botón para copiar el archivo
        self.copyButton = ttk.Button(self.button_frame, text="Descargar Archivo", command=self.copy_file, style="TButton")
        self.copyButton.grid(row=0, column=0, padx=10)

        # Botón para limpiar la selección
        self.resetButton = ttk.Button(self.button_frame, text="Limpiar", command=self.reset_app, style="TButton")
        self.resetButton.grid(row=0, column=1, padx=10)

        # Etiqueta de estado para mostrar mensajes de éxito o error
        self.statusLabel = ttk.Label(root, text="", wraplength=500, style="TLabel")
        self.statusLabel.pack(pady=10)

        # Barra de progreso
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", style="TProgressbar")
        self.progress.pack(pady=10)

    def center_window(self, width, height):
        """Centra la ventana en la pantalla."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def select_options(self):
        """Obtiene la ruta seleccionada automáticamente al elegir una opción o escribir en 'Otro'."""
        selected = self.selected_option.get()
        if selected == "Otra":
            self.other_label.pack(pady=5, padx=20)
            self.other_entry.pack(pady=5, padx=20)
        else:
            self.other_label.pack_forget()
            self.other_entry.pack_forget()
            self.other_entry.delete(0, tk.END)
        self.update_selected_options()

    def update_custom_path(self, event):
        """Actualizar opciones seleccionadas cuando se cambia el campo de texto 'Otro'."""
        self.update_selected_options()

    def update_selected_options(self):
        """Actualiza la lista de opciones seleccionadas."""
        self.selected_options = []
        selected = self.selected_option.get()
        if selected == "Otra":
            custom_path = self.other_entry.get().strip()
            if custom_path:
                self.selected_options.append(custom_path)
        elif selected:
            self.selected_options.append(selected)
        print(f"Opciones seleccionadas: {self.selected_options}")

    def copy_file(self):
        """Intenta copiar el archivo desde la ruta seleccionada"""
        fileName = self.fileNameField.get().strip()
        destination = r"C:\Users\Public\Downloads"

        if not self.selected_options:
            self.statusLabel.config(text="Por favor, seleccione una ruta.", foreground="red")
            return

        for path in self.selected_options:
            source = os.path.join(path, fileName)
            if os.path.exists(source):
                try:
                    self.copy_with_progress(source, os.path.join(destination, fileName))
                    self.statusLabel.config(text="Archivo Descargado exitosamente.", foreground="green")
                    return
                except Exception as e:
                    self.statusLabel.config(text=f"Error al Descargar el archivo: {e}", foreground="red")
                    return
        self.statusLabel.config(text="Archivo no encontrado en la ruta seleccionada.", foreground="red")

    def copy_with_progress(self, source, destination):
        """Copia el archivo en bloques y actualiza la barra de progreso."""
        total_size = os.path.getsize(source)
        block_size = 1024 * 1024  # 1MB
        copied_size = 0

        self.progress["maximum"] = total_size

        with open(source, "rb") as src, open(destination, "wb") as dst:
            while True:
                block = src.read(block_size)
                if not block:
                    break
                dst.write(block)
                copied_size += len(block)
                self.progress["value"] = copied_size
                self.root.update_idletasks()

    def reset_app(self):
        """Reinicia los campos y selecciones"""
        self.fileNameField.delete(0, tk.END)
        self.statusLabel.config(text="")
        self.selected_option.set("")
        self.other_label.pack_forget()
        self.other_entry.pack_forget()
        self.other_entry.delete(0, tk.END)
        self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCopyApp(root)
    root.mainloop()