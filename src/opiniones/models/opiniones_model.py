from src.database.db_sqlite import conexion_BD, dict_factory

def crear_opinion(id_libro, nombre_creador, apellido_creador, opinion, valoracion):
    """
    Crea una nueva opinión/reseña para un libro.
    Por defecto se crea con estado "Pendiente" (id_estado = 1)
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    try:
        query.execute("""
            INSERT INTO Opiniones (id_libro, nombre_creador, apellido_creador, opinion, 
                                   fecha_opinion, valoracion, id_estado)
            VALUES (?, ?, ?, ?, date('now','localtime'), ?, 1)
        """, (id_libro, nombre_creador, apellido_creador, opinion, valoracion))
        conexion.commit()
        alerta = ""
    except Exception as e:
        print(f"Error al crear opinión: {e}")
        alerta = "Error al crear reseña."
    finally:
        query.close()
        conexion.close()
    return alerta

def get_opiniones_pendientes():
    """
    Obtiene todas las opiniones con estado "Pendiente" (id_estado = 1)
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    query.execute("""
        SELECT o.id_opinion, o.id_libro, o.nombre_creador, o.apellido_creador, 
               o.opinion, o.fecha_opinion, o.valoracion, l.titulo
        FROM Opiniones o
        JOIN Libros l ON o.id_libro = l.id_libro
        WHERE o.id_estado = 1
        ORDER BY o.fecha_opinion DESC
    """)
    opiniones = dict_factory(query)
    query.close()
    conexion.close()
    return opiniones

def contar_opiniones_pendientes():
    """
    Cuenta cuántas opiniones están pendientes de aprobación
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    query.execute("SELECT COUNT(*) FROM Opiniones WHERE id_estado = 1")
    total = query.fetchone()[0]
    query.close()
    conexion.close()
    return total

def get_opiniones_aceptadas_libro(id_libro, limit=None):
    """
    Obtiene opiniones aceptadas para un libro específico
    Args:
        id_libro: ID del libro
        limit: Número máximo de opiniones a retornar (None para todas)
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    
    sql = """
        SELECT o.id_opinion, o.nombre_creador, o.apellido_creador, 
        o.opinion, strftime('%d-%m-%Y', o.fecha_opinion) as fecha_opinion, o.valoracion
        FROM Opiniones o
        WHERE o.id_libro = ? AND o.id_estado = 2
        ORDER BY o.valoracion DESC
    """
    
    if limit:
        sql += f" LIMIT {limit}"
    
    query.execute(sql, (id_libro,))
    opiniones = dict_factory(query)
    query.close()
    conexion.close()
    return opiniones

def aceptar_opinion(id_opinion, id_administrador):
    """
    Acepta una opinión (cambia el estado a 2)
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    try:
        query.execute("UPDATE Opiniones SET id_estado = 2 WHERE id_opinion = ?", (id_opinion,))
        conexion.commit()
        alerta = ""
    except Exception as e:
        print(f"Error al aceptar opinión: {e}")
        alerta = "Error al aceptar reseña."
    finally:
        query.close()
        conexion.close()
    return alerta

def rechazar_opinion(id_opinion, id_administrador, motivo):
    """
    Rechaza una opinión (cambia el estado a 3 y guarda el log)
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    try:
        # Obtener información de la opinión antes de rechazarla
        query.execute("""
            SELECT o.id_libro, l.titulo, o.nombre_creador, o.apellido_creador, o.opinion
            FROM Opiniones o
            JOIN Libros l ON o.id_libro = l.id_libro
            WHERE o.id_opinion = ?
        """, (id_opinion,))
        opinion_info = query.fetchone()
        
        if opinion_info:
            id_libro = opinion_info[0]
            titulo_libro = opinion_info[1]
            nombre_creador = opinion_info[2]
            apellido_creador = opinion_info[3]
            texto_opinion = opinion_info[4]
            
            # Insertar en logs_eliminados
            query.execute("""
                INSERT INTO logs_eliminados (id_administrador, id_eliminado, tabla_afectada, 
                                            fecha, titulo, motivo)
                VALUES (?, ?, 'Opiniones', datetime('now','localtime'), ?, ?)
            """, (id_administrador, id_opinion, 
                f"{nombre_creador} {apellido_creador} para '{titulo_libro}'", motivo))
            
            # Cambiar estado a rechazado
            query.execute("UPDATE Opiniones SET id_estado = 3 WHERE id_opinion = ?", (id_opinion,))
            
        conexion.commit()
        alerta = ""
    except Exception as e:
        print(f"Error al rechazar opinión: {e}")
        alerta = "Error al rechazar reseña."
    finally:
        query.close()
        conexion.close()
    return alerta

def get_opinion_detalle(id_opinion):
    """
    Obtiene los detalles de una opinión específica
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    query.execute("""
        SELECT o.id_opinion, o.id_libro, o.nombre_creador, o.apellido_creador, 
               o.opinion, o.fecha_opinion, o.valoracion, l.titulo, e.estado
        FROM Opiniones o
        JOIN Libros l ON o.id_libro = l.id_libro
        JOIN Estados_opiniones e ON o.id_estado = e.id_estado
        WHERE o.id_opinion = ?
    """, (id_opinion,))
    opinion = dict_factory(query)
    query.close()
    conexion.close()
    return opinion

def get_opiniones_rechazadas():
    """
    Obtiene todas las opiniones rechazadas desde logs_eliminados
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    query.execute("""
        SELECT l.id_log, l.id_eliminado, l.titulo, l.fecha, l.motivo, 
        a.usuario, r.rol, o.opinion,
        strftime('%d', l.fecha) as dia,
        CASE strftime('%m', l.fecha)
            WHEN '01' THEN 'ENE'
            WHEN '02' THEN 'FEB'
            WHEN '03' THEN 'MAR'
            WHEN '04' THEN 'ABR'
            WHEN '05' THEN 'MAY'
            WHEN '06' THEN 'JUN'
            WHEN '07' THEN 'JUL'
            WHEN '08' THEN 'AGO'
            WHEN '09' THEN 'SEP'
            WHEN '10' THEN 'OCT'
            WHEN '11' THEN 'NOV'
            WHEN '12' THEN 'DIC'
        END as mes
        FROM logs_eliminados l
        JOIN Administradores a ON l.id_administrador = a.id_administrador
        JOIN Roles r ON a.id_rol = r.id_rol
        JOIN Opiniones o ON l.id_eliminado = o.id_opinion and l.tabla_afectada = 'Opiniones'
        WHERE l.tabla_afectada = 'Opiniones'
        ORDER BY l.fecha DESC
    """)
    logs = dict_factory(query)
    query.close()
    conexion.close()
    return logs

def get_promedio_valoracion_libro(id_libro):
    """
    Calcula el promedio de valoración de un libro basado en opiniones aceptadas
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    query.execute("""
        SELECT AVG(valoracion) as promedio, COUNT(*) as total
        FROM Opiniones
        WHERE id_libro = ? AND id_estado = 2
    """, (id_libro,))
    resultado = query.fetchone()
    query.close()
    conexion.close()
    
    if resultado and resultado[0]:
        return {
            'promedio': round(resultado[0], 1),
            'total': resultado[1]
        }
    return {'promedio': 0, 'total': 0}

def get_libro_opinion(id_opinion):
    """
    Obtiene el título del libro asociado a una opinión
    """
    conexion = conexion_BD()
    query = conexion.cursor()
    query.execute("""
        SELECT l.titulo
        FROM Opiniones o
        JOIN Libros l ON o.id_libro = l.id_libro
        WHERE o.id_opinion = ?
    """, (id_opinion,))
    resultado = query.fetchone()
    query.close()
    conexion.close()
    
    if resultado:
        return resultado[0]
    return None