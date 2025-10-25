from flask import request,Blueprint, render_template, current_app
import uuid # Para generar nombres de fichero únicos
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials import AzureNamedKeyCredential
from utils.textoOCR import obtener_texto_ocr
from utils.traduccionImg import traducir_texto_ocr
from utils.analisisTexto import analizar_texto_azure

controller = Blueprint('textoController', __name__, url_prefix="/upload")

@controller.route('/', methods=['POST'])
def subida_analisis_texto():
    NOMBRE_CUENTA_ALMACENAMIENTO = current_app.config["NOMBRE_CUENTA_ALMACENAMIENTO"]
    CREDENCTIAL_BLOB = current_app.config["CREDENCTIAL_BLOB"]

    file = request.files['file']
    filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)


    # Conectar y subir
    credential = AzureNamedKeyCredential(
        NOMBRE_CUENTA_ALMACENAMIENTO,
        CREDENCTIAL_BLOB
    )

    blob_service_client = BlobServiceClient(account_url=f"https://{NOMBRE_CUENTA_ALMACENAMIENTO}.blob.core.windows.net", credential=credential)
    container_name = "imagenes-ocr"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    #Subir el archivo
    blob_client.upload_blob(data=file.stream, overwrite=True)

    #Obtener la URL pública
    blob_url = blob_client.url

    texto_extraido = extraer(blob_url)
    idioma_detectado, texto_traducido, idioma_destino = traduccion(texto_extraido)

    if texto_traducido != " ":
        sentimiento, _, categorias, resultado_texto = analisis(texto_traducido)

    return render_template(
        'index.html',
        imagen_url=blob_url,
        texto_original=texto_extraido if texto_extraido != " " else "Sin texto que extraer",
        idioma=idioma_detectado if texto_traducido != " " else "No se pudo detectar el idioma",
        idioma_destino = idioma_destino if texto_traducido != " " else "No se pudo detectar el idioma",
        texto_traducido = texto_traducido if texto_traducido != " " else " No se pudo realizar la traducción",
        sentimiento = sentimiento if texto_traducido != " " else " No se pudo detectar el sentimiento", 
        frases_clave = categorias if texto_traducido != " " else "",
        temas=resultado_texto if texto_traducido != " " else " No se pudo extraer el tema"
    )

def extraer(imagen_url) -> str:
    ENPOINT_URL_VISION = current_app.config["ENPOINT_URL_VISION"]
    SUBSCRIPTION_ID = current_app.config["SUBSCRIPTION_ID"]

    credential = AzureKeyCredential(
        SUBSCRIPTION_ID
    )

    texto_extraido = obtener_texto_ocr(
        credential=credential,
        endpoint=ENPOINT_URL_VISION,
        image_url=imagen_url          
    ) 

    return texto_extraido

def traduccion(texto):
    ENPOINT_URL_TRANSLATOR = current_app.config["ENPOINT_URL_TRANSLATOR"]
    CREDENTIAL_TRANSLATOR = current_app.config["CREDENTIAL_TRANSLATOR"]

    credential = AzureKeyCredential(
        CREDENTIAL_TRANSLATOR
    )

    idioma_detectado, texto_traducido, idioma_destino= traducir_texto_ocr(credential, ENPOINT_URL_TRANSLATOR, texto)

    return idioma_detectado, texto_traducido, idioma_destino

def analisis(texto) -> str:
    ENPOINT_URL_LANGUAGE = current_app.config["ENPOINT_URL_LANGUAGE"]
    CREDENTIAL_LANGUAGE = current_app.config["CREDENTIAL_LANGUAGE"]

    credential = AzureKeyCredential(
        CREDENTIAL_LANGUAGE
    )

    resultado_texto = analizar_texto_azure(credential, ENPOINT_URL_LANGUAGE, texto)

    return resultado_texto['sentimiento'], resultado_texto['confianza'], resultado_texto['categorias'], resultado_texto["etiqueta"]
