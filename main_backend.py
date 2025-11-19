# main_backend.py
import os
from backend.db import crear_tabla_usuarios, crear_tabla_historial
from backend.users import crear_usuario
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/create_admin", methods=["POST"])
def create_admin():
    """
    POST JSON: {"nombre": "admin", "contrasena": "admin123"}
    Use this to create an admin if you don't want to run python interactive.
    """
    data = request.get_json() or {}
    nombre = data.get("nombre")
    contrasena = data.get("contrasena")
    if not nombre or not contrasena:
        return jsonify({"error":"nombre and contrasena required"}), 400
    try:
        crear_usuario(nombre, contrasena, rol="admin")
        return jsonify({"created": nombre}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    print("Iniciando backend: creando/verificando tablas...")
    crear_tabla_usuarios()
    crear_tabla_historial()
    print("Tablas listas. Arrancando servidor healthcheck (Flask) en 127.0.0.1:5000")
    # Ejecutar Flask en 127.0.0.1 para solo localmente (seguro). Cambia host/port si lo necesitas.
    app.run(host="127.0.0.1", port=5000)

if __name__ == "__main__":
    main()
