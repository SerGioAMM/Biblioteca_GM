from flask import Blueprint, session, redirect, request, render_template, url_for
from datetime import datetime
import math
from src.database.db_sqlite import conexion_BD, dict_factory

bp_visitantes = Blueprint('visitantes', __name__, template_folder="../templates")

# ----------------------------------------------------- REGISTRO VISITANTES ----------------------------------------------------- #

@bp_visitantes.route("/registro_visitantes", methods=["GET", "POST"])
def registro_visitantes():
    if "usuario" not in session:
        return redirect("/")  # Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("SELECT * FROM Tipos_Visitantes")
    tipos_visitantes = query.fetchall()
    
    query.execute("SELECT * FROM Rangos_Edad ORDER BY id_rango")
    rangos_edad = query.fetchall()

    # Verifica la acción que realiza el formulario en registro_visitantes.html
    if request.method == "POST":
        # Obtiene los datos del formulario en registro_visitantes.html
        cantidad_hombres = request.form["cantidad_hombres"]
        cantidad_mujeres = request.form["cantidad_mujeres"]
        tipo_visitante = request.form["tipo_visitante"]
        id_rango_edad = request.form["id_rango_edad"]
        fecha = request.form["fecha"]
        
        # Si el usuario eligió "nuevo", crear el nuevo tipo
        if tipo_visitante == "nuevo":
            nuevo_tipo = request.form.get("nuevo_tipo_visitante", "").strip()
            if not nuevo_tipo:
                alerta = "Debe ingresar el nombre del nuevo tipo de visitante."
                return render_template("registro_visitantes.html", tipos_visitantes=tipos_visitantes, rangos_edad=rangos_edad, alerta=alerta)
            
            try:
                # Verificar si el tipo ya existe
                query.execute("SELECT id_tipo_visitante FROM Tipos_Visitantes WHERE tipo_visitante = ?", (nuevo_tipo,))
                tipo_existente = query.fetchone()
                
                if tipo_existente:
                    tipo_visitante = tipo_existente[0]
                else:
                    # Insertar el nuevo tipo
                    query.execute("INSERT INTO Tipos_Visitantes (tipo_visitante) VALUES (?)", (nuevo_tipo,))
                    conexion.commit()
                    tipo_visitante = query.lastrowid
                    
                    # Notificación
                    from src.usuarios.routes.usuarios import crear_notificacion
                    crear_notificacion(f"{session['rol']} {session['usuario']} ha creado un nuevo tipo de visitante: {nuevo_tipo}")
            except Exception as e:
                alerta = f"Error al crear el nuevo tipo de visitante: {str(e)}"
                return render_template("registro_visitantes.html", tipos_visitantes=tipos_visitantes, rangos_edad=rangos_edad, alerta=alerta)

        try:
            # INSERT DE VISITANTES
            query.execute("""INSERT INTO Visitantes(cantidad_hombres, cantidad_mujeres, id_tipo_visitante, id_rango_edad, fecha)
                            VALUES (?,?,?,?,?)""", (cantidad_hombres, cantidad_mujeres, tipo_visitante, id_rango_edad, fecha))

            # Guardar cambios
            conexion.commit()
            
            # Crear notificación
            from src.usuarios.routes.usuarios import crear_notificacion
            total_visitantes = int(cantidad_hombres) + int(cantidad_mujeres)
            crear_notificacion(f"{session['rol']} {session['usuario']} ha registrado {total_visitantes} visitantes.")
            
            registro_exitoso = "El registro de visitantes se completó exitosamente."
            return render_template("registro_visitantes.html", tipos_visitantes=tipos_visitantes, rangos_edad=rangos_edad, registro_exitoso=registro_exitoso)

        except Exception as e:
            alerta = f"Error al registrar visitantes: {str(e)}"
            return render_template("registro_visitantes.html", tipos_visitantes=tipos_visitantes, rangos_edad=rangos_edad, alerta=alerta)
        finally:
            query.close()
            conexion.close()

    return render_template("registro_visitantes.html", tipos_visitantes=tipos_visitantes, rangos_edad=rangos_edad)

# ----------------------------------------------------- VISITANTES ----------------------------------------------------- #

@bp_visitantes.route("/visitantes", methods=["POST", "GET"])
def visitantes():
    if "usuario" not in session:
        return redirect("/")  # Solo se puede acceder con session iniciada
    
    exito = request.args.get("exito", "")

    conexion = conexion_BD()
    query = conexion.cursor()

    #Paginacion
    pagina = request.args.get("page", 1, type=int)
    visitantes_por_pagina = 100
    offset = (pagina - 1) * visitantes_por_pagina

    # Obtener rangos de edad para el filtro
    query.execute("SELECT * FROM Rangos_Edad ORDER BY id_rango")
    rangos_edad = dict_factory(query)

    # Obtener tipos de visitantes para el filtro
    query.execute("SELECT * FROM Tipos_Visitantes ORDER BY tipo_visitante")
    tipos_visitantes = dict_factory(query)

    # Consulta para contar todos los visitantes
    query.execute("SELECT COUNT(*) FROM Visitantes")
    total_visitantes = query.fetchone()[0]
    total_paginas = math.ceil(total_visitantes / visitantes_por_pagina)

    query.execute("""SELECT v.id_registro, v.cantidad_hombres, v.cantidad_mujeres, 
                        (v.cantidad_hombres + v.cantidad_mujeres) as total,
                        tv.tipo_visitante, re.rango as rango_edad, v.fecha
                        FROM Visitantes v
                        JOIN Tipos_Visitantes tv ON v.id_tipo_visitante = tv.id_tipo_visitante
                        LEFT JOIN Rangos_Edad re ON v.id_rango_edad = re.id_rango
                        ORDER BY v.fecha DESC
                        LIMIT ? OFFSET ?""", (visitantes_por_pagina, offset))
    visitantes = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("visitantes.html", visitantes=visitantes, exito=exito, 
                          pagina=pagina, total_paginas=total_paginas, 
                          fecha_inicio="", fecha_fin="", rango_edad_seleccionado="",
                          tipo_visitante_seleccionado="",
                          rangos_edad=rangos_edad, tipos_visitantes=tipos_visitantes)

# ----------------------------------------------------- ELIMINAR VISITANTE ----------------------------------------------------- #

@bp_visitantes.route("/eliminar_visitante", methods=["GET", "POST"])
def eliminar_visitante():
    id_registro = request.form["id_registro"]
    id_administrador = session.get("id_administrador")
    motivo = request.form["motivo"]

    conexion = conexion_BD()
    query = conexion.cursor()

    # Primero obtener los datos del visitante antes de eliminarlo
    query.execute("SELECT cantidad_hombres, cantidad_mujeres FROM Visitantes WHERE id_registro = ?", (id_registro,))
    visitante_data = query.fetchone()
    
    if visitante_data:
        cantidad_hombres = visitante_data[0]
        cantidad_mujeres = visitante_data[1]
        
        # Insertar en logs usando los campos disponibles (nombre_lector para hombres, titulo para mujeres)
        query.execute("INSERT INTO logs_eliminados(id_administrador, id_eliminado, tabla_afectada, nombre_lector, titulo, fecha, motivo) VALUES(?,?,'Visitantes',?,?,datetime('now','localtime'),?)", 
                        (id_administrador, id_registro, cantidad_hombres, cantidad_mujeres, motivo))
        
        # Eliminar el registro
        query.execute("DELETE FROM Visitantes WHERE id_registro = ?", (id_registro,))
        
        conexion.commit()
        
        # Crear notificación
        from src.usuarios.routes.usuarios import crear_notificacion
        total_eliminados = cantidad_hombres + cantidad_mujeres
        crear_notificacion(f"{session['rol']} {session['usuario']} ha eliminado un registro de {cantidad_hombres} hombres y {cantidad_mujeres} mujeres (Total: {total_eliminados}).")
        
        exito = "Registro de visitantes eliminado exitosamente."
    else:
        exito = "Error: No se encontró el registro de visitantes."

    query.close()
    conexion.close()

    return redirect(url_for("visitantes.visitantes", exito=exito))

# ----------------------------------------------------- BUSCAR VISITANTES ----------------------------------------------------- #

@bp_visitantes.route("/buscar_visitante", methods=["GET", "POST"])
def buscar_visitante():
    if "usuario" not in session:
        return redirect("/")  # Solo se puede acceder con session iniciada
    
    exito = request.args.get("exito", "")
    
    conexion = conexion_BD()
    query = conexion.cursor()

    # Obtener rangos de edad para el filtro
    query.execute("SELECT * FROM Rangos_Edad ORDER BY id_rango")
    rangos_edad = dict_factory(query)

    # Obtener tipos de visitantes para el filtro
    query.execute("SELECT * FROM Tipos_Visitantes ORDER BY tipo_visitante")
    tipos_visitantes = dict_factory(query)

    fecha_inicio = request.args.get("fecha_inicio", "")
    fecha_fin = request.args.get("fecha_fin", "")
    rango_edad_seleccionado = request.args.get("rango_edad", "")
    tipo_visitante_seleccionado = request.args.get("tipo_visitante", "")
    
    #Paginacion
    pagina = request.args.get("page", 1, type=int)
    visitantes_por_pagina = 100
    offset = (pagina - 1) * visitantes_por_pagina
    
    SQL_where_fecha = ""
    if fecha_inicio and fecha_fin:
        # Validar que fecha_inicio no sea mayor que fecha_fin
        if fecha_inicio <= fecha_fin:
            fecha_inicio_completa = fecha_inicio + "-01"  # Primer día del mes
            # Para fecha_fin, necesitamos el último día del mes
            import calendar
            from datetime import datetime
            año, mes = map(int, fecha_fin.split('-'))
            ultimo_dia = calendar.monthrange(año, mes)[1]
            fecha_fin_completa = f"{fecha_fin}-{ultimo_dia:02d}"
            SQL_where_fecha = f"AND v.fecha BETWEEN '{fecha_inicio_completa}' AND '{fecha_fin_completa}'"
    elif fecha_inicio:
        fecha_inicio_completa = fecha_inicio + "-01"
        SQL_where_fecha = f"AND v.fecha >= '{fecha_inicio_completa}'"
    elif fecha_fin:
        import calendar
        from datetime import datetime
        año, mes = map(int, fecha_fin.split('-'))
        ultimo_dia = calendar.monthrange(año, mes)[1]
        fecha_fin_completa = f"{fecha_fin}-{ultimo_dia:02d}"
        SQL_where_fecha = f"AND v.fecha <= '{fecha_fin_completa}'"
    
    # Filtro de rango de edad
    SQL_where_rango = ""
    if rango_edad_seleccionado:
        SQL_where_rango = f"AND v.id_rango_edad = {rango_edad_seleccionado}"
    
    # Filtro de tipo de visitante
    SQL_where_tipo = ""
    if tipo_visitante_seleccionado:
        SQL_where_tipo = f"AND v.id_tipo_visitante = {tipo_visitante_seleccionado}"

    # Consulta para contar visitantes con filtros
    query_count = f"""SELECT COUNT(*) FROM Visitantes v
                        JOIN Tipos_Visitantes tv ON v.id_tipo_visitante = tv.id_tipo_visitante
                        LEFT JOIN Rangos_Edad re ON v.id_rango_edad = re.id_rango
                        WHERE 1=1 {SQL_where_fecha} {SQL_where_rango} {SQL_where_tipo}"""
    query.execute(query_count)
    total_visitantes = query.fetchone()[0]
    total_paginas = math.ceil(total_visitantes / visitantes_por_pagina)

    query_busqueda = f"""SELECT v.id_registro, v.cantidad_hombres, v.cantidad_mujeres, 
                            (v.cantidad_hombres + v.cantidad_mujeres) as total,
                            tv.tipo_visitante, re.rango as rango_edad, v.fecha
                            FROM Visitantes v
                            JOIN Tipos_Visitantes tv ON v.id_tipo_visitante = tv.id_tipo_visitante
                            LEFT JOIN Rangos_Edad re ON v.id_rango_edad = re.id_rango
                            WHERE 1=1 {SQL_where_fecha} {SQL_where_rango} {SQL_where_tipo}
                            ORDER BY v.fecha DESC
                            LIMIT {visitantes_por_pagina} OFFSET {offset}"""

    query.execute(query_busqueda)
    visitantes = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("visitantes.html", visitantes=visitantes, exito=exito, 
                            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
                            rango_edad_seleccionado=rango_edad_seleccionado,
                            tipo_visitante_seleccionado=tipo_visitante_seleccionado,
                            rangos_edad=rangos_edad, tipos_visitantes=tipos_visitantes,
                            pagina=pagina, total_paginas=total_paginas)