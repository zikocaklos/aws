import mysql.connector
from backend.db import conectar

def registrar_accion(usuario: str, accion: str, archivo: str):
    """
    Registra una acción realizada por un usuario en la tabla 'historial'.

    Parámetros:
        usuario (str): Nombre del usuario que ejecuta la acción.
        accion (str): Tipo de acción (subió, descargó, eliminó, etc.).
        archivo (str): Nombre del archivo afectado.
    """
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO historial (usuario, accion, archivo)
            VALUES (%s, %s, %s)
            """,
            (usuario, accion, archivo)
        )

        conn.commit()
        print(f"🧾 Acción registrada: {usuario} {accion} '{archivo}'")

    except mysql.connector.Error as e:
        print(f"⚠️ Error al registrar acción en la base de datos: {e}")

    finally:
        if conn.is_connected():
            conn.close()
