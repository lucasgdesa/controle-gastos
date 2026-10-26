from django.contrib import admin

from .models import Categoria, Lancamento


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nome", "tipo"]
    list_filter = ["tipo"]


@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = ["data", "descricao", "tipo", "categoria", "valor"]
    list_filter = ["tipo", "categoria"]
