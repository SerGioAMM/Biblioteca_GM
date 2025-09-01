from flask import Flask

#Rutas
from .routes import libros,login,prestamos,sugerencias,usuarios,main,logs_eliminados

app = Flask(__name__, template_folder="templates", static_folder="static")

def init_app(config):
    # Configuration
    app.config.from_object(config)
    # Blueprints
    app.register_blueprint(main.main)
    app.register_blueprint(libros.bp_libros)
    app.register_blueprint(prestamos.bp_prestamos)
    app.register_blueprint(usuarios.bp_usuarios)
    app.register_blueprint(login.bp_login)
    app.register_blueprint(sugerencias.bp_sugerencias)
    app.register_blueprint(logs_eliminados.bp_eliminados)

    return app

