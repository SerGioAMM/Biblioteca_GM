from flask import Blueprint, session, redirect, request,render_template,url_for
from datetime import datetime
import math
from src.database.db_sqlite import conexion_BD, dict_factory

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

        try:
            #? INSERT DE USUARIOS
            query.execute(f"""Insert into Administradores(usuario,contrasena,telefono,id_rol,email)
                            values (?,?,?,?,?)""",(usuario,contrasena,telefono,rol,email))

            #? Guardar cambios
            conexion.commit()  
            
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

    query.execute("""Select a.id_rol,r.rol,a.usuario,a.contrasena,a.telefono,a.id_administrador,a.email,ea.estado,a.tiempo_bloqueo from administradores a
                    join roles r on a.id_rol = r.id_rol
                    join estados_administradores ea on a.id_estado = ea.id_estado
                    where ea.estado == 'Activo'
                    order by a.usuario asc""")
    usuarios = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("usuarios.html",usuarios = usuarios,exito=exito)

# ----------------------------------------------------- DESACTIVAR USUARIO ----------------------------------------------------- #

@bp_usuarios.route("/desactivar_usuario", methods=["GET", "POST"])
def desactivar_usuario():
    id_usuario = request.form["id_usuario"]
    id_administrador = session.get("id_administrador")
    motivo = request.form["motivo"]

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("update administradores set id_estado = 2 where id_administrador = ?",(id_usuario,))
    query.execute("insert into logs_eliminados(id_administrador,id_eliminado,tabla_afectada,fecha, motivo) values(?,?,'Usuarios',datetime('now'),?)",(id_administrador,id_usuario,motivo))

    conexion.commit()

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

    query_busqueda = (f"""Select a.id_rol,r.rol,a.usuario,a.contrasena,a.telefono,a.id_administrador,a.email,ea.estado,a.tiempo_bloqueo,
                    (select motivo from logs_eliminados where id_eliminado = a.id_administrador and tabla_afectada = 'Usuarios' order by fecha desc limit 1) as motivo
                    from administradores a
                    join roles r on a.id_rol = r.id_rol
                    join estados_administradores ea on a.id_estado = ea.id_estado
                    where a.usuario like '%{busqueda}%' """)

    query_busqueda = query_busqueda + SQL_where_rol + SQL_where_estado + " order by a.usuario asc"
    query.execute(query_busqueda)
    usuarios = dict_factory(query)
    print(usuarios)
        

    query.close()
    conexion.close()


    return render_template("usuarios.html",usuarios=usuarios,exito=exito, filtro_rol=filtro_rol, filtro_estado=filtro_estado)

# ----------------------------------------------------- Ver perfil ----------------------------------------------------- #
@bp_usuarios.route("/ver_perfil", methods=["GET"])
def ver_perfil():
    if "usuario" not in session:
        return redirect("/")  # Solo se puede acceder con sesión iniciada

    id_usuario = session["id_administrador"]

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""SELECT a.id_administrador, a.usuario, a.email, a.telefono, r.rol, ea.estado
                    FROM administradores a
                    JOIN roles r ON a.id_rol = r.id_rol
                    JOIN estados_administradores ea ON a.id_estado = ea.id_estado
                    WHERE a.id_administrador = ?""", (id_usuario,))
    perfil = dict_factory(query)

    query.close()
    conexion.close()

    return render_template("perfil.html", perfil=perfil)