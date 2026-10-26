from django import forms
from django.utils import timezone

from .models import Categoria, Lancamento

MSG_VALOR_INVALIDO = "Informe um valor válido, por exemplo 12,50."


class LancamentoForm(forms.ModelForm):
    # localize=True faz o campo aceitar vírgula (12,50 e 1.234,56).
    valor = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        localize=True,
        error_messages={
            "required": "Informe o valor.",
            "invalid": MSG_VALOR_INVALIDO,
            "max_decimal_places": MSG_VALOR_INVALIDO,
        },
    )

    class Meta:
        model = Lancamento
        # O tipo não aparece aqui: ele vem da URL (cadastro) ou do lançamento (edição).
        fields = ["valor", "data", "descricao", "categoria"]
        labels = {"descricao": "Descrição"}
        widgets = {"data": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}
        error_messages = {
            "data": {
                "required": "Informe uma data válida.",
                "invalid": "Informe uma data válida.",
            },
            "descricao": {"required": "Informe uma descrição."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tipo = self.instance.tipo
        # Só mostra categorias do mesmo tipo do lançamento.
        self.fields["categoria"].queryset = Categoria.objects.filter(tipo=tipo)
        self.fields["categoria"].empty_label = "Selecione uma categoria"
        mensagem = f"Escolha uma categoria de {tipo}."
        self.fields["categoria"].error_messages["required"] = mensagem
        self.fields["categoria"].error_messages["invalid_choice"] = mensagem
        # No cadastro, a data já vem preenchida com hoje.
        if not self.instance.pk:
            self.initial["data"] = timezone.localdate()
