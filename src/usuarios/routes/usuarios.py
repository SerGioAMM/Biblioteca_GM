from flask import Blueprint, session, redirect, request,render_template,url_for, jsonify
from datetime import datetime
import math
from src.database.db_sqlite import conexion_BD, dict_factory
from werkzeug.security import generate_password_hash, check_password_hash

bp_usuarios = Blueprint('usuarios',__name__, template_folder="../templates")

# ----------------------------------------------------- REGISTRO USUARIOS ----------------------------------------------------- #

@bp_usuarios.route("/registro_usuarios", methods=["GET", "POST"])
def registro_usuarios():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("Select * from roles")
    roles = query.fetchall()

    #Verifica la accion que realiza el formulario en registro_usuairos.html
    if request.method == "POST":
        #Obtiene los datos del formulario en registro-usuarios.html
        usuario = request.form["usuario"]
        contrasena = request.form["contrasena"]
        telefono = request.form["telefono"]
        rol = request.form["rol"]
        email = request.form["email"]

        # Verificar si el usuario ya existe
        query.execute("SELECT COUNT(*) FROM Administradores WHERE usuario = ?", (usuario,))
        usuario_existe = query.fetchone()[0]
        
        if usuario_existe > 0:
            alerta = f"Error, el nombre de usuario '{usuario}' ya está registrado."
            query.close()
            conexion.close()
            return render_template("registro_usuarios.html", roles=roles, alerta=alerta)

        # Hash de la contraseña con salt
        password_hash = generate_password_hash(contrasena, method="scrypt", salt_length=16)

        try:
            #? INSERT DE USUARIOS
            query.execute(f"""Insert into Administradores(usuario,contrasena,telefono,id_rol,email)
                            values (?,?,?,?,?)""",(usuario,password_hash,telefono,rol,email))

            #? Guardar cambios
            conexion.commit()  
            
            # Crear notificación
            crear_notificacion(f"{session['rol']} {session['usuario']} ha registrado un nuevo usuario: {usuario}.")
            
            registro_exitoso = "El usuario se registró exitósamente."
            return render_template("registro_usuarios.html",roles=roles,registro_exitoso=registro_exitoso)
            

        except Exception as e:
            print(f"Error: {e}")
            alerta = "Error al ingresar el nuevo usuario"
            return render_template("registro_usuarios.html",roles=roles,alerta=alerta)
        finally:
            query.close()
            conexion.close()


    return render_template("registro_usuarios.html",roles=roles)

# ----------------------------------------------------- USUARIOS ----------------------------------------------------- #

@bp_usuarios.route("/usuarios",methods = ["POST","GET"])
def usuarios():
    if "usuario" not in session or session["rol"] == "Bibliotecario":
        return redirect("/prestamos") #Solo se puede acceder con session iniciada
    
    exito = request.args.get("exito","")

    conexion = conexion_BD()
    query = conexion.cursor()

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    usuarios_por_pagina = 20
    offset = (pagina - 1) * usuarios_por_pagina

    # Consulta para contar todos los usuarios activos
    query.execute("SELECT COUNT(*) FROM administradores a JOIN estados_administradores ea ON a.id_estado = ea.id_estado WHERE ea.estado = 'Activo'")
    total_usuarios = query.fetchone()[0]
    total_paginas = math.ceil(total_usuarios / usuarios_por_pagina)

    query.execute("""Select a.id_rol,r.rol,a.usuario,a.contrasena,a.telefono,a.id_administrador,a.email,ea.estado,a.tiempo_bloqueo from administradores a
                    join roles r on a.id_rol = r.id_rol
                    join estados_administradores ea on a.id_estado = ea.id_estado
                    where ea.estado == 'Activo'
                    order by a.usuario asc
                    LIMIT ? OFFSET ?""", (usuarios_por_pagina, offset))
    usuarios = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("usuarios.html",usuarios = usuarios,exito=exito,pagina=pagina,total_paginas=total_paginas,busqueda="")

# ----------------------------------------------------- DESACTIVAR USUARIO ----------------------------------------------------- #

@bp_usuarios.route("/desactivar_usuario", methods=["GET", "POST"])
def desactivar_usuario():
    id_usuario = request.form["id_usuario"]
    id_administrador = session.get("id_administrador")
    motivo = request.form["motivo"]

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("update administradores set id_estado = 2 where id_administrador = ?",(id_usuario,))
    query.execute("insert into logs_eliminados(id_administrador,id_eliminado,tabla_afectada,fecha, motivo) values(?,?,'Usuarios',datetime('now','localtime'),?)",(id_administrador,id_usuario,motivo))

    conexion.commit()

    # Crear notificación
    query.execute("SELECT usuario FROM administradores WHERE id_administrador = ?", (id_usuario,))
    usuario_desactivado = query.fetchone()[0]
    crear_notificacion(f"{session['rol']} {session['usuario']} ha desactivado el usuario: {usuario_desactivado}.")

    query.close()
    conexion.close()

    exito = "Usuario desactivado exiósamente."

    return redirect(url_for("usuarios.usuarios",exito=exito))

# ----------------------------------------------------- ACTIVAR USUARIO ----------------------------------------------------- #

@bp_usuarios.route("/activar_usuario", methods=["GET", "POST"])
def activar_usuario():
    id_usuario = request.form["id_usuario"]

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("update administradores set id_estado = 1 where id_administrador = ?",(id_usuario,))
    conexion.commit()

    # Crear notificación
    query.execute("SELECT usuario FROM administradores WHERE id_administrador = ?", (id_usuario,))
    usuario_activado = query.fetchone()[0]
    crear_notificacion(f"{session['rol']} {session['usuario']} ha activado el usuario: {usuario_activado}.")

    query.close()
    conexion.close()

    exito = "Usuario activado exiósamente."

    return redirect(url_for("usuarios.usuarios",exito=exito))

# ----------------------------------------------------- BUSCAR Usuarios ----------------------------------------------------- #

@bp_usuarios.route("/buscar_usuario",methods = ["GET","POST"])
def buscar_usuario():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    exito = request.args.get("exito","")
    
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar","")
    filtro_rol = request.args.get("filtro-busqueda","")
    filtro_estado = request.args.get("filtro-categorias","")
    
    #Paginacion
    pagina = request.args.get("page", 1, type=int)
    usuarios_por_pagina = 20
    offset = (pagina - 1) * usuarios_por_pagina
    
    if filtro_rol != "Todos":
        SQL_where_rol = (f"and r.rol = '{filtro_rol}'")
    else:
        SQL_where_rol = " "

    if filtro_estado == "Activo":
        SQL_where_estado = (f"and ea.estado = 'Activo'")
    elif filtro_estado == "Inactivo":
        SQL_where_estado = (f"and ea.estado = 'Inactivo'")
    else:
        SQL_where_estado = " "

    # Consulta para contar usuarios con filtros
    query_count = (f"""SELECT COUNT(*) FROM administradores a
                    join roles r on a.id_rol = r.id_rol
                    join estados_administradores ea on a.id_estado = ea.id_estado
                    where a.usuario like '%{busqueda}%' """)
    query_count = query_count + SQL_where_rol + SQL_where_estado
    query.execute(query_count)
    total_usuarios = query.fetchone()[0]
    total_paginas = math.ceil(total_usuarios / usuarios_por_pagina)

    query_busqueda = (f"""Select a.id_rol,r.rol,a.usuario,a.contrasena,a.telefono,a.id_administrador,a.email,ea.estado,a.tiempo_bloqueo,
                    (select motivo from logs_eliminados where id_eliminado = a.id_administrador and tabla_afectada = 'Usuarios' order by fecha desc limit 1) as motivo
                    from administradores a
                    join roles r on a.id_rol = r.id_rol
                    join estados_administradores ea on a.id_estado = ea.id_estado
                    where a.usuario like '%{busqueda}%' """)

    query_busqueda = query_busqueda + SQL_where_rol + SQL_where_estado + f" order by a.usuario asc LIMIT {usuarios_por_pagina} OFFSET {offset}"
    query.execute(query_busqueda)
    usuarios = dict_factory(query)
    print(usuarios)
        

    query.close()
    conexion.close()


    return render_template("usuarios.html",usuarios=usuarios,exito=exito, filtro_rol=filtro_rol, filtro_estado=filtro_estado,
                         pagina=pagina, total_paginas=total_paginas, busqueda=busqueda)

# ----------------------------------------------------- Ver perfil ----------------------------------------------------- #
@bp_usuarios.route("/ver_perfil", methods=["GET"])
def ver_perfil():
    if "usuario" not in session:
        return redirect("/")  # Solo se puede acceder con sesión iniciada

    id_usuario = session["id_administrador"]
    exito = request.args.get("exito", "")
    alerta = request.args.get("alerta", "")

    conexion = conexion_BD()
    query = conexion.cursor()

    # Obtener datos del perfil
    query.execute("""SELECT a.id_administrador, a.usuario, a.email, a.telefono, r.rol, ea.estado
                    FROM administradores a
                    JOIN roles r ON a.id_rol = r.id_rol
                    JOIN estados_administradores ea ON a.id_estado = ea.id_estado
                    WHERE a.id_administrador = ?""", (id_usuario,))
    perfil = dict_factory(query)

    # Obtener actividad reciente (últimos 5 logs del usuario)
    query.execute("""SELECT 
                        CASE 
                            WHEN tabla_afectada = 'Libros' THEN 'Eliminaste el libro "' || titulo || '"'
                            WHEN tabla_afectada = 'Prestamos' THEN 'Eliminaste el préstamo de "' || nombre_lector || '"'
                            WHEN tabla_afectada = 'Usuarios' THEN 'Desactivaste el usuario "' || nombre_lector || '"'
                            WHEN tabla_afectada = 'Visitantes' THEN 'Eliminaste un registro de visitantes (' || nombre_lector || ' hombres, ' || titulo || ' mujeres)'
                            WHEN tabla_afectada = 'Opiniones' THEN 'Rechazaste la reseña de ' || titulo || ''
                            ELSE 'Acción en ' || tabla_afectada
                        END as descripcion,
                        motivo,
                        fecha,
                        (strftime('%d', fecha)||' de '||
                        CASE strftime('%m', fecha) 
                            WHEN '01' THEN 'Enero' WHEN '02' THEN 'Febrero' WHEN '03' THEN 'Marzo'
                            WHEN '04' THEN 'Abril' WHEN '05' THEN 'Mayo' WHEN '06' THEN 'Junio'
                            WHEN '07' THEN 'Julio' WHEN '08' THEN 'Agosto' WHEN '09' THEN 'Septiembre'
                            WHEN '10' THEN 'Octubre' WHEN '11' THEN 'Noviembre' WHEN '12' THEN 'Diciembre'
                        END || ' de ' ||strftime('%Y', fecha) || ' a las ' ||strftime('%H:%M', fecha)) as fecha_formateada
                    FROM logs_eliminados 
                    WHERE id_administrador = ?
                    ORDER BY fecha DESC
                    LIMIT 5""", (id_usuario,))
    actividad_reciente = dict_factory(query)

    # Obtener notificaciones (si el usuario es administrador o bibliotecario)
    if session["rol"] in ["Administrador", "Bibliotecario"]:
        from datetime import datetime, timedelta
        
        # Notificaciones de hoy
        query.execute("""SELECT 
                            n.detalle,
                            COALESCE(na.visto, 0) as visto,
                            n.fecha,
                            strftime('%H:%M', n.fecha) as hora_formateada,
                            (strftime('%d', n.fecha)||' de '||
                            CASE strftime('%m', n.fecha) 
                                WHEN '01' THEN 'Enero' WHEN '02' THEN 'Febrero' WHEN '03' THEN 'Marzo'
                                WHEN '04' THEN 'Abril' WHEN '05' THEN 'Mayo' WHEN '06' THEN 'Junio'
                                WHEN '07' THEN 'Julio' WHEN '08' THEN 'Agosto' WHEN '09' THEN 'Septiembre'
                                WHEN '10' THEN 'Octubre' WHEN '11' THEN 'Noviembre' WHEN '12' THEN 'Diciembre'
                            END || ' de ' ||strftime('%Y', n.fecha) || ' a las ' ||strftime('%H:%M', n.fecha)) as fecha_formateada
                        FROM Notificaciones n
                        LEFT JOIN Notificaciones_admins na ON n.id_notificacion = na.id_notificacion 
                            AND na.id_administrador = ?
                        WHERE DATE(n.fecha) = DATE('now', 'localtime')
                        ORDER BY n.fecha DESC""", (id_usuario,))
        notificaciones_hoy = dict_factory(query)
        
        # Notificaciones de ayer
        query.execute("""SELECT 
                            n.detalle,
                            COALESCE(na.visto, 0) as visto,
                            n.fecha,
                            strftime('%H:%M', n.fecha) as hora_formateada,
                            (strftime('%d', n.fecha)||' de '||
                            CASE strftime('%m', n.fecha) 
                                WHEN '01' THEN 'Enero' WHEN '02' THEN 'Febrero' WHEN '03' THEN 'Marzo'
                                WHEN '04' THEN 'Abril' WHEN '05' THEN 'Mayo' WHEN '06' THEN 'Junio'
                                WHEN '07' THEN 'Julio' WHEN '08' THEN 'Agosto' WHEN '09' THEN 'Septiembre'
                                WHEN '10' THEN 'Octubre' WHEN '11' THEN 'Noviembre' WHEN '12' THEN 'Diciembre'
                            END || ' de ' ||strftime('%Y', n.fecha) || ' a las ' ||strftime('%H:%M', n.fecha)) as fecha_formateada
                        FROM Notificaciones n
                        LEFT JOIN Notificaciones_admins na ON n.id_notificacion = na.id_notificacion 
                            AND na.id_administrador = ?
                        WHERE DATE(n.fecha) = DATE('now', 'localtime', '-1 day')
                        ORDER BY n.fecha DESC""", (id_usuario,))
        notificaciones_ayer = dict_factory(query)
        
        # Notificaciones anteriores (más de 2 días)
        query.execute("""SELECT 
                            n.detalle,
                            COALESCE(na.visto, 0) as visto,
                            n.fecha,
                            strftime('%H:%M', n.fecha) as hora_formateada,
                            (strftime('%d', n.fecha)||' de '||
                            CASE strftime('%m', n.fecha) 
                                WHEN '01' THEN 'Enero' WHEN '02' THEN 'Febrero' WHEN '03' THEN 'Marzo'
                                WHEN '04' THEN 'Abril' WHEN '05' THEN 'Mayo' WHEN '06' THEN 'Junio'
                                WHEN '07' THEN 'Julio' WHEN '08' THEN 'Agosto' WHEN '09' THEN 'Septiembre'
                                WHEN '10' THEN 'Octubre' WHEN '11' THEN 'Noviembre' WHEN '12' THEN 'Diciembre'
                            END || ' de ' ||strftime('%Y', n.fecha) || ' a las ' ||strftime('%H:%M', n.fecha)) as fecha_formateada
                        FROM Notificaciones n
                        LEFT JOIN Notificaciones_admins na ON n.id_notificacion = na.id_notificacion 
                            AND na.id_administrador = ?
                        WHERE DATE(n.fecha) < DATE('now', 'localtime', '-1 day')
                        ORDER BY n.fecha DESC
                        LIMIT 50""", (id_usuario,))
        notificaciones_anteriores = dict_factory(query)
        
        # Contar notificaciones no vistas
        query.execute("""SELECT COUNT(*) 
                        FROM Notificaciones n
                        LEFT JOIN Notificaciones_admins na ON n.id_notificacion = na.id_notificacion 
                            AND na.id_administrador = ?
                        WHERE COALESCE(na.visto, 0) = 0""", (id_usuario,))
        notificaciones_no_vistas = query.fetchone()[0]
    else:
        notificaciones_hoy = []
        notificaciones_ayer = []
        notificaciones_anteriores = []
        notificaciones_no_vistas = 0

    query.close()
    conexion.close()

    return render_template("perfil.html", 
                            perfil=perfil, 
                            actividad_reciente=actividad_reciente,
                            notificaciones_hoy=notificaciones_hoy,
                            notificaciones_ayer=notificaciones_ayer,
                            notificaciones_anteriores=notificaciones_anteriores,
                            notificaciones_no_vistas=notificaciones_no_vistas,
                            exito=exito,
                            alerta=alerta)

# ----------------------------------------------------- Editar perfil ----------------------------------------------------- #
@bp_usuarios.route("/editar_perfil", methods=["POST"])
def editar_perfil():
    if "usuario" not in session:
        return redirect("/")

    id_usuario = session["id_administrador"]
    email = request.form.get("email", "")
    telefono = request.form.get("telefono", "")
    nueva_contrasena = request.form.get("nueva_contrasena", "")
    confirmar_contrasena = request.form.get("confirmar_contrasena", "")
    contrasena_actual = request.form["contrasena_actual"]

    conexion = conexion_BD()
    query = conexion.cursor()

    try:
        # Verificar contraseña actual
        query.execute("SELECT contrasena FROM administradores WHERE id_administrador = ?", (id_usuario,))
        stored_password = query.fetchone()[0]
        
        if not check_password_hash(stored_password, contrasena_actual):
            alerta = "La contraseña actual es incorrecta."
            return redirect(url_for("usuarios.ver_perfil", alerta=alerta))

        # Verificar confirmación de contraseña si se quiere cambiar
        if nueva_contrasena and nueva_contrasena != confirmar_contrasena:
            alerta = "La nueva contraseña y su confirmación no coinciden."
            return redirect(url_for("usuarios.ver_perfil", alerta=alerta))

        # Actualizar datos
        if nueva_contrasena:
            password_hash = generate_password_hash(nueva_contrasena, method="pbkdf2:sha256", salt_length=16)
            query.execute("UPDATE administradores SET email = ?, telefono = ?, contrasena = ? WHERE id_administrador = ?",
                            (email, telefono, password_hash, id_usuario))
        else:
            query.execute("UPDATE administradores SET email = ?, telefono = ? WHERE id_administrador = ?",
                            (email, telefono, id_usuario))

        conexion.commit()
        exito = "Perfil actualizado exitosamente."
        
        return redirect(url_for("usuarios.ver_perfil", exito=exito))

    except Exception as e:
        print(f"Error: {e}")
        alerta = "Error al actualizar el perfil."
        return redirect(url_for("usuarios.ver_perfil", alerta=alerta))
    finally:
        query.close()
        conexion.close()

# ----------------------------------------------------- Obtener notificaciones para navbar ----------------------------------------------------- #
@bp_usuarios.route("/api/notificaciones", methods=["GET"])
def obtener_notificaciones():
    if "usuario" not in session:
        return jsonify({"success": False})

    id_usuario = session["id_administrador"]

    conexion = conexion_BD()
    query = conexion.cursor()

    try:
        # Obtener últimas 10 notificaciones
        query.execute("""SELECT 
                            n.detalle,
                            COALESCE(na.visto, 0) as visto,
                            n.fecha,
                            (strftime('%d', n.fecha)||' de '||
                            CASE strftime('%m', n.fecha) 
                                WHEN '01' THEN 'Enero' WHEN '02' THEN 'Febrero' WHEN '03' THEN 'Marzo'
                                WHEN '04' THEN 'Abril' WHEN '05' THEN 'Mayo' WHEN '06' THEN 'Junio'
                                WHEN '07' THEN 'Julio' WHEN '08' THEN 'Agosto' WHEN '09' THEN 'Septiembre'
                                WHEN '10' THEN 'Octubre' WHEN '11' THEN 'Noviembre' WHEN '12' THEN 'Diciembre'
                            END || ' de ' ||strftime('%Y', n.fecha) || ' a las ' ||strftime('%H:%M', n.fecha)) as fecha_formateada
                        FROM Notificaciones n
                        LEFT JOIN Notificaciones_admins na ON n.id_notificacion = na.id_notificacion 
                            AND na.id_administrador = ?
                        ORDER BY n.fecha DESC
                        LIMIT 10""", (id_usuario,))
        notificaciones = dict_factory(query)
        
        # Contar notificaciones no vistas
        query.execute("""SELECT COUNT(*) 
                        FROM Notificaciones n
                        LEFT JOIN Notificaciones_admins na ON n.id_notificacion = na.id_notificacion 
                            AND na.id_administrador = ?
                        WHERE COALESCE(na.visto, 0) = 0""", (id_usuario,))
        notificaciones_no_vistas = query.fetchone()[0]
        
        return jsonify({
            "success": True,
            "notificaciones": notificaciones,
            "no_vistas": notificaciones_no_vistas
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        query.close()
        conexion.close()

# ----------------------------------------------------- Marcar notificaciones como leídas ----------------------------------------------------- #
@bp_usuarios.route("/marcar_notificaciones_leidas", methods=["POST"])
def marcar_notificaciones_leidas():
    if "usuario" not in session:
        return jsonify({"success": False})

    id_usuario = session["id_administrador"]

    conexion = conexion_BD()
    query = conexion.cursor()

    try:
        # Obtener todas las notificaciones que el usuario no ha visto
        query.execute("""SELECT n.id_notificacion 
                        FROM Notificaciones n
                        LEFT JOIN Notificaciones_admins na ON n.id_notificacion = na.id_notificacion 
                            AND na.id_administrador = ?
                        WHERE COALESCE(na.visto, 0) = 0""", (id_usuario,))
        notificaciones_no_vistas = query.fetchall()
        
        for notificacion in notificaciones_no_vistas:
            id_notificacion = notificacion[0]
            
            # Verificar si ya existe un registro para este usuario y notificación
            query.execute("""SELECT COUNT(*) FROM Notificaciones_admins 
                            WHERE id_notificacion = ? AND id_administrador = ?""", 
                         (id_notificacion, id_usuario))
            existe = query.fetchone()[0]
            
            if existe > 0:
                # Actualizar el estado existente
                query.execute("""UPDATE Notificaciones_admins 
                                SET visto = 1 
                                WHERE id_notificacion = ? AND id_administrador = ?""", 
                             (id_notificacion, id_usuario))
            else:
                # Insertar nuevo registro marcado como visto
                query.execute("""INSERT INTO Notificaciones_admins (id_notificacion, id_administrador, visto) 
                                VALUES (?, ?, 1)""", (id_notificacion, id_usuario))
        
        conexion.commit()
        
        query.close()
        conexion.close()
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False})

# ----------------------------------------------------- Función para crear notificaciones ----------------------------------------------------- #
def crear_notificacion(detalle, id_receptor=None):
    """
    Crea una notificación en la base de datos
    Si id_receptor es None, la notificación es para todos los administradores activos
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    
    try:
        # Insertar la notificación en la tabla principal
        query.execute("INSERT INTO Notificaciones (detalle, fecha) VALUES (?, datetime('now','localtime'))",
                     (detalle,))
        
        # Obtener el ID de la notificación recién creada
        id_notificacion = query.lastrowid
        
        if id_receptor:
            # Crear entrada para un administrador específico (no vista por defecto)
            query.execute("INSERT INTO Notificaciones_admins (id_notificacion, id_administrador, visto) VALUES (?, ?, 0)",
                         (id_notificacion, id_receptor))
        else:
            # Crear entradas para todos los administradores activos (no vistas por defecto)
            query.execute("SELECT id_administrador FROM administradores WHERE id_estado = 1")
            administradores = query.fetchall()
            
            for admin in administradores:
                query.execute("INSERT INTO Notificaciones_admins (id_notificacion, id_administrador, visto) VALUES (?, ?, 0)",
                             (id_notificacion, admin[0]))
        
        conexion.commit()
    except Exception as e:
        print(f"Error creando notificación: {e}")
    finally:
        query.close()
        conexion.close()