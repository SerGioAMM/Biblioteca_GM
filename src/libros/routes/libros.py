from flask import Blueprint, session, redirect, request,render_template,url_for
from datetime import datetime
import math
from src.database.db_sqlite import conexion_BD

bp_libros = Blueprint('libros',__name__, template_folder="../templates")

# ----------------------------------------------------- REGISTRO LIBROS ----------------------------------------------------- #

@bp_libros.route("/registro_libros", methods=["GET", "POST"])
def registro_libros():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada

    #Abrir conexion con la base de datos
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
        

    #Consulta para mostrar un listado de todas las secciones del Sistema Dewey
    query.execute("select * from SistemaDewey")
    secciones = query.fetchall()

    #Verifica la accion que realiza el formulario en insertar.html
    if request.method == "POST":
        #Obtiene los datos del formulario en insertar.html
        Titulo = request.form["titulo"]
        NumeroPaginas = request.form["num_paginas"]
        ISBN = request.form["ISBN"]
        tomo = request.form["tomo"]
        NumeroCopias = request.form["num_copias"]
        NombreAutor = request.form["nombre_autor"]
        ApellidoAutor = request.form["apellido_autor"]
        editorial = request.form["editorial"]
        LugarPublicacion = request.form["lugar"]
        AnoPublicacion = request.form["anio"]
        
        SistemaDewey = request.form.get("sistema_dewey")

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
                print(_notacion)

        #Cuado no se ingresa un lugar de publicacion se ingresa un lugar vacio(id_lugar 1 = "-")
        if LugarPublicacion=="":
            LugarPublicacion = "-"

        try:
            #? INSERT DE LIBROS
            query.execute(f"Insert into Libros (Titulo,ano_publicacion,numero_paginas,isbn,tomo,numero_copias) values (?,?,?,?,?,?)",(Titulo,AnoPublicacion,NumeroPaginas,ISBN,tomo,NumeroCopias))
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

            #Esta consulta devuelve la ultima seccion ingresada en RegistroLibros para que sea mas facil ingresar libros de manera ordenada
            #Si se ingresan por seccion no hace falta estar seleccionando nuevamente la seccion
            query.execute("select codigo_seccion from RegistroLibros order by id_registro desc limit 1")
            select_seccion = query.fetchone()
            
            if not select_seccion:
                ultima_seccion = "0"
            else:
                query.execute("""
                select * from SistemaDewey 
                where SistemaDewey.codigo_seccion = 
                (?)""",(select_seccion[0],))
                ultima_seccion = query.fetchall()

            
            registro_exitoso = "Libro registrado exitosamente."
            return render_template("registro_libros.html", secciones = secciones, ultima_seccion = ultima_seccion, registro_exitoso=registro_exitoso) 

        except Exception as e:
            print(f"Error: {e}")
            alerta = "Error al ingresar libro."
            return render_template("registro_libros.html", secciones = secciones, ultima_seccion = ultima_seccion, alerta=alerta) 
        finally:
            query.close()
            conexion.close()
    

    return render_template("registro_libros.html", secciones = secciones, ultima_seccion = ultima_seccion) #Devuelve variables para poder usarlas en insert.html

# ----------------------------------------------------- CATALOGO DE LIBROS ----------------------------------------------------- #

##! Para dividir los resultados del query usar offset y limit, con variable para el numero de pagina
##! VIDEO: https://www.youtube.com/watch?v=jUVPtMnbuv4

    #! Recordatorio de posible bug (04/04/2025)
    #TODO: El libro "Los 10 retos" se inserto sin autor, aunque el autor si se inserto correctamente, en la tabla notaciones se le fue asignado el autor X
    #TODO: El libro se inserto utilizando las facilidades de autorellenado del navegador Microsoft Edge
    #* Recordatorio: El commit estaba comentado en el primer intento de insert, este podria ser el origen del problema. 
    #* Observacion: El libro no tiene editorial, este tambien podria ser el origen del bug, pero en este caso lo dudo.

@bp_libros.route("/libros", methods=["GET", "POST"])
def libros():

    #Abrir conexion con la base de datos
    conexion = conexion_BD()
    query = conexion.cursor()

    pagina = request.args.get("pag", 1, type=int)
    libros_por_pagina = 36
    offset = (pagina - 1) * libros_por_pagina

    # Consulta para contar todos los libros
    query.execute("select count(*) from Libros")
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina)

    #? Selecciona todos los libros disponibles
    # Consulta paginada
    query.execute("""
        select l.id_libro, Titulo, tomo, ano_publicacion, ISBN, numero_paginas, numero_copias,
        sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor, e.editorial, n.notacion,lu.lugar
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
    
    #? Selecciona todas las secciones del sistema dewey, para ser usados en los filtros
    query.execute("select * from SistemaDewey")
    categorias = query.fetchall()

    resultado = []
    for i in range(10):
        query.execute(f"""select l.id_libro,count(l.id_libro) as cantidad
                        from Prestamos p
                        join libros l on p.id_libro = l.id_libro
                        join RegistroLibros r on r.id_libro = l.id_libro
                        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
                        where sd.codigo_seccion LIKE "{i}%"
                        group by p.id_libro
                        order by cantidad desc
                        limit 3;""")
        destacados = query.fetchall()
        if destacados:
            for libro in destacados:
                resultado.append((libro[0])) 

    query.close()
    conexion.close()
    
    alerta = request.args.get("alerta", "")
    exito = request.args.get("exito", "")

    return render_template("libros.html",libros=libros,categorias=categorias,pagina=pagina,total_paginas=total_paginas,
                            alerta=alerta, exito = exito, destacados=resultado)

# ----------------------------------------------------- BUSCAR LIBROS ----------------------------------------------------- #

@bp_libros.route("/buscar_libro", methods=["GET","POST"])
def buscar_libro():
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar", "")
    filtro_busqueda = request.args.get("filtro-busqueda", "Titulo") 
    Seccion = request.args.get("categorias", "Todas") 
    alerta = request.args.get("alerta","")
    exito = request.args.get("exito","")


    pagina = request.args.get("pag", 1, type=int)
    libros_por_pagina = 36
    offset = (pagina - 1) * libros_por_pagina

    # Secciones Dewey para filtros
    query.execute("select * from SistemaDewey")
    categorias = query.fetchall()

    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f"where l.titulo like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f"where (a.nombre_autor || ' ' || a.apellido_autor) like '%{busqueda}%'")

    if not Seccion or Seccion == "Todas":
        SQL_where_seccion = ""
    else:
        SQL_where_seccion = (f" and sd.codigo_seccion = {Seccion}")

    filtro_total = SQL_where_busqueda + SQL_where_seccion

    # Conteo total para paginación
    query.execute(f"""
        select count(*) from Libros l
        join RegistroLibros r on r.id_libro = l.id_libro
        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
        join notaciones n on n.id_notacion = r.id_notacion
        join Autores a on a.id_autor = n.id_autor
        join Editoriales e on e.id_editorial = n.id_editorial
        join Lugares lu on r.id_lugar = lu.id_lugar
        {filtro_total}
    """)
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina) #Redondea el resultado hacia arriba, si hay (11 libros / 10 libros por pagina) = 1.1, math.ceil(1.1) = 2 paginas

    # Consulta paginada
    query.execute(f"""
        select l.id_libro, Titulo, tomo, ano_publicacion, ISBN, numero_paginas, numero_copias,
        sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor, e.editorial, n.notacion, lu.lugar
        from Libros l
        join RegistroLibros r on r.id_libro = l.id_libro
        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
        join notaciones n on n.id_notacion = r.id_notacion
        join Autores a on a.id_autor = n.id_autor
        join Editoriales e on e.id_editorial = n.id_editorial
        join Lugares lu on r.id_lugar = lu.id_lugar
        {filtro_total}
        order by sd.codigo_seccion asc,Titulo asc
        limit ? offset ?
    """, (libros_por_pagina, offset))

    libros = query.fetchall()

    resultado = []
    for i in range(10):
        query.execute(f"""select l.id_libro,count(l.id_libro) as cantidad
                        from Prestamos p
                        join libros l on p.id_libro = l.id_libro
                        join RegistroLibros r on r.id_libro = l.id_libro
                        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
                        where sd.codigo_seccion LIKE "{i}%"
                        group by p.id_libro
                        order by cantidad desc
                        limit 3;""")
        destacados = query.fetchall()
        if destacados:
            for libro in destacados:
                resultado.append((libro[0]))

    query.close()
    conexion.close()

    return render_template("libros.html", libros=libros, categorias=categorias,
                            pagina=pagina, total_paginas=total_paginas,
                            busqueda=busqueda, filtro_busqueda=filtro_busqueda, Seccion=Seccion, 
                            alerta = alerta, exito = exito, destacados=resultado)

# ----------------------------------------------------- ELIMINAR LIBROS ----------------------------------------------------- #

@bp_libros.route("/eliminar_libro", methods=["GET", "POST"])
def eliminar_libro():
    id_libro = request.form["id_libro"]
    motivo = request.form["motivo"]

    # Obtenre la fecha actual
    hoy = datetime.today().date()
    id_administrador = session.get("id_administrador")

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select id_prestamo from prestamos where id_libro = ?",(id_libro,))
    libroprestado = query.fetchall()

    if(libroprestado):
        alerta = "Error, el libro está prestado."
        return redirect(url_for("libros.libros",alerta = alerta))

    query.execute("select titulo from libros where id_libro = ?",(id_libro,))
    titulo_libro = query.fetchone()[0]

    query.execute("insert into libros_eliminados(id_administrador,id_libro,fecha,titulo,motivo) values(?,?,?,?,?)",(id_administrador,id_libro,hoy,titulo_libro,motivo))

    query.execute("delete from libros where id_libro = ?",(id_libro,))
    conexion.commit()

    query.close()
    conexion.close()

    exito = "Libro eliminado exitósamente."

    return redirect(url_for("libros.libros",exito = exito))


# ----------------------------------------------------- DETALLE LIBROS ----------------------------------------------------- #

def get_detalle_libro(id_libro):
    import sqlite3

    conexion = conexion_BD()
    conexion.row_factory = sqlite3.Row
    query = conexion.cursor()

    query.execute("""select l.id_libro, Titulo, tomo, ano_publicacion, ISBN, numero_paginas, numero_copias,
        sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor, e.editorial, n.notacion, lu.lugar
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

'''
def get_descripcion(Titulo):
    import requests

    url = f"https://openlibrary.org/search.json?title={Titulo}"
    respuesta = requests.get(url)
    respuesta = respuesta.json()

    if respuesta["numFound"] > 0:
        primer_libro = respuesta["docs"][0]
        work_key = primer_libro.get("key") 

        # Obtener detalles más completos
        work_url = f"https://openlibrary.org{work_key}.json"
        work_response = requests.get(work_url)
        work_data = work_response.json()

        return {
            "description": (
                work_data.get("description", "Sin descripción disponible")
                if isinstance(work_data.get("description"), str)
                else work_data.get("description", {}).get("value", "Sin descripción disponible")
            )
        }
    else:
        return None
'''

@bp_libros.route("/detalle_libro/<ID>/<Titulo>", methods=["GET", "POST"])
def detalle_libro(ID,Titulo):
    
    detalle = get_detalle_libro(ID)
    #descripcion = get_descripcion(Titulo)
    
    return render_template("detalle_libro.html",detalle=detalle, descripcion="Nada")