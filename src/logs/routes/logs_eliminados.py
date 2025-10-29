from flask import Blueprint, session, redirect, request,render_template,url_for
from datetime import datetime
import math
from src.database.db_sqlite import conexion_BD, dict_factory

bp_eliminados = Blueprint('eliminados',__name__, template_folder="../templates")

# ----------------------------------------------------- Libros Eliminados ----------------------------------------------------- #

@bp_eliminados.route("/libros_e",methods = ["POST","GET"])
def libros_e():
    if "usuario" not in session:
        return redirect("/")
    
    if session.get("rol") != "Administrador":
        return redirect("/prestamos") #Solo administradores pueden acceder a logs
    
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
        return redirect("/")
    
    if session.get("rol") != "Administrador":
        return redirect("/prestamos") #Solo administradores pueden acceder a logs
    
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar","")
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")
    filtro_rol = request.args.get("rol","Todos")
    
    # Construir filtros SQL de manera segura
    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = " and le.titulo like ?"
    else:
        SQL_where_busqueda = " and a.usuario like ?"
    
    param_busqueda = f"%{busqueda}%"
    params = [param_busqueda]
    
    if filtro_rol == "Todos":
        SQL_where_rol = ""
    else:
        SQL_where_rol = " and r.rol = ?"
        params.append(filtro_rol)

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    libros_por_pagina = 10
    offset = (pagina - 1) * libros_por_pagina

    # Consulta para contar todos los libros
    query.execute(f"""select count(*) from logs_eliminados le 
                    join administradores a on le.id_administrador = a.id_administrador 
                    join roles r on a.id_rol = r.id_rol 
                    where tabla_afectada = 'Libros' {SQL_where_busqueda}{SQL_where_rol}""", params)
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
                            limit ? offset ?""")
    
    # Agregar parámetros de paginación
    params.extend([libros_por_pagina, offset])
    query.execute(query_busqueda, params)
    logs_libros = dict_factory(query)

    query.close()
    conexion.close()


    return render_template("libros_eliminados.html",logs=logs_libros,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)


# ----------------------------------------------------- Prestamos Eliminados ----------------------------------------------------- #

@bp_eliminados.route("/prestamos_e",methods = ["POST","GET"])
def prestamos_e():
    if "usuario" not in session:
        return redirect("/")
    
    if session.get("rol") != "Administrador":
        return redirect("/prestamos") #Solo administradores pueden acceder a logs
    
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
        return redirect("/")
    
    if session.get("rol") != "Administrador":
        return redirect("/prestamos") #Solo administradores pueden acceder a logs
    
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar","")
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")
    filtro_rol = request.args.get("rol","Todos")
    
    # Construir filtros SQL de manera segura
    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = " and le.titulo like ?"
    else:
        SQL_where_busqueda = " and a.usuario like ?"
    
    param_busqueda = f"%{busqueda}%"
    params = [param_busqueda]
    
    if filtro_rol == "Todos":
        SQL_where_rol = ""
    else:
        SQL_where_rol = " and r.rol = ?"
        params.append(filtro_rol)

    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    prestamos_por_pagina = 10
    offset = (pagina - 1) * prestamos_por_pagina

    # Consulta para contar todos los prestamos conforme a la busqueda
    query.execute(f"""select count(*) from logs_eliminados le 
                    join administradores a on le.id_administrador = a.id_administrador 
                    join roles r on a.id_rol = r.id_rol 
                    where tabla_afectada = 'Prestamos' {SQL_where_busqueda}{SQL_where_rol}""", params)
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
                            limit ? offset ?""")

    # Agregar parámetros de paginación
    params.extend([prestamos_por_pagina, offset])
    query.execute(query_busqueda, params)
    prestamos_eliminados = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("prestamos_eliminados.html",logs=prestamos_eliminados,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)


# ----------------------------------------------------- Visitantes Eliminados ----------------------------------------------------- #

@bp_eliminados.route("/visitantes_e",methods = ["POST","GET"])
def visitantes_e():
    if "usuario" not in session:
        return redirect("/")
    
    if session.get("rol") != "Administrador":
        return redirect("/prestamos") #Solo administradores pueden acceder a logs
    
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
        return redirect("/")
    
    if session.get("rol") != "Administrador":
        return redirect("/prestamos") #Solo administradores pueden acceder a logs
    
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar","")
    #Obtiene los datos del formulario filtros
    filtro_busqueda = request.args.get("filtro-busqueda","Usuario")
    filtro_rol = request.args.get("rol","Todos")
    
    # Construir filtros SQL de manera segura
    if filtro_busqueda == "Usuario":
        SQL_where_busqueda = " and a.usuario like ?"
        param_busqueda = f"%{busqueda}%"
        params = [param_busqueda]
    else:
        # Para cantidad, buscamos en ambos campos (hombres y mujeres)
        SQL_where_busqueda = " and (le.nombre_lector like ? or le.titulo like ?)"
        param_busqueda = f"%{busqueda}%"
        params = [param_busqueda, param_busqueda]
    
    if filtro_rol == "Todos":
        SQL_where_rol = ""
    else:
        SQL_where_rol = " and r.rol = ?"
        params.append(filtro_rol)

    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    visitantes_por_pagina = 10
    offset = (pagina - 1) * visitantes_por_pagina

    # Consulta para contar todos los visitantes conforme a la busqueda
    query.execute(f"""select count(*) from logs_eliminados le 
                    join administradores a on le.id_administrador = a.id_administrador 
                    join roles r on a.id_rol = r.id_rol 
                    where tabla_afectada = 'Visitantes' {SQL_where_busqueda}{SQL_where_rol}""", params)
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
                            limit ? offset ?""")

    # Agregar parámetros de paginación
    params.extend([visitantes_por_pagina, offset])
    query.execute(query_busqueda, params)
    visitantes_eliminados = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("visitantes_eliminados.html",logs=visitantes_eliminados,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)


# ----------------------------------------------------- Libros Modificados ----------------------------------------------------- #
@bp_eliminados.route("/libros_modificados",methods = ["POST","GET"])
def libros_modificados():
    if "usuario" not in session:
        return redirect("/")
    
    if session.get("rol") != "Administrador":
        return redirect("/prestamos") #Solo administradores pueden acceder a logs
    
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

    query_busqueda = (f"""select a.usuario, r.rol, strftime('%d-%m-%Y', lm.fecha_modificacion) as fecha, lm.motivo, lm.id_modificacion,
                            -- Datos antiguos (guardados en libros_modificados)
                            lm.titulo as old_titulo,
                            lm.tomo as old_tomo,
                            lm.num_paginas as old_num_paginas,
                            lm.num_copias as old_num_copias,
                            lm.portada as old_portada,
                            lm.ISBN_antiguo as old_isbn,
                            lm.ano_publicacion_antiguo as old_anio,
                            -- Datos actuales (de la tabla libros) - cantidad real incluyendo prestados
                            l.Titulo as titulo_actual, 
                            l.Tomo as tomo_actual, 
                            l.numero_paginas as num_paginas_actual, 
                            (l.numero_copias + COALESCE(prestados_activos.cantidad_prestada, 0)) as num_copias_actual, 
                            l.portada as portada_actual,
                            l.ISBN as isbn_actual,
                            l.ano_publicacion as anio_actual,
                            lm.id_libro,
                            -- Referencias antiguas de RegistroLibros
                            ed_old.editorial as old_editorial,
                            aut_old.nombre_autor || ' ' || aut_old.apellido_autor as old_autor,
                            not_old.notacion as old_notacion,
                            lug_old.lugar as old_lugar,
                            lm.codigo_seccion_antiguo || ' - ' || sd_old.seccion as old_seccion,
                            -- Referencias actuales de RegistroLibros
                            ed_new.editorial as editorial_actual,
                            aut_new.nombre_autor || ' ' || aut_new.apellido_autor as autor_actual,
                            not_new.notacion as notacion_actual,
                            lug_new.lugar as lugar_actual,
                            rl.codigo_seccion || ' - ' || sd_new.seccion as seccion_actual,
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
                            -- Subconsulta para contar préstamos activos por libro
                            left join (
                                SELECT id_libro, COUNT(*) as cantidad_prestada
                                FROM Prestamos 
                                WHERE id_estado IN (1, 2) -- Estados: Vencido y Activo
                                GROUP BY id_libro
                            ) prestados_activos ON prestados_activos.id_libro = l.id_libro
                            join RegistroLibros rl on rl.id_libro = l.id_libro
                            join Notaciones not_new on not_new.id_notacion = rl.id_notacion
                            join Editoriales ed_new on ed_new.id_editorial = not_new.id_editorial
                            join Autores aut_new on aut_new.id_autor = not_new.id_autor
                            join Lugares lug_new on lug_new.id_lugar = rl.id_lugar
                            join SistemaDewey sd_new on sd_new.codigo_seccion = rl.codigo_seccion
                            left join Notaciones not_old on not_old.id_notacion = lm.id_notacion_antigua
                            left join Editoriales ed_old on ed_old.id_editorial = lm.id_editorial_antigua
                            left join Autores aut_old on aut_old.id_autor = lm.id_autor_antiguo
                            left join Lugares lug_old on lug_old.id_lugar = lm.id_lugar_antiguo
                            left join SistemaDewey sd_old on sd_old.codigo_seccion = lm.codigo_seccion_antiguo
                            order by lm.fecha_modificacion desc, lm.id_modificacion desc
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
        return redirect("/")
    
    if session.get("rol") != "Administrador":
        return redirect("/prestamos") #Solo administradores pueden acceder a logs
    
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar","")
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")
    filtro_rol = request.args.get("rol","Todos")
    
    # Construir filtros SQL de manera segura
    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = " and lm.titulo like ?"
    else:
        SQL_where_busqueda = " and a.usuario like ?"
    
    param_busqueda = f"%{busqueda}%"
    params = [param_busqueda]
    
    if filtro_rol == "Todos":
        SQL_where_rol = ""
    else:
        SQL_where_rol = " and r.rol = ?"
        params.append(filtro_rol)

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    libros_por_pagina = 10
    offset = (pagina - 1) * libros_por_pagina

    # Consulta para contar todos los libros
    query.execute(f"""select count(*) from libros_modificados lm
                    join administradores a on lm.id_administrador = a.id_administrador 
                    join roles r on a.id_rol = r.id_rol 
                    join libros l on lm.id_libro = l.id_libro
                    where 1=1 {SQL_where_busqueda}{SQL_where_rol}""", params)
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina)

    query.execute(f"""select a.usuario, r.rol, strftime('%d-%m-%Y', lm.fecha_modificacion) as fecha, lm.motivo,
                            -- Datos antiguos (guardados en libros_modificados)
                            lm.titulo as old_titulo,
                            lm.tomo as old_tomo,
                            lm.num_paginas as old_num_paginas,
                            lm.num_copias as old_num_copias,
                            lm.portada as old_portada,
                            lm.ISBN_antiguo as old_isbn,
                            lm.ano_publicacion_antiguo as old_anio,
                            lm.id_modificacion, 
                            l.Titulo as titulo_actual, 
                            l.Tomo as tomo_actual, 
                            l.numero_paginas as num_paginas_actual, 
                            (l.numero_copias + COALESCE(prestados_activos.cantidad_prestada, 0)) as num_copias_actual, 
                            l.portada as portada_actual,
                            l.ISBN as isbn_actual,
                            l.ano_publicacion as anio_actual,
                            lm.id_libro,
                            ed_old.editorial as old_editorial,
                            aut_old.nombre_autor || ' ' || aut_old.apellido_autor as old_autor,
                            not_old.notacion as old_notacion,
                            lug_old.lugar as old_lugar,
                            lm.codigo_seccion_antiguo || ' - ' || sd_old.seccion as old_seccion,
                            ed_new.editorial as editorial_actual,
                            aut_new.nombre_autor || ' ' || aut_new.apellido_autor as autor_actual,
                            not_new.notacion as notacion_actual,
                            lug_new.lugar as lugar_actual,
                            rl.codigo_seccion || ' - ' || sd_new.seccion as seccion_actual,
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
                            -- Subconsulta para contar préstamos activos por libro
                            left join (
                                SELECT id_libro, COUNT(*) as cantidad_prestada
                                FROM Prestamos 
                                WHERE id_estado IN (1, 2) -- Estados: Vencido y Activo
                                GROUP BY id_libro
                            ) prestados_activos ON prestados_activos.id_libro = l.id_libro
                            -- Referencias actuales
                            join RegistroLibros rl on rl.id_libro = l.id_libro
                            join Notaciones not_new on not_new.id_notacion = rl.id_notacion
                            join Editoriales ed_new on ed_new.id_editorial = not_new.id_editorial
                            join Autores aut_new on aut_new.id_autor = not_new.id_autor
                            join Lugares lug_new on lug_new.id_lugar = rl.id_lugar
                            join SistemaDewey sd_new on sd_new.codigo_seccion = rl.codigo_seccion
                            left join Notaciones not_old on not_old.id_notacion = lm.id_notacion_antigua
                            left join Editoriales ed_old on ed_old.id_editorial = lm.id_editorial_antigua
                            left join Autores aut_old on aut_old.id_autor = lm.id_autor_antiguo
                            left join Lugares lug_old on lug_old.id_lugar = lm.id_lugar_antiguo
                            left join SistemaDewey sd_old on sd_old.codigo_seccion = lm.codigo_seccion_antiguo
                            where 1=1 {SQL_where_busqueda}{SQL_where_rol}
                            order by lm.fecha_modificacion desc
                            limit ? offset ?""")
    
    # Agregar parámetros de paginación
    params.extend([libros_por_pagina, offset])
    libros_m = dict_factory(query)

    query.close()
    conexion.close()
    return render_template("libros_modificados.html",logs=libros_m,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)

# ----------------------------------------------------- Revertir cambios ----------------------------------------------------- #
@bp_eliminados.route("/revertir_cambios/<int:id_modificacion>", methods=["POST"])
def revertir_cambios(id_modificacion):
    if "usuario" not in session:
        return redirect("/")
    
    if session.get("rol") != "Administrador":
        return redirect("/prestamos") #Solo administradores pueden acceder a logs
    
    conexion = conexion_BD()
    query = conexion.cursor()

    # Obtener los datos de la modificación a revertir (incluyendo nuevos campos)
    query.execute("""SELECT id_libro, titulo, tomo, num_paginas, num_copias, portada, 
                     ISBN_antiguo, ano_publicacion_antiguo,
                     id_notacion_antigua, id_editorial_antigua, id_autor_antiguo, 
                     id_lugar_antiguo, codigo_seccion_antiguo 
                     FROM libros_modificados WHERE id_modificacion = ?""", (id_modificacion,))
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
    antiguo_isbn = modificacion[6]
    antiguo_anio = modificacion[7]
    antigua_id_notacion = modificacion[8]
    antiguo_id_lugar = modificacion[11]
    antiguo_codigo_seccion = modificacion[12]

    # Obtener los datos actuales del libro y contar préstamos activos
    query.execute("""SELECT l.id_libro, l.titulo, l.tomo, l.numero_paginas, l.numero_copias, l.portada, 
                     l.ISBN, l.ano_publicacion,
                     COALESCE(prestados_activos.cantidad_prestada, 0) as prestados_activos
                     FROM libros l
                     LEFT JOIN (
                         SELECT id_libro, COUNT(*) as cantidad_prestada
                         FROM Prestamos 
                         WHERE id_estado IN (1, 2) -- Estados: Vencido y Activo
                         GROUP BY id_libro
                     ) prestados_activos ON prestados_activos.id_libro = l.id_libro
                     WHERE l.id_libro = ?""", (id_libro,))
    libro_actual = query.fetchone()

    if not libro_actual:
        query.close()
        conexion.close()
        return "Libro no encontrado", 404

    # Calcular la cantidad de ejemplares disponibles que debe quedar
    # Cantidad antigua - préstamos activos = ejemplares disponibles después de revertir
    prestamos_activos_count = libro_actual[8]
    ejemplares_disponibles_revertidos = antiguo_num_copias - prestamos_activos_count

    # Asegurar que no sea negativo
    if ejemplares_disponibles_revertidos < 0:
        ejemplares_disponibles_revertidos = 0

    # Revertir los cambios en la tabla Libros
    query.execute("""
        UPDATE libros
        SET Titulo = ?, Tomo = ?, numero_paginas = ?, numero_copias = ?, portada = ?,
            ISBN = ?, ano_publicacion = ?
        WHERE id_libro = ?
    """, (antiguo_titulo, antiguo_tomo, antiguo_num_paginas, ejemplares_disponibles_revertidos, 
          antigua_portada, antiguo_isbn, antiguo_anio, id_libro))

    # Revertir los cambios en RegistroLibros (si existen referencias antiguas)
    if antigua_id_notacion and antiguo_id_lugar and antiguo_codigo_seccion:
        query.execute("""
            UPDATE RegistroLibros
            SET id_notacion = ?, id_lugar = ?, codigo_seccion = ?
            WHERE id_libro = ?
        """, (antigua_id_notacion, antiguo_id_lugar, antiguo_codigo_seccion, id_libro))

    # Eliminar el registro de modificación
    query.execute("DELETE FROM libros_modificados WHERE id_modificacion = ?", (id_modificacion,))
    
    conexion.commit()
    query.close()
    conexion.close()

    return redirect(url_for('eliminados.libros_modificados'))