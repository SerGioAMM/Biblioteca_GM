from src.database.db_sqlite import conexion_BD
import sqlite3

def get_prestamos(prestamos_por_pagina,offset):
    conexion = conexion_BD()
    conexion.row_factory = sqlite3.Row
    query = conexion.cursor()
    # Consulta para mostrar los prestamos en tarjetas de prestamos.html
    query.execute(f"""select (strftime('%d', p.fecha_prestamo)||' de '||
                    CASE strftime('%m', p.fecha_prestamo) 
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
                    END || ' de ' ||strftime('%Y', p.fecha_prestamo)) as fecha_prestamo, 
                    strftime('%d', p.fecha_entrega_estimada) as dia_estimado,
                    CASE strftime('%m',p.fecha_entrega_estimada)
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
                    END as mes_estimado,
                    strftime('%d-%m-%Y', p.fecha_devolucion) as fecha_devolucion, l.Titulo, p.nombre, p.apellido, p.dpi_usuario, p.num_telefono,  p.direccion, 
                    e.estado, p.id_prestamo, l.id_libro
                    from Prestamos p
                    join Libros l on p.id_libro = l.id_libro
                    join Estados e on p.id_estado = e.id_estado
                    order by e.id_estado asc, p.fecha_prestamo desc
                    limit ? offset ?""",(prestamos_por_pagina,offset))
    prestamos = query.fetchall()
    query.close()
    conexion.close()
    return [dict(fila) for fila in prestamos]