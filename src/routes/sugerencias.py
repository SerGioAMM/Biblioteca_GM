from flask import Blueprint, jsonify
from src.database.db_sqlite import conexion_BD

bp_sugerencias = Blueprint('sugerencias',__name__)

# ----------------------------------------------------- SUGERENCIAS DINAMICAS ----------------------------------------------------- #

from flask import Blueprint, jsonify
from src.database.db_sqlite import conexion_BD

bp_sugerencias = Blueprint("sugerencias", __name__)

# Diccionario de consultas parametrizadas
consulta = {
    "buscar_libroTitulo": "SELECT titulo FROM libros",
    "buscar_libroAutor": "SELECT DISTINCT (nombre_autor || ' ' || apellido_autor) AS NombreCompleto FROM autores",
    "buscar_libroTitulo_categoria": "SELECT titulo FROM libros JOIN RegistroLibros rl on libros.id_libro = rl.id_libro WHERE rl.codigo_seccion = '?'",
    "buscar_libroAutor_categoria": "SELECT DISTINCT (nombre_autor || ' ' || apellido_autor) AS NombreCompleto FROM autores JOIN Notaciones n on autores.id_autor = n.id_autor JOIN RegistroLibros rl on n.id_notacion = rl.id_notacion WHERE rl.codigo_seccion = '?'",
    "buscar_prestamoTitulo": "SELECT l.titulo || ' (' || p.nombre || ' ' || p.apellido || ')' FROM prestamos p JOIN libros l ON l.id_libro = p.id_libro",
    "buscar_prestamoLector": "SELECT DISTINCT (nombre || ' ' || apellido) FROM prestamos",
    "buscar_prestamoTitulo_categoria": "SELECT l.titulo || ' (' || p.nombre || ' ' || p.apellido || ')' FROM prestamos p JOIN libros l ON l.id_libro = p.id_libro JOIN Estados e ON p.id_estado = e.id_estado WHERE e.estado = '?'",
    "buscar_prestamoLector_categoria": "SELECT DISTINCT (nombre || ' ' || apellido) FROM prestamos p JOIN Estados e ON p.id_estado = e.id_estado WHERE e.estado = '?'",
    "buscar_usuarioTodos": "SELECT usuario FROM administradores",
    "buscar_usuarioAdministrador": "SELECT usuario FROM administradores a JOIN Roles r ON a.id_rol = r.id_rol WHERE r.rol = 'Administrador'",
    "buscar_usuarioBibliotecario": "SELECT usuario FROM administradores a JOIN Roles r ON a.id_rol = r.id_rol WHERE r.rol = 'Bibliotecario'",
    "buscar-libro-prestamoTitulo": "SELECT (titulo || '(' || ano_publicacion || ')') FROM libros WHERE numero_copias > 0",
    "input-editorial": "SELECT editorial FROM editoriales",
    "input-lugar": "SELECT Lugar FROM lugares",
    #! FALTA POR HACER
    "prestamo_eliminado_admins": "SELECT DISTINCT a.usuario FROM administradores a JOIN prestamos_eliminados pe ON a.id_administrador = pe.id_administrador",
    "prestamo_eliminado_libros": "SELECT DISTINCT titulo FROM prestamos_eliminados",
    "libro_eliminado_admins": "SELECT DISTINCT a.usuario FROM administradores a JOIN libros_eliminados le ON a.id_administrador = le.id_administrador",
    "libro_eliminado": "SELECT DISTINCT titulo FROM libros_eliminados",
}

@bp_sugerencias.route("/sugerencias/<tipo>")
@bp_sugerencias.route("/sugerencias/<tipo><filtro>")
@bp_sugerencias.route("/sugerencias/<tipo><filtro>/<categoria>")
def sugerencias(tipo, filtro=None,categoria=None):
    try:
        print(f"Tipo: {tipo}, Filtro: {filtro}, Categoria: {categoria}")
        print(tipo + (filtro if filtro else "") + ("_categoria" if categoria and (categoria != "Todas" and categoria != "Todos") else ""))
        identificar = tipo + (filtro if filtro else "") + ("_categoria" if categoria and (categoria != "Todas" and categoria != "Todos") else "")
        print(identificar)
        conexion = conexion_BD()
        query = conexion.cursor()

        if (categoria and categoria != "Todas"):
            print(consulta[identificar].replace('?',categoria))
            query.execute(consulta[identificar].replace('?',categoria))
            
        else:
            query.execute(consulta[identificar])
            print(consulta[identificar])
        
        sugerencia = query.fetchall()
        query.close()
        conexion.close()
        return jsonify([fila[0] for fila in sugerencia])
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Tipo de sugerencia no válido"}), 400



'''
@bp_sugerencias.route("/sugerencias-lugares")
def sugerencias_lugares():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select Lugar from lugares")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-editoriales")
def sugerencias_editoriales():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select editorial from editoriales")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-libros")
def sugerencias_libros():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select titulo from libros")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-autores")
def sugerencias_autores():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select DISTINCT (nombre_autor || ' ' || apellido_autor) as NombreCompleto from autores;")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-libros-prestamos")
def sugerencias_libros_prestamos():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select (titulo || '(' || ano_publicacion || ')') from libros where numero_copias > 0")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-prestamo")
def sugerencias_prestamo():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select l.titulo || ' (' || p.nombre || ' ' || p.apellido || ')' 
                    from prestamos p
                    join libros l on l.id_libro = p.id_libro;
                    """)
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-lectores")
def sugerencias_lector():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT (nombre || ' ' || apellido) from prestamos;""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-usuarios")
def sugerencias_usuarios():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select usuario from administradores")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-prestamo-eliminado-administradores")
def sugerencias_prestamo_eliminado_administradores():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT a.usuario from administradores a
                    join prestamos_eliminados pe on a.id_administrador = pe.id_administrador""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-prestamo-eliminado-libro")
def sugerencias_prestamo_eliminado_libro():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT titulo from prestamos_eliminados""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-libro-eliminado-administradores")
def sugerencias_libro_eliminado_administradores():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT a.usuario from administradores a
                    join libros_eliminados le on a.id_administrador = le.id_administrador""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-libro-eliminado")
def sugerencias_libro_eliminado():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT titulo from libros_eliminados""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])
'''