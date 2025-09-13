from src.database.db_sqlite import conexion_BD
import sqlite3

def get_catalogo(libros_por_pagina,offset):
    conexion = conexion_BD()
    conexion.row_factory = sqlite3.Row
    query = conexion.cursor()

    #? Selecciona todos los libros disponibles
    # Consulta paginada
    query.execute("""
        select l.id_libro, titulo, tomo, ano_publicacion, ISBN, numero_paginas, numero_copias,
        sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor, e.editorial, n.notacion,lu.lugar, l.portada
        from Libros l
        join RegistroLibros r ON r.id_libro = l.id_libro
        join SistemaDewey sd ON sd.codigo_seccion = r.codigo_seccion 
        join notaciones n ON n.id_notacion = r.id_notacion
        join Autores a ON a.id_autor = n.id_autor
        join Editoriales e ON e.id_editorial = n.id_editorial
        join Lugares lu ON r.id_lugar = lu.id_lugar
        order by sd.codigo_seccion asc, Titulo asc
        LIMIT ? OFFSET ?
    """, (libros_por_pagina, offset))
    libros = query.fetchall()
    query.close()
    conexion.close()
    return [dict(fila) for fila in libros]

def get_catalogo_filtrado(libros_por_pagina,offset,filtro):
    conexion = conexion_BD()
    conexion.row_factory = sqlite3.Row
    query = conexion.cursor()

    #? Selecciona todos los libros disponibles
    # Consulta paginada
    query.execute(f"""
        select l.id_libro, Titulo, tomo, ano_publicacion, ISBN, numero_paginas, numero_copias,
        sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor, e.editorial, n.notacion, lu.lugar, l.portada
        from Libros l
        join RegistroLibros r on r.id_libro = l.id_libro
        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
        join notaciones n on n.id_notacion = r.id_notacion
        join Autores a on a.id_autor = n.id_autor
        join Editoriales e on e.id_editorial = n.id_editorial
        join Lugares lu on r.id_lugar = lu.id_lugar
        {filtro}
        order by sd.codigo_seccion asc,Titulo asc
        limit ? offset ?
    """, (libros_por_pagina, offset))
    libros = query.fetchall()
    query.close()
    conexion.close()
    return [dict(fila) for fila in libros]

def get_categorias():
    conexion = conexion_BD()
    query = conexion.cursor()
    query.execute("select * from SistemaDewey")
    categorias = query.fetchall()
    query.close()
    conexion.close()
    return categorias

def get_detalle_libro(id_libro):

    conexion = conexion_BD()
    conexion.row_factory = sqlite3.Row
    query = conexion.cursor()

    query.execute("""select l.id_libro, Titulo, tomo, ano_publicacion, ISBN, numero_paginas, numero_copias,
        sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor, e.editorial, n.notacion, lu.lugar , l.portada
        from Libros l
        join RegistroLibros r on r.id_libro = l.id_libro
        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
        join notaciones n on n.id_notacion = r.id_notacion
        join Autores a on a.id_autor = n.id_autor
        join Editoriales e on e.id_editorial = n.id_editorial
        join Lugares lu on r.id_lugar = lu.id_lugar 
        where l.id_libro = ?;""",(id_libro,))
    detalle = query.fetchall()
    query.close()
    conexion.close()

    return [dict(fila) for fila in detalle]

def get_destacados(seccion):
    conexion = conexion_BD()
    conexion.row_factory = sqlite3.Row
    query = conexion.cursor()
    query.execute(f"""select l.id_libro,count(l.id_libro) as cantidad
                        from Prestamos p
                        join libros l on p.id_libro = l.id_libro
                        join RegistroLibros r on r.id_libro = l.id_libro
                        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
                        where sd.codigo_seccion LIKE "{seccion}%"
                        group by p.id_libro
                        order by cantidad desc
                        limit 3;""")
    resultado = query.fetchall()
    query.close()
    conexion.close()
    return resultado

def total_libros(filtro):
    conexion = conexion_BD()
    query = conexion.cursor()
    query.execute(f"""
        select count(*) from Libros l
        join RegistroLibros r on r.id_libro = l.id_libro
        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
        join notaciones n on n.id_notacion = r.id_notacion
        join Autores a on a.id_autor = n.id_autor
        join Editoriales e on e.id_editorial = n.id_editorial
        join Lugares lu on r.id_lugar = lu.id_lugar
        {filtro}""")
    total = query.fetchone()[0]
    query.close()
    conexion.close()
    return total