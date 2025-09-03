from flask import Blueprint, session, redirect, request,render_template,url_for
from src.database.db_sqlite import conexion_BD
from src.utils.logger import logger
import traceback

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
        alerta= request.args.get("alerta", "")

        conexion = conexion_BD()
        query = conexion.cursor()
        
        if request.method == "POST":
            usuario = request.form["usuario"]
            password = request.form["password"]

            query.execute("""Select a.id_administrador,a.usuario,r.rol from Administradores a 
                        Join roles r on a.id_rol = r.id_rol
                        where usuario = ? and contrasena = ?""", (usuario, password))
            login_usuario = query.fetchone()

            if (login_usuario):
                # Guardar datos en session
                session["id_administrador"] = login_usuario[0] 
                session["usuario"] = login_usuario[1]
                session["rol"] = login_usuario[2]         

                return redirect(url_for('prestamos.prestamos'))
            else:
                alerta = "Datos incorrectos"
                session["rol"] = "false"
                logger.add_to_log("error", str(f"{alerta} - Usuario: {usuario}"))
    except Exception as ex:
        logger.add_to_log("error", str(ex))
        logger.add_to_log("error", traceback.format_exc())
    
    query.close()
    conexion.close()

    return render_template("login.html", alerta = alerta)
