"""
Script de prueba para la funcionalidad de trazabilidad de registros de libros.
Este script verifica que la lógica de duplicación funcione correctamente.
"""

import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.database.db_sqlite import conexion_BD, dict_factory

def verificar_estructura_tabla():
    """
    Verifica que la tabla Libros_modificados tenga el campo id_registro_libro_antiguo
    """
    print("=" * 70)
    print("VERIFICANDO ESTRUCTURA DE LA TABLA Libros_modificados")
    print("=" * 70)
    
    conexion = conexion_BD()
    query = conexion.cursor()
    
    try:
        # Obtener información de columnas
        query.execute("PRAGMA table_info(Libros_modificados)")
        columnas = query.fetchall()
        
        print("\nColumnas encontradas:")
        for col in columnas:
            print(f"  - {col[1]} ({col[2]})")
        
        # Verificar que exista la columna id_registro_libro_antiguo
        nombres_columnas = [col[1] for col in columnas]
        if 'id_registro_libro_antiguo' in nombres_columnas:
            print("\n✅ La columna 'id_registro_libro_antiguo' existe correctamente")
            return True
        else:
            print("\n❌ ERROR: La columna 'id_registro_libro_antiguo' NO existe")
            print("   Ejecute la migración: src/database/migracion_registro_antiguo.sql")
            return False
            
    except Exception as e:
        print(f"\n❌ Error al verificar estructura: {e}")
        return False
    finally:
        query.close()
        conexion.close()

def verificar_registros_existentes():
    """
    Muestra estadísticas de registros en Libros_modificados
    """
    print("\n" + "=" * 70)
    print("ESTADÍSTICAS DE REGISTROS MODIFICADOS")
    print("=" * 70)
    
    conexion = conexion_BD()
    query = conexion.cursor()
    
    try:
        # Total de modificaciones
        query.execute("SELECT COUNT(*) FROM Libros_modificados")
        total = query.fetchone()[0]
        print(f"\nTotal de modificaciones registradas: {total}")
        
        # Modificaciones con registro antiguo
        query.execute("""
            SELECT COUNT(*) 
            FROM Libros_modificados 
            WHERE id_registro_libro_antiguo IS NOT NULL
        """)
        con_registro = query.fetchone()[0]
        print(f"Modificaciones con registro antiguo: {con_registro}")
        
        # Modificaciones sin registro antiguo
        sin_registro = total - con_registro
        print(f"Modificaciones sin registro antiguo: {sin_registro}")
        
        if total > 0:
            porcentaje = (con_registro / total) * 100
            print(f"\nPorcentaje con duplicación: {porcentaje:.2f}%")
        
        # Últimas 5 modificaciones
        print("\n" + "-" * 70)
        print("ÚLTIMAS 5 MODIFICACIONES:")
        print("-" * 70)
        
        query.execute("""
            SELECT lm.id_modificacion, lm.titulo, lm.fecha_modificacion, 
                   lm.motivo, lm.id_registro_libro_antiguo,
                   CASE 
                       WHEN lm.id_registro_libro_antiguo IS NOT NULL THEN '✅ Duplicado'
                       ELSE '⊘ Sin duplicar'
                   END as estado
            FROM Libros_modificados lm
            ORDER BY lm.fecha_modificacion DESC
            LIMIT 5
        """)
        
        modificaciones = query.fetchall()
        
        if modificaciones:
            for mod in modificaciones:
                print(f"\nID: {mod[0]}")
                print(f"  Libro: {mod[1]}")
                print(f"  Fecha: {mod[2]}")
                print(f"  Motivo: {mod[3]}")
                print(f"  Estado: {mod[5]}")
                if mod[4]:
                    print(f"  ID Registro Antiguo: {mod[4]}")
        else:
            print("\nNo hay modificaciones registradas aún.")
            
    except Exception as e:
        print(f"\n❌ Error al verificar registros: {e}")
    finally:
        query.close()
        conexion.close()

def simular_escenarios():
    """
    Muestra ejemplos de qué cambios generarían duplicación
    """
    print("\n" + "=" * 70)
    print("ESCENARIOS DE DUPLICACIÓN")
    print("=" * 70)
    
    escenarios = [
        {
            "cambio": "Modificar solo el título del libro",
            "duplica": False,
            "razon": "El título no afecta a RegistroLibros"
        },
        {
            "cambio": "Modificar la editorial del libro",
            "duplica": True,
            "razon": "Cambia la notación (id_notacion)"
        },
        {
            "cambio": "Modificar el autor del libro",
            "duplica": True,
            "razon": "Cambia la notación (id_notacion)"
        },
        {
            "cambio": "Modificar el lugar de publicación",
            "duplica": True,
            "razon": "Cambia el lugar (id_lugar)"
        },
        {
            "cambio": "Cambiar la sección Dewey",
            "duplica": True,
            "razon": "Cambia codigo_seccion"
        },
        {
            "cambio": "Modificar número de páginas",
            "duplica": False,
            "razon": "Solo afecta la tabla Libros"
        },
        {
            "cambio": "Modificar número de copias",
            "duplica": False,
            "razon": "Solo afecta la tabla Libros"
        },
        {
            "cambio": "Cambiar la portada",
            "duplica": False,
            "razon": "Solo afecta la tabla Libros"
        }
    ]
    
    for i, escenario in enumerate(escenarios, 1):
        estado = "✅ SÍ duplica" if escenario["duplica"] else "❌ NO duplica"
        print(f"\n{i}. {escenario['cambio']}")
        print(f"   {estado}")
        print(f"   Razón: {escenario['razon']}")

def verificar_integridad_referencial():
    """
    Verifica que no haya registros huérfanos
    """
    print("\n" + "=" * 70)
    print("VERIFICANDO INTEGRIDAD REFERENCIAL")
    print("=" * 70)
    
    conexion = conexion_BD()
    query = conexion.cursor()
    
    try:
        # Verificar que todos los id_registro_libro_antiguo existan en RegistroLibros
        query.execute("""
            SELECT COUNT(*) 
            FROM Libros_modificados lm
            WHERE lm.id_registro_libro_antiguo IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM RegistroLibros rl 
                WHERE rl.id_registro = lm.id_registro_libro_antiguo
            )
        """)
        
        huerfanos = query.fetchone()[0]
        
        if huerfanos == 0:
            print("\n✅ Todos los registros antiguos tienen referencias válidas")
        else:
            print(f"\n⚠️  ADVERTENCIA: {huerfanos} registros antiguos sin referencia válida")
            
    except Exception as e:
        print(f"\n❌ Error al verificar integridad: {e}")
    finally:
        query.close()
        conexion.close()

def main():
    """
    Función principal que ejecuta todas las verificaciones
    """
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "VERIFICACIÓN DE TRAZABILIDAD DE REGISTROS" + " " * 12 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Verificar estructura
    estructura_ok = verificar_estructura_tabla()
    
    if not estructura_ok:
        print("\n⚠️  No se puede continuar sin la estructura correcta")
        print("   Por favor ejecute la migración primero.")
        return
    
    # Verificar registros
    verificar_registros_existentes()
    
    # Mostrar escenarios
    simular_escenarios()
    
    # Verificar integridad
    verificar_integridad_referencial()
    
    print("\n" + "=" * 70)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 70)
    print("\nPara probar la funcionalidad:")
    print("  1. Edite un libro cambiando solo el título")
    print("  2. Edite un libro cambiando la editorial o autor")
    print("  3. Verifique que solo el segundo genere duplicación")
    print("\n")

if __name__ == "__main__":
    main()
