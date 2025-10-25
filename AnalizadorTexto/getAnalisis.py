import re
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError


def analizar_texto_azure(credential, endpoint, texto: str):
    """
    Analiza un texto con Azure Text Analytics para obtener:
    - Sentimiento general del texto
    - Frases clave (categorías simples)
    - Clasificación por tema
    """
    try:
        client = TextAnalyticsClient(endpoint=endpoint, credential=credential)
    except Exception as e:
        raise RuntimeError(f"No se pudo crear el cliente de TextAnalytics: {e}")

    if isinstance(texto, str):
        texto = [texto]
    elif isinstance(texto, list):
        texto = [t for t in texto if isinstance(t, str)]
    else:
        raise ValueError("El parámetro 'texto' debe ser una cadena o una lista de cadenas")

    try:
        # Análisis de sentimiento
        sentiment_response = client.analyze_sentiment(documents=texto)[0]
        sentimiento = sentiment_response.sentiment
        confianza = sentiment_response.confidence_scores

        # Extracción de frases clave
        categoria_response = client.extract_key_phrases(documents=texto)[0]
        categorias = categoria_response.key_phrases

        # Clasificación simple
        etiqueta = clasificar_por_temas(categorias)

        # Resultado estructurado
        return {
            "sentimiento": sentimiento,
            "confianza": {
                "positivo": round(confianza.positive, 3),
                "neutral": round(confianza.neutral, 3),
                "negativo": round(confianza.negative, 3)
            },
            "categorias": categorias,
            "etiqueta": etiqueta
        }

    except ClientAuthenticationError as e:
        raise PermissionError(f"Error de autenticación con Azure: {e}")
    except HttpResponseError as e:
        raise ConnectionError(f"Error HTTP {e.status_code} al contactar Azure: {e}")
    except Exception as e:
        raise RuntimeError(f"Error inesperado durante el análisis: {e}")


def clasificar_por_temas(texto):
    """
    Clasifica un texto según su contenido en un tema predefinido.
    Devuelve el nombre del tema más probable o 'otro' si no hay coincidencias.
    """
    TEMAS = {
        "rendimiento": [
            "velocidad", "potencia", "rendimiento", "lag", "fluidez", "eficiencia",
            "rapidez", "procesador", "frames", "fps", "tiempo de carga", "respuesta"
        ],
        "calidad_de_fabricacion": [
            "calidad", "materiales", "resistente", "acabado", "construcción", "durabilidad",
            "robusto", "plástico", "metal", "carcasa", "fragil", "debil"
        ],
        "bateria_y_energia": [
            "batería", "autonomía", "carga", "cargador", "duración", "consumo", "energía",
            "powerbank", "rapida", "lenta", "enchufe", "adaptador"
        ],
        "pantalla_y_visualizacion": [
            "pantalla", "resolución", "brillo", "color", "contraste", "ángulo de visión",
            "oled", "lcd", "display", "nitidez", "reflejos"
        ],
        "audio_y_sonido": [
            "sonido", "audio", "volumen", "altavoz", "auriculares", "ruido",
            "graves", "agudos", "microfono", "claridad", "ecualizador"
        ],
        "facilidad_de_uso": [
            "fácil", "difícil", "intuitivo", "configuración", "manual", "menú",
            "interfaz", "instalación", "plug and play", "conectar", "actualizar"
        ],
        "conectividad_y_compatibilidad": [
            "wifi", "bluetooth", "usb", "hdmi", "conexion", "inalámbrico",
            "sincronizar", "app", "compatibilidad", "drivers", "red"
        ],
        "software_y_funciones": [
            "software", "firmware", "aplicación", "funciones", "opciones",
            "errores", "bugs", "actualización", "rendimiento del sistema",
            "interfaz gráfica"
        ],
        "precio_y_valor": [
            "precio", "barato", "caro", "oferta", "valor", "calidad-precio",
            "inversión", "compensa", "coste", "económico"
        ],
        "diseno_y_estetica": [
            "diseño", "color", "tamaño", "peso", "ergonomía", "estética",
            "compacto", "portátil", "elegante", "moderno"
        ],
        "atencion_al_cliente_y_envio": [
            "envío", "entrega", "paquete", "servicio", "soporte", "garantía",
            "reclamación", "atención", "Amazon", "reembolso", "devolución"
        ],
        "experiencia_general": [
            "satisfecho", "recomendado", "expectativas", "problemas", "feliz",
            "decepcionado", "defectuoso", "excelente", "malo", "perfecto"
        ]
    }


    texto = " ".join(texto).lower()
    coincidencias = {}

    for tema, palabras in TEMAS.items():
        for palabra in palabras:
            if re.search(rf"\b{re.escape(palabra)}\b", texto):
                coincidencias[tema] = coincidencias.get(tema, 0) + 1

    return max(coincidencias, key=coincidencias.get) if coincidencias else "otro"