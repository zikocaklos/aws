import hashlib
import mysql.connector
from backend.db import conectar

def hash_password(password: str) -> str:
    """Retorna el hash SHA-256 de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()


def crear_usuario(nombre: str, contrasena: str, rol: str = "empleado"):
    """Crea un usuario nuevo en MySQL con contraseña hasheada."""
    conn = conectar()
    cursor = conn.cursor()

    try:
        hashed = hash_password(contrasena)

        cursor.execute(
            "INSERT INTO usuarios (nombre, contrasena, rol) VALUES (%s, %s, %s)",
            (nombre, hashed, rol)
        )
        conn.commit()
        print(f"✅ Usuario '{nombre}' creado correctamente")

    except mysql.connector.IntegrityError:
        print("❌ El usuario ya existe")
        raise

    except Exception as e:
        print(f"⚠️ Error al crear usuario: {e}")
        raise

    finally:
        conn.close()


def verificar_usuario(nombre: str, contrasena: str):
    """Verifica si existe un usuario y si la contraseña coincide."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, nombre, rol, contrasena FROM usuarios WHERE nombre=%s",
        (nombre,)
    )

    user = cursor.fetchone()
    conn.close()

    if user and user[3] == hash_password(contrasena):
        return {
            "id": user[0],
            "nombre": user[1],
            "rol": user[2]
        }

    return None
