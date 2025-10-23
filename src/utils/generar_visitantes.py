"""
Script para generar datos aleatorios de visitantes para la biblioteca
Genera registros de enero a octubre de 2025 con datos variados
"""

import sqlite3
import random
from datetime import datetime, timedelta

# Conectar a la base de datos
conn = sqlite3.connect('src/database/Biblioteca_GM.db')
cursor = conn.cursor()

# Tipos de visitantes (IDs basados en la tabla Tipos_visitantes)
# Asumiendo que existen estos tipos en la BD
tipos_visitantes = [
    (1, "Estudiantes universitarios"),
    (2, "Estudiantes de primaria"),
    (3, "Estudiantes de nivel medio"),
    (4, "Profesionales"),
    (5, "Trabajadores"),
    (6, "Personal de la institución"),
    (7, "Otros")
]

# Rangos de edad disponibles (IDs de la tabla Rangos_edad)
rangos_edad = [
    (1, '0-12'),
    (2, '13-21'),
    (3, '22+')
]

# Año y meses a generar (enero a octubre 2025)
year = 2025
meses = range(1, 11)  # enero (1) a octubre (10)

print("Generando registros de visitantes...")
print("="*50)

registros_creados = 0

for mes in meses:
    # Determinar cuántos días tiene el mes
    if mes in [1, 3, 5, 7, 8, 10]:
        dias_en_mes = 31
    elif mes in [4, 6, 9]:
        dias_en_mes = 30
    else:  # febrero
        dias_en_mes = 28
    
    # Generar entre 15 y 25 días con visitantes por mes
    dias_con_visitantes = random.sample(range(1, dias_en_mes + 1), random.randint(15, 25))
    
    for dia in dias_con_visitantes:
        fecha = f"{year}-{mes:02d}-{dia:02d}"
        
        # Asegurar al menos 4 tipos diferentes de visitantes este día
        tipos_hoy = random.sample(tipos_visitantes, random.randint(4, 7))
        
        for tipo_id, tipo_nombre in tipos_hoy:
            # Generar cantidades aleatorias entre 0 y 30
            cantidad_mujeres = random.randint(0, 30)
            cantidad_hombres = random.randint(0, 30)
            
            # Asegurar que al menos uno no sea cero (evitar registros sin visitantes)
            if cantidad_mujeres == 0 and cantidad_hombres == 0:
                if random.choice([True, False]):
                    cantidad_mujeres = random.randint(1, 15)
                else:
                    cantidad_hombres = random.randint(1, 15)
            
            # Seleccionar rango de edad aleatorio (usando el ID)
            id_rango_edad, rango_nombre = random.choice(rangos_edad)
            
            try:
                # Insertar en la base de datos
                cursor.execute("""
                    INSERT INTO Visitantes 
                    (cantidad_mujeres, cantidad_hombres, id_tipo_visitante, fecha, id_rango_edad)
                    VALUES (?, ?, ?, ?, ?)
                """, (cantidad_mujeres, cantidad_hombres, tipo_id, fecha, id_rango_edad))
                
                registros_creados += 1
                
            except sqlite3.Error as e:
                print(f"Error al insertar registro: {e}")
                continue

# Confirmar cambios
conn.commit()

print(f"\n✅ Proceso completado!")
print(f"📊 Total de registros creados: {registros_creados}")
print(f"📅 Período: Enero - Octubre 2025")
print("="*50)

# Mostrar estadísticas
cursor.execute("""
    SELECT COUNT(*) as total_registros,
           SUM(cantidad_hombres) as total_hombres,
           SUM(cantidad_mujeres) as total_mujeres
    FROM Visitantes
    WHERE fecha BETWEEN '2025-01-01' AND '2025-10-31'
""")

stats = cursor.fetchone()
print(f"\n📈 Estadísticas generadas:")
print(f"   - Total de registros: {stats[0]}")
print(f"   - Total hombres: {stats[1]}")
print(f"   - Total mujeres: {stats[2]}")
print(f"   - Total visitantes: {stats[1] + stats[2]}")

# Cerrar conexión
conn.close()

print("\n✨ Base de datos actualizada exitosamente!")
