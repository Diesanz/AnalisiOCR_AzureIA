from flask import abort
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError


def analizar_texto_azure(credential, endpoint, texto: str):
    """
    Analiza un texto con Azure Text Analytics para obtener:
    - Sentimiento general del texto
    - Frases clave (categorías simples)

    Devuelve:
    - dict con 'sentimiento', 'confianza' y 'categorias' si todo va bien.
    - abort(400/403/500) con mensaje HTML si ocurre un error.
    """

    # --- Crear cliente ---
    try:
        client = TextAnalyticsClient(endpoint=endpoint, credential=credential)
    except Exception as e:
        abort(500, description=f"No se pudo crear el cliente de TextAnalytics. Detalle: {e}")

    texto = [texto]

    # --- Llamadas a la API de Azure ---
    try:
        # Análisis de sentimiento
        sentiment_response = client.analyze_sentiment(documents=texto)[0]
        sentimiento = sentiment_response.sentiment
        confianza = sentiment_response.confidence_scores

        # Extracción de frases clave
        categoria_response = client.extract_key_phrases(documents=texto)[0]
        categorias = categoria_response.key_phrases

        # Resultado estructurado
        return {
            "sentimiento": sentimiento,
            "confianza": {
                "positivo": round(confianza.positive, 3),
                "neutral": round(confianza.neutral, 3),
                "negativo": round(confianza.negative, 3)
            },
            "categorias": categorias
        }

    except ClientAuthenticationError as e:
        abort(403, description=f"Error de autenticación: {e.message}")
    except HttpResponseError as e:
        abort(400, description=f"Error en la respuesta de Azure (HTTP {e.status_code}): {e.message}")
    except Exception as e:
        abort(500, description=f"Error inesperado durante el análisis: {e}")
