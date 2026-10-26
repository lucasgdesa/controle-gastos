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


def test_links_de_navegacao_dezembro(client):  # CA19
    html = client.get("/2026/12/").content.decode()
    assert 'href="/2027/1/"' in html
    assert 'href="/2026/11/"' in html


def test_link_mes_anterior_em_janeiro(client):  # CA19
    html = client.get("/2026/1/").content.decode()
    assert 'href="/2025/12/"' in html
    assert 'href="/2026/2/"' in html


def dados_do_form(tipo, **campos):
    nome = "Alimentação" if tipo == "gasto" else "Salário"
    categoria = Categoria.objects.get(nome=nome, tipo=tipo)
    dados = {
        "valor": "50,00",
        "data": "10/10/2026",
        "descricao": "Mercado",
        "categoria": categoria.pk,
    }
    dados.update(campos)
    return dados


def mensagens_da(resposta):
    return [str(m) for m in resposta.context["messages"]]


def test_cadastro_de_gasto(client):  # CA1
    url = "/lancamentos/novo/gasto/"
    resposta = client.post(url, dados_do_form("gasto"), follow=True)
    assert resposta.redirect_chain == [("/2026/10/", 302)]
    assert mensagens_da(resposta) == ["Gasto cadastrado com sucesso."]
    lancamento = Lancamento.objects.get()
    assert lancamento.tipo == Tipo.GASTO
    assert lancamento.valor == Decimal("50.00")
    assert lancamento.data == date(2026, 10, 10)


def test_cadastro_de_receita(client):  # CA2
    dados = dados_do_form("receita", valor="3000")
    resposta = client.post("/lancamentos/novo/receita/", dados, follow=True)
    assert resposta.redirect_chain == [("/2026/10/", 302)]
    lancamento = Lancamento.objects.get()
    assert lancamento.tipo == Tipo.RECEITA
    assert lancamento.valor == Decimal("3000.00")
    assert mensagens_da(resposta) == ["Receita cadastrada com sucesso."]


def test_formulario_de_novo_gasto(client):  # CA3
    resposta = client.get("/lancamentos/novo/gasto/")
    html = resposta.content.decode()
    form = resposta.context["form"]
    assert {c.tipo for c in form.fields["categoria"].queryset} == {Tipo.GASTO}
    assert form.initial["data"] == timezone.localdate()
    assert f'value="{timezone.localdate():%Y-%m-%d}"' in html
    assert "Novo gasto" in html


@pytest.mark.parametrize("valor", ["0", "-10"])
def test_cadastro_com_valor_zero_ou_negativo(client, valor):  # CA4
    dados = dados_do_form("gasto", valor=valor)
    resposta = client.post("/lancamentos/novo/gasto/", dados)
    assert resposta.status_code == 200
    assert "O valor deve ser maior que zero." in resposta.content.decode()
    assert Lancamento.objects.count() == 0


@pytest.mark.parametrize("valor", ["abc", ""])
def test_cadastro_com_valor_invalido(client, valor):  # CA5
    dados = dados_do_form("gasto", valor=valor)
    resposta = client.post("/lancamentos/novo/gasto/", dados)
    assert resposta.status_code == 200
    assert resposta.context["form"].errors["valor"]
    assert Lancamento.objects.count() == 0


def test_cadastro_com_descricao_so_espacos(client):  # CA6
    dados = dados_do_form("gasto", descricao="   ")
    resposta = client.post("/lancamentos/novo/gasto/", dados)
    assert "Informe uma descrição." in resposta.content.decode()
    assert Lancamento.objects.count() == 0


def test_cadastro_com_categoria_de_receita_num_gasto(client):  # CA7
    receita = Categoria.objects.get(nome="Salário")
    dados = dados_do_form("gasto", categoria=receita.pk)
    resposta = client.post("/lancamentos/novo/gasto/", dados)
    assert resposta.context["form"].errors["categoria"]
    assert Lancamento.objects.count() == 0


def test_tipo_invalido_da_404(client):  # CA8
    assert client.get("/lancamentos/novo/outro/").status_code == 404
    assert client.post("/lancamentos/novo/outro/", {}).status_code == 404


def test_cadastro_com_valor_em_formato_brasileiro(client):  # CA9
    dados = dados_do_form("gasto", valor="1.234,56")
    client.post("/lancamentos/novo/gasto/", dados)
    assert Lancamento.objects.get().valor == Decimal("1234.56")


def test_botoes_de_novo_na_pagina_do_mes(client):
    html = client.get("/2026/10/").content.decode()
    assert "/lancamentos/novo/gasto/" in html
    assert "/lancamentos/novo/receita/" in html


def test_editar_gasto(client):  # CA10
    gasto = cria(Tipo.GASTO, "10.00", 15, descricao="Antigo")
    dados = dados_do_form("gasto", descricao="Novo", valor="99,90", data="02/11/2026")
    resposta = client.post(f"/lancamentos/{gasto.pk}/editar/", dados, follow=True)
    assert resposta.redirect_chain == [("/2026/11/", 302)]
    assert mensagens_da(resposta) == ["Gasto atualizado com sucesso."]
    gasto.refresh_from_db()
    assert gasto.descricao == "Novo"
    assert gasto.valor == Decimal("99.90")
    assert gasto.tipo == Tipo.GASTO


def test_editar_nao_deixa_trocar_o_tipo(client):  # CA10
    gasto = cria(Tipo.GASTO, "10.00", 15)
    dados = {**dados_do_form("gasto"), "tipo": "receita"}
    client.post(f"/lancamentos/{gasto.pk}/editar/", dados)
    gasto.refresh_from_db()
    assert gasto.tipo == Tipo.GASTO


def test_tela_de_edicao(client):  # CA11
    gasto = cria(Tipo.GASTO, "10.00", 15)
    resposta = client.get(f"/lancamentos/{gasto.pk}/editar/")
    form = resposta.context["form"]
    assert "tipo" not in form.fields
    assert {c.tipo for c in form.fields["categoria"].queryset} == {Tipo.GASTO}
    assert "Editar gasto" in resposta.content.decode()


def test_edicao_com_erro_nao_salva(client):
    gasto = cria(Tipo.GASTO, "10.00", 15, descricao="Antigo")
    dados = dados_do_form("gasto", valor="0")
    resposta = client.post(f"/lancamentos/{gasto.pk}/editar/", dados)
    assert resposta.status_code == 200
    gasto.refresh_from_db()
    assert gasto.valor == Decimal("10.00")


def test_editar_id_inexistente_da_404(client):  # CA14
    assert client.get("/lancamentos/999/editar/").status_code == 404
