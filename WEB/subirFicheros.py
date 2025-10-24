from azure.core.credentials import AzureNamedKeyCredential
from azure.storage.blob import BlobServiceClient
import os # Añadido para gestionar la ruta del archivo

# Datos de tu cuenta
account_name = 
account_url = f"https://{account_name}.blob.core.windows.net"

# Credencial (nombre de cuenta y clave)
credential = AzureNamedKeyCredential(
    account_name,
    
)

# Crear cliente del servicio Blob
blob_service_client = BlobServiceClient(account_url, credential=credential)

print(blob_service_client)

container_name = "imagenes-ocr"

# Nombre del archivo local y el blob destino
local_image_path = "./imgs/texto.png"   # <-- Cambia esto
blob_name = "imagen_subida456.jpg"            # Nombre con el que se guardará en Azure

# Obtener el cliente del contenedor
container_client = blob_service_client.get_container_client(container_name)

try:
    # Subir la imagen
    with open(local_image_path, "rb") as data:
        # --- INICIO DE LA CORRECCIÓN ---
        # Captura el 'blob_client' que devuelve la función de subida
        blob_client = container_client.upload_blob(name=blob_name, data=data, overwrite=True)
        # --- FIN DE LA CORRECCIÓN ---

    print(f"✅ Imagen '{blob_name}' subida correctamente al contenedor '{container_name}'")

    # Ahora pide la URL al 'blob_client' que has capturado
    print(f"\nURL PÚBLICA: {blob_client.url}")

except FileNotFoundError:
    print(f"❌ ERROR: No se encontró el archivo en la ruta: '{local_image_path}'")
except Exception as e:
    print(f"❌ ERROR al subir la imagen: {e}")
    print("Asegúrate de que la clave, el nombre de la cuenta y el nombre del contenedor son correctos.")