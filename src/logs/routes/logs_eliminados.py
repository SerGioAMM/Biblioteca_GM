from flask import Blueprint, session, redirect, request,render_template,url_for
from datetime import datetime
import math
from src.database.db_sqlite import conexion_BD, dict_factory

bp_eliminados = Blueprint('eliminados',__name__, template_folder="../templates")

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
    query.execute("select count(*) from logs_eliminados where tabla_afectada = 'Libros'")
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina)
    
    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', le.fecha) as fecha,le.titulo,le.motivo,
                            strftime('%d', le.fecha) as dia,
                            CASE strftime('%m',le.fecha)
                            WHEN '01' THEN 'ENE'
                            WHEN '02' THEN 'FEB'
                            WHEN '03' THEN 'MAR'
                            WHEN '04' THEN 'ABR'
                            WHEN '05' THEN 'MAY'
                            WHEN '06' THEN 'JUN'
                            WHEN '07' THEN 'JUL'
                            WHEN '08' THEN 'AGO'
                            WHEN '09' THEN 'SEP'
                            WHEN '10' THEN 'OCT'
                            WHEN '11' THEN 'NOV'
                            WHEN '12' THEN 'DIC'
                            END as mes
                            from logs_eliminados le
                            join Administradores a on le.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            where le.tabla_afectada = 'Libros'
                            order by le.fecha desc
                            limit {libros_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    logs_libros = dict_factory(query)

    query.close()
    conexion.close()


    return render_template("libros_eliminados.html",logs=logs_libros,pagina=pagina,total_paginas=total_paginas)

# ----------------------------------------------------- Buscar Libro Eliminado ----------------------------------------------------- #

@bp_eliminados.route("/buscar_libro_e", methods = ["GET"])
def buscar_libro_e():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar","")
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")
    filtro_rol = request.args.get("rol","Todos")
    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f" and le.titulo like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f" and a.usuario like '%{busqueda}%'")
    
    if filtro_rol == "Todos":
        SQL_where_rol = ""
    else:
        SQL_where_rol = (f" and r.rol = '{filtro_rol}'")

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    libros_por_pagina = 10
    offset = (pagina - 1) * libros_por_pagina

    # Consulta para contar todos los libros
    query.execute(f"""select count(*) from logs_eliminados le 
                    join administradores a on le.id_administrador = a.id_administrador 
                    join roles r on a.id_rol = r.id_rol 
                    where tabla_afectada = 'Libros' {SQL_where_busqueda}{SQL_where_rol}""")
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina)
    
    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', le.fecha) as fecha,le.titulo,le.motivo,
                            strftime('%d', le.fecha) as dia,
                            CASE strftime('%m',le.fecha)
                            WHEN '01' THEN 'ENE'
                            WHEN '02' THEN 'FEB'
                            WHEN '03' THEN 'MAR'
                            WHEN '04' THEN 'ABR'
                            WHEN '05' THEN 'MAY'
                            WHEN '06' THEN 'JUN'
                            WHEN '07' THEN 'JUL'
                            WHEN '08' THEN 'AGO'
                            WHEN '09' THEN 'SEP'
                            WHEN '10' THEN 'OCT'
                            WHEN '11' THEN 'NOV'
                            WHEN '12' THEN 'DIC'
                            END as mes
                            from logs_eliminados le
                            join Administradores a on le.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            where tabla_afectada = 'Libros'{SQL_where_busqueda}{SQL_where_rol}
                            order by le.fecha desc
                            limit {libros_por_pagina} offset {offset}""")
    query.execute(query_busqueda)
    logs_libros = dict_factory(query)

    query.close()
    conexion.close()


    return render_template("libros_eliminados.html",logs=logs_libros,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)


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
    query.execute("select count(*) from logs_eliminados where tabla_afectada = 'Prestamos'")
    total_prestamos = query.fetchone()[0]
    total_paginas = math.ceil(total_prestamos / prestamos_por_pagina)
    
    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', le.fecha) as fecha,le.titulo,le.motivo,le.nombre_lector,
                            strftime('%d', le.fecha) as dia,
                            CASE strftime('%m',le.fecha)
                            WHEN '01' THEN 'ENE'
                            WHEN '02' THEN 'FEB'
                            WHEN '03' THEN 'MAR'
                            WHEN '04' THEN 'ABR'
                            WHEN '05' THEN 'MAY'
                            WHEN '06' THEN 'JUN'
                            WHEN '07' THEN 'JUL'
                            WHEN '08' THEN 'AGO'
                            WHEN '09' THEN 'SEP'
                            WHEN '10' THEN 'OCT'
                            WHEN '11' THEN 'NOV'
                            WHEN '12' THEN 'DIC'
                            END as mes
                            from logs_eliminados le
                            join Administradores a on le.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            where le.tabla_afectada = 'Prestamos'
                            order by le.fecha desc
                            limit {prestamos_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    prestamos_eliminados = dict_factory(query)

    query.close()
    conexion.close()


    return render_template("prestamos_eliminados.html",logs=prestamos_eliminados,pagina=pagina,total_paginas=total_paginas)


# ----------------------------------------------------- BUSCAR Prestamo Eliminado ----------------------------------------------------- #

@bp_eliminados.route("/buscar_prestamo_e", methods = ["GET"])
def buscar_prestamo_e():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar","")
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")
    filtro_rol = request.args.get("rol","Todos")
    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f" and le.titulo like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f" and a.usuario like '%{busqueda}%'")
    
    if filtro_rol == "Todos":
        SQL_where_rol = ""
    else:
        SQL_where_rol = (f" and r.rol = '{filtro_rol}'")

    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    prestamos_por_pagina = 10
    offset = (pagina - 1) * prestamos_por_pagina

    # Consulta para contar todos los prestamos conforme a la busqueda
    query.execute(f"""select count(*) from logs_eliminados le 
                    join administradores a on le.id_administrador = a.id_administrador 
                    join roles r on a.id_rol = r.id_rol 
                    where tabla_afectada = 'Prestamos' {SQL_where_busqueda}{SQL_where_rol}""")
    total_prestamos_eliminados = query.fetchone()[0]
    total_paginas = math.ceil(total_prestamos_eliminados / prestamos_por_pagina) #Calculo para cantidad de paginas, redondeando hacia arriba (ej, 2.1 = 3)

    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', le.fecha) as fecha,le.titulo,le.motivo,le.nombre_lector,
                            strftime('%d', le.fecha) as dia,
                            CASE strftime('%m',le.fecha)
                            WHEN '01' THEN 'ENE'
                            WHEN '02' THEN 'FEB'
                            WHEN '03' THEN 'MAR'
                            WHEN '04' THEN 'ABR'
                            WHEN '05' THEN 'MAY'
                            WHEN '06' THEN 'JUN'
                            WHEN '07' THEN 'JUL'
                            WHEN '08' THEN 'AGO'
                            WHEN '09' THEN 'SEP'
                            WHEN '10' THEN 'OCT'
                            WHEN '11' THEN 'NOV'
                            WHEN '12' THEN 'DIC'
                            END as mes
                            from logs_eliminados le
                            join Administradores a on le.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            where tabla_afectada = 'Prestamos' {SQL_where_busqueda}{SQL_where_rol}
                            order by le.fecha desc
                            limit {prestamos_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    prestamos_eliminados = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("prestamos_eliminados.html",logs=prestamos_eliminados,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)


# ----------------------------------------------------- Visitantes Eliminados ----------------------------------------------------- #

@bp_eliminados.route("/visitantes_e",methods = ["POST","GET"])
def visitantes_e():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    visitantes_por_pagina = 10
    offset = (pagina - 1) * visitantes_por_pagina

    # Consulta para contar todos los visitantes eliminados
    query.execute("select count(*) from logs_eliminados where tabla_afectada = 'Visitantes'")
    total_visitantes = query.fetchone()[0]
    total_paginas = math.ceil(total_visitantes / visitantes_por_pagina)
    
    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', le.fecha) as fecha,le.motivo,le.nombre_lector as cantidad_hombres,le.titulo as cantidad_mujeres,
                            strftime('%d', le.fecha) as dia,
                            CASE strftime('%m',le.fecha)
                            WHEN '01' THEN 'ENE'
                            WHEN '02' THEN 'FEB'
                            WHEN '03' THEN 'MAR'
                            WHEN '04' THEN 'ABR'
                            WHEN '05' THEN 'MAY'
                            WHEN '06' THEN 'JUN'
                            WHEN '07' THEN 'JUL'
                            WHEN '08' THEN 'AGO'
                            WHEN '09' THEN 'SEP'
                            WHEN '10' THEN 'OCT'
                            WHEN '11' THEN 'NOV'
                            WHEN '12' THEN 'DIC'
                            END as mes
                            from logs_eliminados le
                            join Administradores a on le.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            where le.tabla_afectada = 'Visitantes'
                            order by le.fecha desc
                            limit {visitantes_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    visitantes_eliminados = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("visitantes_eliminados.html",logs=visitantes_eliminados,pagina=pagina,total_paginas=total_paginas)


# ----------------------------------------------------- BUSCAR Visitante Eliminado ----------------------------------------------------- #

@bp_eliminados.route("/buscar_visitante_e", methods = ["GET"])
def buscar_visitante_e():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar","")
    #Obtiene los datos del formulario filtros
    filtro_busqueda = request.args.get("filtro-busqueda","Usuario")
    filtro_rol = request.args.get("rol","Todos")
    
    if filtro_busqueda == "Usuario":
        SQL_where_busqueda = (f" and a.usuario like '%{busqueda}%'")
    else:
        # Para cantidad, buscamos en ambos campos (hombres y mujeres)
        SQL_where_busqueda = (f" and (le.nombre_lector like '%{busqueda}%' or le.titulo like '%{busqueda}%')")
    
    if filtro_rol == "Todos":
        SQL_where_rol = ""
    else:
        SQL_where_rol = (f" and r.rol = '{filtro_rol}'")

    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    visitantes_por_pagina = 10
    offset = (pagina - 1) * visitantes_por_pagina

    # Consulta para contar todos los visitantes conforme a la busqueda
    query.execute(f"""select count(*) from logs_eliminados le 
                    join administradores a on le.id_administrador = a.id_administrador 
                    join roles r on a.id_rol = r.id_rol 
                    where tabla_afectada = 'Visitantes' {SQL_where_busqueda}{SQL_where_rol}""")
    total_visitantes_eliminados = query.fetchone()[0]
    total_paginas = math.ceil(total_visitantes_eliminados / visitantes_por_pagina) #Calculo para cantidad de paginas, redondeando hacia arriba (ej, 2.1 = 3)

    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', le.fecha) as fecha,le.motivo,le.nombre_lector as cantidad_hombres,le.titulo as cantidad_mujeres,
                            strftime('%d', le.fecha) as dia,
                            CASE strftime('%m',le.fecha)
                            WHEN '01' THEN 'ENE'
                            WHEN '02' THEN 'FEB'
                            WHEN '03' THEN 'MAR'
                            WHEN '04' THEN 'ABR'
                            WHEN '05' THEN 'MAY'
                            WHEN '06' THEN 'JUN'
                            WHEN '07' THEN 'JUL'
                            WHEN '08' THEN 'AGO'
                            WHEN '09' THEN 'SEP'
                            WHEN '10' THEN 'OCT'
                            WHEN '11' THEN 'NOV'
                            WHEN '12' THEN 'DIC'
                            END as mes
                            from logs_eliminados le
                            join Administradores a on le.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            where tabla_afectada = 'Visitantes' {SQL_where_busqueda}{SQL_where_rol}
                            order by le.fecha desc
                            limit {visitantes_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    visitantes_eliminados = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("visitantes_eliminados.html",logs=visitantes_eliminados,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)


# ----------------------------------------------------- Libros Modificados ----------------------------------------------------- #
@bp_eliminados.route("/libros_modificados",methods = ["POST","GET"])
def libros_modificados():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    libros_por_pagina = 10
    offset = (pagina - 1) * libros_por_pagina

    # Consulta para contar todos los libros
    query.execute("select count(*) from libros_modificados")
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina)
    
    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', lm.fecha_modificacion) as fecha,lm.motivo,
                            -- Solo mostrar campos que realmente cambiaron
                            CASE WHEN lm.titulo != l.Titulo THEN lm.titulo ELSE NULL END as old_titulo,
                            CASE WHEN lm.tomo != l.Tomo THEN lm.tomo ELSE NULL END as old_tomo,
                            CASE WHEN lm.num_paginas != l.numero_paginas THEN lm.num_paginas ELSE NULL END as old_num_paginas,
                            CASE WHEN lm.num_copias != l.numero_copias THEN lm.num_copias ELSE NULL END as old_num_copias,
                            CASE WHEN lm.portada != l.portada THEN lm.portada ELSE NULL END as old_portada,
                            lm.id_modificacion, l.Titulo as titulo_actual, l.Tomo as tomo_actual, l.numero_paginas as num_paginas_actual, l.numero_copias as num_copias_actual, l.portada as portada_actual, lm.id_libro,
                            strftime('%d', lm.fecha_modificacion) as dia,
                            CASE strftime('%m',lm.fecha_modificacion)
                            WHEN '01' THEN 'ENE'
                            WHEN '02' THEN 'FEB'
                            WHEN '03' THEN 'MAR'
                            WHEN '04' THEN 'ABR'
                            WHEN '05' THEN 'MAY'
                            WHEN '06' THEN 'JUN'
                            WHEN '07' THEN 'JUL'
                            WHEN '08' THEN 'AGO'
                            WHEN '09' THEN 'SEP'
                            WHEN '10' THEN 'OCT'
                            WHEN '11' THEN 'NOV'
                            WHEN '12' THEN 'DIC'
                            END as mes
                            from libros_modificados lm
                            join Administradores a on lm.id_administrador = a.id_administrador
                            join roles r on a.id_rol = r.id_rol
                            join libros l on lm.id_libro = l.id_libro
                            order by lm.fecha_modificacion desc
                            limit {libros_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    libros_m = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("libros_modificados.html",logs=libros_m,pagina=pagina,total_paginas=total_paginas)


# ----------------------------------------------------- Buscar Libro Modificado ----------------------------------------------------- #
@bp_eliminados.route("/buscar_libro_m", methods = ["GET"])
def buscar_libro_m():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar","")
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")
    filtro_rol = request.args.get("rol","Todos")
    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f" and lm.titulo like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f" and a.usuario like '%{busqueda}%'")
    
    if filtro_rol == "Todos":
        SQL_where_rol = ""
    else:
        SQL_where_rol = (f" and r.rol = '{filtro_rol}'")

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    libros_por_pagina = 10
    offset = (pagina - 1) * libros_por_pagina

    # Consulta para contar todos los libros
    query.execute(f"""select count(*) from libros_modificados lm
                    join administradores a on lm.id_administrador = a.id_administrador 
                    join roles r on a.id_rol = r.id_rol 
                    join libros l on lm.id_libro = l.id_libro
                    where 1=1 {SQL_where_busqueda}{SQL_where_rol}""")
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina)

    query.execute(f"""select a.usuario,r.rol,strftime('%d-%m-%Y', lm.fecha_modificacion) as fecha,lm.motivo,
                            -- Solo mostrar campos que realmente cambiaron
                            CASE WHEN lm.titulo != l.Titulo THEN lm.titulo ELSE NULL END as old_titulo,
                            CASE WHEN lm.tomo != l.Tomo THEN lm.tomo ELSE NULL END as old_tomo,
                            CASE WHEN lm.num_paginas != l.numero_paginas THEN lm.num_paginas ELSE NULL END as old_num_paginas,
                            CASE WHEN lm.num_copias != l.numero_copias THEN lm.num_copias ELSE NULL END as old_num_copias,
                            CASE WHEN lm.portada != l.portada THEN lm.portada ELSE NULL END as old_portada,
                            lm.id_modificacion, l.Titulo as titulo_actual, l.Tomo as tomo_actual, l.numero_paginas as num_paginas_actual, l.numero_copias as num_copias_actual, l.portada as portada_actual, lm.id_libro,
                            strftime('%d', lm.fecha_modificacion) as dia,
                            CASE strftime('%m',lm.fecha_modificacion)
                            WHEN '01' THEN 'ENE'
                            WHEN '02' THEN 'FEB'
                            WHEN '03' THEN 'MAR'
                            WHEN '04' THEN 'ABR'
                            WHEN '05' THEN 'MAY'
                            WHEN '06' THEN 'JUN'
                            WHEN '07' THEN 'JUL'
                            WHEN '08' THEN 'AGO'
                            WHEN '09' THEN 'SEP'
                            WHEN '10' THEN 'OCT'
                            WHEN '11' THEN 'NOV'
                            WHEN '12' THEN 'DIC'
                            END as mes
                            from libros_modificados lm
                            join Administradores a on lm.id_administrador = a.id_administrador
                            join roles r on a.id_rol = r.id_rol
                            join libros l on lm.id_libro = l.id_libro
                            where 1=1 {SQL_where_busqueda}{SQL_where_rol}
                            order by lm.fecha_modificacion desc
                            limit {libros_por_pagina} offset {offset}""")
    libros_m = dict_factory(query)

    query.close()
    conexion.close()
    return render_template("libros_modificados.html",logs=libros_m,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)

# ----------------------------------------------------- Revertir cambios ----------------------------------------------------- #
@bp_eliminados.route("/revertir_cambios/<int:id_modificacion>", methods=["POST"])
def revertir_cambios(id_modificacion):
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    # Obtener los datos de la modificación a revertir
    query.execute("SELECT id_libro,titulo,tomo,num_paginas,num_copias,portada FROM libros_modificados WHERE id_modificacion = ?", (id_modificacion,))
    modificacion = query.fetchone()

    if not modificacion:
        query.close()
        conexion.close()
        return "Modificación no encontrada", 404

    id_libro = modificacion[0]
    antiguo_titulo = modificacion[1]
    antiguo_tomo = modificacion[2]
    antiguo_num_paginas = modificacion[3]
    antiguo_num_copias = modificacion[4]
    antigua_portada = modificacion[5]

    # Obtener los datos actuales del libro
    query.execute("SELECT id_libro,titulo,tomo,numero_paginas,numero_copias,portada FROM libros WHERE id_libro = ?", (id_libro,))
    libro_actual = query.fetchone()

    if not libro_actual:
        query.close()
        conexion.close()
        return "Libro no encontrado", 404

    # Revertir los cambios solo si los nuevos valores son diferentes de los actuales
    titulo_revertido = antiguo_titulo if antiguo_titulo != libro_actual[1] else libro_actual[1]
    tomo_revertido = antiguo_tomo if antiguo_tomo != libro_actual[2] else libro_actual[2]
    num_paginas_revertido = antiguo_num_paginas if antiguo_num_paginas != libro_actual[3] else libro_actual[3]
    num_copias_revertido = antiguo_num_copias if antiguo_num_copias != libro_actual[4] else libro_actual[4]
    portada_revertida = antigua_portada if antigua_portada != libro_actual[5] else libro_actual[5]

    # Actualizar el libro con los valores revertidos
    query.execute("""
        UPDATE libros
        SET Titulo = ?, Tomo = ?, numero_paginas = ?, numero_copias = ?, portada = ?
        WHERE id_libro = ?
    """, (titulo_revertido, tomo_revertido, num_paginas_revertido, num_copias_revertido, portada_revertida, id_libro))

    query.execute("DELETE FROM libros_modificados WHERE id_modificacion = ?", (id_modificacion,))
    
    conexion.commit()
    query.close()
    conexion.close()

    return redirect(url_for('eliminados.libros_modificados'))