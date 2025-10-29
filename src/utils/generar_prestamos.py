"""
Script para generar préstamos aleatorios del libro ID 219 (prueba prestamos)
Genera préstamos con diferentes estados y fechas variadas
"""

import sqlite3
import random
from datetime import datetime, timedelta

# Conectar a la base de datos
conn = sqlite3.connect('src/database/Biblioteca_GM.db')
cursor = conn.cursor()

# Verificar que el libro existe y tiene copias suficientes
cursor.execute("SELECT Titulo, numero_copias FROM Libros WHERE id_libro = 219")
libro = cursor.fetchone()

if not libro:
    print("❌ Error: El libro con ID 219 no existe en la base de datos")
    conn.close()
    exit()

print(f"📚 Libro encontrado: {libro[0]}")
print(f"📦 Copias disponibles: {libro[1]}")
print("="*60)

# Datos para generar préstamos aleatorios
nombres = [
    "Juan", "María", "Carlos", "Ana", "Pedro", "Laura", "Luis", "Carmen", 
    "José", "Rosa", "Miguel", "Sofia", "Diego", "Elena", "Fernando", 
    "Patricia", "Roberto", "Isabel", "Antonio", "Gabriela", "Ricardo",
    "Valentina", "Andrés", "Camila", "Francisco", "Daniela", "Jorge",
    "Lucía", "Manuel", "Victoria"
]

apellidos = [
    "García", "Rodríguez", "Martínez", "Fernández", "López", "González",
    "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez",
    "Díaz", "Cruz", "Morales", "Reyes", "Gutiérrez", "Ortiz", "Méndez",
    "Silva", "Castro", "Romero", "Álvarez", "Ruiz", "Herrera", "Jiménez"
]

direcciones = [
    "Zona 1, Ciudad de Guatemala",
    "Zona 5, Mixco",
    "Zona 11, Ciudad de Guatemala",
    "Villa Nueva",
    "San Miguel Petapa",
    "Santa Catarina Pinula",
    "Zona 18, Ciudad de Guatemala",
    "Zona 7, Ciudad de Guatemala",
    "Amatitlán",
    "Zona 12, Ciudad de Guatemala",
    "San José Pinula",
    "Fraijanes",
    "Zona 21, Ciudad de Guatemala",
    "Palencia"
]

grados = [
    "Primaria", "Básicos", "Diversificado", "Universidad", 
    "Profesional", "Maestría", "Doctorado", "Ninguno"
]

# Estados: 1=Vencido, 2=Activo, 3=Devuelto
estados = [
    (1, "Vencido"),
    (2, "Activo"),
    (3, "Devuelto")
]

# Fecha base: usar fechas del 2024 y 2025
fecha_inicio = datetime(2024, 6, 1)
fecha_fin = datetime(2025, 10, 23)

print("\n🔄 Generando préstamos...")
print("="*60)

prestamos_creados = 0
num_prestamos = 150  # Generar 150 préstamos aleatorios

for i in range(num_prestamos):
    # Generar datos aleatorios
    nombre = random.choice(nombres)
    apellido = random.choice(apellidos)
    dpi = f"{random.randint(1000, 9999)} {random.randint(10000, 99999)} {random.randint(100, 999)}"
    direccion = random.choice(direcciones)
    telefono = f"{random.choice([2, 3, 4, 5])}{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    grado = random.choice(grados)
    
    # Generar fecha de préstamo aleatoria
    dias_diff = (fecha_fin - fecha_inicio).days
    fecha_prestamo = fecha_inicio + timedelta(days=random.randint(0, dias_diff))
    
    # Fecha estimada de entrega (15 días después del préstamo)
    fecha_entrega_estimada = fecha_prestamo + timedelta(days=15)
    
    # Seleccionar estado aleatorio con distribución: 40% devueltos, 35% activos, 25% vencidos
    rand = random.random()
    if rand < 0.40:
        estado_id = 3  # Devuelto
    elif rand < 0.75:
        estado_id = 2  # Activo
    else:
        estado_id = 1  # Vencido
    
    # Configurar fecha de devolución y observaciones según el estado
    fecha_devolucion = None
    observaciones = None
    
    if estado_id == 3:  # Devuelto
        # Algunos devueltos a tiempo, otros tarde
        if random.random() < 0.7:  # 70% a tiempo
            dias_devolucion = random.randint(1, 15)
        else:  # 30% tarde
            dias_devolucion = random.randint(16, 30)
        
        fecha_devolucion = fecha_prestamo + timedelta(days=dias_devolucion)
        
        # Agregar observaciones aleatorias a algunos
        if random.random() < 0.3:  # 30% con observaciones
            observaciones_posibles = [
                "Libro devuelto en buen estado",
                "Pequeña mancha en la página 45",
                "Libro en perfecto estado",
                "Leve doblez en esquina",
                "Sin observaciones",
                "Devuelto con retraso de 3 días",
                "Libro mojado en las esquinas",
                "Todo correcto"
            ]
            observaciones = random.choice(observaciones_posibles)
    
    try:
        # Insertar préstamo
        cursor.execute("""
            INSERT INTO Prestamos 
            (dpi_usuario, nombre, apellido, direccion, num_telefono, grado, 
             id_libro, id_estado, fecha_prestamo, fecha_entrega_estimada, 
             fecha_devolucion, observaciones_devolucion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (dpi, nombre, apellido, direccion, telefono, grado, 
              219, estado_id, fecha_prestamo.strftime('%Y-%m-%d'), 
              fecha_entrega_estimada.strftime('%Y-%m-%d'),
              fecha_devolucion.strftime('%Y-%m-%d') if fecha_devolucion else None,
              observaciones))
        
        prestamos_creados += 1
        
        # Mostrar progreso cada 30 registros
        if prestamos_creados % 30 == 0:
            print(f"   ✓ {prestamos_creados} préstamos creados...")
        
    except sqlite3.Error as e:
        print(f"❌ Error al insertar préstamo #{i+1}: {e}")
        continue

# Confirmar cambios
conn.commit()

print(f"\n✅ Proceso completado!")
print(f"📊 Total de préstamos creados: {prestamos_creados}")
print("="*60)

# Mostrar estadísticas
cursor.execute("""
    SELECT 
        e.estado,
        COUNT(*) as cantidad
    FROM Prestamos p
    JOIN Estados_prestamos e ON p.id_estado = e.id_estado
    WHERE p.id_libro = 219
    GROUP BY e.estado
""")

print(f"\n📈 Estadísticas por estado:")
for row in cursor.fetchall():
    print(f"   - {row[0]}: {row[1]} préstamos")

cursor.execute("""
    SELECT COUNT(*) as total
    FROM Prestamos
    WHERE id_libro = 219
""")
total = cursor.fetchone()[0]
print(f"\n📚 Total de préstamos del libro ID 219: {total}")

# Cerrar conexión
conn.close()

print("\n✨ Base de datos actualizada exitosamente!")
print("💡 Nota: Las copias del libro NO fueron reducidas (999 copias se mantienen)")
