from fastapi import FastAPI, UploadFile, File
from backend.db import conectar
from backend.s3_client import subir_archivo_s3, listar_archivos_s3, eliminar_archivo_s3
import os

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

# ------------ USUARIOS ------------
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
    if user:
        return {"login": True}
    return {"login": False}

# ------------ ARCHIVOS S3 ------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_location = f"/tmp/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    subir_archivo_s3(file_location, file.filename)
    os.remove(file_location)
    return {"upload": "ok"}

@app.get("/files")
def files():
    return listar_archivos_s3()

@app.delete("/files/{filename}")
def delete_file(filename: str):
    eliminar_archivo_s3(filename)
    return {"delete": "ok"}
