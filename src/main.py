import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
import os
import shutil 
import re
import sqlite3
import os

class Database:
    def __init__(self):
        # Crear directorio Clientes en el escritorio del usuario
        user_home = os.path.expanduser("~")
        db_dir = os.path.join(user_home, "Desktop", "Clientes")
        if not os.path.exists(db_dir):
            os.makedirs(db_dir) # Crea el directorio si no existe
        
        # Conexión a la base de datos
        self.conn = sqlite3.connect(os.path.join(db_dir, "clientes.db"))
        self.cursor = self.conn.cursor()

    def inicializar_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Clientes (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL CHECK (LENGTH(Nombre) <= 50),
                Apellido TEXT NOT NULL CHECK (LENGTH(Apellido) <= 50),
                Ciudad TEXT NOT NULL CHECK (LENGTH(Ciudad) <= 50),
                Email TEXT CHECK (LENGTH(Email) <= 50),
                Telefono TEXT CHECK (LENGTH(Telefono) <= 15),
                Tipo TEXT NOT NULL CHECK (Tipo IN ('Turno', 'Privado')),
                FechaCreacion DATE DEFAULT CURRENT_DATE,
                UNIQUE (Nombre, Apellido, Ciudad, Tipo)
            )""")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Documentos (
                RutaArchivo TEXT PRIMARY KEY,
                ClienteID INTEGER NOT NULL,
                NombreDocumento TEXT NOT NULL,
                Jurisdiccion TEXT NOT NULL,
                TipoDocumento TEXT NOT NULL,
                FechaCreacion DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (ClienteID) REFERENCES Clientes(ID) ON DELETE CASCADE
            )""")
        self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Guardias(
                    Fecha DATE PRIMARY KEY,
                    Ciudad TEXT NOT NULL CHECK (LENGTH(Ciudad) <= 50),
                    ClienteID INTEGER NOT NULL,
                    TipoGuardia TEXT NOT NULL,
                    FOREIGN KEY (ClienteID) REFERENCES Clientes(ID) ON DELETE CASCADE
                    )""")
                        
        self.conn.commit()
    
    def fetch_all_clients_db(self):
        self.cursor.execute("SELECT Nombre, Apellido, Ciudad, Email, Telefono, Tipo, FechaCreacion FROM Clientes")
        return self.cursor.fetchall()

    def add_client_db(self, nombre, apellido, ciudad, email, telefono, tipo):
        try:
            self.cursor.execute("INSERT INTO Clientes (Nombre, Apellido, Ciudad, Email, Telefono, Tipo) VALUES (?, ?, ?, ?, ?, ?)",
                                (nombre, apellido, ciudad, email, telefono, tipo))
            self.conn.commit()
            return "Cliente " + nombre + " " + apellido+" agregado"
        except sqlite3.IntegrityError:
            return "Error: Cliente " + nombre + " " + apellido + " ya existe"
        
    def get_client_by_id(self, client_id):
        try:
            self.cursor.execute("SELECT Nombre, Apellido, Ciudad, Email, Telefono, Tipo, FechaCreacion FROM Clientes WHERE ID = ?", (client_id,))
            return self.cursor.fetchone()
        except sqlite3.Error:
            return None

    def get_client_id(self, nombre, apellido, ciudad, tipo):
        try:
            self.cursor.execute("SELECT ID FROM Clientes WHERE Nombre = ? AND Apellido = ? AND Ciudad = ? AND Tipo = ?", (nombre, apellido, ciudad, tipo))
            return self.cursor.fetchone()[0]
        except sqlite3.Error:
            return None
        
    def delete_client_db(self, client_id):
        try:
            self.cursor.execute("DELETE FROM Clientes WHERE ID = ?", (client_id,))
            self.conn.commit()
            return "Cliente eliminado"
        except sqlite3.Error:
            return "Error: Cliente no encontrado"

    def build_search_query(self, palabras):
        query = "SELECT Nombre, Apellido, Ciudad, Email, Telefono, Tipo, FechaCreacion FROM Clientes WHERE"
        params = []
        if len(palabras) == 1:
            query += " (Nombre LIKE ? OR Apellido LIKE ? OR Ciudad LIKE ?)"
            params = ['%' + palabras[0] + '%'] * 3
        elif len(palabras) == 2:
            query += " (Nombre LIKE ? AND Apellido LIKE ?) OR (Nombre LIKE ? AND Ciudad LIKE ?) OR (Apellido LIKE ? AND Ciudad LIKE ?)"
            params = ['%' + palabras[0] + '%', '%' + palabras[1] + '%'] * 3
        else:
            query += " (Nombre LIKE ? AND Apellido LIKE ? AND Ciudad LIKE ?)"
            params = ['%' + palabras[0] + '%', '%' + palabras[1] + '%', '%' + palabras[2] + '%']
        return query, params

    def search_clients_db(self, query, params):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def connect(self):
        user_home = os.path.expanduser("~")
        db_dir = os.path.join(user_home, "Desktop", "Clientes")
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        self.conn = sqlite3.connect(os.path.join(db_dir, "clientes.db"))
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

import re
import os
import shutil

def validate_email(email):
    """
    Valida una dirección de email.
    Retorna True si es válida, False si no.
    """
    if not isinstance(email, str) or len(email) > 320:
        return False
    
    # Validación carácter por carácter antes de usar el regex
    for char in email:
        if char.isspace():
            return False
    
    # Expresión regular para validar emails
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    match = re.match(pattern, email)
    if match:
        return True
    return False

def validate_telefono(telefono):
    """
    Valida un número de teléfono.
    Retorna True si es válido, False si no.
    """
    if not isinstance(telefono, str) or len(telefono) > 15:
        return False

    # Validar que no contenga caracteres que no sean números
    for char in telefono:
        if not char.isdigit():
            return False

    # Expresión regular para validar teléfonos
    pattern = r"^\d{7,15}$"
    match = re.match(pattern, telefono)
    if match:
        return True
    return False


class Clientes:
    def __init__(self, db):
        self.db = db
        self.clientes_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.base_folder = os.path.join(self.clientes_path, "Clientes")
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)

    def agregar_cliente(self, nombre, apellido, ciudad, email, telefono, tipo):
        # Validar datos del cliente paso a paso
        if not nombre:
            return "Error: El nombre es obligatorio."
        if not apellido:
            return "Error: El apellido es obligatorio."
        if not ciudad:
            return "Error: La ciudad es obligatoria."
        if not tipo:
            return "Error: El tipo es obligatorio."

        if email:
            if not validate_email(email):
                return "Error: Email inválido. Formato no válido."
        if telefono:
            if not validate_telefono(telefono):
                return "Error: Teléfono inválido. Debe contener entre 7 y 15 dígitos"

        # Normalizar datos por separado
        nombre = self.capitalizar_palabra(nombre)
        apellido = self.capitalizar_palabra(apellido)
        ciudad = self.capitalizar_palabra(ciudad)
        email = email.lower() if email else email
        tipo = self.capitalizar_palabra(tipo)

        # Crear carpeta paso a paso
        cliente_path = self.crear_carpeta_cliente(nombre, apellido, ciudad, tipo)
        if not cliente_path:
            return "Error: No se pudo crear la carpeta del cliente."

        # Guardar cliente en la base de datos
        resultado = self.db.add_client_db(nombre, apellido, ciudad, email, telefono, tipo)
        if not resultado:
            return "Error: No se pudo agregar el cliente a la base de datos."
        return "Cliente agregado correctamente."

    def eliminar_cliente(self, nombre, apellido, ciudad, tipo):
        # Normalizar datos paso a paso
        nombre = self.capitalizar_palabra(nombre)
        apellido = self.capitalizar_palabra(apellido)
        ciudad = self.capitalizar_palabra(ciudad)
        tipo = self.capitalizar_palabra(tipo)

        # Construir ruta de cliente
        cliente_path = os.path.join(self.base_folder, tipo, ciudad, f"{nombre} {apellido}")
        if not self.eliminar_carpeta(cliente_path):
            return "Error: No se pudo eliminar la carpeta del cliente."

        # Obtener ID y eliminar cliente de la base de datos
        client_id = self.db.get_client_id(nombre, apellido, ciudad, tipo)
        if not client_id:
            return "Error: No se encontró el cliente en la base de datos."
        resultado = self.db.delete_client_db(client_id)
        if not resultado:
            return "Error: No se pudo eliminar el cliente de la base de datos."
        return "Cliente eliminado correctamente."

    def capitalizar_palabra(self, palabra):
        """Capitaliza la primera letra de una palabra."""
        if not palabra or not isinstance(palabra, str):
            return ""
        return palabra[0].upper() + palabra[1:].lower()

    def crear_carpeta_cliente(self, nombre, apellido, ciudad, tipo):
        tipo_path = os.path.join(self.base_folder, tipo)
        ciudad_path = os.path.join(tipo_path, ciudad)
        cliente_path = os.path.join(ciudad_path, f"{nombre} {apellido}")
        try:
            if not os.path.exists(tipo_path):
                os.makedirs(tipo_path)
            if not os.path.exists(ciudad_path):
                os.makedirs(ciudad_path)
            if not os.path.exists(cliente_path):
                os.makedirs(cliente_path)
            return cliente_path
        except Exception as e:
            print(f"Error al crear carpeta: {e}")
            return None

    def eliminar_carpeta(self, path):
        if os.path.exists(path):
            try:
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    else:
                        shutil.rmtree(file_path)
                shutil.rmtree(path)
                return True
            except Exception as e:
                print(f"Error al eliminar carpeta: {e}")
        return False

        
        
def mostrar_estado(texto):
    # Verifica si el texto contiene la palabra "Error"
    if texto == None:
        return
    elif "Error" in texto:
        label_status.config(text=texto, foreground="red")  # Mostrar texto en rojo si contiene "Error"
    else:
        label_status.config(text=texto, foreground="blue")  # Mostrar texto en azul si no contiene "Error"


def agregar_cliente():
    # Obtener los datos de los campos de entrada
    nombre = entry_nombre.get()
    apellido = entry_apellido.get()
    ciudad = combobox_ciudad.get()
    email = entry_email.get()
    telefono = entry_telefono.get()
    tipo = combobox_tipo.get()

    clientes = Clientes(database)
    mostrar_estado(clientes.agregar_cliente(nombre, apellido, ciudad, email, telefono, tipo))
    cargar_todos_los_clientes()  # Actualizar la tabla con los nuevos datos

def eliminar_cliente():
    # Obtener los IDs de los clientes seleccionados en la tabla
    selected_items = tree.selection()

    if not selected_items:
        mostrar_estado("Error: Seleccione uno o más clientes para eliminar")
        return

    clientes_a_eliminar = []
    for item in selected_items:
        cliente = tree.item(item)["values"]
        clientes_a_eliminar.append({
            "nombre": cliente[0],
            "apellido": cliente[1],
            "ciudad": cliente[2],
            "tipo": cliente[5],
        })

    # Confirmar eliminación
    nombres_clientes = ", ".join([f"{c['nombre']} {c['apellido']}" for c in clientes_a_eliminar])
    respuesta = messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar los siguientes clientes?\n{nombres_clientes}")
    
    if respuesta:
        clientes = Clientes(database)
        for cliente in clientes_a_eliminar:
            estado = clientes.eliminar_cliente(cliente["nombre"], cliente["apellido"], cliente["ciudad"], cliente["tipo"])
            mostrar_estado(estado)
        
        buscar_dinamico()  # Actualizar la tabla después de eliminar los clientes

def obtener_cliente_seleccionado():
    # Obtener el ID del cliente seleccionado en la tabla
    selected_item = tree.selection()

    nombre = tree.item(selected_item)["values"][0]
    apellido = tree.item(selected_item)["values"][1]
    ciudad = tree.item(selected_item)["values"][2]
    tipo = tree.item(selected_item)["values"][5]
    return nombre, apellido, ciudad, tipo

def buscar_dinamico(event=None):
    # Obtener lo que el usuario escribe en el campo de búsqueda y eliminar espacios extras
    texto_busqueda = entry_buscar.get().strip()

    # Si no hay texto en el campo, no hacer nada
    if not texto_busqueda:
        cargar_todos_los_clientes()  # Cargar todos los clientes en la tabla
        return

    # Separar el texto de búsqueda en palabras (dividiendo por espacios)
    palabras = texto_busqueda.split()

    # Construir la consulta SQL y los parámetros
    query, params = database.build_search_query(palabras)
    # Realizar la búsqueda en la base de datos
    resultados = database.search_clients_db(query, params)

    # Limpiar los resultados previos y agregar los nuevos
    tree.delete(*tree.get_children())  # Limpiar resultados previos
    for row in resultados:
        tree.insert("", "end", values=row)

# Función para cargar todos los clientes en la tabla
def cargar_todos_los_clientes():
    # Borra los datos actuales de la tabla
    for item in tree.get_children():
        tree.delete(item)
    
    # Obtener todos los clientes desde la base de datos
    clientes = database.fetch_all_clients_db()  # Función para obtener todos los clientes desde la base de datos
    
    # Insertar los clientes en la tabla
    for cliente in clientes:
        tree.insert("", "end", values=cliente)


def ordenar_columnas(col):
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    data.sort(reverse=False)
    for index, (val, k) in enumerate(data):
        tree.move(k, "", index)


# Inicializar la base de datos
database = Database()
print("Inicializando base de datos...")
database.inicializar_db()

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Gestión de Clientes")

# Configurar estilos
style = ttk.Style(ventana)
style.theme_use("clam")

ventana.config(bg="#f0f0f0")  # Un gris claro

style.map("TButton",
          background=[("active", "#45A049")],  # Color de fondo al presionar
          foreground=[("active", "white")])    # Color del texto al presionar

# Estilo de los campos de entrada
style.configure("TEntry",
                font=("Helvetica", 12),
                padding=5,
                relief="flat",          # Bordes suaves
                foreground="black",     # Color del texto
                background="#f0f0f0",   # Fondo suave
                fieldbackground="#f0f0f0",  # Fondo suave cuando el campo está vacío
                insertbackground="black", # Color del cursor
                width=20)               # Ancho fijo de las entradas

# Estilo de las cabeceras de la tabla
style.configure("Treeview.Heading",
                background="#e0e0e0",   # Fondo gris claro para las cabeceras
                foreground="black",     # Color del texto de las cabeceras
                font=("Helvetica", 12, "bold"))  # Fuente para las cabeceras

# Estilo de las filas de la tabla
style.configure("Treeview",
                background="#ffffff",   # Fondo blanco para las filas
                foreground="black",     # Color del texto
                fieldbackground="#f9f9f9")  # Fondo gris claro para las filas

# Configurar estilos para ttk.Label
style.configure("TLabel",
                background="#f0f0f0")   # Fondo gris claro para combinar con la ventana

# Campo de búsqueda dinámico
ttk.Label(ventana, text="Buscar Cliente  ---->").grid(row=0, column=0, columnspan=2)
entry_buscar = ttk.Entry(ventana)
entry_buscar.grid(row=0, column=1)
entry_buscar.bind("<KeyRelease>", buscar_dinamico)  # Se ejecuta cada vez que se presiona una tecla

# Sección: Agregar Cliente
ttk.Label(ventana, text="Introduce los datos para agregar un cliente").grid(row=2, column=0, columnspan=2)
ttk.Label(ventana, text="Nombre:").grid(row=3, column=0)
entry_nombre = ttk.Entry(ventana)
entry_nombre.grid(row=3, column=1)
ttk.Label(ventana, text="Apellido:").grid(row=4, column=0)
entry_apellido = ttk.Entry(ventana)
entry_apellido.grid(row=4, column=1)
# Desplegable para seleccionar Ciudad
ttk.Label(ventana, text="Ciudad:").grid(row=5, column=0)
combobox_ciudad = ttk.Combobox(ventana, values=["Madrid", "Guadalajara", "Alcala"], state="readonly")
combobox_ciudad.grid(row=5, column=1)
ttk.Label(ventana, text="Email:").grid(row=6, column=0)
entry_email = ttk.Entry(ventana)
entry_email.grid(row=6, column=1)
ttk.Label(ventana, text="Teléfono:").grid(row=7, column=0)
entry_telefono = ttk.Entry(ventana)
entry_telefono.grid(row=7, column=1)
# Desplegable para seleccionar Tipo
ttk.Label(ventana, text="Tipo:").grid(row=8, column=0)
combobox_tipo = ttk.Combobox(ventana, values=["Privado", "Turno"], state="readonly")
combobox_tipo.grid(row=8, column=1)

# Botón para agregar cliente
ttk.Button(ventana, text="Agregar Cliente", command=agregar_cliente).grid(row=9, column=0, columnspan=2)
# Botón para eliminar cliente
ttk.Button(ventana, text="Eliminar Cliente", command=eliminar_cliente).grid(row=10, column=0, columnspan=2)
# Mensaje de estado
label_status = ttk.Label(ventana, text="", font=("Helvetica", 12, "bold")) 
label_status.grid(row=11, column=0, columnspan=2)

# Tabla para resultados
tree = ttk.Treeview(ventana, columns=("Nombre", "Apellido", "Ciudad", "Email", "Telefono", "Tipo", "FechaCreacion"), show="headings", height=20)
tree.grid(row=15, column=0, columnspan=2)
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.heading(col, text=col, command=lambda _col=col: ordenar_columnas(_col))

cargar_todos_los_clientes()  # Cargar todos los clientes en la tabla

try:
    ventana.mainloop()  # Iniciar la interfaz
except KeyboardInterrupt:
    print("Saliendo del programa...")
finally:
    database.close()

