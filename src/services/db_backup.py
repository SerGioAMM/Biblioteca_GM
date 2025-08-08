from flask import Blueprint, session, redirect, send_file

backup_bd = Blueprint('backup_bd',__name__)

# ----------------------------------------------------- Descargar BD ----------------------------------------------------- #

@backup_bd.route('/descargar-bd')
def descargar_bd():
    if ("usuario" not in session) or (session["rol"]  != 'Administrador'):
        return redirect("/") #Solo se puede acceder con session iniciada

    return send_file('Data/Biblioteca_GM.db', as_attachment=True)