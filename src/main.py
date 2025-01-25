import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
from src.documents import Documents
from src.database import Database
from src.clientes import Clientes
import os

def mostrar_estado(texto):
    # Verifica si el texto contiene la palabra "Error"
    if texto == None:
        return
    elif "Error" in texto:
        label_status.config(text=texto, fg="red")  # Mostrar texto en rojo si contiene "Error"
    else:
        label_status.config(text=texto, fg="blue")  # Mostrar texto en azul si no contiene "Error"


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

def eliminar_cliente():
    # Obtener el ID del cliente seleccionado en la tabla
    selected_item = tree.selection()
    if not selected_item:
        mostrar_estado("Error: Seleccione un cliente para eliminar")
        return

    id = tree.item(selected_item)["values"][0]
    nombre = tree.item(selected_item)["values"][1]
    apellido = tree.item(selected_item)["values"][2]
    ciudad = tree.item(selected_item)["values"][3]
    tipo = tree.item(selected_item)["values"][6]

    respuesta = messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar el cliente {nombre} {apellido}?")
    if respuesta:
        clientes = Clientes(database)
        estado = clientes.eliminar_cliente(id, nombre, apellido, ciudad, tipo)
        mostrar_estado(estado)
        buscar_dinamico()


def buscar_dinamico(event=None):
    # Obtener lo que el usuario escribe en el campo de búsqueda y eliminar espacios extras
    texto_busqueda = entry_buscar.get().strip()

    # Si no hay texto en el campo, no hacer nada
    if not texto_busqueda:
        tree.delete(*tree.get_children())  # Limpiar resultados
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
        
def agregar_documento():
    file_path = filedialog.askopenfilename(title="Seleccionar Documento")
    if not file_path:
        return  # Si el usuario cancela, no hacer nada

    # Obtener el ID del cliente seleccionado en la tabla
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Seleccione un cliente para asociar el documento")
        return
    
    # Si se ha selccionado mas de un cliente, mostrar error
    if len(selected_item) > 1:
        messagebox.showerror("Error", "Seleccione solo un cliente para asociar el documento")
        return

    cliente_id = tree.item(selected_item)["values"][0]

    # Solicitar la jurisdicción del documento
    jurisdiccion = solicitar_jurisdiccion()
    if not jurisdiccion:
        messagebox.showerror("Error", "Debe seleccionar una jurisdicción")
        return

    if jurisdiccion == "Datos Personales":
        procedimiento = solicitar_datos_personales()
        if not procedimiento:
            messagebox.showerror("Error", "Debe seleccionar un dato personal")
            return
    else:
        # Solicitar el procedimiento del documento
        procedimiento = solicitar_procedimiento()
        if not procedimiento:
            messagebox.showerror("Error", "Debe seleccionar un procedimiento")
            return
    documentos = Documents(database)
    mostrar_estado(documentos.agregar_documento(cliente_id, file_path, jurisdiccion, procedimiento))

def solicitar_jurisdiccion():
    seleccion = None  # Variable para almacenar la selección

    def confirmar():
        nonlocal seleccion  # Permitir modificar la variable local de solicitar_jurisdiccion
        seleccion = combobox_jurisdiccion.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar una jurisdicción")
        else:
            ventana_jurisdiccion.destroy()

    # Crear la ventana emergente
    ventana_jurisdiccion = tk.Toplevel()
    ventana_jurisdiccion.title("Seleccionar Jurisdicción")
    ventana_jurisdiccion.geometry("400x200")
    ventana_jurisdiccion.resizable(False, False)

    tk.Label(ventana_jurisdiccion, text="Seleccione la jurisdicción:").pack(pady=10)
    
    # Opciones para el desplegable
    opciones = ["Contencioso", "Civil", "Penal", "Laboral", "Administrativo", "Mercantil", "Datos Personales"]
    combobox_jurisdiccion = ttk.Combobox(ventana_jurisdiccion, values=opciones, state="readonly")
    combobox_jurisdiccion.pack(pady=5)

    # Botón de confirmación
    tk.Button(ventana_jurisdiccion, text="Confirmar", command=confirmar).pack(pady=10)

    # Bloquear interacción con la ventana principal
    ventana_jurisdiccion.transient(ventana)  # Hacer que esté vinculada a la ventana principal
    ventana_jurisdiccion.grab_set()         # Bloquear interacción con la ventana principal
    ventana_jurisdiccion.wait_window()      # Esperar hasta que la ventana emergente se cierre

    return seleccion

def solicitar_procedimiento():
    seleccion = None  # Variable para almacenar la selección

    def confirmar():
        nonlocal seleccion  # Permitir modificar la variable local de solicitar_procedimiento
        seleccion = combobox_procedimiento.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar un procedimiento")
        else:
            ventana_procedimiento.destroy()

    # Crear la ventana emergente
    ventana_procedimiento = tk.Toplevel()
    ventana_procedimiento.title("Seleccionar Procedimiento")
    ventana_procedimiento.geometry("400x200")
    ventana_procedimiento.resizable(False, False)

    tk.Label(ventana_procedimiento, text="Seleccione el procedimiento:").pack(pady=10)
    
    # Opciones para el desplegable
    opciones = ["Recurso", "Apelación", "Amparo", "Revisión", "Casación"]
    combobox_procedimiento = ttk.Combobox(ventana_procedimiento, values=opciones, state="readonly")
    combobox_procedimiento.pack(pady=5)

    # Botón de confirmación
    tk.Button(ventana_procedimiento, text="Confirmar", command=confirmar).pack(pady=10)

    # Bloquear interacción con la ventana principal
    ventana_procedimiento.transient(ventana)  # Hacer que esté vinculada a la ventana principal
    ventana_procedimiento.grab_set()         # Bloquear interacción con la ventana principal
    ventana_procedimiento.wait_window()      # Esperar hasta que la ventana emergente se cierre

    return seleccion

def solicitar_datos_personales():
    seleccion = None  # Variable para almacenar la selección

    def confirmar():
        nonlocal seleccion  # Permitir modificar la variable local de solicitar_datos_personales
        seleccion = combobox_jurisdiccion.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar un dato personal")
        else:
            ventana_jurisdiccion.destroy()

    # Crear la ventana emergente
    ventana_jurisdiccion = tk.Toplevel()
    ventana_jurisdiccion.title("Seleccionar Dato Personal")
    ventana_jurisdiccion.geometry("400x200")
    ventana_jurisdiccion.resizable(False, False)

    tk.Label(ventana_jurisdiccion, text="Seleccione el dato personal:").pack(pady=10)
    
    # Opciones para el desplegable
    opciones = ["DNI", "Pasaporte", "NIE", "Tarjeta de Residencia", "Número de Seguridad Social", "Nómina", "Contrato de Trabajo"]
    combobox_jurisdiccion = ttk.Combobox(ventana_jurisdiccion, values=opciones, state="readonly")
    combobox_jurisdiccion.pack(pady=5)

    # Botón de confirmación
    tk.Button(ventana_jurisdiccion, text="Confirmar", command=confirmar).pack(pady=10)

    # Bloquear interacción con la ventana principal
    ventana_jurisdiccion.transient(ventana)  # Hacer que esté vinculada a la ventana principal
    ventana_jurisdiccion.grab_set()         # Bloquear interacción con la ventana principal
    ventana_jurisdiccion.wait_window()      # Esperar hasta que la ventana emergente se cierre

    return seleccion

def mostrar_documentos():
    documentos = Documents(database)
    mostrar_estado(documentos.mostrar_documentos(tree))

def abrir_documento():
    # Obtener el ID del cliente seleccionado
    selected_item = tree.selection()
    if not selected_item:
        mostrar_estado("Error: Seleccione un cliente para abrir un documento")
        return

     # Si se ha selccionado mas de un cliente, mostrar error
    if len(selected_item) > 1:
        messagebox.showerror("Error", "Seleccione solo un cliente para abrir sus documentos")
        return

    cliente_id = tree.item(selected_item)["values"][0]

    # Seleccionar un documento del cliente
    conn = sqlite3.connect("clientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT RutaArchivo FROM Documentos WHERE ClienteID = ?", (cliente_id,))
    documentos = cursor.fetchall()
    conn.close()

    if documentos:
        file_path = documentos[0][0]  # Ejemplo: abrir el primer documento
        os.startfile(file_path)  # Abre el archivo en su programa predeterminado
    else:
        mostrar_estado("No hay documentos asociados a este cliente")
        
def exportar_base_datos():
    """Permite exportar la base de datos a un archivo seleccionado por el usuario."""
    ruta_exportacion = filedialog.asksaveasfilename(
        title="Exportar Base de Datos",
        defaultextension=".db",
        filetypes=[("Archivos SQLite", "*.db"), ("Todos los archivos", "*.*")]
    )
    if not ruta_exportacion:
        return
    try:
        database.close()  # Cerrar conexión antes de copiar
        with open("clientes.db", "rb") as db_origen:
            with open(ruta_exportacion, "wb") as db_destino:
                db_destino.write(db_origen.read())
        messagebox.showinfo("Éxito", "Base de datos exportada correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar la base de datos: {str(e)}")
    finally:
        database.connect() # Reconectar para seguir trabajando

def importar_base_datos():
    """Permite importar una base de datos desde un archivo seleccionado por el usuario."""
    ruta_importacion = filedialog.askopenfilename(
        title="Importar Base de Datos",
        filetypes=[("Archivos SQLite", "*.db"), ("Todos los archivos", "*.*")]
    )
    if not ruta_importacion:
        return
    try:
        database.close()  # Cerrar conexión actual antes de sobrescribir
        with open(ruta_importacion, "rb") as db_origen:
            with open("clientes.db", "wb") as db_destino:
                db_destino.write(db_origen.read())
        messagebox.showinfo("Éxito", "Base de datos importada correctamente.")
        # Reconectar y reconfigurar la base de datos importada
        database.connect() # Reconectar para seguir trabajando
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo importar la base de datos: {str(e)}")


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

# Campo de búsqueda dinámico
tk.Label(ventana, text="Buscar Cliente  ---->").grid(row=0, column=0, columnspan=2)
entry_buscar = tk.Entry(ventana)
entry_buscar.grid(row=0, column=1)
entry_buscar.bind("<KeyRelease>", buscar_dinamico)  # Se ejecuta cada vez que se presiona una tecla

# Sección: Agregar Cliente
tk.Label(ventana, text="Introduce los datos para agregar un cliente").grid(row=2, column=0, columnspan=2)
tk.Label(ventana, text="Nombre:").grid(row=3, column=0)
entry_nombre = tk.Entry(ventana)
entry_nombre.grid(row=3, column=1)
tk.Label(ventana, text="Apellido:").grid(row=4, column=0)
entry_apellido = tk.Entry(ventana)
entry_apellido.grid(row=4, column=1)
# Desplegable para seleccionar Ciudad
tk.Label(ventana, text="Ciudad:").grid(row=5, column=0)
combobox_ciudad = ttk.Combobox(ventana, values=["Madrid", "Guadalajara", "Alcala"], state="readonly")
combobox_ciudad.grid(row=5, column=1)
tk.Label(ventana, text="Email:").grid(row=6, column=0)
entry_email = tk.Entry(ventana)
entry_email.grid(row=6, column=1)
tk.Label(ventana, text="Teléfono:").grid(row=7, column=0)
entry_telefono = tk.Entry(ventana)
entry_telefono.grid(row=7, column=1)
# Desplegable para seleccionar Tipo
tk.Label(ventana, text="Tipo:").grid(row=8, column=0)
combobox_tipo = ttk.Combobox(ventana, values=["Privado", "Turno"], state="readonly")
combobox_tipo.grid(row=8, column=1)
# Botón para agregar cliente
tk.Button(ventana, text="Agregar Cliente", command=agregar_cliente).grid(row=9, column=0, columnspan=2)
# Botón para eliminar cliente
tk.Button(ventana, text="Eliminar Cliente", command=eliminar_cliente).grid(row=10, column=0, columnspan=2)
# Mensaje de estado
label_status = tk.Label(ventana, text="", font=("Helvetica", 12, "bold")) 
label_status.grid(row=11, column=0, columnspan=2)

# Botones para gestionar documentos
tk.Button(ventana, text="Agregar Documento", command=agregar_documento).grid(row=18, column=0, columnspan=1)
tk.Button(ventana, text="Ver Documentos", command=mostrar_documentos).grid(row=18, column=1, columnspan=1)

# Tabla para resultados
tree = ttk.Treeview(ventana, columns=("ID", "Nombre", "Apellido", "Ciudad", "Email", "Telefono", "Tipo", "FechaCreacion"), show="headings", height=20)
tree.grid(row=15, column=0, columnspan=2)
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.heading(col, text=col, command=lambda _col=col: ordenar_columnas(_col))


tree.column("ID", width=50)

# Botones para exportar e importar la base de datos
tk.Button(ventana, text="Exportar Base de Datos", command=exportar_base_datos).grid(row=20, column=0, columnspan=1)
tk.Button(ventana, text="Importar Base de Datos", command=importar_base_datos).grid(row=20, column=1, columnspan=1)

ventana.mainloop() # Iniciar la interfaz
