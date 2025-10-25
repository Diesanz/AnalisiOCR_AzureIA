"""
Módulo encargado de traducir texto utilizando el servicio Azure Translator Text.

Define la función `traducir_texto_ocr`, que recibe un texto (por ejemplo, obtenido mediante OCR)
y lo traduce al idioma deseado utilizando las credenciales y el endpoint de Azure.
"""

from azure.ai.translation.text import TextTranslationClient
from azure.core.exceptions import HttpResponseError


def traducir_texto_ocr(credential, endpoint, texto_original: str, idioma_destino: str = "es"):
    """
    Traduce un texto usando el servicio Azure Translator.

    Parámetros:
    - credential: Credencial válida (por ejemplo, AzureKeyCredential).
    - endpoint (str): URL del endpoint del servicio Translator.
    - texto_original (str): Texto que se desea traducir.
    - idioma_destino (str, opcional): Idioma al que se traducirá el texto (por defecto español "es").

    Devuelve:
    - idioma_detectado (str): Idioma de origen detectado por Azure.
    - traduccion (str): Texto traducido.
    - idioma_destino (str): Idioma final de la traducción.
    """
    try:
        """Intentamos crear el cliente de traducción con las credenciales y endpoint proporcionados"""
        client = TextTranslationClient(
            credential=credential,
            endpoint=endpoint,
        )
    except Exception as e:
        """Error al crear el cliente (posible fallo en credenciales o endpoint incorrecto)"""
        print("Error: No se pudo crear el cliente de TextTranslationClient. ¿Endpoint o credencial incorrectos?")
        print(f"Detalle: {e}")
        return None, None

    try:
        """Realizamos la llamada al servicio de traducción"""
        response = client.translate(
            body=[texto_original],
            to_language=[idioma_destino]
        )

        """Verificamos que la respuesta sea válida y contenga traducciones"""
        if not response or not response[0].translations:
            print("No se obtuvo respuesta o no hay traducciones.")
            return None, None, None

        """Procesamos los resultados obtenidos"""
        translate_result = response[0]
        idioma_detectado = translate_result.detected_language.language if translate_result.detected_language else "desconocido"

        """Recopilamos todas las traducciones devueltas por el servicio"""
        traducciones = []
        if idioma_detectado != "desconocido":
            for t in translate_result.translations:
                traducciones.append(t.text)
            
            idioma_destino = t.to

        """Devolvemos el idioma detectado, el texto traducido concatenado y el idioma destino"""
        return idioma_detectado, " ".join(traducciones), idioma_destino

    except HttpResponseError as e:
        """Error devuelto por el servicio Azure (problemas con la solicitud HTTP)"""
        print(f"Error de Azure al traducir: {e.message}")
        return None, None
    except Exception as e:
        """Cualquier otro error no controlado"""
        print(f"Error inesperado en la traducción: {e}")
        return None, None
