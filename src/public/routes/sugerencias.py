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
    "buscar_prestamoTitulo_categoria": "SELECT l.titulo || ' (' || p.nombre || ' ' || p.apellido || ')' FROM prestamos p JOIN libros l ON l.id_libro = p.id_libro JOIN Estados_prestamos e ON p.id_estado = e.id_estado WHERE e.estado = '?'",
    "buscar_prestamoLector_categoria": "SELECT DISTINCT (nombre || ' ' || apellido) FROM prestamos p JOIN Estados_prestamos e ON p.id_estado = e.id_estado WHERE e.estado = '?'",
    "buscar_usuarioTodos": "SELECT usuario FROM administradores",
    "buscar_usuarioAdministrador": "SELECT usuario FROM administradores a JOIN Roles r ON a.id_rol = r.id_rol WHERE r.rol = 'Administrador'",
    "buscar_usuarioBibliotecario": "SELECT usuario FROM administradores a JOIN Roles r ON a.id_rol = r.id_rol WHERE r.rol = 'Bibliotecario'",
    "buscar_usuarioTodos_categoria": "SELECT usuario FROM administradores a JOIN estados_administradores ea ON a.id_estado = ea.id_estado WHERE ea.estado = '?'",
    "buscar_usuarioAdministrador_categoria": "SELECT usuario FROM administradores a JOIN estados_administradores ea ON a.id_estado = ea.id_estado WHERE r.rol = 'Administrador' and ea.estado = '?'",
    "buscar_usuarioBibliotecario_categoria": "SELECT usuario FROM administradores a JOIN estados_administradores ea ON a.id_estado = ea.id_estado WHERE r.rol = 'Bibliotecario'and ea.estado = '?'",
    "buscar-libro-prestamoTitulo": "SELECT (titulo || '(' || ano_publicacion || ')') FROM libros WHERE numero_copias > 0",
    "input-editorial": "SELECT editorial FROM editoriales",
    "input-lugar": "SELECT Lugar FROM lugares",
    "buscar_libro_eTitulo": "SELECT DISTINCT titulo FROM logs_eliminados where tabla_afectada = 'Libros'",
    "buscar_libro_eUsuario": "SELECT DISTINCT a.usuario FROM logs_eliminados le join Administradores a on le.id_administrador = a.id_administrador where tabla_afectada = 'Libros'",
    "buscar_prestamo_eTitulo": "SELECT DISTINCT titulo FROM logs_eliminados where tabla_afectada = 'Prestamos'",
    "buscar_prestamo_eUsuario": "SELECT DISTINCT a.usuario FROM administradores a JOIN logs_eliminados le ON a.id_administrador = le.id_administrador where tabla_afectada = 'Prestamos'",
    "buscar_libro_mTitulo": "SELECT DISTINCT l.titulo FROM libros_modificados lm JOIN libros l ON lm.id_libro = l.id_libro",
    "buscar_libro_mUsuario": "SELECT DISTINCT a.usuario FROM administradores a JOIN libros_modificados lm ON a.id_administrador = lm.id_administrador",
    #! FALTA POR HACER
    "libro_eliminado_admins": "SELECT DISTINCT a.usuario FROM administradores a JOIN libros_eliminados le ON a.id_administrador = le.id_administrador",
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
