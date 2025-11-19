from fastapi import FastAPI, UploadFile, File
from backend.db import conectar
from backend.s3_client import (
    subir_archivo,
    listar_archivos,
    eliminar_archivo
)
import os

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
def login(usuario: str, contrasena: str):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE usuario=%s AND contrasena=%s",
        (usuario, contrasena)
    )
    user = cursor.fetchone()
    conn.close()
    return {"login": bool(user)}


# ---------- S3: SUBIR ARCHIVOS ----------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # Guardar archivo temporalmente
    temp_path = f"/tmp/{file.filename}"
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Usar la función REAL de tu s3_client
    subir_archivo(temp_path)

    # Borrar archivo temporal
    os.remove(temp_path)

    return {"status": "uploaded", "filename": file.filename}


# ---------- S3: LISTAR ARCHIVOS ----------
@app.get("/files")
def files():
    return listar_archivos()


# ---------- S3: ELIMINAR ARCHIVO ----------
@app.delete("/files/{filename}")
def delete_file(filename: str):
    eliminar_archivo(filename)
    return {"status": "deleted", "filename": filename}
