from django.urls import path

from . import views

urlpatterns = [
    path("", views.mes_atual, name="mes_atual"),
    path("<int:ano>/<int:mes>/", views.mes, name="mes"),
]
