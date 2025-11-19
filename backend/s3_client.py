import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from backend.logs import registrar_accion

BUCKET_NAME = "intelnegobucket"
REGION_NAME = "us-east-2"

s3 = boto3.client("s3", region_name=REGION_NAME)

def subir_archivo(file_path: str, usuario: str = "desconocido") -> str:
    """Sube un archivo local al bucket de S3 y registra la acción."""
    try:
        file_name = file_path.split("/")[-1]
        s3.upload_file(file_path, BUCKET_NAME, file_name)
        registrar_accion(usuario, "subió", file_name)
        print(f"✅ Archivo '{file_name}' subido correctamente por {usuario}.")
        return file_name
    except FileNotFoundError:
        print("❌ Archivo no encontrado.")
    except NoCredentialsError:
        print("❌ Credenciales de AWS no configuradas correctamente.")
    except ClientError as e:
        print(f"❌ Error al subir archivo: {e}")


def listar_archivos() -> list:
    """Obtiene una lista con los nombres de los archivos en el bucket."""
    try:
        files = s3.list_objects_v2(Bucket=BUCKET_NAME)
        return [obj["Key"] for obj in files.get("Contents", [])]
    except ClientError as e:
        print(f"❌ Error al listar archivos: {e}")
        return []


def descargar_archivo(file_name: str, save_path: str, usuario: str = "desconocido") -> None:
    """Descarga un archivo del bucket al sistema local y registra la acción."""
    try:
        s3.download_file(BUCKET_NAME, file_name, save_path)
        registrar_accion(usuario, "descargó", file_name)
        print(f"📥 Archivo '{file_name}' descargado por {usuario} en '{save_path}'.")
    except ClientError as e:
        print(f"❌ Error al descargar archivo: {e}")


def eliminar_archivo(file_name: str, usuario: str = "desconocido") -> None:
    """Elimina un archivo del bucket y registra la acción."""
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=file_name)
        registrar_accion(usuario, "eliminó", file_name)
        print(f"🗑️ Archivo '{file_name}' eliminado del bucket por {usuario}.")
    except ClientError as e:
        print(f"❌ Error al eliminar archivo: {e}")


def obtener_imagen(file_name: str) -> bytes:
    """Obtiene los bytes de una imagen almacenada en el bucket."""
    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=file_name)
        return obj["Body"].read()
    except ClientError as e:
        print(f"❌ Error al obtener imagen '{file_name}': {e}")
        return b""
