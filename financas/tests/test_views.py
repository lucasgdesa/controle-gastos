from datetime import date
from decimal import Decimal

import pytest
from django.utils import timezone

from financas.models import Categoria, Lancamento, Tipo

pytestmark = pytest.mark.django_db


def cria(tipo, valor, dia, descricao="Item", mes=10, ano=2026):
    categoria = Categoria.objects.filter(tipo=tipo).first()
    return Lancamento.objects.create(
        tipo=tipo,
        valor=Decimal(valor),
        data=date(ano, mes, dia),
        descricao=descricao,
        categoria=categoria,
    )


def test_totais_do_mes(client):  # CA15
    cria(Tipo.RECEITA, "3000.00", 5)
    cria(Tipo.GASTO, "1200.50", 6)
    cria(Tipo.GASTO, "299.50", 7)
    resposta = client.get("/2026/10/")
    html = resposta.content.decode()
    assert resposta.context["total_receitas"] == Decimal("3000.00")
    assert resposta.context["total_gastos"] == Decimal("1500.00")
    assert resposta.context["saldo"] == Decimal("1500.00")
    assert html.count("R$ 3.000,00") >= 1
    assert html.count("R$ 1.500,00") >= 2  # gastos e saldo


def test_saldo_negativo_destacado(client):  # CA16
    cria(Tipo.GASTO, "100.00", 5)
    html = client.get("/2026/10/").content.decode()
    assert "R$ -100,00" in html
    assert "saldo-negativo" in html


def test_so_lancamentos_do_mes(client):  # CA17
    cria(Tipo.GASTO, "10.00", 31, descricao="Do fim de outubro")
    cria(Tipo.GASTO, "20.00", 1, descricao="Do inicio de novembro", mes=11)
    resposta = client.get("/2026/10/")
    html = resposta.content.decode()
    assert "Do fim de outubro" in html
    assert "Do inicio de novembro" not in html
    assert resposta.context["total_gastos"] == Decimal("10.00")


def test_mes_vazio(client):  # CA18
    html = client.get("/2026/10/").content.decode()
    assert "Nenhum lançamento neste mês." in html
    assert html.count("R$ 0,00") == 3


def test_pagina_inicial_mostra_mes_atual(client):  # CA20
    hoje = timezone.localdate()
    cria(
        Tipo.GASTO, "10.00", 1, descricao="Gasto de hoje", mes=hoje.month, ano=hoje.year
    )
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert resposta.context["data_mes"] == date(hoje.year, hoje.month, 1)
    assert "Gasto de hoje" in resposta.content.decode()


@pytest.mark.parametrize("url", ["/2026/13/", "/2026/0/", "/1999/5/", "/2101/5/"])
def test_mes_invalido_da_404(client, url):  # CA21
    assert client.get(url).status_code == 404


def test_ordem_da_lista(client):  # CA22
    cria(Tipo.GASTO, "1.00", 3, descricao="terceiro-dia")
    cria(Tipo.GASTO, "1.00", 20, descricao="vigésimo-dia")
    cria(Tipo.GASTO, "1.00", 10, descricao="décimo-dia")
    cria(Tipo.GASTO, "1.00", 10, descricao="décimo-dia-depois")
    descricoes = [x.descricao for x in client.get("/2026/10/").context["lancamentos"]]
    assert descricoes == [
        "vigésimo-dia",
        "décimo-dia-depois",
        "décimo-dia",
        "terceiro-dia",
    ]
