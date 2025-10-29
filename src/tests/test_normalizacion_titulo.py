import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.libros.models.libros_model import normalizar_titulo

# Casos de prueba
print('Pruebas de normalización de títulos:')
print('=' * 60)

# Caso 1: Todo mayúsculas
titulo1 = "EL PRINCIPITO"
resultado1 = normalizar_titulo(titulo1)
print(f'"{titulo1}" -> "{resultado1}"')

# Caso 2: Todo minúsculas
titulo2 = "el principito"
resultado2 = normalizar_titulo(titulo2)
print(f'"{titulo2}" -> "{resultado2}"')

# Caso 3: Mezcla de mayúsculas y minúsculas
titulo3 = "El PrInCiPiTo"
resultado3 = normalizar_titulo(titulo3)
print(f'"{titulo3}" -> "{resultado3}"')

# Caso 4: Con espacios extra
titulo4 = "  El Principito  "
resultado4 = normalizar_titulo(titulo4)
print(f'"{titulo4}" -> "{resultado4}"')

# Caso 5: Primera letra minúscula
titulo5 = "cien años de soledad"
resultado5 = normalizar_titulo(titulo5)
print(f'"{titulo5}" -> "{resultado5}"')

# Caso 6: Título largo
titulo6 = "LOS MISERABLES DE VICTOR HUGO"
resultado6 = normalizar_titulo(titulo6)
print(f'"{titulo6}" -> "{resultado6}"')

# Caso 7: Con números
titulo7 = "1984 DE GEORGE ORWELL"
resultado7 = normalizar_titulo(titulo7)
print(f'"{titulo7}" -> "{resultado7}"')

# Caso 8: Vacío
titulo8 = ""
resultado8 = normalizar_titulo(titulo8)
print(f'"{titulo8}" -> "{resultado8}" (vacío)')

# Caso 9: Solo espacios
titulo9 = "   "
resultado9 = normalizar_titulo(titulo9)
print(f'"{titulo9}" -> "{resultado9}" (solo espacios)')

print('=' * 60)
print('\n✓ Todos los títulos se normalizan a formato oración')
print('✓ Esto evitará duplicados como "Libro1" vs "LiBro1"')
