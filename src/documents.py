import os
import shutil

class Documents:
    def __init__(self, db):
        self.db = db

    def agregar_documento(self, nombre_cliente, apellido_cliente, ciudad_cliente, tipo_cliente, file_path, jurisdiccion_documento, procedimiento_documento):
        
        cliente_id = self.db.get_client_id(nombre_cliente, apellido_cliente, ciudad_cliente, tipo_cliente)

        # Crear ruta de la carpeta del cliente en el escritorio
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        main_folder = os.path.join(desktop_path, "Clientes")
        tipo_folder = os.path.join(main_folder, tipo_cliente)
        ciudad_folder = os.path.join(tipo_folder, ciudad_cliente)
        cliente_folder = os.path.join(ciudad_folder, f"{nombre_cliente} {apellido_cliente}")
        jurisdiccion_folder = os.path.join(cliente_folder, jurisdiccion_documento)


        os.makedirs(jurisdiccion_folder, exist_ok=True)  # Crear las carpetas si no existen

        # Renombrar el archivo
        nuevo_nombre = f"{procedimiento_documento}-{ciudad_cliente}-{nombre_cliente}-{apellido_cliente}{os.path.splitext(file_path)[1]}"
        nueva_ruta = os.path.join(jurisdiccion_folder, nuevo_nombre)

        # Copiar el archivo a la nueva ubicación
        try:
            shutil.copy(file_path, nueva_ruta)
        except Exception as e:
            return "Error: Fallo al agregar documento. " + str(e)
        
         # Insertar el cliente en la base de datos
        return self.db.add_document_db(nueva_ruta, cliente_id, nuevo_nombre, jurisdiccion_documento, procedimiento_documento)

    def mostrar_documentos(self, nombre_cliente, apellido_cliente, ciudad_cliente, tipo_cliente):

        # Consultar la ciudad del cliente para construir la ruta de la carpeta
        try:
            # Construir la ruta de la carpeta del cliente
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            main_folder = os.path.join(desktop_path, "Clientes")
            tipo_folder = os.path.join(main_folder, tipo_cliente)
            ciudad_folder = os.path.join(tipo_folder, ciudad_cliente)
            cliente_folder = os.path.join(ciudad_folder, f"{nombre_cliente} {apellido_cliente}")

            if not os.path.exists(cliente_folder):
                return "Error", "La carpeta del cliente no existe."
            
            # Abrir la carpeta del cliente
            os.system(f'open "{cliente_folder}"')  # macOS
            # Alternativas para otros sistemas operativos:
            #os.startfile(cliente_folder)  # Windows
            # os.system(f'xdg-open "{cliente_folder}"')  # Linux

        except Exception as e:
            return "Error", "Fallo al abrir la carpeta"

        
