from flask import Blueprint, session, redirect, request,render_template,url_for
from src.database.db_sqlite import conexion_BD, dict_factory
from src.utils.logger import logger
import traceback
from datetime import datetime, timedelta

bp_datos = Blueprint('datos',__name__, template_folder="../templates")

#!Generar reporte semestral
# ----------------------------------------------------- Generar reporte semestral ----------------------------------------------------- #

@bp_datos.route('/reporte_semestral', methods=['GET', 'POST'])
def reporte_semestral():
    if request.method == 'POST':
        # Lógica para generar el reporte semestral
        pass
    return render_template('reporte_semestral.html')


#!Generar graficas generales (Libros, prestamos)
# ----------------------------------------------------- Generar graficas generales ----------------------------------------------------- #
@bp_datos.route('/graficas_generales', methods=['GET'])
def graficas_generales():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()
    
    # Consulta para obtener la cantidad de libros por categoría principal
    query.execute("""
        SELECT 
            CASE 
                WHEN r.codigo_seccion LIKE '0%' THEN 'Generalidades'
                WHEN r.codigo_seccion LIKE '1%' THEN 'Filosofía y psicología'
                WHEN r.codigo_seccion LIKE '2%' THEN 'Religión'
                WHEN r.codigo_seccion LIKE '3%' THEN 'Ciencias sociales'
                WHEN r.codigo_seccion LIKE '4%' THEN 'Lenguas'
                WHEN r.codigo_seccion LIKE '5%' THEN 'Ciencias naturales y matemáticas'
                WHEN r.codigo_seccion LIKE '6%' THEN 'Tecnología y ciencias aplicadas'
                WHEN r.codigo_seccion LIKE '7%' THEN 'Arte, música y deportes'
                WHEN r.codigo_seccion LIKE '8%' THEN 'Literatura'
                WHEN r.codigo_seccion LIKE '9%' THEN 'Historia y geografía'
                ELSE 'Sin categoría'
            END as categoria,
            COUNT(*) as cantidad
        FROM Libros l 
        JOIN RegistroLibros r ON l.id_libro = r.id_libro 
        GROUP BY 
            CASE 
                WHEN r.codigo_seccion LIKE '0%' THEN '000-090'
                WHEN r.codigo_seccion LIKE '1%' THEN '100-190'
                WHEN r.codigo_seccion LIKE '2%' THEN '200-290'
                WHEN r.codigo_seccion LIKE '3%' THEN '300-390'
                WHEN r.codigo_seccion LIKE '4%' THEN '400-490'
                WHEN r.codigo_seccion LIKE '5%' THEN '500-590'
                WHEN r.codigo_seccion LIKE '6%' THEN '600-690'
                WHEN r.codigo_seccion LIKE '7%' THEN '700-790'
                WHEN r.codigo_seccion LIKE '8%' THEN '800-890'
                WHEN r.codigo_seccion LIKE '9%' THEN '900-990'
                ELSE 'Sin categoría'
            END
        ORDER BY r.codigo_seccion
    """)
    
    resultados_categorias = dict_factory(query)

    labels_categorias = [(f"{resultado['categoria']} ({resultado['cantidad']})") for resultado in resultados_categorias]
    datos_categorias = [resultado["cantidad"] for resultado in resultados_categorias]

    query.execute("""
        SELECT 
            CASE 
                WHEN id_estado = 1 THEN 'Vencidos'
                WHEN id_estado = 2 THEN 'Activos'
                WHEN id_estado = 3 THEN 'Devueltos'
                ELSE 'Sin estado'
            END as estado,
            COUNT(*) as cantidad
        FROM Prestamos 
        GROUP BY id_estado
        ORDER BY id_estado
    """)
    
    resultados_prestamos = dict_factory(query)
    
    # Separar las etiquetas y datos para gráfico de préstamos
    labels_prestamos = [f"{resultado['estado']} ({resultado['cantidad']})" for resultado in resultados_prestamos]
    datos_prestamos = [resultado["cantidad"] for resultado in resultados_prestamos]

    # Consulta para obtener préstamos por mes y estado
    query.execute("""
        SELECT 
            strftime('%Y-%m', fecha_prestamo) as mes,
            CASE strftime('%m', fecha_prestamo)
                WHEN '01' THEN 'Enero'
                WHEN '02' THEN 'Febrero'
                WHEN '03' THEN 'Marzo'
                WHEN '04' THEN 'Abril'
                WHEN '05' THEN 'Mayo'
                WHEN '06' THEN 'Junio'
                WHEN '07' THEN 'Julio'
                WHEN '08' THEN 'Agosto'
                WHEN '09' THEN 'Septiembre'
                WHEN '10' THEN 'Octubre'
                WHEN '11' THEN 'Noviembre'
                WHEN '12' THEN 'Diciembre'
            END || ' ' || strftime('%Y', fecha_prestamo) as mes_nombre,
            SUM(CASE WHEN id_estado = 1 THEN 1 ELSE 0 END) as vencidos,
            SUM(CASE WHEN id_estado = 2 THEN 1 ELSE 0 END) as activos,
            SUM(CASE WHEN id_estado = 3 THEN 1 ELSE 0 END) as devueltos
        FROM Prestamos 
        GROUP BY strftime('%Y-%m', fecha_prestamo)
        ORDER BY strftime('%Y-%m', fecha_prestamo) DESC
        LIMIT 12
    """)
    
    resultados_prestamos_mes = dict_factory(query)
    
    # Separar las etiquetas y datos para gráfico de préstamos por mes
    labels_prestamos_mes = [f"{resultado['mes_nombre']} ({resultado['vencidos'] + resultado['activos'] + resultado['devueltos']})" for resultado in resultados_prestamos_mes]
    datos_vencidos = [resultado["vencidos"] for resultado in resultados_prestamos_mes]
    datos_activos = [resultado["activos"] for resultado in resultados_prestamos_mes]
    datos_devueltos = [resultado["devueltos"] for resultado in resultados_prestamos_mes]

    # Totales para mostrar en contenedores
    query.execute("SELECT COUNT(*) FROM Prestamos")
    total_prestamos = query.fetchone()[0]
    
    query.execute("SELECT COUNT(*) FROM Libros")
    total_libros = query.fetchone()[0]

    
    query.close()
    conexion.close()
    return render_template('graficas_generales.html', 
                            labels_categorias=labels_categorias, 
                            datos_categorias=datos_categorias,
                            labels_prestamos=labels_prestamos,
                            datos_prestamos=datos_prestamos,
                            labels_prestamos_mes=labels_prestamos_mes,
                            datos_vencidos=datos_vencidos,
                            datos_activos=datos_activos,
                            datos_devueltos=datos_devueltos,
                            total_prestamos=total_prestamos,
                            total_libros=total_libros)
