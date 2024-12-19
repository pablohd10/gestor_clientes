
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
        if email and not "@" in email:
            return "Error: Email inválido. Debe contener @"
        
        # Validar que el teléfono tenga un formato correcto
        if telefono and not telefono.isdigit():
            return "Error: Teléfono inválido. Debe contener solo números"
        
        # Insertar el cliente en la base de datos
        return self.db.add_client_db(nombre, apellido, ciudad, email, telefono, tipo)
        
        