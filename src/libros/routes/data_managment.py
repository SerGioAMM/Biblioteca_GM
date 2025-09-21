from flask import Blueprint, session, redirect, request,render_template,url_for, jsonify, send_file
from datetime import datetime
import math
from src.database.db_sqlite import conexion_BD
import pandas as panda

bp_data_managment = Blueprint('data_managment',__name__, template_folder="../templates")

# ----------------------------------------------------- IMPORTAR LIBROS ----------------------------------------------------- #
from time import sleep
import threading
from io import BytesIO
progreso = {"valor":0, "total":0, "actual":0, "error": "", "contador_errores":0}
errores = []


@bp_data_managment.route("/importar_libros", methods=["GET", "POST"])
def importar_libros():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    global progreso 
    progreso["valor"] = 0
    progreso["total"] = 0
    progreso["actual"] = 0
    progreso["contador_errores"] = 0
    datos = ''
    if request.method == "POST":
        if "archivo_excel" not in request.files:
            return render_template("importar_libros.html", alerta="No se subió archivo")
        archivo = request.files["archivo_excel"]
        if archivo.filename == "":
            return render_template("importar_libros.html", alerta="Nombre de archivo vacío")
        try:
            datos = panda.read_excel(archivo)
            total = len(datos)
            # Lanzar la importación en un hilo aparte
            hilo = threading.Thread(target=importar, args=(datos,total))
            hilo.start()
        except Exception as e:
            print(f"Error: {e}")
            alerta = "Error al leer el archivo."
            return render_template("importar_libros.html", alerta=alerta) 

    return render_template("importar_libros.html", datos=datos)


def importar(datos,total):
    global errores
    errores = []
    progreso["error"] = ("DATOS INCORRECTOS EN FILA: ")
    for index,row in datos.iterrows():
        autor = row['AUTOR']
        titulo = row['TITULO DEL LIBRO']
        lugar = row['LUGAR DE PUBLICACIÓN']
        editorial = row['EDITORIAL']
        anio = row['AÑO']
        num_paginas = row['No. DE PAGINAS']
        ISBN = row['ISBN']
        tomo = row['TOMO']
        seccion = row['CÓDIGO']
        notacion = row['NOTACIÓN INTERNA']
        num_copias = row['No. DE COPIAS']
        
        if(panda.isna(titulo)):
            progreso["error"] = progreso["error"] + (f"{index+2}, ")
            errores.append(row.to_dict())
            progreso["contador_errores"] += 1
        progreso["total"] = total
        progreso["actual"] = index + 1
        progreso["valor"] = round((((index + 1) / total) * 100),0)
        #sleep(0.1)

@bp_data_managment.route("/progreso")
def get_progreso():
    return jsonify(progreso)

@bp_data_managment.route("/descargar_errores")
def descargar_errores():
    if not errores:
        return "No hay errores para descargar", 400
    
    output = BytesIO()
    excel = panda.DataFrame(errores)
    excel.to_excel(output, index=False)
    output.seek(0) 

    return send_file(
        output,
        as_attachment=True,
        download_name="errores.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )



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