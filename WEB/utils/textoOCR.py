from flask import abort
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures

def obtener_texto_ocr(credential, endpoint, image_url: str = None):
    """
    Obtiene el texto de una imagen mediante OCR con Azure AI Vision.

    Devuelve:
    - str con el texto extraído si todo va bien.
    - abort(400/403/500) con mensaje HTML si ocurre un error.
    """

    #--- Crear el cliente ---
    try:
        client = ImageAnalysisClient(endpoint=endpoint, credential=credential)
    except Exception as e:
        # Error crítico: no se pudo crear el cliente
        abort(500, description=f"No se pudo crear el cliente de ImageAnalysis. Detalle: {e}")

    #--- Llamada a la API de Azure ---
    try:
        result = client.analyze_from_url(
            image_url=image_url,
            visual_features=[VisualFeatures.READ]
        )
    except ClientAuthenticationError as e:
        abort(403, description=f"Error de autenticación: {e.message}")
    except HttpResponseError as e:
        abort(400, description=f"Error en la respuesta de Azure (HTTP {e.status_code}): {e.message}")
    except Exception as e:
        abort(500, description=f"Error inesperado durante el análisis: {e}")

    #--- Procesamiento del resultado ---
    if result.read is not None and result.read.blocks:
        texto_completo = ""
        for block in result.read.blocks:
            for line in block.lines:
                texto_completo += line.text + "\n"
        return texto_completo.strip()
    else:
        #No se detectó texto
        return " "
