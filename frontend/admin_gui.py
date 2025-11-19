import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
from backend.db import conectar
from backend.users import crear_usuario, hash_password


def crear_admin_gui(user):
    root = ctk.CTk()
    root.title("Panel de Administración")
    root.geometry("900x500")
    root.resizable(False, False)

    # --- Colores base ---
    sidebar_color = "#1f1f1f"
    main_bg = "#2a2a2a"

    # --- Frames principales ---
    frame_left = ctk.CTkFrame(root, width=200, fg_color=sidebar_color)
    frame_left.pack(side="left", fill="y")

    frame_right = ctk.CTkFrame(root, fg_color=main_bg)
    frame_right.pack(side="right", fill="both", expand=True)

    # --- Bienvenida ---
    label_welcome = ctk.CTkLabel(frame_left, text=f"👋 {user['nombre']}", font=("Arial", 16, "bold"))
    label_welcome.pack(pady=20)

    # --- Funciones internas ---
    def clear_right():
        for widget in frame_right.winfo_children():
            widget.destroy()

    # =============================
    # 1️⃣ Ver usuarios
    # =============================
    def ver_usuarios():
        clear_right()
        title = ctk.CTkLabel(frame_right, text="👥 Lista de Usuarios", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        text = ctk.CTkTextbox(frame_right, width=600, height=300)
        text.pack(pady=10)

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, rol FROM usuarios")
        data = cursor.fetchall()
        conn.close()
        text.delete("1.0", "end")
        for row in data:
            text.insert("end", f"ID: {row[0]} | Usuario: {row[1]} | Rol: {row[2]}\n")

    # =============================
    # 2️⃣ Crear usuario
    # =============================
    def crear_usuario_gui():
        clear_right()
        title = ctk.CTkLabel(frame_right, text="➕ Crear Usuario", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        entry_nombre = ctk.CTkEntry(frame_right, placeholder_text="Nombre de usuario")
        entry_nombre.pack(pady=5)
        entry_pass = ctk.CTkEntry(frame_right, placeholder_text="Contraseña", show="*")
        entry_pass.pack(pady=5)
        combo_rol = ctk.CTkComboBox(frame_right, values=["empleado", "admin"])
        combo_rol.set("empleado")
        combo_rol.pack(pady=5)

        def crear():
            nombre = entry_nombre.get().strip()
            contrasena = entry_pass.get().strip()
            rol = combo_rol.get()

            if not nombre or not contrasena:
                messagebox.showerror("Error", "Completa todos los campos")
                return
            try:
                crear_usuario(nombre, contrasena, rol)
                messagebox.showinfo("Éxito", f"Usuario '{nombre}' creado correctamente")
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"No se pudo crear el usuario:\n{e}")

        btn_guardar = ctk.CTkButton(frame_right, text="Guardar Usuario", command=crear)
        btn_guardar.pack(pady=10)

    # =============================
    # 3️⃣ Modificar usuario
    # =============================
    def modificar_usuario_gui():
        clear_right()
        title = ctk.CTkLabel(frame_right, text="✏️ Modificar Usuario", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        entry_nombre = ctk.CTkEntry(frame_right, placeholder_text="Nombre de usuario a modificar")
        entry_nombre.pack(pady=5)
        entry_nueva_pass = ctk.CTkEntry(frame_right, placeholder_text="Nueva contraseña (opcional)", show="*")
        entry_nueva_pass.pack(pady=5)
        combo_rol = ctk.CTkComboBox(frame_right, values=["empleado", "admin"])
        combo_rol.set("empleado")
        combo_rol.pack(pady=5)

        def modificar():
            nombre = entry_nombre.get().strip()
            nueva_pass = entry_nueva_pass.get().strip()
            nuevo_rol = combo_rol.get()

            if not nombre:
                messagebox.showerror("Error", "Debes ingresar el nombre del usuario a modificar")
                return

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM usuarios WHERE nombre=%s", (nombre,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "El usuario no existe")
                conn.close()
                return

            if nueva_pass:
                cursor.execute("UPDATE usuarios SET contrasena=%s WHERE nombre=%s", (hash_password(nueva_pass), nombre))
            cursor.execute("UPDATE usuarios SET rol=%s WHERE nombre=%s", (nuevo_rol, nombre))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", f"Usuario '{nombre}' modificado correctamente")

        btn_guardar = ctk.CTkButton(frame_right, text="Aplicar Cambios", command=modificar)
        btn_guardar.pack(pady=10)

    # =============================
    # 4️⃣ Ver historial
    # =============================
    def ver_historial():
        clear_right()
        title = ctk.CTkLabel(frame_right, text="🧾 Historial de Actividades", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        filter_frame = ctk.CTkFrame(frame_right)
        filter_frame.pack(pady=5)

        entry_filtro = ctk.CTkEntry(filter_frame, placeholder_text="Filtrar por usuario o acción...")
        entry_filtro.pack(side="left", padx=5)

        text = ctk.CTkTextbox(frame_right, width=650, height=300)
        text.pack(pady=10)

        def cargar_historial(filtro=""):
            conn = conectar()
            cursor = conn.cursor()
            if filtro:
                filtro = f"%{filtro}%"
                cursor.execute(
                    "SELECT usuario, accion, archivo, fecha FROM historial WHERE usuario LIKE %s OR accion LIKE %s ORDER BY fecha DESC",
                    (filtro, filtro),
                )
            else:
                cursor.execute("SELECT usuario, accion, archivo, fecha FROM historial ORDER BY fecha DESC")
            data = cursor.fetchall()
            conn.close()

            text.delete("1.0", "end")
            if not data:
                text.insert("end", "No hay registros.\n")
            else:
                for row in data:
                    text.insert("end", f"{row[3]} | {row[0]} {row[1]} '{row[2]}'\n")

        def aplicar_filtro():
            filtro = entry_filtro.get().strip()
            cargar_historial(filtro)

        btn_filtrar = ctk.CTkButton(filter_frame, text="Filtrar", width=70, command=aplicar_filtro)
        btn_filtrar.pack(side="left", padx=5)

        cargar_historial()

    # =============================
    # 5️⃣ Logout
    # =============================
    def logout():
        confirm = messagebox.askyesno("Cerrar sesión", "¿Seguro que deseas salir?")
        if confirm:
            root.destroy()

    # --- Botones del menú lateral ---
    btn_usuarios = ctk.CTkButton(frame_left, text="👥 Ver Usuarios", width=180, command=ver_usuarios)
    btn_crear = ctk.CTkButton(frame_left, text="➕ Crear Usuario", width=180, command=crear_usuario_gui)
    btn_modificar = ctk.CTkButton(frame_left, text="✏️ Modificar Usuario", width=180, command=modificar_usuario_gui)
    btn_historial = ctk.CTkButton(frame_left, text="🧾 Ver Historial", width=180, command=ver_historial)
    btn_logout = ctk.CTkButton(frame_left, text="🚪 Logout", width=180, fg_color="#A83232", hover_color="#8B1E1E", command=logout)

    btn_usuarios.pack(pady=5)
    btn_crear.pack(pady=5)
    btn_modificar.pack(pady=5)
    btn_historial.pack(pady=5)
    btn_logout.pack(side="bottom", pady=20)

    # --- Mostrar historial por defecto ---
    ver_historial()

    root.mainloop()
