from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError

from financas.models import Categoria, Lancamento, Tipo


def novo_lancamento(categoria, tipo=Tipo.GASTO, valor="10.00"):
    return Lancamento(
        tipo=tipo,
        valor=Decimal(valor),
        data=date(2026, 10, 10),
        descricao="Teste",
        categoria=categoria,
    )


def test_categoria_str_e_nome_unico_por_tipo(db):
    Categoria.objects.create(nome="Extra", tipo=Tipo.GASTO)
    # mesmo nome em outro tipo é permitido
    categoria = Categoria.objects.create(nome="Extra", tipo=Tipo.RECEITA)
    assert str(categoria) == "Extra"
    with pytest.raises(IntegrityError):
        Categoria.objects.create(nome="Extra", tipo=Tipo.GASTO)


def test_valor_zero_e_negativo_sao_rejeitados(cat_gasto):
    for valor in ("0", "-5"):
        with pytest.raises(ValidationError) as erro:
            novo_lancamento(cat_gasto, valor=valor).full_clean()
        assert "valor" in erro.value.message_dict


def test_constraint_do_banco_barra_valor_zero(cat_gasto):
    with pytest.raises(IntegrityError):
        novo_lancamento(cat_gasto, valor="0").save()


def test_categoria_de_outro_tipo_e_rejeitada(cat_receita):
    lancamento = novo_lancamento(cat_receita, tipo=Tipo.GASTO)
    with pytest.raises(ValidationError) as erro:
        lancamento.full_clean()
    assert erro.value.message_dict["categoria"] == ["Escolha uma categoria de gasto."]


def test_lancamento_valido_passa(cat_gasto):
    novo_lancamento(cat_gasto).full_clean()


def test_categoria_com_lancamentos_nao_pode_ser_excluida(cat_gasto):
    novo_lancamento(cat_gasto).save()
    with pytest.raises(ProtectedError):
        cat_gasto.delete()  # CA24
