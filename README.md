# Controle de Gastos

Aplicação web local, feita com Django, para registrar **gastos** e **receitas** e ver, mês a mês, quanto entrou, quanto saiu e qual foi o **saldo**. Um único usuário, sem login, rodando no seu computador.

Projeto de estudo: o código é simples de propósito (views em funções, `ModelForm`, HTML/CSS puros, SQLite).

## O que dá para fazer

- Cadastrar, editar e excluir gastos e receitas (valor, data, descrição, categoria).
- Ver a página de cada mês com a lista de lançamentos e os totais (receitas, gastos e saldo).
- Navegar para o mês anterior, o próximo e o mês atual.
- Categorias iniciais já vêm prontas (ajustes pelo admin do Django).

## Como rodar no Windows

Pré-requisito: Python 3 instalado. Os comandos abaixo são para o **PowerShell**, dentro da pasta do projeto. Para abrir o terminal nela: no Explorer, entre na pasta, clique na barra de endereço, digite `powershell` e aperte Enter.

1. Criar o ambiente virtual:

   ```powershell
   python -m venv .venv
   ```

2. Ativar o ambiente virtual:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   Se o PowerShell reclamar de permissão, rode uma vez
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e tente de novo.

3. Instalar as dependências:

   ```powershell
   pip install -r requirements.txt
   ```

4. Criar o arquivo `.env` a partir do modelo:

   ```powershell
   Copy-Item .env.example .env
   ```

   Abra o `.env` e troque `SECRET_KEY` por uma chave própria. Para gerar uma:

   ```powershell
   python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
   ```

   Para uso local, deixe `DEBUG=True` no `.env`; sem isso o `runserver` responde erro 400 e o CSS não carrega.

   O `.env` não vai para o git (está no `.gitignore`).

5. Criar o banco de dados (isso também cria as categorias iniciais):

   ```powershell
   python manage.py migrate
   ```

6. Criar um usuário para o admin (opcional, só para editar categorias):

   ```powershell
   python manage.py createsuperuser
   ```

7. Iniciar o servidor:

   ```powershell
   python manage.py runserver
   ```

   Abra <http://127.0.0.1:8000/> no navegador. O admin fica em <http://127.0.0.1:8000/admin/>.

## Testes e qualidade do código

Com o ambiente virtual ativado:

```powershell
pytest                  # roda os testes
ruff check .            # procura problemas no código
ruff format --check .   # confere a formatação (use "ruff format ." para corrigir)
```

## Estrutura

- `setup/`: configurações do projeto Django.
- `financas/`: o app (modelos, formulário, views, templates, CSS e testes).
- `docs/PRD.md`: documento com os requisitos da v1.

## Categorias iniciais

- Gasto: Alimentação, Moradia, Transporte, Saúde, Educação, Lazer, Contas e serviços, Outros.
- Receita: Salário, Freelance, Presente, Outros.
