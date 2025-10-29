from flask import Blueprint, session,render_template, url_for
from math import floor
import json

main = Blueprint('main',__name__, template_folder="../templates")

# ----------------------------------------------------- PRINCIPAL ----------------------------------------------------- #
from src.public.models import public_model
from src.libros.models.libros_model import total_libros as _total_libros
@main.route("/", methods=["GET"])
def inicio():
    session.clear()

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
    total_libros = _total_libros("")
    total_libros = (floor(total_libros/10))*10

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

    return render_template('acercade.html')
