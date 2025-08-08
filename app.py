from flask import Flask, render_template, request, redirect, url_for, session, send_file
from decouple import config
from datetime import datetime
import math

from src.database.db_sqlite import conexion_BD

from config import config
from src import init_app

configuration = config['development']
app = init_app(configuration)

# ----------------------------------------------------- Descargar BD ----------------------------------------------------- #

@app.route('/descargar-bd')
def descargar_bd():
    if ("usuario" not in session) or (session["rol"]  != 'Administrador'):
        return redirect("/") #Solo se puede acceder con session iniciada

    return send_file('Data/Biblioteca_GM.db', as_attachment=True)

# ----------------------------------------------------- APP ----------------------------------------------------- #

if __name__ == "__main__":
    #app.run()
    app.run(debug=True,port=5000)
