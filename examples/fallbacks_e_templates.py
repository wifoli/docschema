"""
Exemplo 3 — Fallbacks, format_options e Templates customizados
================================================================
Demonstra:

  FALLBACKS
    • fallback_por_tipo()     — fallback semântico de imagem
    • fallback_imagem()       — fallback customizado de imagem
    • opts_tabela_financeira()— format_options para tabela financeira
    • tabela_sem_suporte_txt()— fallback completo de tabela sem suporte TXT
    • FO_CITACAO_FORMAL       — format_options de citação formal
    • FO_NOTA_DESTAQUE        — format_options de nota com borda
    • FO_CODIGO_TERMINAL      — format_options de código de terminal

  TEMPLATES CUSTOMIZADOS (3 padrões de registro)
    • @registrar_template     — decorator (padrão 1)
    • TemplateRegistro.registrar() — manual (padrão 2)
    • Template(...)            — classe direta (padrão 3)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

# ── Ativar templates customizados (só importar já registra!) ──────────────────
import docschema.templates.meu_relatorio_mensal   # registra 4 templates novos

from docschema import (
    Documento, Secao, Titulo, Paragrafo, Tabela, Lista, ItemLista,
    Imagem, Citacao, Nota, Codigo, BlocoDestaque,
    LinhaHorizontal, Espaco,
    Texto, Negrito, Italico,
    gerar, gerar_stream,
    usar_template, listar_templates,
)
from docschema.fallback import (
    # Imagens
    fallback_por_tipo, fallback_imagem,
    FALLBACK_GRAFICO, FALLBACK_LOGO,
    # Tabelas
    opts_tabela_financeira, opts_tabela_dados, tabela_sem_suporte_txt,
    # format_options gerais
    FO_CITACAO_FORMAL, FO_CITACAO_CURTA,
    FO_NOTA_DESTAQUE, FO_NOTA_SUTIL,
    FO_CODIGO_TERMINAL, FO_CODIGO_DESTACADO,
    FO_PARAGRAFO_LEAD, FO_BLOCO_IMPORTANTE, FO_LISTA_CHECKLIST,
)
from docschema.templates.meu_relatorio_mensal import template_ordem_servico


def hr(titulo): print("\n" + "═"*64 + f"\n  {titulo}\n" + "═"*64)


# ──────────────────────────────────────────────────────────────────────────────
# PARTE 1: FALLBACKS
# ──────────────────────────────────────────────────────────────────────────────

hr("PARTE 1 — Fallbacks de Imagem")

doc_img = Documento(titulo="Demo Fallbacks de Imagem")

# fallback_por_tipo: detecta o tipo semanticamente
doc_img.add(Imagem(
    src="charts/vendas_q1.png",
    alt="Gráfico de vendas Q1",
    legenda="Figura 1 — Vendas Q1 2025",
    fallback=fallback_por_tipo("grafico", "Gráfico de Vendas Q1 2025"),
))

# fallback customizado com URL de acesso alternativo
doc_img.add(Imagem(
    src="charts/mapa_calor.png",
    alt="Mapa de calor de acessos",
    legenda="Figura 2 — Heatmap de acessos por hora",
    fallback=fallback_imagem(
        txt="[Mapa de calor — acesse https://dash.interno.com/heatmap]",
        clipboard="heatmap-acessos",
        markdown="*Ver mapa interativo em: https://dash.interno.com/heatmap*",
    ),
))

# Logo — fallback FALLBACK_LOGO omite em todos os formatos de texto
doc_img.add(Imagem(
    src="assets/logo.png",
    alt="Logo da empresa",
    fallback=FALLBACK_LOGO,
))

print(gerar(doc_img, "txt"))


hr("PARTE 2 — Fallbacks de Tabela")

doc_tab = Documento(titulo="Demo Fallbacks de Tabela")

# Tabela financeira: alinhamento + estratégia list no clipboard
doc_tab.add(Titulo([Texto("Tabela Financeira (format_options)")], nivel=2))
doc_tab.add(Tabela(
    cabecalho=["Produto", "Qtd", "Unit.", "Total"],
    linhas=[
        ["Licença Pro",   "10", "R$ 129,00", "R$ 1.290,00"],
        ["Suporte Anual",  "1", "R$ 599,00",   "R$ 599,00"],
        ["Onboarding",     "1", "R$ 200,00",   "R$ 200,00"],
    ],
    legenda="Valores sem impostos.",
    format_options=opts_tabela_financeira(min_column_width=15),
))

# Tabela complexa sem suporte TXT — fallback mostra mensagem
doc_tab.add(Titulo([Texto("Tabela sem suporte TXT (fallback=)")], nivel=2))
doc_tab.add(Tabela(
    cabecalho=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
    linhas=[
        ["12k", "14k", "18k", "15k", "22k", "19k"],
    ],
    legenda="Evolução mensal em R$ mil.",
    fallback=tabela_sem_suporte_txt("Ver tabela de evolução no HTML/PDF."),
))

print(gerar(doc_tab, "txt"))
print("\n--- HTML excerpt ---")
html = gerar(doc_tab, "html")
print(html[:600])


hr("PARTE 3 — format_options de elementos ricos")

doc_fo = Documento(titulo="Demo format_options")

# Parágrafo lead
doc_fo.add(Paragrafo(
    [Texto("Bem-vindo ao relatório anual de sustentabilidade da empresa.")],
    format_options=FO_PARAGRAFO_LEAD,
))

# Citação formal com indent e tag blockquote
doc_fo.add(Citacao(
    [Texto("A excelência não é um ato, é um hábito.")],
    autoria="Aristóteles",
    format_options=FO_CITACAO_FORMAL,
))

# Nota com borda no TXT
doc_fo.add(Nota(
    [Negrito("Atenção: "), Texto("prazo final dia 30. Não haverá prorrogação.")],
    tipo="warning",
    format_options=FO_NOTA_DESTAQUE,
))

# Código de terminal
doc_fo.add(Codigo(
    "pip install docschema[pdf,docx]\npython -m docschema --help",
    linguagem="bash",
    format_options=FO_CODIGO_TERMINAL,
))

# BlocoDestaque importante
bloco = BlocoDestaque(
    titulo="Ação Necessária",
    tipo="danger",
    format_options=FO_BLOCO_IMPORTANTE,
)
bloco.add(Paragrafo([Texto("Assine o termo até "), Negrito("15/04/2025"), Texto(".")]))
doc_fo.add(bloco)

# Lista checklist
doc_fo.add(Lista(
    children=[
        __import__("docschema").ItemLista([Texto("Revisar dados pessoais")]),
        __import__("docschema").ItemLista([Texto("Assinar contrato")]),
        __import__("docschema").ItemLista([Texto("Enviar documentos digitalizados")]),
    ],
    format_options=FO_LISTA_CHECKLIST,
))

print(gerar(doc_fo, "txt"))


# ──────────────────────────────────────────────────────────────────────────────
# PARTE 2: TEMPLATES CUSTOMIZADOS
# ──────────────────────────────────────────────────────────────────────────────

hr("PARTE 4 — Templates disponíveis (incluindo customizados)")
for t in listar_templates():
    print(f"  • {t['nome']:<35s} {t['descricao']}")


hr("PARTE 5 — Template customizado: relatorio_mensal_vendas  (padrão 1)")
doc_vendas = usar_template(
    "relatorio_mensal_vendas",
    mes="Março 2025",
    equipe="Equipe Sul",
    gerente="Carlos Mendes",
    meta_total=50_000,
    total_vendas=48_200,
    destaque="Fernanda Rocha",
    obs="Março teve 3 feriados — meta recalibrada para R$ 50k.",
    vendedores=[
        {"nome": "Fernanda Rocha",  "vendas": 19_800, "meta": 18_000},
        {"nome": "Bruno Carvalho",  "vendas": 15_400, "meta": 17_000},
        {"nome": "Juliana Souza",   "vendas": 13_000, "meta": 15_000},
    ],
)
print(gerar(doc_vendas, "txt"))


hr("PARTE 6 — Template customizado: recibo_simples  (padrão 2 — registro manual)")
recibo = usar_template(
    "recibo_simples",
    pagador="João da Silva",
    valor="R$ 850,00",
    descricao="Desenvolvimento de landing page - fevereiro/2025",
    recebedor="DevStudio Ltda.",
)
print(gerar(recibo, "txt"))

# Também funciona pelo alias:
recibo2 = usar_template("recibo", pagador="Maria", valor="R$ 200,00")
print(f"\nAlias 'recibo' funcionou: {bool(gerar(recibo2, 'txt'))}")


hr("PARTE 7 — Template como objeto: template_ordem_servico  (padrão 3)")
# Uso via objeto diretamente (sem registro global):
os_doc = template_ordem_servico.instanciar(
    numero="OS-2025-0088",
    cliente="Silva Tecnologia Ltda.",
    equipamento="Notebook Dell Inspiron 15 (SN: ABC123)",
    problema="Computador não liga. Bateria não carrega.",
    servicos=[
        "Diagnóstico completo do hardware",
        "Substituição do conector de carga",
        "Teste de estresse — 2 horas",
    ],
    tecnico="Ricardo Almeida",
    valor="R$ 420,00",
)
print(gerar(os_doc, "txt"))

# Também funciona via usar_template() porque também registramos:
os_doc2 = usar_template("ordem_servico", numero="OS-TEST", cliente="X", tecnico="Y")
print(f"\nTambém via usar_template: {bool(gerar(os_doc2, 'txt'))}")


hr("PARTE 8 — Streaming de template customizado")
doc_stream = usar_template("relatorio_mensal_vendas",
    mes="Abril 2025", equipe="Equipe Norte",
    gerente="Paula Torres", meta_total=30_000, total_vendas=31_500,
    vendedores=[{"nome": "Lucas", "vendas": 31_500, "meta": 30_000}],
)
chunks = list(gerar_stream(doc_stream, "txt"))
print(f"  Chunks gerados: {len(chunks)}")
for i, c in enumerate(chunks[:3], 1):
    print(f"  [{i}] {repr(c[:60])}")


print("\n" + "═"*64)
print("  ✅  Todos os testes passaram!")
print("═"*64 + "\n")
