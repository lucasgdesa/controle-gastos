from django.db import migrations

GASTOS = [
    "Alimentação",
    "Moradia",
    "Transporte",
    "Saúde",
    "Educação",
    "Lazer",
    "Contas e serviços",
    "Outros",
]
RECEITAS = ["Salário", "Freelance", "Presente", "Outros"]


def criar_categorias(apps, schema_editor):
    Categoria = apps.get_model("financas", "Categoria")
    for nome in GASTOS:
        Categoria.objects.get_or_create(nome=nome, tipo="gasto")
    for nome in RECEITAS:
        Categoria.objects.get_or_create(nome=nome, tipo="receita")


class Migration(migrations.Migration):
    dependencies = [
        ("financas", "0001_initial"),
    ]

    operations = [
        # Sem função de volta: desfazer a migração não apaga categorias.
        migrations.RunPython(criar_categorias, migrations.RunPython.noop),
    ]
