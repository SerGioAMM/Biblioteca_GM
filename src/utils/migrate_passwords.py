#!/usr/bin/env python3
"""
Script para migrar contraseñas existentes a formato hash con salt
"""

import sqlite3
from werkzeug.security import generate_password_hash

def migrate_passwords():
    # Conectar a la base de datos
    conn = sqlite3.connect('src/database/Biblioteca_GM.db')
    cursor = conn.cursor()
    
    try:
        # Obtener todos los usuarios con sus contraseñas actuales
        cursor.execute("SELECT id_administrador, usuario, contrasena FROM administradores")
        usuarios = cursor.fetchall()
        
        print(f"Encontrados {len(usuarios)} usuarios para migrar:")
        
        for id_admin, usuario, contrasena_actual in usuarios:
            print(f"Migrando usuario: {usuario}")
            
            # Verificar si la contraseña ya está hasheada
            if contrasena_actual.startswith('pbkdf2:sha256:'):
                print(f"  - Usuario {usuario} ya tiene contraseña hasheada, saltando...")
                continue
            
            # Generar hash de la contraseña actual
            password_hash = generate_password_hash(contrasena_actual, method="pbkdf2:sha256", salt_length=16)
            
            # Actualizar la contraseña en la base de datos
            cursor.execute("UPDATE administradores SET contrasena = ? WHERE id_administrador = ?", 
                         (password_hash, id_admin))
            
            print(f"  - Usuario {usuario} migrado exitosamente")
        
        # Confirmar cambios
        conn.commit()
        print("\n✅ Migración completada exitosamente!")
        print("Todas las contraseñas han sido hasheadas con salt.")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔐 Iniciando migración de contraseñas...")
    print("Este script convertirá todas las contraseñas de texto plano a hash con salt.")
    
    respuesta = input("¿Continuar? (y/n): ")
    if respuesta.lower() in ['y', 'yes', 's', 'si']:
        migrate_passwords()
    else:
        print("Migración cancelada.")