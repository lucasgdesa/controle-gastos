# PRD: Controle de Gastos Pessoais (v1)

> Status: rascunho para aprovação · Data: 2026-10-26 · Autor: Organizador (pedido do Lucas)

---

## 1. Contexto

O Lucas está estudando programação e quer um projeto próprio para estudo e portfólio. Ele já concluiu um projeto Django de curso (Alura, em `C:\Users\lucas\Documents\projeto_django`) e conhece a estrutura básica: projeto `setup`, `.venv`, `.env` com `SECRET_KEY` lido via `python-dotenv`. Esse projeto serve **apenas como referência** e não deve ser alterado.

Este projeto é novo, ainda não tem código, e fica em `C:\Users\lucas\Documents\controle-gastos`, com repositório git próprio. A prioridade é **simplicidade e didática**: cada parte deve ser fácil de entender e de acompanhar por quem está aprendendo.

## 2. Objetivo

Criar uma aplicação web local onde uma pessoa registra seus **gastos** e **receitas** e vê, mês a mês, quanto entrou, quanto saiu e qual foi o **saldo do mês**.

Indicador de sucesso da v1: o Lucas consegue registrar os lançamentos de um mês real, navegar entre meses e conferir o saldo sem abrir o admin do Django nem mexer no banco.

## 3. Escopo (o que entra na v1)

- Cadastrar, editar e excluir lançamentos de **gasto** e de **receita** (valor, data, descrição, categoria).
- Categorias pré-cadastradas, separadas por tipo (gasto ou receita).
- Página do mês com a lista de lançamentos e os totais: receitas, gastos e saldo (receitas − gastos).
- Navegação para o mês anterior, o próximo mês e o mês atual.
- Usuário único, **sem login**, rodando localmente (`runserver`).
- Testes automatizados com `pytest` + `pytest-django` e código verificado com `ruff`.

## 4. Usuários

- **Usuário único:** o próprio Lucas, usando o app no computador dele pelo navegador.
- **Público secundário (portfólio):** quem for ler o código no GitHub (recrutadores, colegas). Por isso o README e a organização do código importam.

## 5. Requisitos funcionais

**Lançamentos**
- **RF1:** O sistema deve permitir cadastrar um **gasto** informando valor, data, descrição e categoria.
- **RF2:** O sistema deve permitir cadastrar uma **receita** informando valor, data, descrição e categoria.
- **RF3:** No formulário de gasto, o campo categoria deve listar **apenas categorias de gasto**; no de receita, **apenas categorias de receita**.
- **RF4:** O campo data deve vir preenchido com a data de hoje ao abrir o formulário de cadastro.
- **RF5:** O sistema deve permitir **editar** valor, data, descrição e categoria de um lançamento existente. O **tipo não pode ser alterado** na edição (para trocar, exclui-se e cadastra-se de novo).
- **RF6:** O sistema deve permitir **excluir** um lançamento, sempre passando por uma página de confirmação.
- **RF7:** Após cadastrar, editar ou excluir, o usuário volta para a página do **mês da data do lançamento** e vê uma mensagem de sucesso (ex.: "Gasto cadastrado com sucesso.").

**Categorias**
- **RF8:** As categorias iniciais são criadas automaticamente por uma **migração de dados** (seed), sem passo manual.
- **RF9:** Cada categoria pertence a um tipo: gasto ou receita.
- **RF10:** Na v1 não há tela própria para categorias; ajustes eventuais são feitos pelo **admin do Django**.

**Página do mês**
- **RF11:** A página inicial (`/`) mostra o **mês atual**.
- **RF12:** A página do mês lista todos os lançamentos cuja data está naquele mês, ordenados da data mais recente para a mais antiga (empate: o cadastrado por último aparece primeiro).
- **RF13:** Cada linha mostra: data (dd/mm/aaaa), descrição, categoria, tipo e valor em reais (`R$ 1.234,56`), além dos links "Editar" e "Excluir".
- **RF14:** A página mostra três totais do mês: **Total de receitas**, **Total de gastos** e **Saldo** (receitas − gastos).
- **RF15:** Saldo negativo aparece destacado (ex.: em vermelho) e com sinal de menos.
- **RF16:** A página tem links para **mês anterior**, **próximo mês** e **mês atual**, tratando a virada de ano (dezembro → janeiro e janeiro → dezembro).
- **RF17:** Mês sem lançamentos mostra uma mensagem amigável ("Nenhum lançamento neste mês.") e totais zerados.
- **RF18:** A página do mês tem botões "Novo gasto" e "Nova receita".

## 6. Requisitos não funcionais

- **RNF1 (stack):** Python 3 + Django (mesma versão principal usada no projeto de referência, Django 6.x) + SQLite. Templates Django com HTML, CSS e JavaScript puros, sem framework CSS ou JS.
- **RNF2 (dinheiro):** valores monetários usam `Decimal`/`DecimalField` em todo o fluxo. **Nunca `float`.** Somas feitas no banco com `Sum`.
- **RNF3 (idioma e região):** `LANGUAGE_CODE = "pt-br"`, `TIME_ZONE = "America/Sao_Paulo"`. O formulário aceita vírgula como separador decimal (`12,50` e `1.234,56`).
- **RNF4 (segurança):** `SECRET_KEY` (e `DEBUG`) lidos do `.env` com `python-dotenv`; `.env` no `.gitignore`; um `.env.example` sem valores reais vai para o repositório. Formulários usam `{% csrf_token %}`. Exclusão só via `POST`.
- **RNF5 (qualidade):** `ruff check` e `ruff format --check` sem erros; `pytest` passando. Configuração dos dois no `pyproject.toml`.
- **RNF6 (formatação do front):** `prettier` apenas para arquivos `.css` (e `.js`, se existirem). Os templates `.html` do Django **não** passam pelo prettier, porque ele costuma quebrar as tags `{% %}`; são formatados à mão.
- **RNF7 (desempenho):** a página do mês deve usar uma consulta para a lista (com `select_related("categoria")`) e uma agregação para os totais. Sem otimizações além disso: o volume esperado é pequeno.
- **RNF8 (compatibilidade):** funciona nos navegadores atuais (Chrome, Edge, Firefox) e é legível em tela de celular (layout simples, uma coluna em telas estreitas).
- **RNF9 (didática):** views baseadas em **funções** (mais fáceis de ler que class-based views para quem está começando) e formulários com `ModelForm`. Comentários curtos explicando o "porquê" em pontos não óbvios.

## 7. Telas e fluxo

### Modelo de dados

**`Categoria`**

| Campo | Tipo Django | Regras |
| --- | --- | --- |
| `id` | `BigAutoField` | automático |
| `nome` | `CharField(max_length=50)` | obrigatório |
| `tipo` | `CharField(max_length=7, choices=Tipo.choices)` | `"gasto"` ou `"receita"` |

- Restrição: `nome` + `tipo` únicos juntos (`UniqueConstraint`).
- `__str__` retorna o `nome`. Ordenação padrão por `nome`.
- `Tipo` é um `models.TextChoices` compartilhado com `Lancamento` (`GASTO = "gasto", "Gasto"`, `RECEITA = "receita", "Receita"`).

**`Lancamento`**

| Campo | Tipo Django | Regras |
| --- | --- | --- |
| `id` | `BigAutoField` | automático |
| `tipo` | `CharField(max_length=7, choices=Tipo.choices)` | obrigatório; define o sinal |
| `valor` | `DecimalField(max_digits=12, decimal_places=2)` | obrigatório; **sempre positivo**, mínimo `0.01` (`MinValueValidator(Decimal("0.01"))`) |
| `data` | `DateField` | obrigatório; padrão `date.today` no formulário |
| `descricao` | `CharField(max_length=200)` | obrigatório; não pode ser só espaços |
| `categoria` | `ForeignKey(Categoria, on_delete=models.PROTECT)` | obrigatório; tipo da categoria = tipo do lançamento |
| `criado_em` | `DateTimeField(auto_now_add=True)` | automático |
| `atualizado_em` | `DateTimeField(auto_now=True)` | automático |

- Ordenação padrão: `["-data", "-id"]`.
- **O valor é sempre guardado positivo; o campo `tipo` é que diz se ele soma ou subtrai no saldo.** Isso evita confusão com sinais negativos digitados pelo usuário.
- `on_delete=PROTECT`: não deixa apagar uma categoria que tenha lançamentos (protege o histórico).
- Também há uma `CheckConstraint` no banco garantindo `valor > 0`, como segunda camada além da validação do formulário.

**Categorias iniciais (seed via migração de dados)**

- Gasto: Alimentação, Moradia, Transporte, Saúde, Educação, Lazer, Contas e serviços, Outros.
- Receita: Salário, Freelance, Presente, Outros.

> **Decisão:** categorias fixas via migração de dados (editáveis só pelo admin), porque elimina uma tela inteira de CRUD da v1 e mantém o foco no fluxo principal; uma tela de categorias pode entrar numa versão futura.

### Rotas

| Rota | Nome (`name=`) | Método | O que faz |
| --- | --- | --- | --- |
| `/` | `mes_atual` | GET | Mostra a página do mês atual |
| `/<int:ano>/<int:mes>/` | `mes` | GET | Mostra a página do mês informado; `mes` fora de 1–12 ou `ano` fora de 2000–2100 → 404 |
| `/lancamentos/novo/<tipo>/` | `lancamento_novo` | GET, POST | Formulário de novo gasto (`tipo=gasto`) ou nova receita (`tipo=receita`); outro valor → 404 |
| `/lancamentos/<int:pk>/editar/` | `lancamento_editar` | GET, POST | Formulário de edição; id inexistente → 404 |
| `/lancamentos/<int:pk>/excluir/` | `lancamento_excluir` | GET, POST | GET mostra a confirmação; POST exclui |
| `/admin/` | (padrão) | — | Admin do Django (categorias e lançamentos) |

### Telas (templates)

1. **`base.html`:** estrutura comum (cabeçalho com o nome do app e link para o mês atual, área de mensagens de sucesso/erro, link para o CSS).
2. **`mes.html` (página do mês):** título "Outubro de 2026"; links "‹ Mês anterior", "Mês atual", "Próximo mês ›"; três cartões com Receitas, Gastos e Saldo; botões "Novo gasto" e "Nova receita"; tabela de lançamentos (RF13) ou a mensagem de mês vazio (RF17).
3. **`lancamento_form.html`:** usado para cadastrar e editar. Título muda conforme o caso ("Novo gasto", "Nova receita", "Editar gasto", "Editar receita"). Campos: valor, data (`<input type="date">`), descrição, categoria (já filtrada pelo tipo). Botões "Salvar" e "Cancelar" (volta ao mês). Erros aparecem ao lado de cada campo.
4. **`lancamento_confirmar_exclusao.html`:** mostra os dados do lançamento e pergunta "Tem certeza que deseja excluir?"; botão "Excluir" (formulário POST) e "Cancelar".

JavaScript: **não é necessário na v1.** O filtro de categorias por tipo é feito no servidor (a URL de cadastro já define o tipo). Se algum JS for adicionado, ele deve ser opcional (a página funciona sem ele).

### Fluxo principal

```
/ (mês atual) ──"Novo gasto"──> /lancamentos/novo/gasto/ ──Salvar OK──> /<ano>/<mês da data>/ + mensagem
      │                                      └──erro──> mesmo formulário com mensagens nos campos
      ├──"Editar"──> /lancamentos/<id>/editar/ ──Salvar OK──> /<ano>/<mês da data>/ + mensagem
      ├──"Excluir"──> /lancamentos/<id>/excluir/ ──Confirmar (POST)──> /<ano>/<mês>/ + mensagem
      └──"‹ / ›"──> /<ano>/<mes>/ (mês anterior ou seguinte)
```

### Regras de validação

| # | Campo | Regra | Mensagem de erro |
| --- | --- | --- | --- |
| V1 | valor | obrigatório | "Informe o valor." |
| V2 | valor | número válido, até 2 casas decimais, aceita vírgula | "Informe um valor válido, por exemplo 12,50." |
| V3 | valor | maior ou igual a 0,01 (zero e negativos são rejeitados) | "O valor deve ser maior que zero." |
| V4 | valor | no máximo 9.999.999.999,99 (limite do `max_digits=12`) | mensagem padrão do Django |
| V5 | data | obrigatória e válida (datas futuras são permitidas, para lançamentos agendados) | "Informe uma data válida." |
| V6 | descrição | obrigatória, sem ser só espaços (espaços nas pontas são removidos), até 200 caracteres | "Informe uma descrição." |
| V7 | categoria | obrigatória e do **mesmo tipo** do lançamento | "Escolha uma categoria de gasto." / "Escolha uma categoria de receita." |
| V8 | tipo | definido pela URL no cadastro; não editável | (não aparece no formulário) |

A regra V7 fica no `clean()` do modelo (vale também no admin) e o formulário também restringe o `queryset` da categoria.

## 8. Critérios de aceite

Todos devem ser verificáveis por teste automatizado (`pytest`), exceto quando indicado "(manual)".

**Cadastro**
- **CA1:** Dado que estou em `/lancamentos/novo/gasto/`, quando envio valor `50,00`, data `10/10/2026`, descrição `Mercado` e categoria `Alimentação`, então um lançamento do tipo gasto com valor `Decimal("50.00")` é salvo e sou redirecionado para `/2026/10/` com a mensagem "Gasto cadastrado com sucesso."
- **CA2:** Dado que estou em `/lancamentos/novo/receita/`, quando envio valor `3000`, data válida, descrição e categoria `Salário`, então um lançamento do tipo receita é salvo com valor `Decimal("3000.00")`.
- **CA3:** Dado o formulário de novo gasto, quando o abro, então a lista de categorias contém apenas categorias de gasto e a data vem preenchida com hoje.
- **CA4:** Dado o formulário de novo gasto, quando envio valor `0` ou `-10`, então nada é salvo e aparece "O valor deve ser maior que zero."
- **CA5:** Dado o formulário de novo gasto, quando envio valor `abc` ou campo vazio, então nada é salvo e aparece mensagem de erro no campo valor.
- **CA6:** Dado o formulário de novo gasto, quando envio a descrição só com espaços, então nada é salvo e aparece "Informe uma descrição."
- **CA7:** Dado o formulário de novo gasto, quando forço no POST o id de uma categoria de receita, então nada é salvo e aparece erro no campo categoria.
- **CA8:** Dado que acesso `/lancamentos/novo/outro/`, então recebo 404.
- **CA9:** Dado o formulário de novo gasto, quando envio valor `1.234,56`, então o valor salvo é `Decimal("1234.56")`.

**Edição e exclusão**
- **CA10:** Dado um gasto existente, quando altero a descrição e o valor em `/lancamentos/<id>/editar/` e salvo, então os novos dados ficam gravados, o tipo continua "gasto" e sou redirecionado para o mês da data do lançamento.
- **CA11:** Dado um gasto existente, quando abro a tela de edição, então o formulário não tem campo de tipo e a lista de categorias tem apenas categorias de gasto.
- **CA12:** Dado um lançamento existente, quando acesso `/lancamentos/<id>/excluir/` por GET, então vejo a confirmação e o lançamento **continua** no banco.
- **CA13:** Dado um lançamento existente, quando confirmo a exclusão (POST), então ele é removido e sou redirecionado ao mês dele com a mensagem de sucesso.
- **CA14:** Dado um id que não existe, quando acesso editar ou excluir, então recebo 404.

**Página do mês e saldo**
- **CA15:** Dado que em outubro/2026 existem receita de `3000,00` e gastos de `1200,50` e `299,50`, quando acesso `/2026/10/`, então vejo Receitas `R$ 3.000,00`, Gastos `R$ 1.500,00` e Saldo `R$ 1.500,00`.
- **CA16:** Dado que em outubro/2026 há só um gasto de `100,00`, quando acesso `/2026/10/`, então o saldo exibido é `-R$ 100,00` (ou `R$ -100,00`) com destaque de saldo negativo.
- **CA17:** Dado um lançamento em 31/10/2026 e outro em 01/11/2026, quando acesso `/2026/10/`, então só o de 31/10 aparece e entra nos totais.
- **CA18:** Dado um mês sem lançamentos, quando o acesso, então vejo "Nenhum lançamento neste mês." e os três totais em `R$ 0,00`.
- **CA19:** Dado que estou em `/2026/12/`, então o link "Próximo mês" aponta para `/2027/1/` e o "Mês anterior" para `/2026/11/`; dado `/2026/1/`, o "Mês anterior" aponta para `/2025/12/`.
- **CA20:** Dado que acesso `/`, então vejo a página do mês atual (mesmo conteúdo de `/<ano atual>/<mês atual>/`).
- **CA21:** Dado que acesso `/2026/13/` ou `/2026/0/`, então recebo 404.
- **CA22:** Dado lançamentos em datas diferentes no mesmo mês, quando acesso o mês, então eles aparecem da data mais recente para a mais antiga.

**Dados, segurança e qualidade**
- **CA23:** Dado um banco recém-migrado (`migrate`), então as 8 categorias de gasto e 4 de receita listadas na seção 7 existem.
- **CA24:** Dado uma categoria com lançamentos, quando tento excluí-la, então o Django impede (`ProtectedError`).
- **CA25:** Dado o repositório, então `.env` não está versionado, `.env.example` está, e o `settings.py` não contém a `SECRET_KEY` escrita no código.
- **CA26:** Dado o projeto, quando rodo `ruff check .`, `ruff format --check .` e `pytest`, então os três terminam sem erros.
- **CA27 (manual):** Dado o servidor rodando, quando abro o app no navegador do computador e numa janela estreita (celular), então todas as telas são legíveis e utilizáveis.

## 9. Arquivos e estrutura previstos

```
controle-gastos/
├── .venv/                      # ambiente virtual (fora do git)
├── .env                        # SECRET_KEY e DEBUG (fora do git)
├── .env.example                # modelo do .env, sem valores reais
├── .gitignore                  # .venv/, .env, db.sqlite3, __pycache__/, .pytest_cache/, .ruff_cache/
├── README.md                   # o que é, como instalar, rodar e testar (passo a passo)
├── requirements.txt            # Django, python-dotenv, pytest, pytest-django, ruff (versões fixadas)
├── pyproject.toml              # configuração do ruff e do pytest (DJANGO_SETTINGS_MODULE = "setup.settings")
├── manage.py
├── docs/
│   └── PRD.md                  # este documento
├── setup/                      # projeto Django (mesmo nome do projeto da Alura, por familiaridade)
│   ├── __init__.py
│   ├── settings.py             # dotenv, pt-br, America/Sao_Paulo, app financas
│   ├── urls.py                 # inclui financas.urls e admin
│   ├── asgi.py
│   └── wsgi.py
└── financas/                   # app principal
    ├── __init__.py
    ├── apps.py
    ├── admin.py                # registra Categoria e Lancamento
    ├── models.py               # Tipo, Categoria, Lancamento, função resumo_do_mes(ano, mes)
    ├── forms.py                # LancamentoForm (ModelForm)
    ├── views.py                # mes_atual, mes, lancamento_novo, lancamento_editar, lancamento_excluir
    ├── urls.py
    ├── migrations/
    │   ├── 0001_initial.py
    │   └── 0002_categorias_iniciais.py   # migração de dados (seed)
    ├── templates/financas/
    │   ├── base.html
    │   ├── mes.html
    │   ├── lancamento_form.html
    │   └── lancamento_confirmar_exclusao.html
    ├── static/financas/css/
    │   └── estilo.css
    └── tests/
        ├── __init__.py
        ├── test_models.py      # validações, constraints, seed, resumo do mês
        ├── test_forms.py       # valor com vírgula, zero/negativo, descrição vazia, categoria de outro tipo
        └── test_views.py       # rotas, redirecionamentos, 404, totais e navegação
```

Observações:
- Formatação de dinheiro nos templates: filtro nativo `floatformat:"2g"` com `pt-br` (gera `1.234,56`), precedido de `R$`. Sem filtro customizado.
- Navegação entre meses: cálculo de mês anterior/seguinte feito na view com aritmética simples de ano/mês (sem biblioteca extra).
- `.env.example`:
  ```
  SECRET_KEY=troque-por-uma-chave-secreta
  DEBUG=True
  ```

## 10. Ordem de implementação (etapas pequenas)

Cada etapa termina com algo que dá para **ver funcionando** e um **commit local** com mensagem clara. Nada de `git push` sem confirmação do Lucas.

1. **Ambiente e repositório:** criar a pasta, `git init`, `.venv`, `.gitignore`, `requirements.txt`, `.env` e `.env.example`. Commit: "Configura ambiente do projeto".
2. **Projeto Django:** `django-admin startproject setup .`; ajustar `settings.py` (dotenv, `pt-br`, fuso de São Paulo); `runserver` abre a página padrão. Commit.
3. **Ferramentas de qualidade:** `pyproject.toml` com ruff e pytest-django; um teste simples ("a página de admin responde") passando. Commit.
4. **App e modelos:** criar o app `financas`, os modelos `Categoria` e `Lancamento`, `makemigrations`/`migrate`, registrar no admin. Testes de modelo (valor positivo, categoria do tipo certo, `PROTECT`). Commit.
5. **Categorias iniciais:** migração de dados `0002_categorias_iniciais`. Teste CA23. Commit.
6. **Página do mês (só leitura):** rota `/<ano>/<mes>/` e `/`, função `resumo_do_mes`, template `mes.html` com tabela e totais. Lançamentos de teste criados pelo admin. Testes CA15–CA18, CA20–CA22. Commit.
7. **Navegação entre meses:** links anterior/próximo/atual com virada de ano. Teste CA19. Commit.
8. **Cadastro:** `LancamentoForm`, rota `/lancamentos/novo/<tipo>/`, mensagens de sucesso. Testes CA1–CA9. Commit.
9. **Edição:** rota de editar reutilizando o mesmo formulário e template. Testes CA10, CA11, CA14. Commit.
10. **Exclusão:** página de confirmação + POST. Testes CA12–CA14. Commit.
11. **Acabamento:** CSS (cartões, tabela, saldo negativo em vermelho, layout em uma coluna no celular), estado vazio, README com passo a passo. Commit.
12. **Revisão final:** rodar `ruff check .`, `ruff format --check .`, `pytest` e conferir manualmente o CA27. Commit final da v1.

## 11. Riscos e dependências

- **Dependências:** Python 3 instalado; pacotes `Django`, `python-dotenv`, `pytest`, `pytest-django`, `ruff`. `prettier` só se o Node estiver disponível (é opcional para o CSS).
- **Separador decimal:** o usuário digita `12,50`; se o formulário não estiver com localização ativa, `12,50` é rejeitado. Mitigação: campo `valor` com `localize=True` e o teste CA9.
- **Arredondamento:** usar `float` em qualquer ponto causaria centavos errados. Mitigação: RNF2 e testes com `Decimal`.
- **Fuso horário:** "mês atual" e "hoje" devem usar a data local (`django.utils.timezone.localdate()`), não a UTC, senão perto da meia-noite o mês pode sair errado.
- **Iniciante em Git:** risco de versionar o `.env` ou o `db.sqlite3`. Mitigação: `.gitignore` criado na etapa 1, **antes** do primeiro commit, e CA25.
- **Prettier x templates Django:** ver RNF6.
- **Mudança de categorias via admin:** renomear uma categoria muda todos os lançamentos antigos dela (aceitável na v1).

## 12. Fora de escopo (futuro)

- Gráficos (por categoria, evolução mensal).
- Login e multiusuário.
- Importar extrato bancário em CSV.
- Orçamento/limite por categoria.
- Tela própria para cadastrar/editar categorias (na v1 só pelo admin).
- Filtros e busca na lista, totais por categoria, exportação de dados.
- Lançamentos recorrentes ou parcelados, múltiplas contas/cartões, múltiplas moedas.
- Deploy em servidor/hospedagem; uso de outro banco além do SQLite.
- Alterar o tipo de um lançamento já cadastrado.

## 13. Perguntas em aberto

1. A lista de categorias iniciais (seção 7) atende, ou o Lucas quer incluir/renomear alguma antes da implementação?
2. Na edição, o tipo do lançamento fica travado (para trocar gasto ↔ receita é preciso excluir e cadastrar de novo). Isso está ok?
3. Datas futuras são permitidas (para registrar contas agendadas). Está ok, ou prefere bloquear?
