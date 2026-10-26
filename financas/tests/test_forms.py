from datetime import date
from decimal import Decimal

import pytest

from financas.forms import LancamentoForm
from financas.models import Categoria, Lancamento, Tipo

pytestmark = pytest.mark.django_db


def monta_form(tipo=Tipo.GASTO, **campos):
    categoria = Categoria.objects.filter(tipo=tipo).first()
    dados = {
        "valor": "50,00",
        "data": "10/10/2026",
        "descricao": "Mercado",
        "categoria": categoria.pk,
    }
    dados.update(campos)
    return LancamentoForm(dados, instance=Lancamento(tipo=tipo))


def test_form_valido():
    assert monta_form().is_valid()


@pytest.mark.parametrize(
    "texto, esperado",
    [("1.234,56", "1234.56"), ("12,50", "12.50"), ("3000", "3000.00")],
)
def test_valor_com_virgula(texto, esperado):  # CA9
    form = monta_form(valor=texto)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["valor"] == Decimal(esperado)


@pytest.mark.parametrize("valor", ["0", "-10"])
def test_valor_zero_ou_negativo(valor):  # CA4
    form = monta_form(valor=valor)
    assert not form.is_valid()
    assert form.errors["valor"] == ["O valor deve ser maior que zero."]


def test_valor_invalido_ou_vazio():  # CA5
    assert monta_form(valor="abc").errors["valor"] == [
        "Informe um valor válido, por exemplo 12,50."
    ]
    assert monta_form(valor="").errors["valor"] == ["Informe o valor."]


def test_valor_com_tres_casas_decimais():
    assert "valor" in monta_form(valor="1,234").errors


def test_valor_acima_do_limite():
    assert "valor" in monta_form(valor="10000000000,00").errors


def test_data_invalida_e_futura():
    assert monta_form(data="").errors["data"] == ["Informe uma data válida."]
    assert monta_form(data="31/02/2026").errors["data"] == ["Informe uma data válida."]
    assert monta_form(data="01/01/2099").is_valid()  # datas futuras são permitidas


def test_descricao_so_com_espacos():  # CA6
    form = monta_form(descricao="   ")
    assert form.errors["descricao"] == ["Informe uma descrição."]


def test_descricao_tem_espacos_das_pontas_removidos():
    form = monta_form(descricao="  Mercado  ")
    assert form.is_valid()
    assert form.cleaned_data["descricao"] == "Mercado"


def test_categoria_de_outro_tipo():  # CA7
    receita = Categoria.objects.filter(tipo=Tipo.RECEITA).first()
    form = monta_form(categoria=receita.pk)
    assert form.errors["categoria"] == ["Escolha uma categoria de gasto."]


def test_categoria_obrigatoria_de_receita():
    form = monta_form(tipo=Tipo.RECEITA, categoria="")
    assert form.errors["categoria"] == ["Escolha uma categoria de receita."]


def test_form_nao_tem_campo_tipo_e_filtra_categorias():
    form = LancamentoForm(instance=Lancamento(tipo=Tipo.GASTO))
    assert "tipo" not in form.fields
    tipos = {c.tipo for c in form.fields["categoria"].queryset}
    assert tipos == {Tipo.GASTO}
    assert isinstance(form.initial["data"], date)
