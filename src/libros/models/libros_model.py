from src.database.db_sqlite import conexion_BD, dict_factory
from decouple import config
import cloudinary, cloudinary.uploader

def get_catalogo(libros_por_pagina,offset):
    conexion = conexion_BD()
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
    libros = dict_factory(query)
    query.close()
    conexion.close()
    return libros

def get_catalogo_filtrado(libros_por_pagina,offset,filtro):
    conexion = conexion_BD()
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
    libros = dict_factory(query)
    query.close()
    conexion.close()
    return libros

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
    detalle = dict_factory(query)
    query.close()
    conexion.close()

    return detalle

def get_destacados(seccion):
    conexion = conexion_BD()
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
    resultado = dict_factory(query)
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

def get_ultima_seccion():
    conexion = conexion_BD()
    query = conexion.cursor()
    #Esta consulta devuelve la ultima seccion ingresada en RegistroLibros para que sea mas facil ingresar libros de manera ordenada
    #Si se ingresan por seccion no hace falta estar seleccionando nuevamente la seccion
    query.execute("select codigo_seccion from RegistroLibros order by id_registro desc limit 1")
    select_seccion = query.fetchone()

    if not select_seccion:
        ultima_seccion = "0"
    else:
        query.execute("""
        select codigo_seccion,seccion from SistemaDewey 
        where SistemaDewey.codigo_seccion = 
        (?)""",(select_seccion[0],))
        ultima_seccion = query.fetchall()
    query.close()
    conexion.close()
    return ultima_seccion

def registrar_libro(Titulo,NumeroPaginas,ISBN,tomo,NumeroCopias,NombreAutor,ApellidoAutor,editorial,LugarPublicacion,AnoPublicacion,SistemaDewey,Portada_file):
    conexion = conexion_BD()
    query = conexion.cursor()
    #Variable para guardar la notacion interna
    _notacion = ""
    if editorial:
        Notacion = editorial[0:3].upper() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres de la editorial
    elif (ApellidoAutor) and not editorial:
        editorial = "Otros"
        Notacion = ApellidoAutor[0:3].upper() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres del apellido autor
    elif (NombreAutor) and not ApellidoAutor: #Para el extranio caso de que no exista ni editorial ni apellido de autor
        editorial = "Otros"
        ApellidoAutor = "-"
        Notacion = NombreAutor[0:3].upper() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres del nombre del autor
    else: #No se agrega ni autor ni editorial notacion va a ser "OTR"
        editorial = "Otros"
        NombreAutor = "Otros"
        ApellidoAutor = "-"
        Notacion = "OTR"

    if editorial or ApellidoAutor or NombreAutor:
        for i in range (0,3): #Notacion es un arreglo, este for funciona para pasar ese arreglo a ser una variable
            _notacion = _notacion + Notacion[i]

    #Cuado no se ingresa un lugar de publicacion se ingresa un lugar vacio(id_lugar 1 = "-")
    if LugarPublicacion=="":
        LugarPublicacion = "-"

    try:
        cloudinary.config( 
            cloud_name = config('CLOUDINARY_CLOUD_NAME'),
            api_key = config('CLOUDINARY_API_KEY'),
            api_secret = config('CLOUDINARY_API_SECRET'),
            secure = True
        )
        if Portada_file:
            upload_result = cloudinary.uploader.upload(Portada_file, folder="bibliotecagm/portadas")
            Portada_url = upload_result.get('secure_url')
        else:
            Portada_url = 'book.png'

        #? INSERT DE LIBROS
        query.execute(f"Insert into Libros (Titulo,ano_publicacion,numero_paginas,isbn,tomo,numero_copias,portada) values (?,?,?,?,?,?,?)",(Titulo,AnoPublicacion,NumeroPaginas,ISBN,tomo,NumeroCopias,Portada_url))
        query.execute("Select id_libro from libros where titulo = ?",(Titulo,))
        id_libro = query.fetchone()[0]
        
        #?INSERT DE LUGARES
        #Si no existe insertar nuevo ya que columna lugar es UNIQUE
        query.execute("Insert or ignore into lugares (lugar) values (?)",(LugarPublicacion,))
        query.execute("Select id_lugar from lugares where lugar = ?",(LugarPublicacion,))
        id_lugar = query.fetchone()[0]

        #?INSERT DE AUTORES
        query.execute("insert or ignore into autores (nombre_autor,apellido_autor) values (?,?)", (NombreAutor,ApellidoAutor))
        query.execute("select id_autor from autores where nombre_autor = (?) AND apellido_autor = (?)",(NombreAutor,ApellidoAutor))
        id_autor = query.fetchone()[0]

        #? INSERT DE EDITORIALES
        query.execute("insert or ignore into Editoriales (editorial) values (?)",(editorial,))
        query.execute("select id_editorial from editoriales where editorial = (?)",(editorial,))
        id_editorial = query.fetchone()[0]

        #? INSERT DE NOTACIONES
        #Si no existe insertar nuevo ya que columna notacion es UNIQUE
        query.execute("Insert or ignore into notaciones (notacion,id_editorial,id_autor) values (?,?,?)",(_notacion,id_editorial,id_autor))
        query.execute("Select id_notacion from notaciones where notacion = (?) and id_autor = (?) and id_editorial = (?)",(_notacion,id_autor,id_editorial,))
        id_notacion = query.fetchone()[0]

        #? INSERT DE REGISTRO LIBROS
        #En registro libros, id_libro deberia ser unico? ya que se guarda un solo libro con el numero de copias
        query.execute("Insert into RegistroLibros(id_libro,id_notacion,id_lugar,codigo_seccion) values (?,?,?,?)",(id_libro,id_notacion,id_lugar,SistemaDewey))            

        #? Guardar cambios
        conexion.commit()
        alerta = ""
    except Exception as e:
        if "UNIQUE" in str(e) or "duplicate" in str(e).lower():
            alerta = "Error: libro duplicado."
        else:
            alerta = f"Error: {e}"
    finally:
        query.close()
        conexion.close()
    return alerta

def to_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
    
def editar_libro(id_libro, usuario , new_titulo, new_portada, new_tomo, new_numero_paginas, new_numero_copias,motivo):
    conexion = conexion_BD()
    query = conexion.cursor()
    try:
        libro = get_detalle_libro(id_libro)
        old_titulo = libro[0]['Titulo']
        old_portada = libro[0]['portada']
        old_tomo = libro[0]['Tomo']
        old_numero_paginas = libro[0]['numero_paginas']
        old_numero_copias = libro[0]['numero_copias']
        if not new_portada:
            new_portada = old_portada
        else:
            cloudinary.config( 
            cloud_name = config('CLOUDINARY_CLOUD_NAME'),
            api_key = config('CLOUDINARY_API_KEY'),
            api_secret = config('CLOUDINARY_API_SECRET'),
            secure = True
            )
            upload_result = cloudinary.uploader.upload(new_portada, folder="bibliotecagm/portadas")
            new_portada = upload_result.get('secure_url')
            
        query.execute("insert into libros_modificados(id_libro, id_administrador, titulo, tomo, num_paginas, num_copias, portada, fecha_modificacion, motivo) values (?,?,?,?,?,?,?,date('now'),?)",
                    (id_libro, usuario , old_titulo, old_tomo, old_numero_paginas, old_numero_copias, old_portada, motivo))

        query.execute("update libros set titulo = ?, portada = ?, tomo = ?, numero_paginas = ?, numero_copias = ? where id_libro = ?", 
                        (new_titulo, new_portada, to_int(new_tomo), to_int(new_numero_paginas), to_int(new_numero_copias), (id_libro)))
        alerta = "Libro editado exitósamente."
    except Exception as e:
        print(f"Error model: {e}")
        alerta = "Error al editar libro."  
    finally:
        conexion.commit()
        query.close()
        conexion.close()
    return alerta