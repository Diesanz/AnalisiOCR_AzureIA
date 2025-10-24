from flask import abort
from azure.ai.translation.text import TextTranslationClient
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError

def traducir_texto_ocr(credential, endpoint, texto_original: str, idioma_destino: str = "es"):
    """
    Traduce un texto usando el servicio Azure Translator.

    Devuelve:
    - idioma_detectado (str): Idioma de origen detectado por Azure.
    - traduccion (str): Texto traducido.
    - idioma_destino (str): Idioma final de la traducción.

    En caso de error, aborta con código HTTP adecuado y mensaje.
    """

    # --- Crear el cliente ---
    try:
        client = TextTranslationClient(
            credential=credential,
            endpoint=endpoint,
        )
    except Exception as e:
        abort(500, description=f"No se pudo crear el cliente de TextTranslationClient. Detalle: {e}")

    # --- Llamada al servicio de traducción ---
    try:
        response = client.translate(
            body=[texto_original],
            to_language=[idioma_destino]
        )

        if not response or not response[0].translations:
            return "No se ha detectado el idioma", "Sin traducción disponible"

        translate_result = response[0]
        idioma_detectado = translate_result.detected_language.language if translate_result.detected_language else "desconocido"

        # Recopilar todas las traducciones devueltas
        traducciones = []
        for t in translate_result.translations:
            traducciones.append(t.text)
            
        return idioma_detectado, " ".join(traducciones)

    except ClientAuthenticationError as e:
        abort(403, description=f"Error de autenticación en Azure Translator: {e.message}")
    except HttpResponseError as e:
        abort(400, description=f"Error en la respuesta de Azure Translator (HTTP {e.status_code}): {e.message}")
    except Exception as e:
        abort(500, description=f"Error inesperado durante la traducción: {e}")
