from datetime import date

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import LancamentoForm
from .models import Lancamento, Tipo, resumo_do_mes

TITULOS_NOVO = {Tipo.GASTO: "Novo gasto", Tipo.RECEITA: "Nova receita"}
TITULOS_EDITAR = {Tipo.GASTO: "Editar gasto", Tipo.RECEITA: "Editar receita"}
MENSAGENS_EDICAO = {
    Tipo.GASTO: "Gasto atualizado com sucesso.",
    Tipo.RECEITA: "Receita atualizada com sucesso.",
}
MENSAGENS_CADASTRO = {
    Tipo.GASTO: "Gasto cadastrado com sucesso.",
    Tipo.RECEITA: "Receita cadastrada com sucesso.",
}


def mes_atual(request):
    # localdate() usa o fuso de São Paulo (e não UTC) para saber o mês de hoje.
    hoje = timezone.localdate()
    return pagina_do_mes(request, hoje.year, hoje.month)


def mes(request, ano, mes):
    if not (1 <= mes <= 12 and 2000 <= ano <= 2100):
        raise Http404("Mês inválido.")
    return pagina_do_mes(request, ano, mes)


def pagina_do_mes(request, ano, mes):
    contexto = resumo_do_mes(ano, mes)
    contexto["data_mes"] = date(ano, mes, 1)
    # Mês anterior e seguinte, cuidando da virada de ano.
    contexto["anterior"] = (
        {"ano": ano - 1, "mes": 12} if mes == 1 else {"ano": ano, "mes": mes - 1}
    )
    contexto["proximo"] = (
        {"ano": ano + 1, "mes": 1} if mes == 12 else {"ano": ano, "mes": mes + 1}
    )
    return render(request, "financas/mes.html", contexto)


def redireciona_para_o_mes(data):
    return redirect("mes", ano=data.year, mes=data.month)


def lancamento_novo(request, tipo):
    if tipo not in Tipo.values:
        raise Http404("Tipo inválido.")
    # O lançamento ainda não foi salvo; já nasce com o tipo vindo da URL.
    lancamento = Lancamento(tipo=tipo)
    form = LancamentoForm(request.POST or None, instance=lancamento)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, MENSAGENS_CADASTRO[tipo])
        return redireciona_para_o_mes(lancamento.data)
    contexto = {
        "form": form,
        "titulo": TITULOS_NOVO[tipo],
        "url_cancelar": reverse("mes_atual"),
    }
    return render(request, "financas/lancamento_form.html", contexto)


def lancamento_editar(request, pk):
    lancamento = get_object_or_404(Lancamento, pk=pk)
    # Guarda o mês de antes: o form altera a data do objeto ao validar.
    url_cancelar = reverse("mes", args=[lancamento.data.year, lancamento.data.month])
    form = LancamentoForm(request.POST or None, instance=lancamento)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, MENSAGENS_EDICAO[lancamento.tipo])
        return redireciona_para_o_mes(lancamento.data)
    contexto = {
        "form": form,
        "titulo": TITULOS_EDITAR[lancamento.tipo],
        "url_cancelar": url_cancelar,
    }
    return render(request, "financas/lancamento_form.html", contexto)
