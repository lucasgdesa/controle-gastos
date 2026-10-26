from django.urls import path

from . import views

urlpatterns = [
    path("", views.mes_atual, name="mes_atual"),
    path("<int:ano>/<int:mes>/", views.mes, name="mes"),
    path(
        "lancamentos/novo/<str:tipo>/",
        views.lancamento_novo,
        name="lancamento_novo",
    ),
]
