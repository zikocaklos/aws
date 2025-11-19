import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from backend.s3_client import (
    subir_archivo,
    listar_archivos,
    descargar_archivo,
    eliminar_archivo,
    obtener_imagen,
)
from backend.utils import previsualizar_imagen


def crear_gui(user):
    """
    Interfaz principal del sistema S3 para usuarios.
    'user' es un diccionario con las claves: id, nombre, rol.
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title(f"S3_Bucket - Usuario: {user['nombre']} ({user['rol']})")
    root.geometry("650x520")

    # --- Parte superior ---
    frame_top = ctk.CTkFrame(root, corner_radius=10, fg_color="#1f1f1f")
    frame_top.pack(pady=10, padx=10, fill="x")

    label_user = ctk.CTkLabel(frame_top, text=f"👤 {user['nombre']}", font=("Arial", 14))
    label_user.pack(side="left", padx=10)

    btn_subir = ctk.CTkButton(frame_top, text="Subir archivo")
    btn_subir.pack(side="left", padx=10, pady=10)

    btn_descargar = ctk.CTkButton(frame_top, text="Descargar")
    btn_descargar.pack(side="left", padx=10, pady=10)

    btn_eliminar = ctk.CTkButton(frame_top, text="Eliminar")
    btn_eliminar.pack(side="left", padx=10, pady=10)

    btn_listar = ctk.CTkButton(frame_top, text="Listar archivos")
    btn_listar.pack(side="left", padx=10, pady=10)

    btn_logout = ctk.CTkButton(frame_top, text="Cerrar sesión", fg_color="#A83232", hover_color="#8B1E1E", width=120)
    btn_logout.pack(side="right", padx=10)

    # --- Parte inferior ---
    frame_bottom = ctk.CTkFrame(root, corner_radius=10)
    frame_bottom.pack(pady=10, padx=10, fill="both", expand=True)

    listbox_frame = ctk.CTkFrame(frame_bottom, corner_radius=5)
    listbox_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(listbox_frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
    listbox.pack(fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    frame_preview = ctk.CTkFrame(frame_bottom, width=250, height=250, corner_radius=10)
    frame_preview.pack(side="right", padx=10, pady=10)
    frame_preview.pack_propagate(False)

    label_img = ctk.CTkLabel(frame_preview, text="Previsualización")
    label_img.pack(expand=True)

    # --- Funciones internas ---
    def actualizar_lista():
        listbox.delete(0, tk.END)
        archivos = listar_archivos()
        if archivos:
            for f in archivos:
                listbox.insert(tk.END, f)
        else:
            listbox.insert(tk.END, "No hay archivos en el bucket.")
        label_img.configure(image='', text="Previsualización")

    def subir():
        path = filedialog.askopenfilename(title="Seleccionar archivo a subir")
        if path:
            subir_archivo(path, user["nombre"])
            actualizar_lista()
            messagebox.showinfo("Éxito", "Archivo subido correctamente.")

    def descargar():
        sel = listbox.curselection()
        if sel:
            file_name = listbox.get(sel)
            if file_name.startswith("No hay"):
                return
            save_path = filedialog.asksaveasfilename(initialfile=file_name)
            if save_path:
                descargar_archivo(file_name, save_path, user["nombre"])
                messagebox.showinfo("Éxito", f"Archivo '{file_name}' descargado correctamente.")

    def eliminar():
        sel = listbox.curselection()
        if sel:
            file_name = listbox.get(sel)
            if file_name.startswith("No hay"):
                return
            if messagebox.askyesno("Confirmar", f"¿Eliminar '{file_name}'?"):
                eliminar_archivo(file_name, user["nombre"])
                actualizar_lista()
                messagebox.showinfo("Eliminado", f"Archivo '{file_name}' eliminado correctamente.")

    def previsualizar(event):
        sel = listbox.curselection()
        if sel:
            file_name = listbox.get(sel)
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                data = obtener_imagen(file_name)
                photo = previsualizar_imagen(data)
                if photo:
                    label_img.configure(image=photo, text="")
                    label_img.image = photo
                else:
                    label_img.configure(image='', text="Error al mostrar imagen")
            else:
                label_img.configure(image='', text="(Sin vista previa disponible)")

    def logout():
        confirm = messagebox.askyesno("Cerrar sesión", "¿Deseas salir del sistema?")
        if confirm:
            root.destroy()

    # --- Asignar eventos ---
    btn_subir.configure(command=subir)
    btn_descargar.configure(command=descargar)
    btn_eliminar.configure(command=eliminar)
    btn_listar.configure(command=actualizar_lista)
    btn_logout.configure(command=logout)
    listbox.bind('<<ListboxSelect>>', previsualizar)

    # --- Inicializar lista ---
    actualizar_lista()

    root.mainloop()
