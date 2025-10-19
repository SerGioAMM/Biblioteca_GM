from flask import Blueprint, session, redirect, request, render_template, url_for, jsonify
from src.opiniones.models import opiniones_model

bp_opiniones = Blueprint('opiniones', __name__, template_folder="../templates")

# ----------------------------------------------------- CREAR OPINIÓN ----------------------------------------------------- #

@bp_opiniones.route("/crear_opinion", methods=["POST"])
def crear_opinion():
    if request.method == "POST":
        id_libro = request.form["id_libro"]
        titulo_libro = request.form["titulo_libro"]
        nombre_creador = request.form["nombre_creador"]
        apellido_creador = request.form["apellido_creador"]
        opinion = request.form["opinion"]
        valoracion = request.form["valoracion"]
        
        try:
            alerta = opiniones_model.crear_opinion(id_libro, nombre_creador, apellido_creador, opinion, valoracion)
            
            if not alerta:
                # Crear notificación para administradores
                if "usuario" in session:
                    from src.usuarios.routes.usuarios import crear_notificacion
                    crear_notificacion(f"Nueva reseña pendiente para el libro: {titulo_libro}")
                
                exito = "Reseña enviada exitosamente. Será revisada por un administrador."
                return redirect(url_for('libros.detalle_libro', ID=id_libro, Titulo=titulo_libro, exito=exito))
            else:
                return redirect(url_for('libros.detalle_libro', ID=id_libro, Titulo=titulo_libro, alerta=alerta))
                
        except Exception as e:
            print(f"Error: {e}")
            alerta = "Error al crear reseña."
            return redirect(url_for('libros.detalle_libro', ID=id_libro, Titulo=titulo_libro, alerta=alerta))

# ----------------------------------------------------- OPINIONES PENDIENTES ----------------------------------------------------- #

@bp_opiniones.route("/opiniones_pendientes", methods=["GET"])
def opiniones_pendientes():
    if "usuario" not in session:
        return redirect("/")
    
    opiniones = opiniones_model.get_opiniones_pendientes()
    
    alerta = request.args.get("alerta", "")
    exito = request.args.get("exito", "")
    
    return render_template("opiniones_pendientes.html", opiniones=opiniones, alerta=alerta, exito=exito)

# ----------------------------------------------------- ACEPTAR OPINIÓN ----------------------------------------------------- #

@bp_opiniones.route("/aceptar_opinion", methods=["POST"])
def aceptar_opinion():
    if "usuario" not in session:
        return redirect("/")
    
    id_opinion = request.form["id_opinion"]
    id_administrador = session.get("id_administrador")
    titulo_libro = opiniones_model.get_libro_opinion(id_opinion)
    
    try:
        alerta = opiniones_model.aceptar_opinion(id_opinion, id_administrador)
        
        if not alerta:
            # Crear notificación
            from src.usuarios.routes.usuarios import crear_notificacion
            crear_notificacion(f"{session['rol']} {session['usuario']} ha aceptado una reseña para el libro: {titulo_libro}")
            
            exito = "Reseña aceptada exitosamente."
            return redirect(url_for('opiniones.opiniones_pendientes', exito=exito))
        else:
            return redirect(url_for('opiniones.opiniones_pendientes', alerta=alerta))
            
    except Exception as e:
        print(f"Error: {e}")
        alerta = "Error al aceptar reseña."
        return redirect(url_for('opiniones.opiniones_pendientes', alerta=alerta))

# ----------------------------------------------------- RECHAZAR OPINIÓN ----------------------------------------------------- #

@bp_opiniones.route("/rechazar_opinion", methods=["POST"])
def rechazar_opinion():
    if "usuario" not in session:
        return redirect("/")
    
    id_opinion = request.form["id_opinion"]
    motivo = request.form["motivo"]
    id_administrador = session.get("id_administrador")
    titulo_libro = opiniones_model.get_libro_opinion(id_opinion)
    
    try:
        alerta = opiniones_model.rechazar_opinion(id_opinion, id_administrador, motivo)
        
        if not alerta:
            # Crear notificación
            from src.usuarios.routes.usuarios import crear_notificacion
            crear_notificacion(f"{session['rol']} {session['usuario']} ha rechazado una reseña para el libro: {titulo_libro}")
            
            exito = "Reseña rechazada exitosamente."
            return redirect(url_for('opiniones.opiniones_pendientes', exito=exito))
        else:
            return redirect(url_for('opiniones.opiniones_pendientes', alerta=alerta))
            
    except Exception as e:
        print(f"Error: {e}")
        alerta = "Error al rechazar reseña."
        return redirect(url_for('opiniones.opiniones_pendientes', alerta=alerta))

# ----------------------------------------------------- CONTAR OPINIONES PENDIENTES (API) ----------------------------------------------------- #

@bp_opiniones.route("/api/opiniones_pendientes_count", methods=["GET"])
def api_opiniones_pendientes_count():
    """
    API para obtener el conteo de opiniones pendientes (para el badge en navbar)
    """
    if "usuario" not in session:
        return jsonify({"count": 0})
    
    count = opiniones_model.contar_opiniones_pendientes()
    return jsonify({"count": count})

# ----------------------------------------------------- LOGS OPINIONES RECHAZADAS ----------------------------------------------------- #

@bp_opiniones.route("/opiniones_rechazadas", methods=["GET"])
def opiniones_rechazadas():
    if "usuario" not in session:
        return redirect("/")
    
    logs = opiniones_model.get_opiniones_rechazadas()
    
    return render_template("opiniones_rechazadas.html", logs=logs)

# ----------------------------------------------------- DETALLE OPINIÓN RECHAZADA ----------------------------------------------------- #

@bp_opiniones.route("/detalle_opinion_rechazada/<int:id_opinion>", methods=["GET"])
def detalle_opinion_rechazada(id_opinion):
    if "usuario" not in session:
        return redirect("/")
    
    opinion = opiniones_model.get_opinion_detalle(id_opinion)
    
    return render_template("detalle_opinion_rechazada.html", opinion=opinion)
