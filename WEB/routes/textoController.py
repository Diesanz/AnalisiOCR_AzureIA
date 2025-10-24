from flask import Flask, request, jsonify, Blueprint, render_template, redirect, url_for, flash, current_app
from datetime import datetime, timedelta
import uuid # Para generar nombres de fichero únicos
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials import AzureNamedKeyCredential
import os
from dotenv import load_dotenv

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

    return render_template(
        'index.html',
        imagen_url=blob_url,
        texto_original="Chupa"
    )

