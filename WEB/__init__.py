from flask import Flask, render_template

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.secret_key = 'clave-super-secreta-123'
    
    # Importas el Blueprint de autentificar
    from .routes.autentificar import autentificar_usuarios
    from .routes.carritoController import carrito
    from .routes.menuController import menu
    from .routes.pedidoController import pedido
    from .routes.productosController import producto

    app.register_blueprint(autentificar_usuarios)
    app.register_blueprint(carrito)
    app.register_blueprint(menu)
    app.register_blueprint(pedido)
    app.register_blueprint(producto)

    register_error_handlers(app)

    return app

def register_error_handlers(app):
    @app.errorhandler(400)
    def error400(error):
        return render_template('error.html', error=400, mensaje="No se pudo procesar la petición."), 400

    @app.errorhandler(401)
    def error401(error):
        return render_template('error.html', error=401, mensaje="Credenciales incorrectas"), 401

    @app.errorhandler(404)
    def error404(error):
        return render_template('error.html', error=404, mensaje="Página no encontrada."), 404

    @app.errorhandler(500)
    def error500(error):
        return render_template('error.html', error=500, mensaje="Ha ocurrido un error interno en el servidor."), 500