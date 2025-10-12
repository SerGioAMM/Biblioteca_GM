from flask import Blueprint, session, redirect, request, render_template, url_for
from datetime import datetime
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

    # Verifica la acción que realiza el formulario en registro_visitantes.html
    if request.method == "POST":
        # Obtiene los datos del formulario en registro_visitantes.html
        cantidad_hombres = request.form["cantidad_hombres"]
        cantidad_mujeres = request.form["cantidad_mujeres"]
        tipo_visitante = request.form["tipo_visitante"]
        fecha = request.form["fecha"]

        try:
            # INSERT DE VISITANTES
            query.execute("""INSERT INTO Visitantes(cantidad_hombres, cantidad_mujeres, id_tipo_visitante, fecha)
                            VALUES (?,?,?,?)""", (cantidad_hombres, cantidad_mujeres, tipo_visitante, fecha))

            # Guardar cambios
            conexion.commit()
            
            registro_exitoso = "El registro de visitantes se completó exitosamente."
            return render_template("registro_visitantes.html", tipos_visitantes=tipos_visitantes, registro_exitoso=registro_exitoso)

        except Exception as e:
            alerta = f"Error al registrar visitantes: {str(e)}"
            return render_template("registro_visitantes.html", tipos_visitantes=tipos_visitantes, alerta=alerta)
        finally:
            query.close()
            conexion.close()

    return render_template("registro_visitantes.html", tipos_visitantes=tipos_visitantes)

# ----------------------------------------------------- VISITANTES ----------------------------------------------------- #

@bp_visitantes.route("/visitantes", methods=["POST", "GET"])
def visitantes():
    if "usuario" not in session:
        return redirect("/")  # Solo se puede acceder con session iniciada
    
    exito = request.args.get("exito", "")

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""SELECT v.id_registro, v.cantidad_hombres, v.cantidad_mujeres, 
                            (v.cantidad_hombres + v.cantidad_mujeres) as total,
                            tv.tipo_visitante, v.fecha
                     FROM Visitantes v
                     JOIN Tipos_Visitantes tv ON v.id_tipo_visitante = tv.id_tipo_visitante
                     ORDER BY v.fecha DESC""")
    visitantes = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("visitantes.html", visitantes=visitantes, exito=exito)

# ----------------------------------------------------- ELIMINAR VISITANTE ----------------------------------------------------- #

@bp_visitantes.route("/eliminar_visitante", methods=["GET", "POST"])
def eliminar_visitante():
    id_registro = request.form["id_registro"]
    id_administrador = session.get("id_administrador")
    motivo = request.form["motivo"]

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("DELETE FROM Visitantes WHERE id_registro = ?", (id_registro,))
    query.execute("INSERT INTO logs_eliminados(id_administrador, id_eliminado, tabla_afectada, fecha, motivo) VALUES(?,?,'Visitantes',datetime('now'),?)", 
                  (id_administrador, id_registro, motivo))

    conexion.commit()

    query.close()
    conexion.close()

    exito = "Registro de visitante eliminado exitosamente."

    return redirect(url_for("visitantes.visitantes", exito=exito))

# ----------------------------------------------------- BUSCAR VISITANTES ----------------------------------------------------- #

@bp_visitantes.route("/buscar_visitante", methods=["GET", "POST"])
def buscar_visitante():
    if "usuario" not in session:
        return redirect("/")  # Solo se puede acceder con session iniciada
    
    exito = request.args.get("exito", "")
    
    conexion = conexion_BD()
    query = conexion.cursor()

    fecha_inicio = request.args.get("fecha_inicio", "")
    fecha_fin = request.args.get("fecha_fin", "")
    
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

    query_busqueda = f"""SELECT v.id_registro, v.cantidad_hombres, v.cantidad_mujeres, 
                                (v.cantidad_hombres + v.cantidad_mujeres) as total,
                                tv.tipo_visitante, v.fecha
                         FROM Visitantes v
                         JOIN Tipos_Visitantes tv ON v.id_tipo_visitante = tv.id_tipo_visitante
                         WHERE 1=1 {SQL_where_fecha}
                         ORDER BY v.fecha DESC"""

    query.execute(query_busqueda)
    visitantes = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("visitantes.html", visitantes=visitantes, exito=exito, 
                          fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)