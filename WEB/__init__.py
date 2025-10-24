from flask import Flask
import os

def create_app():
    app = Flask(__name__, template_folder='templates')

    #Secret key
    app.secret_key = os.getenv("CLAVE_APP")
    if not app.secret_key:
        raise RuntimeError("CLAVE_APP no definida en el entorno")

    #Lista de variables críticas
    required_env_vars = {
        "NOMBRE_CUENTA_ALMACENAMIENTO": None,
        "CREDENCTIAL_BLOB": None,
        "ENPOINT_URL_VISION": None,
        "SUBSCRIPTION_ID": None,
        "ENPOINT_URL_TRANSLATOR": None,
        "CREDENTIAL_TRANSLATOR": None,
        "ENPOINT_URL_LANGUAGE": None,
        "CREDENTIAL_LANGUAGE": None
    }

    # Validar y asignar
    for var in required_env_vars:
        value = os.getenv(var)
        if not value:
            raise RuntimeError(f"Variable de entorno {var} no definida")
        app.config[var] = value

    # Importar y registrar Blueprints
    try:
        from .routes.textoController import controller
        app.register_blueprint(controller)
    except ImportError as e:
        raise ImportError(f"No se pudo importar el blueprint: {e}")

    print("Iniaciando la app....")
    return app
