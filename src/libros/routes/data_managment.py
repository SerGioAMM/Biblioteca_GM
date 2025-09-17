from flask import Blueprint, session, redirect, request,render_template,url_for
from datetime import datetime
import math
from src.database.db_sqlite import conexion_BD

bp_data_managment = Blueprint('data_managment',__name__, template_folder="../templates")

# ----------------------------------------------------- IMPORTAR LIBROS ----------------------------------------------------- #

@bp_data_managment.route("/importar_libros", methods=["GET", "POST"])
def importar_libros():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada

    conexion = conexion_BD()
    query = conexion.cursor()
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        alerta = "Error al ingresar libro."
        return render_template("importar_libros.html", alerta=alerta) 
    finally:
        query.close()
        conexion.close()

    return render_template("importar_libros.html")


# ----------------------------------------------------- EXPORTAR LIBROS ----------------------------------------------------- #

@bp_data_managment.route("/exportar_libros", methods=["GET", "POST"])
def exportar_libros():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada

    conexion = conexion_BD()
    query = conexion.cursor()
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        alerta = "Error al ingresar libro."
        return render_template("exportar_libros.html", alerta=alerta) 
    finally:
        query.close()
        conexion.close()

    return render_template("exportar_libros.html")