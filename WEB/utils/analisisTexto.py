from flask import abort
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
import re

def analizar_texto_azure(credential, endpoint, texto: str):
    """
    Analiza un texto con Azure Text Analytics para obtener:
    - Sentimiento general del texto
    - Frases clave (categorías simples)

    Devuelve:
    - dict con 'sentimiento', 'confianza' y 'categorias' si todo va bien.
    - abort(400/403/500) con mensaje HTML si ocurre un error.
    """

    #--- Crear cliente ---
    try:
        client = TextAnalyticsClient(endpoint=endpoint, credential=credential)
    except Exception as e:
        abort(500, description=f"No se pudo crear el cliente de TextAnalytics. Detalle: {e}")

    texto = [texto]

    #--- Llamadas a la API de Azure ---
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
        abort(403, description=f"Error de autenticación: {e.message}")
    except HttpResponseError as e:
        abort(400, description=f"Error en la respuesta de Azure (HTTP {e.status_code}): {e.message}")
    except Exception as e:
        abort(500, description=f"Error inesperado durante el análisis: {e}")



def clasificar_por_temas(texto):
    """
    Clasifica un texto según su contenido en un tema predefinido.
    Devuelve el nombre del tema más probable o 'otro' si no hay coincidencias.
    """
    #Diccionario de temas y palabras clave
    TEMAS = {
        "queja": [
            "problema", "problemas", "error", "errores", "tarde", "malo", "mal", "defectuoso",
            "dañado", "reclamo", "queja", "fallo", "incidencia", "cancelado", "cancelada",
            "no funciona", "no sirve", "no llegó", "inaceptable", "mala atención",
            "decepcionado", "decepcionante", "pésimo", "frustrado", "demasiado caro",
            "horrible", "lento", "vergonzoso", "esperando", "nunca llegó", "no recibido"
        ],
        "elogio": [
            "excelente", "perfecto", "bueno", "buenísimo", "genial", "feliz", "maravilloso",
            "rápido", "satisfecho", "recomiendo", "gracias", "encantado", "fantástico",
            "increíble", "me encanta", "muy bien", "gran servicio", "contento", "eficiente",
            "amable", "profesional", "volveré", "cinco estrellas", "encantadora", "precioso",
            "bonito", "hermoso", "de diez", "todo correcto"
        ],
        "consulta": [
            "precio", "coste", "cuánto cuesta", "información", "cuánto vale", "dónde está",
            "disponible", "hay stock", "tiempo de entrega", "fecha", "horario", "política",
            "condiciones", "garantía", "oferta", "promoción", "cupón", "descuento",
            "tienen servicio", "todavía funciona", "cómo se usa", "me podrían decir"
        ],
        "pedido": [
            "pedido", "pedidos", "orden", "compra", "venta", "checkout", "carrito",
            "envío", "entrega", "repartidor", "mensajero", "transportista", "tracking",
            "transporte", "seguimiento", "retraso", "confirmación", "compra online",
            "hacer pedido", "procesando", "factura del pedido"
        ],
        "soporte": [
            "ayuda", "soporte", "técnico", "contraseña", "cuenta", "login", "error de acceso",
            "bloqueado", "usuario", "restablecer", "inicio de sesión", "no puedo entrar",
            "configurar", "asistencia", "bug", "crash", "fallo técnico", "problema con la app",
            "no carga", "pantalla en blanco"
        ],
        "facturacion": [
            "factura", "facturación", "pago", "cobro", "tarjeta", "recibo", "importe",
            "reembolso", "devolución", "transferencia", "saldo", "cuenta bancaria",
            "suscripción", "cancelar pago", "descuento", "cuota", "plan", "no me cobraron",
            "me cobraron doble", "problema con el pago"
        ],
        "producto": [
            "producto", "artículo", "material", "calidad", "tamaño", "color", "modelo",
            "defectuoso", "mal estado", "descripción", "foto", "contenido", "característica",
            "funciona", "rendimiento", "muestra", "sabor", "olor", "apariencia", "empaque"
        ],
        "sugerencia": [
            "mejorar", "sugerencia", "añadir", "idea", "recomendación", "sería bueno",
            "propongo", "actualizar", "cambiar", "más opciones", "optimizar",
            "me gustaría", "deberían tener", "sugiero", "podrían hacer", "agregar función"
        ],
        "marketing": [
            "publicidad", "anuncio", "promoción", "oferta", "newsletter", "email",
            "mensaje", "redes sociales", "facebook", "instagram", "tiktok", "campaña",
            "banner", "marketing", "recomendación", "publicar", "post"
        ],
        "experiencia_usuario": [
            "navegación", "interfaz", "diseño", "usabilidad", "lento", "rápido", "difícil",
            "fácil", "confuso", "intuitivo", "poco claro", "error de página", "botón",
            "clic", "pantalla", "visual", "diseño bonito", "interfaz moderna"
        ],
        "servicio_cliente": [
            "atención", "servicio", "contactar", "responder", "no atienden", "llamar",
            "respuesta", "chat", "correo", "amabilidad", "trato", "espera", "contestan",
            "soporte al cliente", "centro de ayuda", "servicio técnico", "agente"
        ],
        "politica_empresa": [
            "política", "condiciones", "devolución", "privacidad", "términos", "envíos",
            "cambios", "garantía", "reembolso", "cancelación", "seguridad", "protección de datos",
            "declaración legal", "confidencialidad"
        ],
        "plataforma": [
            "app", "aplicación", "móvil", "android", "ios", "windows", "actualización",
            "instalar", "descargar", "notificación", "bug", "crash", "versión", "navegador",
            "interfaz", "sistema", "error de login", "pantalla congelada"
        ],
        "logistica": [
            "envío", "paquete", "repartidor", "transporte", "entrega", "seguimiento",
            "camión", "mensajería", "recogida", "almacén", "tarde", "llegada",
            "entregaron", "no entregaron", "transportista", "hub", "centro de distribución"
        ]
    }

    texto = " ".join(texto).lower()
    coincidencias = {}

    #Buscar coincidencias en cada tema
    for tema, palabras in TEMAS.items():
        for palabra in palabras:
            if re.search(rf"\b{re.escape(palabra)}\b", texto):
                coincidencias[tema] = coincidencias.get(tema, 0) + 1

    #Si hay coincidencias, devuelve el tema con más matches
    if coincidencias:
        return max(coincidencias, key=coincidencias.get)
    else:
        return "otro"