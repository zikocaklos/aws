import os
import hashlib
from fastapi import FastAPI, UploadFile, File
from backend.db import conectar
from backend.s3_client import (
    subir_archivo,
    listar_archivos,
    eliminar_archivo
)
from backend.logs import registrar_accion
from backend.auth import crear_usuario, hash_password

app = FastAPI()

# ============================================================
#               HEALTH CHECK
# ============================================================
@app.get("/health")
def health():
    return {"status": "ok"}

# ============================================================
#               USUARIOS
# ============================================================
@app.get("/usuarios")
def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    data = cursor.fetchall()
    conn.close()
    return data


# ---------- LOGIN ----------
@app.post("/login")
def login(nombre: str, contrasena: str):
    conn = conectar()
    cursor = conn.cursor()

    hashed = hashlib.sha256(contrasena.encode()).hexdigest()

    cursor.execute(
        "SELECT * FROM usuarios WHERE nombre=%s AND contrasena=%s",
        (nombre, hashed)
    )
    user = cursor.fetchone()
    conn.close()

    return {"login": bool(user)}


# ---------- CREAR USUARIO ----------
@app.post("/usuarios")
def crear_usuario_api(data: dict):
    nombre = data.get("nombre")
    contrasena = data.get("contrasena")
    rol = data.get("rol", "empleado")

    if not nombre or not contrasena:
        return {"error": "Faltan datos"}

    try:
        crear_usuario(nombre, contrasena, rol)
        return {"status": "ok", "message": "Usuario creado"}
    except Exception as e:
        return {"error": str(e)}


# ---------- MODIFICAR USUARIO ----------
@app.put("/usuarios")
def modificar_usuario_api(data: dict):
    nombre = data.get("nombre")
    nueva_pass = data.get("nueva_pass")
    nuevo_rol = data.get("nuevo_rol")

    if not nombre:
        return {"error": "Debes enviar el nombre del usuario"}

    conn = conectar()
    cursor = conn.cursor()

    try:
        if nueva_pass:
            hashed = hash_password(nueva_pass)
            cursor.execute(
                "UPDATE usuarios SET contrasena=%s WHERE nombre=%s",
                (hashed, nombre)
            )

        if nuevo_rol:
            cursor.execute(
                "UPDATE usuarios SET rol=%s WHERE nombre=%s",
                (nuevo_rol, nombre)
            )

        conn.commit()
        return {"status": "ok", "message": "Usuario actualizado"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        conn.close()


# ---------- ELIMINAR USUARIO ----------
@app.delete("/usuarios/{nombre}")
def eliminar_usuario_api(nombre: str):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE nombre=%s", (nombre,))
    conn.commit()

    if cursor.rowcount > 0:
        return {"status": "ok", "message": "Usuario eliminado"}
    else:
        return {"error": "Usuario no encontrado"}


# ============================================================
#                    HISTORIAL
# ============================================================
@app.get("/historial")
def historial(filtro: str = None):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if filtro:
        query = """
            SELECT usuario, accion, archivo, fecha 
            FROM historial 
            WHERE usuario LIKE %s OR accion LIKE %s
            ORDER BY fecha DESC
        """
        cursor.execute(query, (f"%{filtro}%", f"%{filtro}%"))
    else:
        cursor.execute("SELECT usuario, accion, archivo, fecha FROM historial ORDER BY fecha DESC")

    data = cursor.fetchall()
    conn.close()
    return data


# ============================================================
#               ARCHIVOS S3
# ============================================================
@app.post("/upload")
async def upload(file: UploadFile = File(...), usuario: str = "desconocido"):
    temp_path = f"/tmp/{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    subir_archivo(temp_path)
    registrar_accion(usuario, "subió", file.filename)

    os.remove(temp_path)

    return {"status": "uploaded", "filename": file.filename}


@app.get("/files")
def files():
    return listar_archivos()


@app.delete("/files/{filename}")
def delete_file(filename: str, usuario: str = "desconocido"):
    eliminar_archivo(filename)
    registrar_accion(usuario, "eliminó", filename)
    return {"status": "deleted", "filename": filename}
