from validations import validate_email
from validations import validate_telefono
import os
import shutil 

class Clientes:
    def __init__(self, db):
        self.db = db
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Clientes")
    
    def agregar_cliente(self, nombre, apellido, ciudad, email, telefono, tipo):
        """ Agrega un cliente a la base de datos y crea la carpeta del cliente en la carpeta 'Clientes' del escritorio """
        # Validamos los datos del cliente
        error = self.validar_datos(nombre, apellido, ciudad, email, telefono, tipo)
        if error:
            return error

        # Normalizamos los datos
        nombre, apellido, ciudad, email, tipo = self.normalizar_datos(nombre, apellido, ciudad, email, tipo)

        # Creamos la carpeta del cliente
        cliente_path = self.crear_carpeta_cliente(nombre, apellido, ciudad, tipo)
        if not cliente_path:
            return "Error: No se pudo crear la carpeta del cliente."

        # Guardamos cliente en la base de datos
        return self.db.add_client_db(nombre, apellido, ciudad, email, telefono, tipo)

    def eliminar_cliente(self, nombre, apellido, ciudad, tipo):
        """ Elimina un cliente de la base de datos y elimina la carpeta del cliente en la carpeta 'Clientes' del escritorio """
        # Normalizamos los datos
        nombre, apellido, ciudad, tipo = map(str.capitalize, [nombre, apellido, ciudad, tipo])

        # Eliminamos la carpeta del cliente
        cliente_path = os.path.join(self.desktop_path, tipo, ciudad, f"{nombre} {apellido}")
        if not self.eliminar_carpeta(cliente_path):
            return "Error: No se pudo eliminar la carpeta del cliente."

        # Eliminamos al cliente de la base de datos
        client_id = self.db.get_client_id(nombre, apellido, ciudad, tipo)
        return self.db.delete_client_db(client_id)

    # Métodos auxiliares
    def validar_datos(self, nombre, apellido, ciudad, email, telefono, tipo):
        if not nombre or not apellido or not ciudad or not tipo:
            return "Error: Nombre, Apellido, Ciudad y Tipo son obligatorios"
        if email and not validate_email(email):
            return "Error: Email inválido. Formato no válido."
        if telefono and not validate_telefono(telefono):
            return "Error: Teléfono inválido. Debe contener entre 7 y 15 dígitos"
        return None

    def normalizar_datos(self, nombre, apellido, ciudad, email, tipo):
        nombre = nombre.capitalize()
        apellido = apellido.capitalize()
        ciudad = ciudad.capitalize()
        email = email.lower() if email else None
        tipo = tipo.capitalize()
        return nombre, apellido, ciudad, email, tipo

    def crear_carpeta_cliente(self, nombre, apellido, ciudad, tipo):
        """ Crea una carpeta en la carpeta 'Clientes' del escritorio """
        cliente_path = os.path.join(self.desktop_path, tipo, ciudad, f"{nombre} {apellido}")
        try:
            os.makedirs(cliente_path, exist_ok=True)
            return cliente_path
        except Exception as e:
            print(f"Error al crear carpeta: {e}")
            return None

    def eliminar_carpeta(self, path):
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                return True
            except Exception as e:
                print(f"Error al eliminar carpeta: {e}")
        return False
