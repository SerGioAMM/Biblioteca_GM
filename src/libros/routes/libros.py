from flask import Blueprint, session, redirect, request,render_template,url_for
from datetime import datetime
import math
from src.database.db_sqlite import conexion_BD
from src.libros.models import libros_model

bp_libros = Blueprint('libros',__name__, template_folder="../templates")

# ----------------------------------------------------- REGISTRO LIBROS ----------------------------------------------------- #

@bp_libros.route("/registro_libros", methods=["GET", "POST"])
def registro_libros():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada

    ultima_seccion = libros_model.get_ultima_seccion()

    #Consulta para mostrar un listado de todas las secciones del Sistema Dewey
    secciones = libros_model.get_categorias()

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
        Portada_file = request.files.get("portada")
        SistemaDewey = request.form.get("sistema_dewey")
        
        try:
            alerta = libros_model.registrar_libro(Titulo,NumeroPaginas,ISBN,tomo,NumeroCopias,NombreAutor,ApellidoAutor,editorial,LugarPublicacion,AnoPublicacion,SistemaDewey,Portada_file)    
            ultima_seccion = libros_model.get_ultima_seccion()
            
            if alerta: return render_template("registro_libros.html", secciones = secciones, ultima_seccion = ultima_seccion, alerta=alerta)
            else:
                registro_exitoso = "Libro registrado exitosamente."
                return render_template("registro_libros.html", secciones = secciones, ultima_seccion = ultima_seccion, registro_exitoso=registro_exitoso) 

        except Exception as e:
            print(f"Error: {e}")
            alerta = "Error al ingresar libro."
            return render_template("registro_libros.html", secciones = secciones, ultima_seccion = ultima_seccion, alerta=alerta) 

    return render_template("registro_libros.html", secciones = secciones, ultima_seccion = ultima_seccion) #Devuelve variables para poder usarlas en insert.html

# ----------------------------------------------------- CATALOGO DE LIBROS ----------------------------------------------------- #

    #! Recordatorio de posible bug (04/04/2025)
    #TODO: El libro "Los 10 retos" se inserto sin autor, aunque el autor si se inserto correctamente, en la tabla notaciones se le fue asignado el autor X
    #TODO: El libro se inserto utilizando las facilidades de autorellenado del navegador Microsoft Edge
    #* Recordatorio: El commit estaba comentado en el primer intento de insert, este podria ser el origen del problema. 
    #* Observacion: El libro no tiene editorial, este tambien podria ser el origen del bug, pero en este caso lo dudo.
@bp_libros.route("/libros", methods=["GET", "POST"])
def libros():

    pagina = request.args.get("pag", 1, type=int)
    libros_por_pagina = 36
    offset = (pagina - 1) * libros_por_pagina
    
    total_libros = libros_model.total_libros(" ")
    total_paginas = math.ceil(total_libros / libros_por_pagina)
    
    libros = libros_model.get_catalogo(libros_por_pagina,offset)
    
    #? Selecciona todas las secciones del sistema dewey, para ser usados en los filtros
    categorias = libros_model.get_categorias()

    destacados = []
    for i in range(10):
        resultado = libros_model.get_destacados(i)
        if resultado:
            for libro in resultado:
                destacados.append((libro["id_libro"])) 
    
    alerta = request.args.get("alerta", "")
    exito = request.args.get("exito", "")

    return render_template("libros.html",libros=libros,categorias=categorias,pagina=pagina,total_paginas=total_paginas,
                            alerta=alerta, exito = exito, destacados=destacados)

# ----------------------------------------------------- BUSCAR LIBROS ----------------------------------------------------- #

@bp_libros.route("/buscar_libro", methods=["GET","POST"])
def buscar_libro():
    busqueda = request.args.get("buscar", "")
    filtro_busqueda = request.args.get("filtro-busqueda", "Titulo") 
    Seccion = request.args.get("categorias", "Todas") 
    alerta = request.args.get("alerta","")
    exito = request.args.get("exito","")

    pagina = request.args.get("pag", 1, type=int)
    libros_por_pagina = 36
    offset = (pagina - 1) * libros_por_pagina

    # Secciones Dewey para filtros
    categorias = libros_model.get_categorias()

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
    total_paginas = math.ceil((libros_model.total_libros(filtro_total)) / libros_por_pagina) #Redondea el resultado hacia arriba, si hay (11 libros / 10 libros por pagina) = 1.1, math.ceil(1.1) = 2 paginas

    # Consulta paginada
    libros = libros_model.get_catalogo_filtrado(libros_por_pagina,offset,filtro_total)
    
    if not libros:
        alerta = "No se encontraron libros."
        return redirect(url_for("libros.libros",alerta = alerta))

    destacados = []
    for i in range(10):
        resultado = libros_model.get_destacados(i)
        if resultado:
            for libro in resultado:
                destacados.append((libro["id_libro"])) 

    return render_template("libros.html", libros=libros, categorias=categorias,
                            pagina=pagina, total_paginas=total_paginas,
                            busqueda=busqueda, filtro_busqueda=filtro_busqueda, Seccion=Seccion, 
                            alerta = alerta, exito = exito, destacados=destacados)

# ----------------------------------------------------- ELIMINAR LIBROS ----------------------------------------------------- #

@bp_libros.route("/eliminar_libro", methods=["GET", "POST"])
def eliminar_libro():
    id_libro = request.form["id_libro"]
    motivo = request.form["motivo"]
    id_administrador = session.get("id_administrador")

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select id_prestamo from prestamos where id_libro = ? and (id_estado == 1 or id_estado == 2)",(id_libro,))
    libroprestado = query.fetchall()

    if(libroprestado):
        alerta = "Error, el libro está prestado."
        return redirect(url_for("libros.libros",alerta = alerta))

    query.execute("select titulo from libros where id_libro = ?",(id_libro,))
    titulo_libro = query.fetchone()[0]

    query.execute("insert into logs_eliminados(id_administrador,id_eliminado,tabla_afectada,fecha,titulo,motivo) values(?,?,'Libros',datetime('now'),?,?)",(id_administrador,id_libro,titulo_libro,motivo))

    query.execute("delete from Libros where id_libro = ?",(id_libro,))
    query.execute("delete from RegistroLibros where id_libro = ?",(id_libro,))
    
    conexion.commit()

    query.close()
    conexion.close()

    exito = "Libro eliminado exitósamente."

    return redirect(url_for("libros.libros",exito = exito))


# ----------------------------------------------------- DETALLE LIBROS ----------------------------------------------------- #

@bp_libros.route("/detalle_libro/<ID>/<Titulo>", methods=["GET", "POST"])
def detalle_libro(ID,Titulo):
    
    detalle = libros_model.get_detalle_libro(ID)
    
    return render_template("detalle_libro.html",detalle=detalle, descripcion="Nada")

@bp_libros.route("/editar_libro", methods=["GET", "POST"])
def editar_libro():
    if(request.method=="POST"):
        id_libro = request.form["id_libro"]
        new_titulo = request.form["titulo"]
        new_portada = request.files.get("portada")
        new_tomo = request.form["tomo"]
        new_numero_paginas = request.form["numero_paginas"]
        new_numero_copias = request.form["numero_copias"]
        motivo = request.form["motivo"]
        usuario = session.get("id_administrador")
        try:
            libros_model.editar_libro(id_libro, usuario, new_titulo, new_portada, new_tomo, new_numero_paginas, new_numero_copias, motivo)
        except Exception as e:
            print(f"Error: {e}")
            alerta = "Error al editar libro."
            return redirect(url_for('libros.detalle_libro', ID=id_libro, Titulo=new_titulo, alerta=alerta))
        
    return redirect(url_for('libros.detalle_libro', ID=id_libro, Titulo=new_titulo))