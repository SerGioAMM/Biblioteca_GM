from flask import Blueprint, session,render_template, url_for
from src.database.db_sqlite import conexion_BD
from math import floor
import json

main = Blueprint('main',__name__)

# ----------------------------------------------------- PRINCIPAL ----------------------------------------------------- #

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
        "Historia - Geografía - Biografía"]

    libros_destacados = []
    for i in range(10):
        contador_aleatorios = 0
        query.execute(f"""select l.id_libro,count(l.id_libro) as cantidad, n.notacion, l.Titulo, a.nombre_autor, a.apellido_autor, l.ano_publicacion, sd.codigo_seccion, sd.seccion, l.numero_copias
                        from Prestamos p
                        join libros l on p.id_libro = l.id_libro
                        join RegistroLibros r on r.id_libro = l.id_libro
                        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
                        join notaciones n on n.id_notacion = r.id_notacion
                        join Autores a on a.id_autor = n.id_autor
                        where sd.codigo_seccion LIKE "{i}%"
                        group by p.id_libro
                        order by cantidad desc
                        limit 3;""")
        destacados = query.fetchall()
        resultado = {
                    "seccion": secciones_principales[i],
                    "destacados": destacados,
                    "aleatorios": []
            }
        print(resultado)
        while (len(destacados) + contador_aleatorios) < 6: contador_aleatorios += 1
        query.execute(f"""SELECT l.id_libro, 0 AS cantidad, n.notacion, l.Titulo, a.nombre_autor, a.apellido_autor, l.ano_publicacion, sd.codigo_seccion, sd.seccion, l.numero_copias
                        FROM Libros l
                        JOIN RegistroLibros r ON r.id_libro = l.id_libro
                        JOIN SistemaDewey sd ON sd.codigo_seccion = r.codigo_seccion
                        JOIN Notaciones n ON n.id_notacion = r.id_notacion
                        JOIN Autores a ON a.id_autor = n.id_autor
                        where sd.codigo_seccion LIKE "{i}%"
                        order by RANDOM()
                        limit {contador_aleatorios};""")
        aleatorios = query.fetchall()
        resultado["aleatorios"] = aleatorios    
        libros_destacados.append(resultado)
    
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
