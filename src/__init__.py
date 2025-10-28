#Rutas
from flask import Flask, session, redirect, url_for, request
from datetime import datetime, timedelta
from .prestamos.routes import prestamos
from .public.routes import main, sugerencias, bienvenida
from .usuarios.routes import login, usuarios, visitantes
from .libros.routes import libros
from .libros.routes import data_managment
from .logs.routes import logs_eliminados
from .usuarios.routes import data
from .opiniones.routes import opiniones

app = Flask(__name__, static_folder="static")

def init_app(config):
    # Configuration
    app.config.from_object(config)
    
    # Middleware para verificar timeout de sesión
    @app.before_request
    def check_session_timeout():
        # Rutas excluidas del timeout (públicas y login)
        excluded_paths = ['/login', '/logout', '/', '/static/', '/acercade', 
                        '/buscar_libro', '/detalle_libro/', '/libros', '/crear_opinion']
        
        # Verificar si la ruta actual está excluida
        is_excluded = any(request.path.startswith(path) for path in excluded_paths)
        
        # Si el usuario está logueado y no es una ruta excluida
        if 'usuario' in session:
            # Hacer la sesión permanente para que use PERMANENT_SESSION_LIFETIME
            session.permanent = True
            
            # Verificar última actividad
            last_activity = session.get('last_activity')
            if last_activity:
                last_activity_time = datetime.fromisoformat(last_activity)
                now = datetime.now()
                inactive_time = now - last_activity_time
                # Si han pasado más de 2 minutos de inactividad #! Cambiar a timedelta(minutes=15) para 15 minutos
                if inactive_time > timedelta(minutes=2):
                    # Limpiar sesión y redirigir a login
                    session.clear()
                    return redirect(url_for('login.login', alerta='Sesión expirada por inactividad'))
            
            # Actualizar última actividad
            session['last_activity'] = datetime.now().isoformat()
        
        # Si está en una ruta pública, asegurar que la sesión no sea permanente
        elif 'usuario' not in session:
            session.permanent = False
    
    # Blueprints
    app.register_blueprint(main.main)
    app.register_blueprint(libros.bp_libros)
    app.register_blueprint(data_managment.bp_data_managment)
    app.register_blueprint(prestamos.bp_prestamos)
    app.register_blueprint(usuarios.bp_usuarios)
    app.register_blueprint(visitantes.bp_visitantes)
    app.register_blueprint(login.bp_login)
    app.register_blueprint(sugerencias.bp_sugerencias)
    app.register_blueprint(bienvenida.bp_bienvenida)
    app.register_blueprint(logs_eliminados.bp_eliminados)
    app.register_blueprint(data.bp_datos)
    app.register_blueprint(opiniones.bp_opiniones)

    return app

