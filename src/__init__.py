#Rutas
from flask import Flask
from .prestamos.routes import prestamos
from .public.routes import main, sugerencias
from .usuarios.routes import login, usuarios, visitantes
from .libros.routes import libros
from .libros.routes import data_managment
from .logs.routes import logs_eliminados
from .usuarios.routes import data

app = Flask(__name__, static_folder="static")

def init_app(config):
    # Configuration
    app.config.from_object(config)
    # Blueprints
    app.register_blueprint(main.main)
    app.register_blueprint(libros.bp_libros)
    app.register_blueprint(data_managment.bp_data_managment)
    app.register_blueprint(prestamos.bp_prestamos)
    app.register_blueprint(usuarios.bp_usuarios)
    app.register_blueprint(visitantes.bp_visitantes)
    app.register_blueprint(login.bp_login)
    app.register_blueprint(sugerencias.bp_sugerencias)
    app.register_blueprint(logs_eliminados.bp_eliminados)
    app.register_blueprint(data.bp_datos)

    return app

