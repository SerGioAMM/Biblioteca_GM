import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.libros.models.libros_model import validar_notacion

# Casos de prueba
print('Pruebas de validar_notacion:')
print(f'Editorial "A" -> "{validar_notacion("A")}" (longitud: {len(validar_notacion("A"))})')
print(f'Editorial "AB" -> "{validar_notacion("AB")}" (longitud: {len(validar_notacion("AB"))})')
print(f'Editorial "ABC" -> "{validar_notacion("ABC")}" (longitud: {len(validar_notacion("ABC"))})')
print(f'Editorial "ABCDEF" -> "{validar_notacion("ABCDEF")}" (longitud: {len(validar_notacion("ABCDEF"))})')
print(f'Editorial "" -> "{validar_notacion("")}" (longitud: {len(validar_notacion(""))})')
print(f'Editorial None -> "{validar_notacion(None)}" (longitud: {len(validar_notacion(None))})')
print(f'Editorial "  x  " -> "{validar_notacion("  x  ")}" (longitud: {len(validar_notacion("  x  "))})')
print(f'Apellido "García" -> "{validar_notacion("García")}" (longitud: {len(validar_notacion("García"))})')
print(f'Nombre "J" -> "{validar_notacion("J")}" (longitud: {len(validar_notacion("J"))})')