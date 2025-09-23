from src.database.db_sqlite import conexion_BD, dict_factory
import sqlite3

def get_destacados(seccion):
    conexion = conexion_BD()
    conexion.row_factory = dict_factory
    query = conexion.cursor()
    query.execute(f"""select l.id_libro,count(l.id_libro) as cantidad, n.notacion, l.Titulo, a.nombre_autor, a.apellido_autor, l.ano_publicacion, sd.codigo_seccion, sd.seccion, l.numero_copias
                        from Prestamos p
                        join libros l on p.id_libro = l.id_libro
                        join RegistroLibros r on r.id_libro = l.id_libro
                        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
                        join notaciones n on n.id_notacion = r.id_notacion
                        join Autores a on a.id_autor = n.id_autor
                        where sd.codigo_seccion LIKE "{seccion}%"
                        group by p.id_libro
                        order by cantidad desc
                        limit 3;""")
    libros = query.fetchall()
    query.close()
    conexion.close()
    return libros


def get_aleatorios(seccion,cantidad):
    conexion = conexion_BD()
    conexion.row_factory = dict_factory
    query = conexion.cursor()
    query.execute(f"""SELECT l.id_libro, 0 AS cantidad, n.notacion, l.Titulo, a.nombre_autor, a.apellido_autor, l.ano_publicacion, sd.codigo_seccion, sd.seccion, l.numero_copias
                        FROM Libros l
                        JOIN RegistroLibros r ON r.id_libro = l.id_libro
                        JOIN SistemaDewey sd ON sd.codigo_seccion = r.codigo_seccion
                        JOIN Notaciones n ON n.id_notacion = r.id_notacion
                        JOIN Autores a ON a.id_autor = n.id_autor
                        where sd.codigo_seccion LIKE "{seccion}%"
                        order by RANDOM()
                        limit {cantidad};""")
    aleatorios = query.fetchall()
    query.close()
    conexion.close()
    return aleatorios

def get_nuevos():
    conexion = conexion_BD()
    conexion.row_factory = dict_factory
    query = conexion.cursor()
    query.execute("""SELECT l.id_libro, 0 AS cantidad, n.notacion, l.Titulo, a.nombre_autor, a.apellido_autor, l.ano_publicacion, sd.codigo_seccion, sd.seccion, l.numero_copias
                        FROM Libros l
                        JOIN RegistroLibros r ON r.id_libro = l.id_libro
                        JOIN SistemaDewey sd ON sd.codigo_seccion = r.codigo_seccion
                        JOIN Notaciones n ON n.id_notacion = r.id_notacion
                        JOIN Autores a ON a.id_autor = n.id_autor
                        order by l.id_libro desc
                        limit 12""")
    nuevos = query.fetchall()
    query.close()
    conexion.close()
    return nuevos