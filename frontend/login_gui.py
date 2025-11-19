import customtkinter as ctk
from tkinter import messagebox
from backend.users import verificar_usuario
from frontend.gui import crear_gui
from frontend.admin_gui import crear_admin_gui
import mysql.connector


def crear_login():
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title("Inicio de Sesión")
    root.geometry("350x250")

    frame = ctk.CTkFrame(root, corner_radius=10)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    label_title = ctk.CTkLabel(frame, text="Iniciar Sesión", font=("Arial", 18))
    label_title.pack(pady=10)

    entry_user = ctk.CTkEntry(frame, placeholder_text="Usuario")
    entry_user.pack(pady=5)

    entry_pass = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*")
    entry_pass.pack(pady=5)

    def login():
        nombre = entry_user.get().strip()
        contrasena = entry_pass.get().strip()

        if not nombre or not contrasena:
            messagebox.showwarning("Atención", "Por favor ingrese usuario y contraseña")
            return

        try:
            user = verificar_usuario(nombre, contrasena)
            if user:
                rol = user["rol"]
                messagebox.showinfo("Bienvenido", f"Hola {nombre} ({rol})")
                root.destroy()

                if rol == "admin":
                    crear_admin_gui(user)
                else:
                    crear_gui(user)
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        except mysql.connector.Error as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar con la base de datos:\n{e}")

    btn_login = ctk.CTkButton(frame, text="Entrar", command=login)
    btn_login.pack(pady=10)

    root.mainloop()
