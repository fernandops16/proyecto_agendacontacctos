import sqlite3

DB_FILE = "contactos.db"

class ContactoModel:

    @staticmethod
    def crear_tabla():
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contactos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT NOT NULL,
                correo TEXT
            )
        """)
        con.commit()
        con.close()

    @staticmethod
    def obtener_contactos():
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("SELECT * FROM contactos ORDER BY nombre")
        datos = cur.fetchall()
        con.close()
        return datos

    @staticmethod
    def agregar_contacto(nombre, telefono, correo):
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("INSERT INTO contactos (nombre, telefono, correo) VALUES (?, ?, ?)", (nombre, telefono, correo))
        con.commit()
        con.close()

    @staticmethod
    def editar_contacto(id_contacto, nombre, telefono, correo):
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("UPDATE contactos SET nombre=?, telefono=?, correo=? WHERE id=?", (nombre, telefono, correo, id_contacto))
        con.commit()
        con.close()

    @staticmethod
    def eliminar_contacto(id_contacto):
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("DELETE FROM contactos WHERE id=?", (id_contacto,))
        con.commit()
        con.close()

    @staticmethod
    def limpiar_todos_contactos():
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("DELETE FROM contactos")
        con.commit()
        con.close()
