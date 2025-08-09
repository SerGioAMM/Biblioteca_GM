from flask import Flask

#Rutas
from .routes import libros,login,prestamos,sugerencias,usuarios,main

app = Flask(__name__, template_folder="templates", static_folder="static")

def init_app(config):
    # Configuration
    app.config.from_object(config)
    # Blueprints
    app.register_blueprint(main.main, url_prefix='/')
    app.register_blueprint(libros.bp_libros, url_prefix='/libros')
    app.register_blueprint(prestamos.bp_prestamos, url_prefix='/prestamos')
    app.register_blueprint(usuarios.bp_usuarios, url_prefix='/usuarios')
    app.register_blueprint(login.bp_login)
    # Registering the Sugerencias blueprint
    app.register_blueprint(sugerencias.bp_sugerencias, url_prefix='/sugerencias')

    return app

