from flask import Blueprint, session, redirect, request,render_template,url_for
from src.database.db_sqlite import conexion_BD
from src.utils.logger import logger
import traceback
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from src.usuarios.routes.usuarios import crear_notificacion


bp_login = Blueprint('login',__name__, template_folder="../templates")

# ----------------------------------------------------- LOGOUT ----------------------------------------------------- #

@bp_login.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.inicio"))

# ----------------------------------------------------- LOGIN ----------------------------------------------------- #

@bp_login.route("/login", methods=["GET", "POST"])
def login():
    try:
        alerta = request.args.get("alerta", "")

        conexion = conexion_BD()
        query = conexion.cursor()
        
        if request.method == "POST":
            usuario = request.form["usuario"]
            password = request.form["password"]

            query.execute("""SELECT a.id_administrador, a.usuario, r.rol, e.estado, a.login_fail, 
                            a.tiempo_bloqueo, a.contrasena 
                            FROM Administradores a 
                            JOIN roles r ON a.id_rol = r.id_rol 
                            JOIN estados_administradores e ON a.id_estado = e.id_estado 
                            WHERE a.usuario = ?
                        """, (usuario,))
            user_data = query.fetchone()
            if user_data:
                id_admin, usuario_db, rol, estado, login_fail, tiempo_bloqueo, stored_password = user_data
                ahora = datetime.now()
                
                if tiempo_bloqueo:
                    if isinstance(tiempo_bloqueo, str):
                        tiempo_bloqueo = datetime.fromisoformat(tiempo_bloqueo)
                if tiempo_bloqueo and tiempo_bloqueo > ahora:
                    tiempo_restante = (tiempo_bloqueo - ahora).seconds
                    minutos = tiempo_restante // 60
                    segundos = tiempo_restante % 60
                    alerta = f"Cuenta bloqueada temporalmente por intentos fallidos. Intente de nuevo en {minutos}:{segundos:02d}."
                    logger.add_to_log("error", f"{alerta} - Usuario: {usuario}")
                    #return render_template("login.html", alerta=alerta)
                else:
                    if tiempo_bloqueo and tiempo_bloqueo <= ahora:
                        query.execute("""
                            UPDATE administradores 
                            SET login_fail = 0, tiempo_bloqueo = NULL 
                            WHERE id_administrador = ?
                        """, (id_admin,))
                        login_fail = 0
                        tiempo_bloqueo = None
                    if estado == "Activo" and check_password_hash(stored_password, password):
                        session["id_administrador"] = id_admin
                        session["usuario"] = usuario_db
                        session["rol"] = rol
                        query.execute("""
                            UPDATE administradores 
                            SET login_fail = 0, tiempo_bloqueo = NULL 
                            WHERE id_administrador = ?
                        """, (id_admin,))
                        conexion.commit()
                        return redirect(url_for('bienvenida.bienvenida'))
                    else:
                        if estado != "Activo":
                            alerta = "Usuario inactivo, contacte al administrador"
                        else:
                            new_fails = (login_fail or 0) + 1
                            alerta = f"Datos incorrectos, intentos fallidos: {new_fails}"
                            if new_fails >= 3:
                                lock_until = ahora + timedelta(minutes=3)  # Bloqueo de 3 minutos
                                query.execute("""
                                    UPDATE administradores 
                                    SET login_fail = ?, tiempo_bloqueo = ? 
                                    WHERE id_administrador = ?
                                """, (new_fails, lock_until, id_admin))
                                conexion.commit()
                                alerta = "Demasiados intentos fallidos. Su cuenta está bloqueada por 3 minutos."
                                crear_notificacion(f"El usuario {usuario} ha sido bloqueado temporalmente por intentos fallidos de inicio de sesión.")
                            else:
                                query.execute("""
                                    UPDATE administradores 
                                    SET login_fail = ? 
                                    WHERE id_administrador = ?
                                """, (new_fails, id_admin))
                                conexion.commit()

                        logger.add_to_log("error", f"{alerta} - Usuario: {usuario}")
                        session["rol"] = "false"
            else:
                alerta = "Datos incorrectos"
                session["rol"] = "false"
                logger.add_to_log("error", f"{alerta} - Usuario: {usuario}")

    except Exception as ex:
        logger.add_to_log("error", str(ex))
        logger.add_to_log("error", traceback.format_exc())
    finally:
        query.close()
        conexion.close()

    return render_template("login.html", alerta=alerta)
