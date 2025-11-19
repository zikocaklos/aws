import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="proyecto.cz2uso644fxd.us-east-2.rds.amazonaws.com",
        user="admin",
        password="admin123.,",
        database="proyecto",
        port=3306 
    )

def crear_tabla_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) UNIQUE NOT NULL,
            contrasena VARCHAR(256) NOT NULL,
            rol VARCHAR(50) DEFAULT 'empleado'
        )
    """)
    conn.commit()
    conn.close()

def crear_tabla_historial():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(100) NOT NULL,
            accion VARCHAR(100) NOT NULL,
            archivo VARCHAR(200) NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
