from flask import Blueprint, session, redirect, request,render_template,url_for, jsonify, send_file
from datetime import datetime
import math
from src.database.db_sqlite import conexion_BD
import pandas as panda
from src.libros.models import libros_model
from src.libros.models.libros_model import to_int

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
            datos = panda.read_excel(archivo, dtype={"CÓDIGO":str}).fillna("")
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
    progreso["error"] = ("Datos faltantes en fila: ")
    progreso["duplicados"] = ("Libro duplicado en fila: ")

    for index,row in datos.iterrows():
        Titulo = row['TITULO DEL LIBRO']
        NumeroPaginas = row['No. DE PAGINAS']
        ISBN = row['ISBN']
        tomo = (row['TOMO'])
        NumeroCopias = (row['No. DE COPIAS'])
        Autor = row['AUTOR']
        editorial = row['EDITORIAL']
        LugarPublicacion = row['LUGAR DE PUBLICACIÓN']
        AnoPublicacion = (row['AÑO'])
        SistemaDewey = (row['CÓDIGO'])
        notacion = row['NOTACIÓN INTERNA']

        if SistemaDewey == 0:
            SistemaDewey = "000"
        
        if not Titulo or not NumeroCopias or not NumeroPaginas or not SistemaDewey:
            progreso["error"] = progreso["error"] + (f"{index+2}, ")
            errores.append(row.to_dict())
            progreso["contador_errores"] += 1
        else:
            if Autor:
                #Separar Variable autor, en nombre y apellido
                autores = [a.strip() for a in Autor.split(",")]
                primer_autor = autores[0]
                partes = primer_autor.split()
                    
                if len(partes) > 1:
                    NombreAutor = partes[0]
                    ApellidoAutor = " ".join(partes[1:])
                else:
                    NombreAutor = primer_autor
                    ApellidoAutor = ""
                #Si existen varios autores, se agregan al apellido
                if len(autores) > 1:
                    ApellidoAutor += ", " + ", ".join(autores[1:])
            else:
                NombreAutor = ""
                ApellidoAutor = ""
            alerta = libros_model.registrar_libro(Titulo,to_int(NumeroPaginas),ISBN,to_int(tomo),to_int(NumeroCopias),NombreAutor,ApellidoAutor,editorial,LugarPublicacion,to_int(AnoPublicacion),(SistemaDewey))
            
            if alerta:
                progreso["duplicados"] = progreso["duplicados"] + (f"{index+2}, ")
                errores.append(row.to_dict())
                progreso["contador_errores"] += 1

        progreso["total"] = total
        progreso["actual"] = index + 1
        progreso["valor"] = round((((index + 1) / total) * 100),0)
        #sleep(0.1)
    progreso["error"] = progreso["error"].rstrip(", ") + "."

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