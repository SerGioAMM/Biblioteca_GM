from flask import Blueprint, session, redirect, request,render_template,url_for
from datetime import datetime,date
import math
from src.database.db_sqlite import conexion_BD,dict_factory

bp_prestamos = Blueprint('prestamos',__name__, template_folder="../templates")

from src.prestamos.models import prestamos_model
# ----------------------------------------------------- Verificar prestamos vencidos ----------------------------------------------------- #

def verificar_vencidos():
    conexion = conexion_BD()
    query = conexion.cursor()
    # Obtenre la fecha actual
    hoy = datetime.today().date()

    # Buscar prestamos para verificar si estan vencidos
    query.execute("""select id_prestamo, fecha_entrega_estimada
                    from Prestamos
                    where id_estado = 2""")  # Solo prestamos que esten activos (no revisaremos los que ya esten devueltos o vencidos)
    prestamos_para_verificar = query.fetchall()

    #Verifica que si existan prestamos activos
    if prestamos_para_verificar:
        # for para revisar cada prestamo
        for prestamo in prestamos_para_verificar:
            id_prestamo = prestamo[0]
            fecha_entrega_estimada = datetime.strptime(prestamo[1], "%Y-%m-%d").date()

            #Actualiza el estado de los prestamos a vencidos cuando se pasan dela fecha estimada de entrega
            if fecha_entrega_estimada < hoy:
                query.execute("""update Prestamos
                                set id_estado = 1
                                where id_prestamo = ?""", (id_prestamo,)) #Establece estado vencido
                conexion.commit()  # Guardamos los cambios

    query.close()
    conexion.close()

# ----------------------------------------------------- PRESTAMOS ----------------------------------------------------- #

@bp_prestamos.route("/prestamos",methods = ["GET","POST"])
def prestamos():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    estados = request.args.get("estados", "Todos")
    exito = request.args.get("exito","")
    devuelto = request.args.get("devuelto","")

    verificar_vencidos()

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    prestamos_por_pagina = 10
    offset = (pagina - 1) * prestamos_por_pagina

    # Consulta para contar todos los libros
    query.execute("select count(*) from prestamos")
    total_prestamos = query.fetchone()[0]
    total_paginas = math.ceil(total_prestamos / prestamos_por_pagina)

    prestamos = prestamos_model.get_prestamos(prestamos_por_pagina,offset)

    query.close()
    conexion.close()

    return render_template("prestamos.html",prestamos=prestamos,estados=estados,pagina=pagina,total_paginas=total_paginas,
                            exito = exito, devuelto = devuelto)

# ----------------------------------------------------- BUSCAR Prestamo ----------------------------------------------------- #

@bp_prestamos.route("/buscar_prestamo", methods = ["GET"])
def buscar_prestamo():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar","")  # Cambiado de "buscar_prestamo" a "buscar"
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")
    estados = request.args.get("estados","Todos")
    exito = request.args.get("exito","")
    devuelto = request.args.get("devuelto","")

    # Construir filtros SQL de manera segura con parámetros
    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = " where l.titulo || ' (' || p.nombre || ' ' || p.apellido || ')' like ?"
    else:
        SQL_where_busqueda = " where p.nombre || ' ' || p.apellido like ?"
    
    param_busqueda = f"%{busqueda}%"
    
    if estados == "Todos":
        SQL_where_estado = " "
        param_estado = None
    else:
        SQL_where_estado = " and e.estado = ?"
        param_estado = estados

    # Preparar lista de parámetros
    params_count = [param_busqueda]
    params_query = [param_busqueda]
    if param_estado is not None:
        params_count.append(param_estado)
        params_query.append(param_estado)

    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    prestamos_por_pagina = 10
    offset = (pagina - 1) * prestamos_por_pagina

    # Consulta para contar todos los libros conforme a la busqueda
    query.execute(f"""select count(*) from Prestamos p
                    join Libros l on p.id_libro = l.id_libro
                    join Estados_prestamos e on p.id_estado = e.id_estado 
                    {SQL_where_busqueda}{SQL_where_estado}""", params_count)
    
    total_prestamos = query.fetchone()[0]
    total_paginas = math.ceil(total_prestamos / prestamos_por_pagina) #Calculo para cantidad de paginas, redondeando hacia arriba (ej, 2.1 = 3)

    query_busqueda = (f"""select (strftime('%d', p.fecha_prestamo)||' de '||
                    CASE strftime('%m', p.fecha_prestamo) 
                    WHEN '01' THEN 'Enero'
                    WHEN '02' THEN 'Febrero'
                    WHEN '03' THEN 'Marzo'
                    WHEN '04' THEN 'Abril'
                    WHEN '05' THEN 'Mayo'
                    WHEN '06' THEN 'Junio'
                    WHEN '07' THEN 'Julio'
                    WHEN '08' THEN 'Agosto'
                    WHEN '09' THEN 'Septiembre'
                    WHEN '10' THEN 'Octubre'
                    WHEN '11' THEN 'Noviembre'
                    WHEN '12' THEN 'Diciembre'
                    END || ' de ' ||strftime('%Y', p.fecha_prestamo)) as fecha_prestamo, 
                    strftime('%d', p.fecha_entrega_estimada) as dia_estimado,
                    CASE strftime('%m',p.fecha_entrega_estimada)
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
                    END as mes_estimado,
                    (strftime('%d', p.fecha_entrega_estimada)||' de '||
                    CASE strftime('%m', p.fecha_entrega_estimada) 
                    WHEN '01' THEN 'Enero'
                    WHEN '02' THEN 'Febrero'
                    WHEN '03' THEN 'Marzo'
                    WHEN '04' THEN 'Abril'
                    WHEN '05' THEN 'Mayo'
                    WHEN '06' THEN 'Junio'
                    WHEN '07' THEN 'Julio'
                    WHEN '08' THEN 'Agosto'
                    WHEN '09' THEN 'Septiembre'
                    WHEN '10' THEN 'Octubre'
                    WHEN '11' THEN 'Noviembre'
                    WHEN '12' THEN 'Diciembre'
                    END || ' de ' ||strftime('%Y', p.fecha_entrega_estimada)) as fecha_estimada,
                    (strftime('%d', p.fecha_devolucion)||' de '||
                    CASE strftime('%m', p.fecha_devolucion) 
                    WHEN '01' THEN 'Enero'
                    WHEN '02' THEN 'Febrero'
                    WHEN '03' THEN 'Marzo'
                    WHEN '04' THEN 'Abril'
                    WHEN '05' THEN 'Mayo'
                    WHEN '06' THEN 'Junio'
                    WHEN '07' THEN 'Julio'
                    WHEN '08' THEN 'Agosto'
                    WHEN '09' THEN 'Septiembre'
                    WHEN '10' THEN 'Octubre'
                    WHEN '11' THEN 'Noviembre'
                    WHEN '12' THEN 'Diciembre'
                    END || ' de ' ||strftime('%Y', p.fecha_devolucion)) as fecha_devolucion, 
                    p.fecha_entrega_estimada as f_estimada, p.fecha_devolucion as f_devolucion,
                    l.Titulo, p.nombre, p.apellido, p.dpi_usuario, p.num_telefono,  p.direccion, e.estado, p.id_prestamo, l.id_libro, p.observaciones_devolucion
                    from Prestamos p
                    join Libros l on p.id_libro = l.id_libro
                    join Estados_prestamos e on p.id_estado = e.id_estado
                    {SQL_where_busqueda}{SQL_where_estado}
                    order by e.id_estado asc, p.fecha_prestamo desc
                    limit ? offset ?""")

    # Agregar parámetros de paginación
    params_query.extend([prestamos_por_pagina, offset])
    
    query.execute(query_busqueda, params_query)
    prestamos = dict_factory(query)

    for p in prestamos:
        fecha_estimada = datetime.strptime(p['f_estimada'], "%Y-%m-%d").date()
        fecha_devolucion = None
        if p['f_devolucion']:
            fecha_devolucion = datetime.strptime(p['f_devolucion'], "%Y-%m-%d").date()

        hoy = date.today()

        if (not fecha_devolucion and hoy > fecha_estimada) or (fecha_devolucion and fecha_devolucion > fecha_estimada):
            p['vencido'] = True
        else:
            p['vencido'] = False

    query.execute("Select Count(*) from prestamos where id_estado = 1") #Prestamos vencidos
    prestamos_vencidos = query.fetchone()[0]

    query.execute("Select Count(*) from prestamos where id_estado = 2") #Prestamos activos
    prestamos_activos = query.fetchone()[0]

    query.execute("Select Count(*) from prestamos where id_estado = 3") #Prestamos devueltos
    prestamos_devueltos = query.fetchone()[0]


    query.close()
    conexion.close()

    return render_template("prestamos.html",prestamos=prestamos,estados=estados,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda,
                            prestamos_activos=prestamos_activos,prestamos_devueltos=prestamos_devueltos,prestamos_vencidos=prestamos_vencidos,
                            exito = exito, devuelto = devuelto)

# ----------------------------------------------------- Devolver Prestamo ----------------------------------------------------- #

@bp_prestamos.route("/devolver_prestamo", methods=["POST"])
def devolver_prestamo():
    id_prestamo = request.form["id_prestamo"]
    observaciones = request.form["observaciones_devolucion"]

    print("TEST DEVOLUCION BUG")
    print(id_prestamo)

    # Obtenre la fecha actual
    hoy = datetime.today().date()

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("update prestamos set fecha_devolucion = (?) where id_prestamo = (?)",(hoy,id_prestamo,))

    #Actualiza el prestamo a estado 3 (devuelto)
    query.execute("update prestamos set id_estado = 3 where id_prestamo = (?)",(id_prestamo,))

    # Guarda las observaciones de la devolucion
    query.execute("update prestamos set observaciones_devolucion = (?) where id_prestamo = (?)",(observaciones,id_prestamo,))

    query.execute("select id_libro from prestamos where id_prestamo = ?",(id_prestamo,))
    id_libro = query.fetchone()[0]

    query.execute("update libros set numero_copias = (numero_copias + 1) where id_libro = ?",(id_libro,))
    conexion.commit()

    # Crear notificación
    from src.usuarios.routes.usuarios import crear_notificacion
    query.execute("SELECT (nombre || ' ' || apellido) FROM prestamos WHERE id_prestamo = ?", (id_prestamo,))
    nombre_lector = query.fetchone()[0]
    crear_notificacion(f"{session['rol']} {session['usuario']} ha registrado la devolución del préstamo de {nombre_lector}.")

    query.close()
    conexion.close()

    devuelto = "Libro devuelto exitósamente."

    return redirect(url_for("prestamos.prestamos",devuelto=devuelto))

# ----------------------------------------------------- Renovar Prestamo ----------------------------------------------------- #

@bp_prestamos.route("/renovar_prestamo", methods=["POST"])
def renovar_prestamo():
    if "usuario" not in session:
        return redirect("/")
    
    id_prestamo_anterior = request.form["id_prestamo"]
    id_libro = request.form["id_libro"]
    
    conexion = conexion_BD()
    query = conexion.cursor()
    
    try:
        # Obtener datos del préstamo anterior
        query.execute("""SELECT dpi_usuario, nombre, apellido, direccion, num_telefono, grado, fecha_entrega_estimada
                        FROM Prestamos WHERE id_prestamo = ?""", (id_prestamo_anterior,))
        prestamo_data = query.fetchone()
        
        if not prestamo_data:
            alerta = "No se encontró el préstamo."
            return redirect(url_for("prestamos.prestamos", alerta=alerta))
        
        dpi, nombre, apellido, direccion, telefono, grado, fecha_estimada_anterior = prestamo_data
        
        # Verificar si el libro existe y tiene al menos 1 copia
        query.execute("SELECT numero_copias, titulo FROM Libros WHERE id_libro = ?", (id_libro,))
        libro_data = query.fetchone()
        
        if not libro_data:
            alerta = "El libro no existe."
            return redirect(url_for("prestamos.prestamos", alerta=alerta))
        
        numero_copias, titulo_libro = libro_data
        
        if numero_copias < 1:
            alerta = "No hay copias disponibles de este libro para renovar."
            return redirect(url_for("prestamos.prestamos", alerta=alerta))
        
        # Agregar observación al préstamo anterior
        observacion_renovacion = "Préstamo renovado"
        query.execute("""UPDATE Prestamos SET observaciones_devolucion = ? 
                        WHERE id_prestamo = ?""", (observacion_renovacion, id_prestamo_anterior))
        
        # Calcular nueva fecha de préstamo y entrega
        from datetime import timedelta
        hoy = datetime.today().date()

        # Actualizar estado del préstamo anterior a devuelto
        query.execute("UPDATE Prestamos SET id_estado = 3, fecha_devolucion = ? WHERE id_prestamo = ?", (hoy, id_prestamo_anterior))

        # Calcular duración del préstamo anterior para mantener la misma duración
        fecha_prestamo_anterior = datetime.strptime(fecha_estimada_anterior, "%Y-%m-%d").date()
        dias_prestamo = 7  # Duración predeterminada de 7 días
        nueva_fecha_entrega = hoy + timedelta(days=dias_prestamo)
        
        # Crear nuevo préstamo
        query.execute("""INSERT INTO Prestamos
                        (dpi_usuario, nombre, apellido, direccion, num_telefono, id_libro, grado, id_estado, 
                        fecha_prestamo, fecha_entrega_estimada, fecha_devolucion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 2, ?, ?, NULL)""",
                        (dpi, nombre, apellido, direccion, telefono, id_libro, grado, hoy, nueva_fecha_entrega))
        
        # Reducir número de copias disponibles
        #query.execute("UPDATE Libros SET numero_copias = (numero_copias - 1) WHERE id_libro = ?", (id_libro,))
        
        conexion.commit()
        
        # Crear notificación
        from src.usuarios.routes.usuarios import crear_notificacion
        crear_notificacion(f"{session['rol']} {session['usuario']} ha renovado el préstamo de {nombre} {apellido} para el libro: {titulo_libro}.")
        
        exito = "Préstamo renovado exitósamente."
        return redirect(url_for("prestamos.prestamos", exito=exito))
        
    except Exception as e:
        print(f"Error al renovar préstamo: {e}")
        alerta = "Error al renovar el préstamo."
        return redirect(url_for("prestamos.prestamos", alerta=alerta))
    finally:
        query.close()
        conexion.close()

# ----------------------------------------------------- Eliminar Prestamo ----------------------------------------------------- #

@bp_prestamos.route("/eliminar_prestamo", methods=["GET", "POST"])
def eliminar_prestamo():
    id_prestamo = request.form["id_prestamo"]
    motivo = request.form["motivo_eliminacion"]
    id_administrador = session.get("id_administrador")

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select (nombre || ' ' || apellido) from prestamos where id_prestamo = ?",(id_prestamo,))
    lector = query.fetchone()[0]

    query.execute("select l.titulo from libros l join prestamos p on l.id_libro = p.id_libro where p.id_prestamo = ?",(id_prestamo,))
    libro = query.fetchone()[0]

    query.execute("insert into logs_eliminados(id_administrador,id_eliminado,tabla_afectada,fecha,nombre_lector,titulo,motivo) values(?,?,'Prestamos',datetime('now','localtime'),?,?,?)",(id_administrador,id_prestamo,lector,libro,motivo))

    query.execute("delete from prestamos where id_prestamo = ?",(id_prestamo,))
    conexion.commit()

    # Crear notificación
    from src.usuarios.routes.usuarios import crear_notificacion
    crear_notificacion(f"{session['rol']} {session['usuario']} ha eliminado el préstamo de {lector} para el libro: {libro}.")

    query.close()
    conexion.close()

    exito = "Préstamo eliminado exitósamente."

    return redirect(url_for("prestamos.prestamos",exito=exito))

# ----------------------------------------------------- REGISTRO PRESTAMOS ----------------------------------------------------- #

@bp_prestamos.route("/registro_prestamos", methods=["GET", "POST"])
def registro_prestamos():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

        #Verifica la accion que realiza el formulario en registro-prestamos.html
    if request.method == "POST":
        #Obtiene los datos del formulario en registro-prestamos.html
        DPI = request.form["DPI"]
        NombreLector = request.form["nombre_lector"]
        ApellidoLector = request.form["apellido_lector"]
        Direccion = request.form["direccion"]
        Telefono = request.form["num_telefono"]
        Libro = request.form["libro"]
        GradoEstudio = request.form["grado"]
        fecha_prestamo = request.form["fecha_prestamo"]
        fecha_entrega_estimada = request.form["fecha_entrega_estimada"]
        Estado = 2 #Activo
        
        # Validaciones de fechas
        from datetime import timedelta
        
        try:
            fecha_prest_obj = datetime.strptime(fecha_prestamo, '%Y-%m-%d')
            fecha_entrega_obj = datetime.strptime(fecha_entrega_estimada, '%Y-%m-%d')
            hoy = datetime.now().date()
            
            # Validar que fecha de préstamo no sea mayor a hoy
            if fecha_prest_obj.date() > hoy:
                alerta = "La fecha de préstamo no puede ser posterior a hoy."
                return render_template("registro_prestamos.html", alerta=alerta,
                        DPI=DPI, nombre_lector=NombreLector, apellido_lector=ApellidoLector,
                        direccion=Direccion, num_telefono=Telefono, libro=Libro,
                        grado=GradoEstudio, fecha_prestamo=fecha_prestamo,
                        fecha_entrega_estimada=fecha_entrega_estimada)
            
            # Validar que fecha de entrega no sea antes de fecha de préstamo
            if fecha_entrega_obj < fecha_prest_obj:
                alerta = "La fecha límite de entrega debe ser igual o posterior a la fecha de préstamo."
                return render_template("registro_prestamos.html", alerta=alerta,
                        DPI=DPI, nombre_lector=NombreLector, apellido_lector=ApellidoLector,
                        direccion=Direccion, num_telefono=Telefono, libro=Libro,
                        grado=GradoEstudio, fecha_prestamo=fecha_prestamo,
                        fecha_entrega_estimada=fecha_entrega_estimada)
                        
        except ValueError:
            alerta = "Formato de fecha inválido. Por favor, use el selector de fechas."
            return render_template("registro_prestamos.html", alerta=alerta,
                    DPI=DPI, nombre_lector=NombreLector, apellido_lector=ApellidoLector,
                    direccion=Direccion, num_telefono=Telefono, libro=Libro,
                    grado=GradoEstudio, fecha_prestamo=fecha_prestamo,
                    fecha_entrega_estimada=fecha_entrega_estimada)
            
        try:
            # Verificar si el libro existe y tiene al menos 1 copia
            query.execute("select id_libro, numero_copias from Libros where (titulo || '(' || ano_publicacion || ')') = ?", (Libro,))
            libro_data = query.fetchone()

            if libro_data is None:
                # El libro no existe
                alerta = "El libro no existe."
                return render_template("registro_prestamos.html", alerta=alerta,
                        DPI=DPI, nombre_lector=NombreLector, apellido_lector=ApellidoLector,
                        direccion=Direccion, num_telefono=Telefono, libro=Libro,
                        grado=GradoEstudio, fecha_prestamo=fecha_prestamo,
                        fecha_entrega_estimada=fecha_entrega_estimada)

            id_libro, numero_copias = libro_data

            if numero_copias < 1:
                # No hay copias disponibles
                alerta = "No hay copias disponibles de este libro"
                return render_template("registro_prestamos.html", alerta=alerta,
                    DPI=DPI, nombre_lector=NombreLector, apellido_lector=ApellidoLector,
                    direccion=Direccion, num_telefono=Telefono, libro=Libro,
                    grado=GradoEstudio, fecha_prestamo=fecha_prestamo,
                    fecha_entrega_estimada=fecha_entrega_estimada)
            
            #? INSERT DE PRESTAMOS
            query.execute(f"""Insert into Prestamos
                    (dpi_usuario,nombre,apellido,direccion,num_telefono,id_libro,grado,id_estado,fecha_prestamo,fecha_entrega_estimada,fecha_devolucion)
                    values (?,?,?,?,?,?,?,?,?,?,NULL)""",
                    (DPI,NombreLector,ApellidoLector,Direccion,Telefono,id_libro,GradoEstudio,Estado,fecha_prestamo,fecha_entrega_estimada))

            query.execute(f"update Libros set numero_copias = (numero_copias-1) where id_libro = ?",(id_libro,))

            #? Guardar cambios
            conexion.commit()  

            # Crear notificación
            from src.usuarios.routes.usuarios import crear_notificacion
            crear_notificacion(f"{session['rol']} {session['usuario']} ha creado un nuevo préstamo para {NombreLector} {ApellidoLector}.")

            registro_exitoso = "Préstamo registrado exitósamente."

            return render_template("registro_prestamos.html", registro_exitoso=registro_exitoso)
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            query.close()
            conexion.close()


    return render_template("registro_prestamos.html")

