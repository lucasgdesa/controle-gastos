import pytest

from financas.models import Categoria, Tipo


@pytest.fixture
def cat_gasto(db):
    return Categoria.objects.create(nome="Cat. gasto de teste", tipo=Tipo.GASTO)


@pytest.fixture
def cat_receita(db):
    return Categoria.objects.create(nome="Cat. receita de teste", tipo=Tipo.RECEITA)
