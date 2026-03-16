from flask import Blueprint, session, redirect, request,render_template,url_for, jsonify
from src.libros.models import libros_model
from flask_cors import CORS
import math

bp_books = Blueprint('books',__name__, template_folder="../templates")

@bp_books.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"]  = "https://luminous-chimera-869965.netlify.app/"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@bp_books.route("/", defaults={"path": ""}, methods=["OPTIONS"])
@bp_books.route("/<path:path>", methods=["OPTIONS"])
def handle_options(path):
    return jsonify({}), 200

# ----------------------------------------------------- API LIBROS ----------------------------------------------------- #

@bp_books.route("/books/api/<int:quantity>",methods=["GET"])
def get_books_2(quantity):
    books = libros_model.get_books_by_quantity(quantity)
    return jsonify({
        "success": True,
        "requested": quantity,
        "returned": len(books),
        "books": books
    }), 200

@bp_books.route("/books/api/total_books",methods=["GET"])
def get_total_books():
    total = libros_model.total_libros("")
    total = math.floor((total/10))
    total *= 10
    return jsonify({
        "total": total
    }), 200

@bp_books.route("/books/api/book_detail/<ID>", methods=["GET"])
def book_detail(ID):
    from src.opiniones.models import opiniones_model
    
    book_detail = libros_model.get_detalle_libro(ID)
    sections = libros_model.get_categorias()
    
    # Obtener reseñas aceptadas (3 iniciales)
    opinions = opiniones_model.get_opiniones_aceptadas_libro(ID, limit=3)
    total_opinions = len(opiniones_model.get_opiniones_aceptadas_libro(ID))
    
    # Calcular promedio de valoración
    average_info = opiniones_model.get_promedio_valoracion_libro(ID)
    
    # Obtener recomendaciones
    if book_detail:
        id_book_detail = book_detail[0]
        id_author = libros_model.get_id_autor_libro(ID)
        section_code = id_book_detail['codigo_seccion']
        
        # Obtener libros del mismo autor
        same_author_books = libros_model.get_libros_recomendados_autor(id_author, ID, limit=2)
        
        # Calcular cuántos libros de categoría necesitamos
        # Si el autor tiene menos de 3 libros, rellenamos con más de categoría
        same_category_books_limit = 4 - len(same_author_books)
        same_category_books = libros_model.get_libros_recomendados_categoria(section_code, ID, limit=same_category_books_limit)
        
        # Combinar recomendaciones
        book_recomendations = same_author_books + same_category_books
    else:
        book_recomendations = []
    
    # Obtener parámetros de alerta y éxito
    # alerta = request.args.get("alerta", "")
    # exito = request.args.get("exito", "")
    
    # return render_template("detalle_libro.html", detalle=detalle, sections=sections, 
    #                         opiniones=opiniones, total_opiniones=total_opiniones,
    #                         promedio_valoracion=promedio_info['promedio'],
    #                         total_valoraciones=promedio_info['total'],
    #                         book_recomendations=book_recomendations,
    #                         alerta=alerta, exito=exito)
    return jsonify({
        "book_detail": book_detail,
        "sections":sections,
        "opinions": opinions,
        "total_opinions":total_opinions,
        "average_rating": average_info['promedio'],
        "book_recomendations": book_recomendations
    }),200