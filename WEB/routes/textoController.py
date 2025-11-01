#Importar las librerías necesarias
from flask import request,Blueprint, render_template, current_app
import uuid #Para generar nombres de fichero únicos
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials import AzureNamedKeyCredential
from utils.textoOCR import obtener_texto_ocr
from utils.traduccionImg import traducir_texto_ocr
from utils.analisisTexto import analizar_texto_azure

#Creación de un Blueprint llamado 'textoController' con prefijo de URL '/upload'
controller = Blueprint('textoController', __name__, url_prefix="/upload")

#Ruta pirncipal: subida y análisis de la imagen
@controller.route('/', methods=['POST'])
def subida_analisis_texto():

    #Obtener las credenciales del almacenamiento desde la configuración de Flask
    NOMBRE_CUENTA_ALMACENAMIENTO = current_app.config["NOMBRE_CUENTA_ALMACENAMIENTO"]
    CREDENCTIAL_BLOB = current_app.config["CREDENCTIAL_BLOB"]

    #Obtener el archivo enviado desde el formulario
    file = request.files['file']
    #Generar un nombre único para el archivo combinando un UUID y el nombre original
    filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)

    #Conectar y subir
    credential = AzureNamedKeyCredential(
        NOMBRE_CUENTA_ALMACENAMIENTO,
        CREDENCTIAL_BLOB
    )

    #Conectar con el servicio de Blob Storage
    blob_service_client = BlobServiceClient(account_url=f"https://{NOMBRE_CUENTA_ALMACENAMIENTO}.blob.core.windows.net", credential=credential)
    container_name = "imagenes-ocr"

    #Obtener el cliente del blob específico
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

    #Subir el archivo
    blob_client.upload_blob(data=file.stream, overwrite=True)

    #Obtener la URL pública
    blob_url = blob_client.url

    #Extraer el texto de la imagen usando el servicio de Azure Vision
    texto_extraido = extraer(blob_url)

    #Traducir el texto extraído usando el servicio de Azure Translator
    idioma_detectado, texto_traducido, idioma_destino = traduccion(texto_extraido)

    #Analizar el texto traducido con el servicio de Azure Language
    if texto_traducido != " ":
        sentimiento, _, categorias, resultado_texto = analisis(texto_traducido)

    #Renderizar la plantilla con los resultados obtenidos
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

#Función para extraer texto de una imagen usando Azure Vision OCR
def extraer(imagen_url) -> str:
    #Obtener configuración del servicio de Azure Vision
    ENPOINT_URL_VISION = current_app.config["ENPOINT_URL_VISION"]
    SUBSCRIPTION_ID = current_app.config["SUBSCRIPTION_ID"]

    #Crear las credenciales del servicio Vision
    credential = AzureKeyCredential(SUBSCRIPTION_ID)

    #Llamar a la función personalizada que realiza el OCR
    texto_extraido = obtener_texto_ocr(
        credential=credential,
        endpoint=ENPOINT_URL_VISION,
        image_url=imagen_url
    )

    #Devolver el texto obtenido
    return texto_extraido

#Función para traducir texto y detectar idioma usando Azure Translator
def traduccion(texto):
    #Obtener configuración del servicio de traducción
    ENPOINT_URL_TRANSLATOR = current_app.config["ENPOINT_URL_TRANSLATOR"]
    CREDENTIAL_TRANSLATOR = current_app.config["CREDENTIAL_TRANSLATOR"]

    #Crear credenciales para el servicio Translator
    credential = AzureKeyCredential(CREDENTIAL_TRANSLATOR)

    #Llamar a la función que traduce el texto y detecta idioma
    idioma_detectado, texto_traducido, idioma_destino = traducir_texto_ocr(credential, ENPOINT_URL_TRANSLATOR, texto)

    #Devolver los resultados de la traducción
    return idioma_detectado, texto_traducido, idioma_destino

#Función para analizar sentimiento, categorías y tema con Azure Language
def analisis(texto) -> str:
    #Obtener configuración del servicio de análisis de lenguaje
    ENPOINT_URL_LANGUAGE = current_app.config["ENPOINT_URL_LANGUAGE"]
    CREDENTIAL_LANGUAGE = current_app.config["CREDENTIAL_LANGUAGE"]

    #Crear credenciales para el servicio de lenguaje
    credential = AzureKeyCredential(CREDENTIAL_LANGUAGE)

    #Llamar a la función que realiza el análisis del texto
    resultado_texto = analizar_texto_azure(credential, ENPOINT_URL_LANGUAGE, texto)

    #Devolver los resultados principales del análisis
    return resultado_texto['sentimiento'], resultado_texto['confianza'], resultado_texto['categorias'], resultado_texto["etiqueta"]
