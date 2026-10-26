from datetime import date

from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from .models import resumo_do_mes


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
