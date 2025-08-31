from flask import Blueprint, session, redirect, request,render_template,url_for
from datetime import datetime
import math
from src.database.db_sqlite import conexion_BD

bp_eliminados = Blueprint('eliminados',__name__)

# ----------------------------------------------------- Libros Eliminados ----------------------------------------------------- #

@bp_eliminados.route("/libros_e",methods = ["POST","GET"])
def libros_e():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    libros_por_pagina = 10
    offset = (pagina - 1) * libros_por_pagina

    # Consulta para contar todos los libros
    query.execute("select count(*) from libros_eliminados")
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina)
    
    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', le.fecha),le.titulo,le.motivo from libros_eliminados le
                            join Administradores a on le.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            order by le.fecha desc
                            limit {libros_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    libros_eliminados = query.fetchall()

    query.close()
    conexion.close()


    return render_template("libros_eliminados.html",libros_eliminados=libros_eliminados,pagina=pagina,total_paginas=total_paginas)

# ----------------------------------------------------- Buscar Libro Eliminado ----------------------------------------------------- #

@bp_eliminados.route("/buscar_libro_e", methods = ["GET"])
def buscar_libro_e():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar_libro_eliminado","")
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")

    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f" where le.titulo like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f" where a.usuario = '{busqueda}'")

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    libros_por_pagina = 10
    offset = (pagina - 1) * libros_por_pagina

    # Consulta para contar todos los libros
    query.execute("select count(*) from libros_eliminados")
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina)
    
    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', le.fecha),le.titulo,le.motivo from libros_eliminados le
                            join Administradores a on le.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            {SQL_where_busqueda}
                            order by le.fecha desc
                            limit {libros_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    libros_eliminados = query.fetchall()

    query.close()
    conexion.close()


    return render_template("libros_eliminados.html",libros_eliminados=libros_eliminados,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)


# ----------------------------------------------------- Prestamos Eliminados ----------------------------------------------------- #

@bp_eliminados.route("/prestamos_e",methods = ["POST","GET"])
def prestamos_e():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    prestamos_por_pagina = 10
    offset = (pagina - 1) * prestamos_por_pagina

    # Consulta para contar todos los libros
    query.execute("select count(*) from prestamos_eliminados")
    total_prestamos = query.fetchone()[0]
    total_paginas = math.ceil(total_prestamos / prestamos_por_pagina)
    
    _query = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', pe.fecha),pe.nombre_lector,pe.titulo,pe.motivo from prestamos_eliminados pe
                        join Administradores a on pe.id_administrador = a.id_administrador
                        join roles r on a.id_rol =  r.id_rol
                        order by pe.fecha desc
                        limit {prestamos_por_pagina} offset {offset}""")

    query.execute(_query)
    prestamos_eliminados = query.fetchall()

    query.close()
    conexion.close()


    return render_template("prestamos_eliminados.html",prestamos_eliminados=prestamos_eliminados,pagina=pagina,total_paginas=total_paginas)


# ----------------------------------------------------- BUSCAR Prestamo Eliminado ----------------------------------------------------- #

@bp_eliminados.route("/buscar_prestamo_e", methods = ["GET"])
def buscar_prestamo_e():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar_prestamo_eliminado","")
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")

    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f" where pe.titulo like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f" where a.usuario = '{busqueda}'")

    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    prestamos_por_pagina = 10
    offset = (pagina - 1) * prestamos_por_pagina

    # Consulta para contar todos los prestamos conforme a la busqueda
    query.execute(f"""select count(*) from prestamos_eliminados pe
                        join administradores a on pe.id_administrador = a.id_administrador
                        {SQL_where_busqueda}""")
    total_prestamos_eliminados = query.fetchone()[0]
    total_paginas = math.ceil(total_prestamos_eliminados / prestamos_por_pagina) #Calculo para cantidad de paginas, redondeando hacia arriba (ej, 2.1 = 3)

    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', pe.fecha),pe.nombre_lector,pe.titulo,pe.motivo from prestamos_eliminados pe
                            join Administradores a on pe.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            {SQL_where_busqueda}
                            order by pe.fecha desc
                            limit {prestamos_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    prestamos_eliminados = query.fetchall()

    query.close()
    conexion.close()

    return render_template("prestamos_eliminados.html",prestamos_eliminados=prestamos_eliminados,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)


