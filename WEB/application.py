from flask import Flask, render_template
import os
from dotenv import load_dotenv

#Función para crear la app
def create_app():
    app = Flask(__name__, template_folder='templates')
    load_dotenv()
    #Clave secreta
    app.secret_key = "clave-secreta-6734"
    if not app.secret_key:
        raise RuntimeError("CLAVE_APP no definida en el entorno")

    #Variables críticas requeridas
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

    #Validar y asignar variables de entorno
    for var in required_env_vars:
        value = os.getenv(var)
        if not value:
            raise RuntimeError(f"Variable de entorno {var} no definida")
        app.config[var] = value

    #Registrar Blueprint
    try:
        from routes.textoController import controller
        app.register_blueprint(controller)
    except ImportError as e:
        raise ImportError(f"No se pudo importar el blueprint: {e}")

    return app


#Crear la app
app = create_app()


#Ruta principal
@app.route('/')
def index():
    """
    Muestra la página principal (index.html)
    con el selector de fichero.
    """
    return render_template('index.html')


#Ejecutar la app con modo debug True, en producción poner a false
if __name__ == '__main__':
    app.run(debug=True)
