from src.validations import validate_email
from src.validations import validate_telefono
import os
import shutil 

class Clientes:
    def __init__(self, db):
        self.db = db
    
    def agregar_cliente(self, nombre, apellido, ciudad, email, telefono, tipo):
        # Validar que los campos no estén vacíos
        if not nombre or not apellido or not ciudad or not tipo:
            return "Error: Nombre, Apellido, Ciudad y Tipo son obligatorios"
            
        # Tranformar los datos a minúsculas menos la primera letra del nombre, apellido y ciudad
        nombre = nombre.capitalize() 
        apellido = apellido.capitalize()
        ciudad = ciudad.capitalize()
        email = email.lower() if email else email
        tipo = tipo.capitalize()

        # Validar que el email tenga un formato correcto
        if email and not validate_email(email):
            return "Error: Email inválido. Formato no válido."
        
        # Validar que el teléfono tenga un formato correcto
        if telefono and not validate_telefono(telefono):
            return "Error: Teléfono inválido. Debe contener entre 7 y 15 dígitos"
        
        # Insertar el cliente en la base de datos
        return self.db.add_client_db(nombre, apellido, ciudad, email, telefono, tipo)
    
    def eliminar_cliente(self, id, nombre, apellido, ciudad, tipo):
        # Eliminar cliente del sistema de archivos
        ruta_base = os.path.join(os.path.expanduser("~"), "Desktop", "Clientes")
        cliente_folder = os.path.join(ruta_base, tipo.capitalize(), ciudad.capitalize(), f"{nombre.capitalize()} {apellido.capitalize()}")

        # Verificar si la carpeta del cliente existe
        if os.path.exists(cliente_folder):
            try:
                # Eliminar la carpeta y su contenido
                shutil.rmtree(cliente_folder)
                print(f"Carpeta del cliente {nombre} {apellido} eliminada correctamente.")
            except Exception as e:
                return f"Error al eliminar la carpeta del cliente: {e}"

        # Eliminar cliente de la base de datos
        return self.db.delete_client_db(id)
        
        