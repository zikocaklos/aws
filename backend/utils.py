from PIL import Image, ImageTk
import io

def previsualizar_imagen(data: bytes, size=(200, 200)):
    try:
        image = Image.open(io.BytesIO(data))
        image.thumbnail(size)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"❌ Error al previsualizar imagen: {e}")
        return None
