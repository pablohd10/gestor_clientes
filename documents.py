import os
import shutil
from tkinter import simpledialog, messagebox

class Documents:
    def __init__(self, db):
        self.db = db


    def agregar_documento(self, cliente_id, file_path, jurisdiccion_documento):
        cliente = self.db.get_client_by_id(cliente_id)
        if not cliente:
            messagebox.showerror("Error", "Cliente no encontrado")
            return
        
        cliente_id, nombre_cliente, apellido_cliente, ciudad_cliente, email_cliente, telefono_cliente, tipo_cliente, fecha_insercion = cliente

        # Solicitar tipo de documento
        tipo_documento = simpledialog.askstring("Tipo de Documento", "Ingrese el tipo de documento (ejemplo: Recurso, Apelacion, Amparo...):")
        if not tipo_documento:
            messagebox.showerror("Error", "Debe ingresar tipo de documento")
            return

        # Crear ruta de la carpeta del cliente en el escritorio
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        main_folder = os.path.join(desktop_path, "Clientes")
        tipo_folder = os.path.join(main_folder, tipo_cliente)
        ciudad_folder = os.path.join(tipo_folder, ciudad_cliente)
        cliente_folder = os.path.join(ciudad_folder, f"{nombre_cliente} {apellido_cliente}")
        jurisdiccion_folder = os.path.join(cliente_folder, jurisdiccion_documento)

        os.makedirs(jurisdiccion_folder, exist_ok=True)  # Crear las carpetas si no existen

        # Renombrar el archivo
        nuevo_nombre = f"{tipo_documento}-{ciudad_cliente}-{nombre_cliente}-{apellido_cliente}{os.path.splitext(file_path)[1]}"
        nueva_ruta = os.path.join(jurisdiccion_folder, nuevo_nombre)

        # Insertar el documento en la base de datos
        try:
            print("Insertando documento en la base de datos: ", nueva_ruta)
            self.db.add_document_db(nueva_ruta, cliente_id, nuevo_nombre, jurisdiccion_documento, tipo_documento)
            messagebox.showinfo("Documento Agregado", "Documento agregado exitosamente")
            # Copiar el archivo a la nueva ubicación
            try:
                shutil.copy(file_path, nueva_ruta)
            except Exception as e:
                messagebox.showerror("Error", "Fallo al copiar archivo")
                return
        except Exception as e:
            messagebox.showerror("Error", "Fallo al agregar documento. El documento " + nueva_ruta + " ya existe")

    def mostrar_documentos(self, tree):
        # Obtener el ID del cliente seleccionado en la tabla
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un cliente para asociar el documento")
            return

        cliente_id = tree.item(selected_item)["values"][0]
        cliente = self.db.get_client_by_id(cliente_id)
        if not cliente:
            messagebox.showerror("Error", "Cliente no encontrado")
            return
        
        cliente_id, nombre_cliente, apellido_cliente, ciudad_cliente, email_cliente, telefono_cliente, tipo_cliente, fecha_insercion = cliente

        # Consultar la ciudad del cliente para construir la ruta de la carpeta
        try:
            # Construir la ruta de la carpeta del cliente
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            main_folder = os.path.join(desktop_path, "Clientes")
            tipo_folder = os.path.join(main_folder, tipo_cliente)
            ciudad_folder = os.path.join(tipo_folder, ciudad_cliente)
            cliente_folder = os.path.join(ciudad_folder, f"{nombre_cliente} {apellido_cliente}")

            if not os.path.exists(cliente_folder):
                messagebox.showerror("Error", "La carpeta del cliente no existe.")
                return

            # Abrir la carpeta del cliente
            os.system(f'open "{cliente_folder}"')  # macOS
            # Alternativas para otros sistemas operativos:
            #os.startfile(cliente_folder)  # Windows
            # os.system(f'xdg-open "{cliente_folder}"')  # Linux

        except Exception as e:
            messagebox.showerror("Error", "Fallo al abrir la carpeta")
            return

        
