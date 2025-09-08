from flask import Blueprint, session,render_template, url_for
from src.database.db_sqlite import conexion_BD
from math import floor
import json


main = Blueprint('main',__name__, template_folder="../templates")

# ----------------------------------------------------- PRINCIPAL ----------------------------------------------------- #
from src.public.models import public_model
@main.route("/", methods=["GET"])
def inicio():
    session.clear()

    conexion = conexion_BD()
    query = conexion.cursor()
    secciones_principales = [
        "Generalidades",
        "Filosofia - Psicología",
        "Religión",
        "Estudios Sociales",
        "Lenguas e Idioma",
        "Ciencias Naturales - Matemáticas",
        "Tecnología - Salud - Cocina",
        "Arte - Deporte - Música",
        "Literatura",
        "Historia - Geografía - Biografía",
        "Recién añadidos"]

    libros_destacados = []
    for i in range(11):
        contador_aleatorios = 0
        destacados = public_model.get_destacados(i)
        resultado = {
                    "seccion": secciones_principales[i],
                    "destacados": destacados,
                    "aleatorios": [],
                    "nuevos":[]
            }
        while (((len(destacados) + contador_aleatorios) < 6) and (i<10)): contador_aleatorios += 1
        aleatorios = public_model.get_aleatorios(i,contador_aleatorios)
        resultado["aleatorios"] = aleatorios    
        libros_destacados.append(resultado)
    
    #?Recien aniadidos
    nuevos = public_model.get_nuevos()
    resultado["nuevos"] = nuevos

    #? Conteo de total de libros para la pagina principal
    query.execute("select count(*) from libros")
    total_libros = query.fetchone()[0]
    total_libros = (floor(total_libros/10))*10

    query.close()
    conexion.close()

    #Cargar actividades desde JSON
    with open("src/database/actividades.json", encoding="utf-8") as archivo:
        actividades = json.load(archivo)

    #Agregar formato url_for a las imagenes
    for act in actividades:
        act["imagen"] = url_for('static', filename=act["imagen"])

    return render_template("index.html",libros_destacados=libros_destacados, total_libros=total_libros, actividades=actividades)

# ----------------------------------------------------- ACERCA DE ----------------------------------------------------- #

@main.route("/acercade")
def acercade():

    return render_template('nosotros.html')
