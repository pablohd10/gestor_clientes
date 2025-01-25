import sqlite3

import os

class Database:
    def __init__(self):
        # Directorio del usuario
        user_home = os.path.expanduser("~")
        db_dir = os.path.join(user_home, "Desktop", "Clientes")
        if not os.path.exists(db_dir):
            os.makedirs(db_dir) # Crea el directorio si no existe
        
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

    def add_client_db(self, nombre, apellido, ciudad, email, telefono, tipo):
        try:
            self.cursor.execute("INSERT INTO Clientes (Nombre, Apellido, Ciudad, Email, Telefono, Tipo) VALUES (?, ?, ?, ?, ?, ?)",
                                (nombre, apellido, ciudad, email, telefono, tipo))
            self.conn.commit()
            return "Cliente " + nombre + " " + apellido+" agregado"
        except sqlite3.IntegrityError:
            return "Error: Cliente " + nombre + " " + apellido + " ya existe"
        
    def add_document_db(self, ruta, cliente_id, nombre_documento, jurisdiccion, tipo_documento):
        try:
            self.cursor.execute("INSERT INTO Documentos (RutaArchivo, ClienteID, NombreDocumento, Jurisdiccion, TipoDocumento) VALUES (?, ?, ?, ?, ?)",
                                (ruta, cliente_id, nombre_documento, jurisdiccion, tipo_documento))
            self.conn.commit()
            return "Documento " + nombre_documento + " agregado"
        except sqlite3.IntegrityError:
            return "Error: Documento " + nombre_documento + " ya existe"
        
    def get_client_by_id(self, client_id):
        try:
            self.cursor.execute("SELECT * FROM Clientes WHERE ID = ?", (client_id,))
            return self.cursor.fetchone()
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
        query = "SELECT * FROM Clientes WHERE"
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
