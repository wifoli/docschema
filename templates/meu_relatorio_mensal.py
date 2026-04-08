"""
docschema/templates/meu_relatorio_mensal.py
============================================
Template customizado de exemplo — Relatório Mensal de Vendas.

Demonstra os 3 padrões de registro:

  PADRÃO 1 — @registrar_template (decorator, preferido)
  PADRÃO 2 — registrar manual sem decorator
  PADRÃO 3 — classe Template instanciada diretamente

Para ativar estes templates no seu projeto, basta importar este módulo
antes de usar usar_template():

    # Em qualquer ponto de entrada (main.py, settings.py, etc.):
    import docschema.templates.meu_relatorio_mensal   # só importar já registra

    # Depois use normalmente:
    from docschema import gerar
    from docschema.templates import usar_template

    doc = usar_template("relatorio_mensal_vendas", ...)
    print(gerar(doc, "html"))
"""
from docschema.templates import registrar_template, Template, TemplateRegistro


# ═══════════════════════════════════════════════════════════════════
# PADRÃO 1 — Decorator @registrar_template  (forma mais limpa)
# ═══════════════════════════════════════════════════════════════════

@registrar_template(
    "relatorio_mensal_vendas",
    descricao="Relatório mensal de performance de vendas por região",
)
def _relatorio_mensal_vendas(dados: dict):
    """
    Parâmetros esperados em dados:

        mes          str   "Janeiro 2025"
        ano          str   "2025"
        equipe       str   "Equipe Sul"
        gerente      str   "Carlos Mendes"
        vendedores   list  [{"nome": ..., "vendas": ..., "meta": ...}]
        total_vendas float
        meta_total   float
        destaque     str   nome do vendedor destaque
        obs          str   observações gerais (opcional)
    """
    from docschema import (
        Documento, Secao, Titulo, Paragrafo, Tabela, Lista, ItemLista,
        LinhaHorizontal, Assinatura, Nota, Texto, Negrito, Italico,
        Badge, DataHora, TabelaConteudo, Espaco,
    )
    from docschema.elements.block import CelulaTabela
    from docschema.fallback import opts_tabela_financeira

    mes          = dados.get("mes",          "Mês/Ano")
    equipe       = dados.get("equipe",       "Equipe")
    gerente      = dados.get("gerente",      "")
    vendedores   = dados.get("vendedores",   [])
    total_vendas = dados.get("total_vendas", 0.0)
    meta_total   = dados.get("meta_total",   0.0)
    destaque     = dados.get("destaque",     "")
    obs          = dados.get("obs",          "")

    # Calcula atingimento de meta
    pct = (total_vendas / meta_total * 100) if meta_total else 0
    status_badge = "success" if pct >= 100 else "warning" if pct >= 80 else "danger"

    doc = Documento(
        titulo=f"Relatório de Vendas — {mes}",
        autor=gerente,
        format_options={
            "html":  {"css_class": "relatorio-vendas"},
            "docx":  {"toc": False},
            "txt":   {"line_width": 80},
        },
    )

    # Cabeçalho
    cab = Secao(id="cabecalho")
    cab.add(Paragrafo([Negrito(equipe), Texto("  "), Badge(mes, tipo="info")]))
    cab.add(Paragrafo([
        Texto("Meta: R$ "), Negrito(f"{meta_total:,.2f}"),
        Texto("  ·  Realizado: R$ "), Negrito(f"{total_vendas:,.2f}"),
        Texto("  ·  "),
        Badge(f"{pct:.1f}%", tipo=status_badge),
    ]))
    if gerente:
        cab.add(Paragrafo([Texto("Gerente: "), Negrito(gerente)]))
    doc.add(cab)

    # Tabela de vendedores
    sec_t = Secao(titulo=Titulo([Texto("Desempenho por Vendedor")], nivel=2))
    cab_t = [
        CelulaTabela("Vendedor",  align="left",  negrito=True),
        CelulaTabela("Vendas",    align="right",  negrito=True),
        CelulaTabela("Meta",      align="right",  negrito=True),
        CelulaTabela("Ating. %",  align="center", negrito=True),
        CelulaTabela("Status",    align="center", negrito=True),
    ]
    rows = []
    for v in vendedores:
        v_pct  = (v["vendas"] / v["meta"] * 100) if v.get("meta") else 0
        v_tipo = "success" if v_pct >= 100 else "warning" if v_pct >= 80 else "danger"
        rows.append([
            CelulaTabela(v["nome"]),
            CelulaTabela(f'R$ {v["vendas"]:,.2f}',    align="right"),
            CelulaTabela(f'R$ {v.get("meta",0):,.2f}', align="right"),
            CelulaTabela(f"{v_pct:.1f}%",              align="center"),
            CelulaTabela([Badge("OK" if v_pct>=100 else "Abaixo", tipo=v_tipo)], align="center"),
        ])
    sec_t.add(Tabela(
        cabecalho=cab_t,
        linhas=rows,
        format_options=opts_tabela_financeira(min_column_width=14),
    ))
    doc.add(sec_t)

    # Destaque
    if destaque:
        sec_d = Secao(titulo=Titulo([Texto("Destaques do Mês")], nivel=2))
        sec_d.add(Paragrafo([
            Texto("⭐ Vendedor destaque: "), Negrito(destaque),
        ]))
        doc.add(sec_d)

    # Observações
    if obs:
        doc.add(Nota([Italico(obs)], tipo="info"))

    doc.add(LinhaHorizontal())
    doc.add(Assinatura(nome=gerente, cargo="Gerente de Vendas", mostrar_data=True))

    return doc


# ═══════════════════════════════════════════════════════════════════
# PADRÃO 2 — Registro manual sem decorator
# ═══════════════════════════════════════════════════════════════════
# Útil quando a função factory já existe em outro módulo
# ou quando você quer registrar sob vários nomes.

def _factory_recibo_simples(dados: dict):
    """
    Template de recibo simples.

    Parâmetros:
        pagador   str
        valor     str  "R$ 1.500,00"
        descricao str
        recebedor str
    """
    from docschema import (
        Documento, Paragrafo, LinhaHorizontal,
        Assinatura, Texto, Negrito, DataHora, Espaco,
    )

    pagador   = dados.get("pagador",   "_______________")
    valor     = dados.get("valor",     "R$ ___________")
    descricao = dados.get("descricao", "")
    recebedor = dados.get("recebedor", "")

    doc = Documento(titulo="Recibo", format_options={"txt": {"line_width": 60}})
    doc.add(Paragrafo([Negrito("RECIBO DE PAGAMENTO")]))
    doc.add(LinhaHorizontal())
    doc.add(Espaco(1))
    doc.add(Paragrafo([Texto("Recebi de "), Negrito(pagador)]))
    doc.add(Paragrafo([Texto("a quantia de "), Negrito(valor)]))
    if descricao:
        doc.add(Paragrafo([Texto("referente a: "), Texto(descricao)]))
    doc.add(Paragrafo([Texto("Data: "), DataHora(formato="%d de %B de %Y")]))
    doc.add(Espaco(2))
    doc.add(Assinatura(nome=recebedor, cargo="Recebedor", mostrar_local=False))
    return doc


# Registro manual — pode registrar sob múltiplos nomes/aliases:
TemplateRegistro.registrar(
    "recibo_simples",
    _factory_recibo_simples,
    descricao="Recibo de pagamento simples",
)
TemplateRegistro.registrar(
    "recibo",                           # alias curto
    _factory_recibo_simples,
    descricao="Alias de recibo_simples",
)


# ═══════════════════════════════════════════════════════════════════
# PADRÃO 3 — Classe Template instanciada diretamente
# ═══════════════════════════════════════════════════════════════════
# Útil quando você quer encapsular o template em um objeto
# com método .instanciar() para uso OO, sem depender do registro global.

def _factory_ordem_servico(dados: dict):
    """
    Template de ordem de serviço técnica.

    Parâmetros:
        numero       str   "OS-2025-0042"
        cliente      str
        equipamento  str
        problema     str
        servicos     list  ["Troca de HD", "Limpeza interna"]
        tecnico      str
        valor        str   "R$ 350,00"
    """
    from docschema import (
        Documento, Secao, Titulo, Paragrafo, Lista, ItemLista,
        LinhaHorizontal, Assinatura, Texto, Negrito, Badge,
        DataHora, Tabela,
    )
    from docschema.elements.block import CelulaTabela

    numero      = dados.get("numero",      "OS-?????")
    cliente     = dados.get("cliente",     "")
    equipamento = dados.get("equipamento", "")
    problema    = dados.get("problema",    "")
    servicos    = dados.get("servicos",    [])
    tecnico     = dados.get("tecnico",     "")
    valor       = dados.get("valor",       "A definir")

    doc = Documento(titulo=f"Ordem de Serviço {numero}")

    doc.add(Paragrafo([Badge(numero, tipo="primary"), Texto("  "), DataHora(formato="%d/%m/%Y")]))
    doc.add(Paragrafo([Texto("Cliente: "), Negrito(cliente)]))
    doc.add(Paragrafo([Texto("Equipamento: "), Negrito(equipamento)]))
    doc.add(Paragrafo([Texto("Problema relatado: "), Texto(problema)]))

    if servicos:
        doc.add(Titulo([Texto("Serviços Realizados")], nivel=2))
        lst = Lista(ordenada=True)
        for s in servicos:
            lst.add(ItemLista([Texto(str(s))]))
        doc.add(lst)

    doc.add(Paragrafo([Texto("Valor total: "), Negrito(valor)]))
    doc.add(LinhaHorizontal())
    doc.add(Assinatura(nome=tecnico, cargo="Técnico Responsável"))
    doc.add(Assinatura(nome=cliente, cargo="Cliente — Ciente e de acordo", mostrar_data=False))

    return doc


# Classe Template instanciada diretamente (não registra no global):
template_ordem_servico = Template(
    nome="ordem_servico",
    fn=_factory_ordem_servico,
    descricao="Ordem de serviço técnica com assinaturas duplas",
)

# Mas também registra no global para usar_template():
TemplateRegistro.registrar(
    "ordem_servico",
    _factory_ordem_servico,
    descricao=template_ordem_servico.descricao,
)
