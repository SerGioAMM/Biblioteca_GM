from flask import Blueprint, session, render_template, redirect, url_for
import random

bp_bienvenida = Blueprint('bienvenida', __name__, template_folder="../templates")

# Lista de frases motivadoras
FRASES_MOTIVADORAS = [
    "Hoy será un gran día!",
    "Cada libro es una nueva aventura",
    "Aprende algo nuevo cada día",
    "La lectura abre mundos",
    "Haz que cada día cuente",
    "Nunca dejes de aprender",
    "La educación es la llave del éxito",
    "Cada día es una nueva oportunidad",
    "Lee, sueña y crece",
    "El cambio empieza contigo",
    "Construye tu mejor versión",
    "La persistencia vence",
    "Hoy es un buen día para empezar",
    "Cree en ti mismo!",
    "Los libros son amigos fieles",
    "El aprendizaje nunca termina",
    "Transforma tu realidad con conocimiento",
    "El esfuerzo de hoy es el éxito de mañana",
    "Tu actitud define tu camino",
    "Aprender es crecer sin límites",
    "Pequeños pasos crean grandes logros",
    "El saber te hace libre",
    "Nunca es tarde para empezar de nuevo",
    "El éxito es la suma de pequeños esfuerzos",
    "Sigue adelante, lo mejor está por venir",
    "Cambia tus pensamientos y cambiarás tu mundo",
    "Cada error es una lección disfrazada",
    "Hazlo con pasión o no lo hagas",
    "El futuro pertenece a quienes creen en sus sueños",
    "Con disciplina todo es posible",
    "El conocimiento ilumina el camino",
    "Aprender algo nuevo te transforma",
    "La curiosidad es la chispa del aprendizaje",
    "Cree, aprende y avanza",
    "Nunca subestimes el poder de un buen hábito",
    "Cada día puedes reinventarte"
]

@bp_bienvenida.route("/bienvenida")
def bienvenida():
    # Verificar que el usuario esté logueado
    if "usuario" not in session:
        return redirect(url_for("login.login"))
    
    # Obtener datos del usuario
    usuario = session.get("usuario", "Usuario")
    rol = session.get("rol", "")
    
    # Seleccionar una frase aleatoria
    frase = random.choice(FRASES_MOTIVADORAS)
    
    return render_template("bienvenida.html", usuario=usuario, rol=rol, frase=frase)
