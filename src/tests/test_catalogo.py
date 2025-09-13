from src.libros.models.libros_model import total_libros

def test_total():
    assert total_libros(" where l.titulo like '%%' and sd.codigo_seccion = 740") == 3


def test_total2():
    assert total_libros(" where l.titulo like '%%' and sd.codigo_seccion = 850") == 2


def test_total3():
    assert total_libros(" ") == 162

