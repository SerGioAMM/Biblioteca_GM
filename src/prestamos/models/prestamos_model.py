from src.database.db_sqlite import conexion_BD, dict_factory
from datetime import datetime,date

def get_prestamos(prestamos_por_pagina,offset):
    conexion = conexion_BD()
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
                    (strftime('%d', p.fecha_entrega_estimada)||' de '||
                    CASE strftime('%m', p.fecha_entrega_estimada) 
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
                    END || ' de ' ||strftime('%Y', p.fecha_entrega_estimada)) as fecha_estimada,
                    (strftime('%d', p.fecha_devolucion)||' de '||
                    CASE strftime('%m', p.fecha_devolucion) 
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
                    END || ' de ' ||strftime('%Y', p.fecha_devolucion)) as fecha_devolucion, 
                    p.fecha_entrega_estimada as f_estimada, p.fecha_devolucion as f_devolucion,
                    l.Titulo, p.nombre, p.apellido, p.dpi_usuario, p.num_telefono,  p.direccion, e.estado, p.id_prestamo, l.id_libro, p.observaciones_devolucion
                    from Prestamos p
                    join Libros l on p.id_libro = l.id_libro
                    join Estados_prestamos e on p.id_estado = e.id_estado
                    order by e.id_estado asc, p.fecha_prestamo desc
                    limit ? offset ?""",(prestamos_por_pagina,offset))
    prestamos = dict_factory(query)

    for p in prestamos:
        fecha_estimada = datetime.strptime(p['f_estimada'], "%Y-%m-%d").date()
        fecha_devolucion = None
        if p['f_devolucion']:
            fecha_devolucion = datetime.strptime(p['f_devolucion'], "%Y-%m-%d").date()

        hoy = date.today()

        if (not fecha_devolucion and hoy > fecha_estimada) or (fecha_devolucion and fecha_devolucion > fecha_estimada):
            p['vencido'] = True
        else:
            p['vencido'] = False

    query.close()
    conexion.close()
    return prestamos