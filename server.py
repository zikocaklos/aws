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

app = FastAPI()

# ---------- HEALTH CHECK ----------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------- USUARIOS ----------
@app.get("/usuarios")
def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    data = cursor.fetchall()
    conn.close()
    return data


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


# ---------- HISTORIAL ----------
@app.get("/historial")
def historial():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM historial ORDER BY fecha DESC")
    data = cursor.fetchall()
    conn.close()
    return data


# ---------- S3: SUBIR ARCHIVOS ----------
@app.post("/upload")
async def upload(file: UploadFile = File(...), usuario: str = "desconocido"):
    temp_path = f"/tmp/{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    subir_archivo(temp_path, usuario)
    registrar_accion(usuario, "subió", file.filename)

    os.remove(temp_path)

    return {"status": "uploaded", "filename": file.filename}


# ---------- S3: LISTAR ARCHIVOS ----------
@app.get("/files")
def files():
    return listar_archivos()


# ---------- S3: ELIMINAR ARCHIVO ----------
@app.delete("/files/{filename}")
def delete_file(filename: str, usuario: str = "desconocido"):
    eliminar_archivo(filename, usuario)
    registrar_accion(usuario, "eliminó", filename)
    return {"status": "deleted", "filename": filename}
