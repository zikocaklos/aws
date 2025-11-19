import hashlib
import mysql.connector
from backend.db import conectar


def hash_password(password):
    """Devuelve el hash SHA-256 de una contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()


def crear_usuario(nombre, contrasena, rol="empleado"):
    """Crea un usuario nuevo en la base de datos MySQL."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, contrasena, rol) VALUES (%s, %s, %s)",
            (nombre, hash_password(contrasena), rol),
        )
        conn.commit()
        print("✅ Usuario creado correctamente")
    except mysql.connector.IntegrityError:
        print("❌ El usuario ya existe")
    except Exception as e:
        print(f"⚠️ Error al crear usuario: {e}")
    finally:
        conn.close()


def verificar_usuario(nombre, contrasena):
    """Verifica si un usuario existe y la contraseña coincide."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, rol, contrasena FROM usuarios WHERE nombre=%s", (nombre,)
    )
    user = cursor.fetchone()
    conn.close()

    if user and user[2] == hash_password(contrasena):
        return {"id": user[0], "nombre": nombre, "rol": user[1]}
    return None
