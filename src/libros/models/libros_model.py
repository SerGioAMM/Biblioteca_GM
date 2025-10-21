from src.database.db_sqlite import conexion_BD, dict_factory
from decouple import config
import cloudinary, cloudinary.uploader

def normalizar_titulo(titulo):
    """
    Normaliza un título al formato de oración (primera letra mayúscula, resto minúsculas).
    Esto ayuda a evitar duplicados por diferencias de mayúsculas/minúsculas.
    
    Args:
        titulo (str): El título a normalizar
    
    Returns:
        str: Título normalizado en formato oración
    """
    if not titulo or titulo.strip() == "":
        return ""
    
    # Eliminar espacios extra y convertir a formato oración
    titulo_limpio = titulo.strip()
    # Primera letra en mayúscula, el resto en minúsculas
    return titulo_limpio.capitalize()

def validar_notacion(texto):
    """
    Valida y completa un texto para crear una notación de 3 caracteres.
    Si el texto tiene menos de 3 caracteres, lo completa con espacios.
    
    Args:
        texto (str): El texto a validar (editorial, apellido, nombre)
    
    Returns:
        str: Texto de exactamente 3 caracteres en mayúsculas
    """
    if not texto or texto.strip() == "":
        return "   "  # 3 espacios si está vacío
    
    texto_limpio = texto.strip().upper()
    
    if len(texto_limpio) < 3:
        # Completar con espacios hasta llegar a 3 caracteres
        return texto_limpio.ljust(3)
    else:
        # Tomar solo los primeros 3 caracteres
        return texto_limpio[:3]

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
    
    # Normalizar el título para evitar duplicados y mantener formato consistente
    Titulo = normalizar_titulo(Titulo)
    
    # Determinar la notación basada en la prioridad: editorial > apellido > nombre > "OTR"
    if editorial and editorial.strip():
        Notacion = validar_notacion(editorial)
    elif ApellidoAutor and ApellidoAutor.strip() and ApellidoAutor != "-":
        if not editorial or not editorial.strip():
            editorial = "Otros"
        Notacion = validar_notacion(ApellidoAutor)
    elif NombreAutor and NombreAutor.strip():
        if not editorial or not editorial.strip():
            editorial = "Otros"
        if not ApellidoAutor or not ApellidoAutor.strip():
            ApellidoAutor = "-"
        Notacion = validar_notacion(NombreAutor)
    else:
        # No hay información suficiente, usar valores por defecto
        editorial = "Otros"
        NombreAutor = "Otros"
        ApellidoAutor = "-"
        Notacion = "OTR"

    # Cuando no se ingresa un lugar de publicación se ingresa un lugar vacío (id_lugar 1 = "-")
    if not LugarPublicacion or LugarPublicacion.strip() == "":
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

        # Verificar si ya existe un libro con el mismo título (normalizado)
        query.execute("Select id_libro from libros where LOWER(titulo) = LOWER(?)",(Titulo,))
        libro_existente = query.fetchone()
        
        if libro_existente:
            alerta = f"Error: Ya existe un libro con el título '{Titulo}'."
            return alerta

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
        query.execute("Insert or ignore into notaciones (notacion,id_editorial,id_autor) values (?,?,?)",(Notacion,id_editorial,id_autor))
        query.execute("Select id_notacion from notaciones where notacion = (?) and id_autor = (?) and id_editorial = (?)",(Notacion,id_autor,id_editorial,))
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
    
def editar_libro(id_libro, usuario, new_titulo, new_portada, new_tomo, new_numero_paginas, new_numero_copias, 
                 new_isbn, new_anio, new_nombre_autor, new_apellido_autor, new_editorial, new_lugar, new_seccion, motivo):
    conexion = conexion_BD()
    query = conexion.cursor()
    try:
        # Normalizar el nuevo título
        new_titulo = normalizar_titulo(new_titulo)
        
        # ============================================================================
        # PASO 1: Obtener datos actuales del libro (tabla Libros)
        # ============================================================================
        libro = get_detalle_libro(id_libro)
        old_titulo = libro[0]['Titulo']
        old_portada = libro[0]['portada']
        old_tomo = libro[0]['Tomo']
        old_numero_paginas = libro[0]['numero_paginas']
        old_numero_copias = libro[0]['numero_copias']
        old_isbn = libro[0]['ISBN']
        old_anio = libro[0]['ano_publicacion']
        
        # ============================================================================
        # PASO 2: Obtener referencias actuales de RegistroLibros
        # Estas son las FK que se guardarán en Libros_modificados
        # ============================================================================
        query.execute("""
            SELECT rl.id_notacion, rl.id_lugar, rl.codigo_seccion,
                   n.id_autor, n.id_editorial
            FROM RegistroLibros rl
            JOIN Notaciones n ON n.id_notacion = rl.id_notacion
            WHERE rl.id_libro = ?
        """, (id_libro,))
        registro_actual = query.fetchone()
        
        if not registro_actual:
            raise Exception("No se encontró el registro del libro en RegistroLibros")
        
        # Almacenar las referencias antiguas (para guardar en Libros_modificados)
        old_id_notacion = registro_actual[0]
        old_id_lugar = registro_actual[1]
        old_codigo_seccion = registro_actual[2]
        old_id_autor = registro_actual[3]
        old_id_editorial = registro_actual[4]
        
        # ============================================================================
        # PASO 3: Procesar y subir nueva portada (si existe)
        # ============================================================================
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
        
        # ============================================================================
        # PASO 4: Actualizar tabla Libros (datos básicos)
        # ============================================================================
        query.execute("""
            UPDATE libros 
            SET titulo = ?, portada = ?, tomo = ?, numero_paginas = ?, numero_copias = ?, isbn = ?, ano_publicacion = ? 
            WHERE id_libro = ?
        """, (new_titulo, new_portada, to_int(new_tomo), to_int(new_numero_paginas), 
              to_int(new_numero_copias), new_isbn, new_anio, id_libro))
        
        # ============================================================================
        # PASO 5: Procesar nuevas relaciones (Lugar, Autor, Editorial, Notación)
        # ============================================================================
        
        # 5.1 - Lugar de publicación
        if not new_lugar or new_lugar.strip() == "":
            new_lugar = "-"
        query.execute("INSERT OR IGNORE INTO lugares (lugar) VALUES (?)", (new_lugar,))
        query.execute("SELECT id_lugar FROM lugares WHERE lugar = ?", (new_lugar,))
        new_id_lugar = query.fetchone()[0]
        
        # 5.2 - Autor
        query.execute("INSERT OR IGNORE INTO autores (nombre_autor, apellido_autor) VALUES (?, ?)", 
                     (new_nombre_autor, new_apellido_autor))
        query.execute("SELECT id_autor FROM autores WHERE nombre_autor = ? AND apellido_autor = ?", 
                     (new_nombre_autor, new_apellido_autor))
        new_id_autor = query.fetchone()[0]
        
        # 5.3 - Editorial
        if not new_editorial or new_editorial.strip() == "":
            new_editorial = "Otros"
        query.execute("INSERT OR IGNORE INTO editoriales (editorial) VALUES (?)", (new_editorial,))
        query.execute("SELECT id_editorial FROM editoriales WHERE editorial = ?", (new_editorial,))
        new_id_editorial = query.fetchone()[0]
        
        # 5.4 - Determinar nueva notación
        if new_editorial and new_editorial.strip() and new_editorial != "Otros":
            Notacion = validar_notacion(new_editorial)
        elif new_apellido_autor and new_apellido_autor.strip() and new_apellido_autor != "-":
            Notacion = validar_notacion(new_apellido_autor)
        elif new_nombre_autor and new_nombre_autor.strip():
            Notacion = validar_notacion(new_nombre_autor)
        else:
            Notacion = "OTR"
        
        # 5.5 - Crear o buscar notación
        query.execute("INSERT OR IGNORE INTO notaciones (notacion, id_editorial, id_autor) VALUES (?, ?, ?)", 
                     (Notacion, new_id_editorial, new_id_autor))
        query.execute("SELECT id_notacion FROM notaciones WHERE notacion = ? AND id_autor = ? AND id_editorial = ?", 
                     (Notacion, new_id_autor, new_id_editorial))
        new_id_notacion = query.fetchone()[0]
        
        # ============================================================================
        # PASO 6: Actualizar o insertar registro en Libros_modificados
        # Solo debe existir UN registro por libro (sin duplicados)
        # Si ya existe, se actualiza con los nuevos datos antiguos
        # Si no existe, se inserta normalmente
        # ============================================================================
        
        # Verificar si ya existe un registro de modificación para este libro
        query.execute("SELECT id_modificacion FROM libros_modificados WHERE id_libro = ?", (id_libro,))
        registro_existente = query.fetchone()
        
        if registro_existente:
            # Ya existe un registro: ACTUALIZAR con los datos actuales como "antiguos"
            query.execute("""
                UPDATE libros_modificados 
                SET id_administrador = ?,
                    titulo = ?,
                    tomo = ?,
                    num_paginas = ?,
                    num_copias = ?,
                    portada = ?,
                    fecha_modificacion = date('now'),
                    motivo = ?,
                    id_notacion_antigua = ?,
                    id_editorial_antigua = ?,
                    id_autor_antiguo = ?,
                    id_lugar_antiguo = ?,
                    codigo_seccion_antiguo = ?,
                    ISBN_antiguo = ?,
                    ano_publicacion_antiguo = ?
                WHERE id_libro = ?
            """, (usuario, old_titulo, old_tomo, old_numero_paginas, old_numero_copias, 
                  old_portada, motivo, old_id_notacion, old_id_editorial, old_id_autor, 
                  old_id_lugar, old_codigo_seccion, old_isbn, old_anio, id_libro))
        else:
            # No existe registro: INSERTAR nuevo
            query.execute("""
                INSERT INTO libros_modificados(
                    id_libro, 
                    id_administrador, 
                    titulo, 
                    tomo, 
                    num_paginas, 
                    num_copias, 
                    portada, 
                    fecha_modificacion, 
                    motivo,
                    id_notacion_antigua,
                    id_editorial_antigua,
                    id_autor_antiguo,
                    id_lugar_antiguo,
                    codigo_seccion_antiguo,
                    ISBN_antiguo,
                    ano_publicacion_antiguo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, date('now'), ?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_libro, usuario, old_titulo, old_tomo, old_numero_paginas, old_numero_copias, 
                  old_portada, motivo, old_id_notacion, old_id_editorial, old_id_autor, 
                  old_id_lugar, old_codigo_seccion, old_isbn, old_anio))
        
        # ============================================================================
        # PASO 7: Actualizar RegistroLibros con las nuevas referencias
        # NO se duplica el registro, solo se actualiza el existente
        # ============================================================================
        query.execute("""
            UPDATE RegistroLibros 
            SET id_notacion = ?, id_lugar = ?, codigo_seccion = ? 
            WHERE id_libro = ?
        """, (new_id_notacion, new_id_lugar, new_seccion, id_libro))
        
        alerta = "Libro editado exitósamente."
    except Exception as e:
        print(f"Error model: {e}")
        alerta = "Error al editar libro."  
    finally:
        conexion.commit()
        query.close()
        conexion.close()
    return alerta

def romano_a_natural(romano):
    """
    Convierte una cadena de número romano a su equivalente natural.
    """
    valores_romanos = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    resultado = 0
    i = 0
    while i < len(romano):
        valor_actual = valores_romanos[romano[i]]

        if i + 1 < len(romano) and valores_romanos[romano[i+1]] > valor_actual:
            resultado -= valor_actual
        else:
            resultado += valor_actual
        i += 1
    return resultado

def get_libros_recomendados_autor(id_autor, id_libro_actual, limit=3):
    """
    Obtiene libros del mismo autor (excluyendo el libro actual)
    Args:
        id_autor: ID del autor
        id_libro_actual: ID del libro que se está visualizando (para excluirlo)
        limit: Número máximo de libros a retornar
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    query.execute("""
        SELECT l.id_libro, l.titulo, l.portada, l.ano_publicacion,
        a.nombre_autor, a.apellido_autor, sd.codigo_seccion, sd.seccion, n.notacion
        FROM Libros l
        JOIN RegistroLibros r ON r.id_libro = l.id_libro
        JOIN notaciones n ON n.id_notacion = r.id_notacion
        JOIN Autores a ON a.id_autor = n.id_autor
        JOIN SistemaDewey sd ON sd.codigo_seccion = r.codigo_seccion
        WHERE a.id_autor = ? AND l.id_libro != ?
        ORDER BY RANDOM()
        LIMIT ?
    """, (id_autor, id_libro_actual, limit))
    libros = dict_factory(query)
    query.close()
    conexion.close()
    return libros

def get_libros_recomendados_categoria(codigo_seccion, id_libro_actual, limit=3):
    """
    Obtiene libros de la misma categoría (excluyendo el libro actual)
    Args:
        codigo_seccion: Código de la sección Dewey
        id_libro_actual: ID del libro que se está visualizando (para excluirlo)
        limit: Número máximo de libros a retornar
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    query.execute("""
        SELECT l.id_libro, l.titulo, l.portada, l.ano_publicacion,
        a.nombre_autor, a.apellido_autor, sd.codigo_seccion, sd.seccion, n.notacion
        FROM Libros l
        JOIN RegistroLibros r ON r.id_libro = l.id_libro
        JOIN notaciones n ON n.id_notacion = r.id_notacion
        JOIN Autores a ON a.id_autor = n.id_autor
        JOIN SistemaDewey sd ON sd.codigo_seccion = r.codigo_seccion
        WHERE sd.codigo_seccion = ? AND l.id_libro != ?
        ORDER BY RANDOM()
        LIMIT ?
    """, (codigo_seccion, id_libro_actual, limit))
    libros = dict_factory(query)
    query.close()
    conexion.close()
    return libros

def get_id_autor_libro(id_libro):
    """
    Obtiene el ID del autor de un libro
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    query.execute("""
        SELECT a.id_autor
        FROM Libros l
        JOIN RegistroLibros r ON r.id_libro = l.id_libro
        JOIN notaciones n ON n.id_notacion = r.id_notacion
        JOIN Autores a ON a.id_autor = n.id_autor
        WHERE l.id_libro = ?
    """, (id_libro,))
    resultado = query.fetchone()
    query.close()
    conexion.close()
    return resultado[0] if resultado else None