from flask import Blueprint, session,render_template
from src.database.db_sqlite import conexion_BD

main = Blueprint('main',__name__)

# ----------------------------------------------------- PRINCIPAL ----------------------------------------------------- #

@main.route("/", methods=["GET"])
def inicio():
    session.clear()

    conexion = conexion_BD()
    query = conexion.cursor()
    
    query.execute("""select l.id_libro,count(l.id_libro) as cantidad, n.notacion, l.Titulo, a.nombre_autor, a.apellido_autor, l.ano_publicacion, sd.codigo_seccion, sd.seccion, l.numero_copias
                    from Prestamos p
					join libros l on p.id_libro = l.id_libro
                    join RegistroLibros r on r.id_libro = l.id_libro
                    join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
                    join notaciones n on n.id_notacion = r.id_notacion
                    join Autores a on a.id_autor = n.id_autor
                    group by p.id_libro
                    order by cantidad desc
                    limit 4;""")
    libros_destacados = query.fetchall()

    query.close()
    conexion.close()

    return render_template("index.html",libros_destacados=libros_destacados)

# ----------------------------------------------------- ACERCA DE ----------------------------------------------------- #

@main.route("/acercade")
def acercade():

    return render_template('nosotros.html')
