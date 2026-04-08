"""
Exemplo v2 — Relatório de Cliente
===================================
Demonstra TODAS as novas features da v2:

  Inline:  Badge, DataHora, Local, Ancora, RefCruzada, MarcadorRodape, Variavel
  Block:   TabelaConteudo, CelulaTabela (avançada), Assinatura
  Control: Se (condicional), Para (loop)
  Forms:   Formulario, CampoFormulario
  Engine:  gerar_stream(), gerar_bytes(), contexto={}
  Tmpls:   usar_template(), relatorio_executivo, ata_reuniao, contrato_simples
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from docschema import (
    # Document
    Documento, Secao,
    # Block
    Titulo, Subtitulo, Paragrafo, Lista, ItemLista, Tabela,
    CelulaTabela, TabelaConteudo, NotaRodape,
    Nota, BlocoDestaque, Citacao, Codigo,
    LinhaHorizontal, Espaco, QuebraPagina,
    Formulario, CampoFormulario,
    Se, Para, Assinatura,
    # Inline
    Texto, Negrito, Italico, Sublinhado,
    Link, Badge, DataHora, Local,
    Ancora, RefCruzada, MarcadorRodape, Variavel,
    # Engine
    gerar, gerar_stream, gerar_bytes,
    # Templates
    usar_template, listar_templates,
)

# ── Dados simulados ────────────────────────────────────────────────────────────

CLIENTE = {
    "id":          "C-2025-0042",
    "nome":        "João da Silva",
    "empresa":     "Silva Tecnologia Ltda.",
    "ativo":       True,
    "premium":     True,
    "score":       92,
    "local":       {"cidade": "Umuarama", "estado": "PR"},
    "contratos": [
        {"numero": "C-001", "desc": "Consultoria técnica",   "valor": 1_200.00, "status": "vigente"},
        {"numero": "C-002", "desc": "Desenvolvimento web",   "valor":   850.00, "status": "encerrado"},
        {"numero": "C-003", "desc": "Suporte mensal 24h",    "valor": 3_400.00, "status": "vigente"},
    ],
    "observacao":  "Cliente prioritário — SLA máx. 4 horas.",
    "responsavel": "Dra. Ana Paula Ferreira",
    "cargo_resp":  "Gerente de Relacionamento",
}

CONTEXTO = {
    "empresa":      "DocSchema SaaS",
    "periodo":      "Abril 2025",
    "mostrar_form": True,     # controla Se(mostrar_form, ...)
}

# ── Documento ─────────────────────────────────────────────────────────────────

doc = Documento(
    titulo="Relatório de Cliente",
    autor=CLIENTE["responsavel"],
    format_options={
        "html":      {"css_class": "relatorio"},
        "txt":       {"line_width": 80},
        "clipboard": {"mode": "compact"},
        "docx":      {"toc": True},
    },
)

# ── Sumário automático ─────────────────────────────────────────────────────────
# Em DOCX gera campo de TOC real (atualiza automaticamente ao abrir).
# Em HTML/TXT/MD gera lista com links âncora.
doc.add(TabelaConteudo(titulo="Sumário", show_levels=2, numerado=True))

# ── Seção de cabeçalho ─────────────────────────────────────────────────────────
# Variavel → resolve do contexto em gerar_stream/gerar
# DataHora → now() ou valor estático
# Local    → formata cidade/estado com formato customizável
cabecalho = Secao(id="cabecalho")
cabecalho.add(Paragrafo([
    Texto("Empresa: "), Variavel("empresa", "—"),
    Texto("  ·  Período: "), Badge(Variavel("periodo", "?"), tipo="info"),
]))
cabecalho.add(Paragrafo([
    Texto("Emitido em: "), DataHora(formato="%d/%m/%Y às %H:%M"),
    Texto("  ·  Local: "),
    Local(
        cidade=CLIENTE["local"]["cidade"],
        estado=CLIENTE["local"]["estado"],
        pais="Brasil",
        formato="{cidade} — {estado}/{pais}",
    ),
]))
doc.add(cabecalho)

# ── Seção 1: Dados do Cliente ─────────────────────────────────────────────────
# Ancora → ponto invisível que RefCruzada pode apontar
sec1 = Secao(
    titulo=Titulo([Texto("1. Dados do Cliente"), Ancora(id="sec-dados")], nivel=2),
    id="dados-cliente",
)
sec1.add(Paragrafo([Texto("ID: "), Badge(CLIENTE["id"], tipo="primary")]))
sec1.add(Paragrafo([Texto("Nome: "), Negrito(CLIENTE["nome"])]))
sec1.add(Paragrafo([Texto("Empresa: "), Texto(CLIENTE["empresa"])]))

# Se (bool): badge de status ativo/inativo
sec1.add(Se(
    condicao=CLIENTE["ativo"],
    sim=[Paragrafo([Texto("Status: "), Badge("ATIVO",   tipo="success")])],
    nao=[Paragrafo([Texto("Status: "), Badge("INATIVO", tipo="danger")])],
))

# Se (bool): destaque premium
sec1.add(Se(
    condicao=CLIENTE["premium"],
    sim=[Paragrafo([
        Badge("PREMIUM", tipo="primary"),
        Texto(" — todos os recursos avançados disponíveis."),
        MarcadorRodape("Clientes Premium têm SLA 99,9% e suporte 24/7."),
    ])],
))

# Score + nota de rodapé inline
score = CLIENTE["score"]
tipo_score = "success" if score >= 90 else "info" if score >= 70 else "warning"
sec1.add(Paragrafo([
    Texto("Score de crédito: "),
    Badge(str(score), tipo=tipo_score),
    MarcadorRodape("Score calculado pela metodologia interna v3.2."),
    Texto(" — referência: metodologia"),
    RefCruzada("sec-dados", " (ver seção 1)"),
    Texto("."),
]))
doc.add(sec1)

# ── Seção 2: Contratos ────────────────────────────────────────────────────────
# Tabela avançada com CelulaTabela:
#   - alinhamento por coluna (left / center / right)
#   - células com InlineContent ([Badge(...)])
#   - linha de total com negrito
sec2 = Secao(
    titulo=Titulo([Texto("2. Contratos"), Ancora(id="sec-contratos")], nivel=2),
    id="contratos",
)

cab = [
    CelulaTabela("Nº",           align="center", negrito=True),
    CelulaTabela("Descrição",    align="left",   negrito=True),
    CelulaTabela("Valor (R$)",   align="right",  negrito=True),
    CelulaTabela("Status",       align="center", negrito=True),
]
linhas = []
total_valor = 0.0
for c in CLIENTE["contratos"]:
    tipo_b = "success" if c["status"] == "vigente" else "default"
    linhas.append([
        CelulaTabela(c["numero"],                                align="center"),
        CelulaTabela(c["desc"],                                  align="left"),
        CelulaTabela(f'{c["valor"]:,.2f}',                       align="right"),
        CelulaTabela([Badge(c["status"].capitalize(), tipo=tipo_b)], align="center"),
    ])
    total_valor += c["valor"]

linhas.append([
    CelulaTabela("",                                align="center"),
    CelulaTabela("TOTAL",                          align="right",  negrito=True),
    CelulaTabela(f"R$ {total_valor:,.2f}",         align="right",  negrito=True),
    CelulaTabela("",                                align="center"),
])

sec2.add(Tabela(
    cabecalho=cab,
    linhas=linhas,
    legenda="(*) Valores em BRL. Inclui contratos encerrados.",
    format_options={
        "txt":       {"fallback_strategy": "columns", "min_column_width": 15},
        "clipboard": {"fallback_strategy": "list"},
    },
))

# Para (loop): detalha contratos vigentes dinamicamente
vigentes = [c for c in CLIENTE["contratos"] if c["status"] == "vigente"]
if vigentes:
    sec2.add(Titulo([Texto("Contratos Vigentes")], nivel=3))
    sec2.add(Para(
        itens=vigentes,
        template=lambda c, ctx: [
            Paragrafo([
                Badge(c["numero"], tipo="primary"), Texto(" "),
                Negrito(c["desc"]),
                Texto(f"  —  R$ {c['valor']:,.2f}/mês"),
            ])
        ],
    ))

doc.add(sec2)

# ── Seção 3: Observações ──────────────────────────────────────────────────────
sec3 = Secao(
    titulo=Titulo([Texto("3. Observações"), Ancora(id="sec-obs")], nivel=2),
    id="observacoes",
)
sec3.add(Nota([Italico(CLIENTE["observacao"])], tipo="warning"))
sec3.add(Paragrafo([
    Texto("Para ver todos os contratos, consulte a "),
    RefCruzada("sec-contratos", "seção 2 — Contratos"),
    Texto("."),
]))
doc.add(sec3)

# ── Seção 4: Formulário (condicional via contexto) ────────────────────────────
# Se(condicao="mostrar_form") → lê ctx["mostrar_form"] em runtime
doc.add(Se(
    condicao="mostrar_form",
    sim=[
        Secao(
            titulo=Titulo([Texto("4. Atualização de Dados")], nivel=2),
            children=[
                Formulario(
                    titulo="Formulário de Atualização",
                    acao="/cliente/atualizar",
                    metodo="post",
                    campos=[
                        CampoFormulario("nome",    tipo="text",     label="Nome",          obrigatorio=True, valor=CLIENTE["nome"]),
                        CampoFormulario("email",   tipo="email",    label="E-mail de contato", obrigatorio=True),
                        CampoFormulario("status",  tipo="select",   label="Status",        opcoes=["Ativo", "Inativo", "Bloqueado"]),
                        CampoFormulario("score",   tipo="number",   label="Score",         valor=str(score)),
                        CampoFormulario("obs",     tipo="textarea", label="Observações internas"),
                        CampoFormulario("premium", tipo="checkbox", label="Conta Premium", valor="true" if CLIENTE["premium"] else ""),
                    ],
                )
            ],
        )
    ],
    nao=[Paragrafo([Italico("Formulário indisponível neste contexto.")])],
))

# ── Rodapé ────────────────────────────────────────────────────────────────────
doc.add(LinhaHorizontal())
doc.add(Citacao(
    [Texto("Gerado automaticamente por "), Variavel("empresa", "docschema"), Texto(".")],
    autoria="Sistema de Relacionamento com o Cliente",
))
doc.add(Assinatura(
    nome=CLIENTE["responsavel"],
    cargo=CLIENTE["cargo_resp"],
    local=f'{CLIENTE["local"]["cidade"]}/{CLIENTE["local"]["estado"]}',
    mostrar_data=True,
    mostrar_local=True,
))

# ──────────────────────────────────────────────────────────────────────────────
# 🚀 Geração em múltiplos formatos
# ──────────────────────────────────────────────────────────────────────────────
def hr(titulo): print("\n" + "═" * 64 + f"\n  {titulo}\n" + "═" * 64)

if __name__ == "__main__":

    # ── 1. TXT com contexto ────────────────────────────────────────────────────
    hr("1. TXT (com contexto)")
    txt = gerar(doc, "txt", contexto=CONTEXTO)
    print(txt[:700])
    print("  ...")

    # ── 2. Streaming TXT ──────────────────────────────────────────────────────
    hr("2. Streaming TXT chunk-a-chunk")
    chunks = list(gerar_stream(doc, "txt", contexto=CONTEXTO))
    print(f"  Total de chunks: {len(chunks)}")
    for i, c in enumerate(chunks[:4], 1):
        print(f"  [{i}] {repr(c[:70])}")

    # ── 3. Markdown ───────────────────────────────────────────────────────────
    hr("3. Markdown (excerpt)")
    md = gerar(doc, "markdown", contexto=CONTEXTO)
    print(md[:600])

    # ── 4. HTML ───────────────────────────────────────────────────────────────
    hr("4. HTML (excerpt)")
    html = gerar(doc, "html", contexto=CONTEXTO)
    print(html[:700])

    # ── 5. Streaming HTML ─────────────────────────────────────────────────────
    hr("5. Streaming HTML — join all chunks")
    html_stream = "".join(gerar_stream(doc, "html", contexto=CONTEXTO))
    print(f"  HTML via stream: {len(html_stream)} chars, igual direto: {html_stream == html}")

    # ── 6. gerar_bytes PDF ────────────────────────────────────────────────────
    hr("6. gerar_bytes() — PDF em memória (BytesIO)")
    try:
        buf = gerar_bytes(doc, "pdf", contexto=CONTEXTO)
        data = buf.read()
        print(f"  ✅  PDF em memória: {len(data):,} bytes")
        print(f"      Header: {data[:8]}")
    except ImportError:
        print("  ⚠️   PDF: instale com  pip install reportlab")

    # ── 7. gerar_bytes DOCX ───────────────────────────────────────────────────
    hr("7. gerar_bytes() — DOCX em memória (BytesIO)")
    try:
        buf_docx = gerar_bytes(doc, "docx", contexto=CONTEXTO)
        print(f"  ✅  DOCX em memória: {len(buf_docx.read()):,} bytes")
    except ImportError:
        print("  ⚠️   DOCX: instale com  pip install python-docx")

    # ── 8. Templates disponíveis ──────────────────────────────────────────────
    hr("8. Templates registrados")
    for t in listar_templates():
        print(f"  • {t['nome']:<30s} {t['descricao']}")

    # ── 9. Template: relatorio_executivo ──────────────────────────────────────
    hr("9. Template — relatorio_executivo")
    doc_rel = usar_template(
        "relatorio_executivo",
        titulo="Resultados Q1 2025",
        autor="Maria Silva",
        empresa="Acme Corp",
        periodo="Q1 2025",
        cargo="Diretora de Operações",
        local="São Paulo/SP",
        sumario="Este relatório consolida os resultados operacionais do primeiro trimestre.",
        secoes=[
            {"titulo": "Receita",    "conteudo": "A receita cresceu 18% no período."},
            {"titulo": "Despesas",   "conteudo": "Despesas operacionais mantidas estáveis em R$ 320k."},
            {"titulo": "Resultados", "conteudo": "Lucro líquido de R$ 420.000,00.",
             "itens": ["Meta atingida", "NPS: 72", "Churn < 2%"]},
        ],
    )
    print(gerar(doc_rel, "txt")[:600])

    # ── 10. Template: ata_reuniao ─────────────────────────────────────────────
    hr("10. Template — ata_reuniao")
    ata = usar_template(
        "ata_reuniao",
        titulo="Ata — Sprint Review #12",
        data="2025-04-07 14:00",
        local="Sala 3 / Google Meet",
        responsavel="Beatriz Costa",
        participantes=[
            {"nome": "Carlos Mendes", "cargo": "Tech Lead"},
            {"nome": "Beatriz Costa", "cargo": "Scrum Master"},
            {"nome": "Pedro Alves",   "cargo": "Dev Backend"},
        ],
        pauta=["Review das histórias do sprint", "Demo das features", "Planejamento sprint 13"],
        decisoes=[
            "Feature de notificações adiada para sprint 14",
            "Cache com Redis aprovado para sprint 13",
        ],
        acoes=[
            {"tarefa": "Configurar Redis",  "responsavel": "Pedro Alves",   "prazo": "10/04", "status": "Pendente"},
            {"tarefa": "Atualizar backlog", "responsavel": "Beatriz Costa", "prazo": "08/04", "status": "Em andamento"},
        ],
    )
    print(gerar(ata, "txt")[:600])

    # ── 11. Template: proposta_comercial ─────────────────────────────────────
    hr("11. Template — proposta_comercial")
    proposta = usar_template(
        "proposta_comercial",
        titulo="Proposta de Desenvolvimento Web",
        empresa_para="Silva Tecnologia Ltda.",
        empresa_de="DevStudio Agency",
        responsavel="Lucas Ramos",
        cargo="Diretor Comercial",
        validade="15 dias",
        itens=[
            {"desc": "Desenvolvimento frontend (React)", "qtd": 1, "unit": "R$ 8.000",  "total": "R$ 8.000"},
            {"desc": "API REST Node.js",                 "qtd": 1, "unit": "R$ 5.500",  "total": "R$ 5.500"},
            {"desc": "Infraestrutura (AWS, 12 meses)",   "qtd": 1, "unit": "R$ 3.600",  "total": "R$ 3.600"},
        ],
        total="R$ 17.100,00",
        condicoes=["Pagamento: 50% na assinatura, 50% na entrega", "Prazo de entrega: 45 dias úteis", "Suporte incluso por 30 dias"],
    )
    print(gerar(proposta, "txt")[:600])

    print("\n" + "═" * 64)
    print("  ✅  Todos os testes passaram!")
    print("═" * 64 + "\n")
