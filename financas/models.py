from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum


class Tipo(models.TextChoices):
    GASTO = "gasto", "Gasto"
    RECEITA = "receita", "Receita"


class Categoria(models.Model):
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=7, choices=Tipo.choices)

    class Meta:
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["nome", "tipo"], name="categoria_nome_tipo_unicos"
            )
        ]

    def __str__(self):
        return self.nome


class Lancamento(models.Model):
    tipo = models.CharField(max_length=7, choices=Tipo.choices)
    # O valor é sempre positivo; é o campo "tipo" que diz se soma ou subtrai.
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.01"), message="O valor deve ser maior que zero."
            )
        ],
    )
    data = models.DateField()
    descricao = models.CharField(max_length=200)
    # PROTECT: não deixa apagar uma categoria que já tem lançamentos.
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(valor__gt=0), name="lancamento_valor_positivo"
            )
        ]

    def __str__(self):
        return f"{self.descricao} ({self.valor})"

    def clean(self):
        # A categoria precisa ser do mesmo tipo do lançamento (vale também no admin).
        if self.categoria_id and self.categoria.tipo != self.tipo:
            raise ValidationError(
                {"categoria": f"Escolha uma categoria de {self.tipo}."}
            )


def resumo_do_mes(ano: int, mes: int) -> dict:
    """Devolve os lançamentos do mês e os totais de receitas, gastos e saldo."""
    lancamentos = Lancamento.objects.filter(
        data__year=ano, data__month=mes
    ).select_related("categoria")
    # Uma única consulta no banco calcula os dois totais.
    totais = lancamentos.aggregate(
        receitas=Sum("valor", filter=Q(tipo=Tipo.RECEITA)),
        gastos=Sum("valor", filter=Q(tipo=Tipo.GASTO)),
    )
    total_receitas = totais["receitas"] or Decimal("0.00")
    total_gastos = totais["gastos"] or Decimal("0.00")
    return {
        "lancamentos": lancamentos,
        "total_receitas": total_receitas,
        "total_gastos": total_gastos,
        "saldo": total_receitas - total_gastos,
    }
