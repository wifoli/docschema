"""
docschema.templates
====================
Template system for reusable document patterns.

Components:
  Template        — named template wrapping a factory function
  TemplateRegistro — global registry of templates
  registrar_template — decorator to register a template
  usar_template   — instantiate a registered template by name

Built-in templates (auto-registered):
  "relatorio_executivo"   — executive report with TOC, sections, signature
  "contrato_simples"      — simple contract with parties, clauses, signatures
  "ata_reuniao"           — meeting minutes with attendees and decisions
  "ficha_tecnica"         — product/project fact sheet
  "email_formal"          — formal email document
  "proposta_comercial"    — commercial proposal with pricing table

Usage:
    from docschema.templates import usar_template, registrar_template, listar_templates

    # Use built-in
    doc = usar_template(
        "relatorio_executivo",
        titulo="Relatório Q3 2025",
        autor="Maria Silva",
        empresa="Acme Corp",
        periodo="3º Trimestre 2025",
    )
    html = gerar(doc, "html")

    # Register custom
    @registrar_template("meu_template")
    def _meu_template(dados: dict):
        from docschema import Documento, Titulo, Paragrafo, Texto
        doc = Documento(titulo=dados.get("titulo", "Documento"))
        doc.add(Paragrafo([Texto(dados.get("conteudo", ""))]))
        return doc

    doc = usar_template("meu_template", titulo="Teste", conteudo="Olá mundo")
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


# ── Template class ────────────────────────────────────────────────────────────

class Template:
    """
    A named document template.

    A template wraps a factory function:
        fn(dados: dict) -> Documento

    The factory receives all keyword arguments passed to usar_template().
    """

    def __init__(self, nome: str, fn: Callable[[Dict[str, Any]], Any], descricao: str = ""):
        self.nome      = nome
        self.fn        = fn
        self.descricao = descricao

    def instanciar(self, **dados) -> Any:
        """Instantiate the template with the given data."""
        return self.fn(dados)

    def __repr__(self) -> str:
        return f"Template({self.nome!r})"


# ── Registry ──────────────────────────────────────────────────────────────────

class TemplateRegistro:
    """Global registry of named templates."""

    _registry: Dict[str, Template] = {}

    @classmethod
    def registrar(cls, nome: str, fn: Callable, descricao: str = "") -> Template:
        t = Template(nome, fn, descricao)
        cls._registry[nome] = t
        return t

    @classmethod
    def obter(cls, nome: str) -> Template:
        if nome not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Template '{nome}' não encontrado.\nDisponíveis: {available}"
            )
        return cls._registry[nome]

    @classmethod
    def listar(cls) -> List[Dict[str, str]]:
        return [{"nome": t.nome, "descricao": t.descricao}
                for t in cls._registry.values()]


# ── Public API ────────────────────────────────────────────────────────────────

def registrar_template(nome: str, descricao: str = ""):
    """
    Decorator to register a template factory function.

    Usage:
        @registrar_template("meu_relatorio", descricao="Relatório customizado")
        def _factory(dados: dict):
            ...
            return doc
    """
    def decorator(fn: Callable) -> Callable:
        TemplateRegistro.registrar(nome, fn, descricao)
        return fn
    return decorator


def usar_template(nome: str, **dados) -> Any:
    """Instantiate a registered template by name."""
    return TemplateRegistro.obter(nome).instanciar(**dados)


def listar_templates() -> List[Dict[str, str]]:
    """Return list of all registered templates with name and description."""
    return TemplateRegistro.listar()


# ── Built-in templates ────────────────────────────────────────────────────────

@registrar_template("relatorio_executivo", descricao="Relatório executivo com TOC, seções e assinatura")
def _relatorio_executivo(dados: dict):
    from docschema import (
        Documento, Secao, Titulo, Paragrafo, TabelaConteudo, Lista, ItemLista,
        LinhaHorizontal, Assinatura, Texto, Negrito, Badge, DataHora, Local,
    )
    titulo   = dados.get("titulo",   "Relatório Executivo")
    autor    = dados.get("autor",    "")
    empresa  = dados.get("empresa",  "")
    periodo  = dados.get("periodo",  "")
    sumario  = dados.get("sumario",  "Este relatório apresenta os resultados e análises do período.")
    secoes   = dados.get("secoes",   [])  # [{"titulo": ..., "conteudo": ...}]
    assinante = dados.get("assinante", autor)
    cargo    = dados.get("cargo",    "")
    local    = dados.get("local",    "")

    doc = Documento(
        titulo=titulo,
        autor=autor,
        metadata={"empresa": empresa, "periodo": periodo},
        format_options={
            "html": {"show_toc": True, "css_class": "relatorio-executivo"},
            "docx": {"toc": True},
        },
    )

    # Cover section
    capa = Secao(id="capa")
    if empresa:
        capa.add(Paragrafo([Negrito(empresa)]))
    if periodo:
        capa.add(Paragrafo([Texto("Período: "), Badge(periodo, tipo="info")]))
    capa.add(Paragrafo([Texto("Elaborado por: "), Negrito(autor or "—")]))
    capa.add(Paragrafo([Texto("Data: "), DataHora(formato="%d/%m/%Y")]))
    doc.add(capa)

    # TOC
    doc.add(TabelaConteudo(titulo="Sumário", show_levels=2))

    # Summary
    sec_resumo = Secao(
        titulo=Titulo([Texto("Resumo Executivo")], nivel=1),
        id="resumo-executivo",
    )
    sec_resumo.add(Paragrafo([Texto(sumario)]))
    doc.add(sec_resumo)

    # Dynamic sections
    for s in secoes:
        sec = Secao(
            titulo=Titulo([Texto(s.get("titulo", "Seção"))], nivel=2),
            id=s.get("id", s.get("titulo", "sec").lower().replace(" ", "-")),
        )
        conteudo = s.get("conteudo", "")
        if conteudo:
            sec.add(Paragrafo([Texto(conteudo)]))
        # Optional items list
        for item in s.get("itens", []):
            lst = Lista()
            lst.add(ItemLista([Texto(item)]))
            sec.add(lst)
        doc.add(sec)

    # Signature
    doc.add(LinhaHorizontal())
    doc.add(Assinatura(
        nome=assinante,
        cargo=cargo,
        local=local,
        mostrar_data=True,
        mostrar_local=bool(local),
    ))

    return doc


@registrar_template("contrato_simples", descricao="Contrato simples com partes, cláusulas e assinaturas")
def _contrato_simples(dados: dict):
    from docschema import (
        Documento, Secao, Titulo, Paragrafo, Lista, ItemLista,
        LinhaHorizontal, Assinatura, Texto, Negrito, Italico,
        DataHora, Local, Espaco, TabelaConteudo,
    )
    from docschema.elements.inline import Variavel

    titulo     = dados.get("titulo",     "Contrato de Prestação de Serviços")
    contratante = dados.get("contratante", {"nome": "", "cpf_cnpj": "", "endereco": ""})
    contratado  = dados.get("contratado",  {"nome": "", "cpf_cnpj": "", "endereco": ""})
    clausulas   = dados.get("clausulas",   [])
    valor       = dados.get("valor",       "")
    prazo       = dados.get("prazo",       "")
    local_assin = dados.get("local",       "")

    doc = Documento(
        titulo=titulo,
        format_options={
            "html":     {"css_class": "contrato"},
            "txt":      {"line_width": 80},
            "markdown": {},
        },
    )

    # TabelaConteudo
    doc.add(TabelaConteudo(titulo="Sumário", show_levels=2))

    # Parties
    sec_partes = Secao(
        titulo=Titulo([Texto("1. DAS PARTES")], nivel=1),
        id="das-partes",
    )
    sec_partes.add(Paragrafo([
        Negrito("CONTRATANTE: "), Texto(contratante.get("nome", "")),
        Texto(", inscrito(a) sob o CPF/CNPJ nº "),
        Texto(contratante.get("cpf_cnpj", "")),
        Texto(", com sede/domicílio em "),
        Texto(contratante.get("endereco", "")).children[0] if contratante.get("endereco") else Texto(""),
    ]))
    sec_partes.add(Paragrafo([
        Negrito("CONTRATADO(A): "), Texto(contratado.get("nome", "")),
        Texto(", inscrito(a) sob o CPF/CNPJ nº "),
        Texto(contratado.get("cpf_cnpj", "")),
        Texto(", com sede/domicílio em "),
        Texto(contratado.get("endereco", "")),
    ]))
    doc.add(sec_partes)

    # Object
    sec_objeto = Secao(
        titulo=Titulo([Texto("2. DO OBJETO")], nivel=1),
        id="do-objeto",
    )
    objeto = dados.get("objeto", "A prestação dos serviços descritos neste instrumento.")
    sec_objeto.add(Paragrafo([Texto(objeto)]))
    doc.add(sec_objeto)

    # Value
    if valor:
        sec_valor = Secao(
            titulo=Titulo([Texto("3. DO VALOR E PAGAMENTO")], nivel=1),
            id="do-valor",
        )
        sec_valor.add(Paragrafo([
            Texto("O valor total do presente contrato é de "),
            Negrito(valor),
            Texto(f", com prazo de {prazo}." if prazo else "."),
        ]))
        doc.add(sec_valor)

    # Custom clauses
    base_num = 4 if valor else 3
    for i, clausula in enumerate(clausulas, base_num):
        sec_cl = Secao(
            titulo=Titulo([Texto(f"{i}. {clausula.get('titulo', 'CLÁUSULA').upper()}")], nivel=1),
            id=f"clausula-{i}",
        )
        sec_cl.add(Paragrafo([Texto(clausula.get("texto", ""))]))
        doc.add(sec_cl)

    # Foro
    foro = dados.get("foro", "")
    sec_foro = Secao(
        titulo=Titulo([Texto(f"{base_num + len(clausulas)}. DO FORO")], nivel=1),
        id="do-foro",
    )
    sec_foro.add(Paragrafo([
        Texto("Fica eleito o foro da comarca de "),
        Negrito(foro or local_assin or "___________"),
        Texto(" para dirimir eventuais conflitos."),
    ]))
    doc.add(sec_foro)

    # Date/Place
    doc.add(Espaco(2))
    doc.add(Paragrafo([
        Texto(local_assin or "___________"),
        Texto(", "),
        DataHora(formato="%d de %B de %Y"),
        Texto("."),
    ]))
    doc.add(Espaco(2))

    # Signatures
    doc.add(Assinatura(
        nome=contratante.get("nome", "CONTRATANTE"),
        mostrar_data=False,
    ))
    doc.add(Espaco(2))
    doc.add(Assinatura(
        nome=contratado.get("nome", "CONTRATADO(A)"),
        mostrar_data=False,
    ))

    return doc


@registrar_template("ata_reuniao", descricao="Ata de reunião com participantes, pauta e decisões")
def _ata_reuniao(dados: dict):
    from docschema import (
        Documento, Secao, Titulo, Paragrafo, Lista, ItemLista,
        LinhaHorizontal, Assinatura, Texto, Negrito, Badge,
        DataHora, Local, Tabela, Espaco,
    )
    from docschema.elements.block import CelulaTabela

    titulo       = dados.get("titulo",       "Ata de Reunião")
    data_reuniao = dados.get("data",         None)
    local_r      = dados.get("local",        "")
    responsavel  = dados.get("responsavel",  "")
    participantes = dados.get("participantes", [])  # [{"nome": ..., "cargo": ...}]
    pauta        = dados.get("pauta",        [])    # [str] ou [{"titulo": ..., "descricao": ...}]
    decisoes     = dados.get("decisoes",     [])    # [str]
    acoes        = dados.get("acoes",        [])    # [{"tarefa": ..., "responsavel": ..., "prazo": ...}]

    doc = Documento(
        titulo=titulo,
        format_options={"html": {"css_class": "ata"}, "docx": {"toc": False}},
    )

    # Header info
    header = Secao(id="cabecalho")
    header.add(Paragrafo([Negrito("Data: "), Texto(DataHora(valor=data_reuniao, formato="%d/%m/%Y %H:%M").renderizado() if data_reuniao else "___/___/______")]))
    if local_r:
        header.add(Paragrafo([Negrito("Local: "), Texto(local_r)]))
    if responsavel:
        header.add(Paragrafo([Negrito("Responsável: "), Texto(responsavel)]))
    doc.add(header)

    # Participants
    if participantes:
        sec_part = Secao(titulo=Titulo([Texto("Participantes")], nivel=2), id="participantes")
        cab = [
            CelulaTabela("Nome", negrito=True),
            CelulaTabela("Cargo", negrito=True),
        ]
        rows = [
            [p.get("nome", ""), p.get("cargo", "")]
            for p in participantes
        ]
        sec_part.add(Tabela(cabecalho=cab, linhas=rows))
        doc.add(sec_part)

    # Agenda
    if pauta:
        sec_pauta = Secao(titulo=Titulo([Texto("Pauta")], nivel=2), id="pauta")
        lista_pauta = Lista(ordenada=True)
        for item in pauta:
            if isinstance(item, dict):
                lista_pauta.add(ItemLista([Negrito(item.get("titulo", "")),
                                           Texto(": " + item.get("descricao", ""))]))
            else:
                lista_pauta.add(ItemLista([Texto(str(item))]))
        sec_pauta.add(lista_pauta)
        doc.add(sec_pauta)

    # Decisions
    if decisoes:
        sec_dec = Secao(titulo=Titulo([Texto("Decisões")], nivel=2), id="decisoes")
        lista_dec = Lista(ordenada=True)
        for d in decisoes:
            lista_dec.add(ItemLista([Texto(str(d))]))
        sec_dec.add(lista_dec)
        doc.add(sec_dec)

    # Action items
    if acoes:
        sec_acoes = Secao(titulo=Titulo([Texto("Ações")], nivel=2), id="acoes")
        cab = [
            CelulaTabela("Tarefa", negrito=True),
            CelulaTabela("Responsável", negrito=True),
            CelulaTabela("Prazo", negrito=True),
            CelulaTabela("Status", negrito=True),
        ]
        rows = [
            [
                a.get("tarefa", ""),
                a.get("responsavel", ""),
                a.get("prazo", ""),
                CelulaTabela(a.get("status", "Pendente")),
            ]
            for a in acoes
        ]
        sec_acoes.add(Tabela(cabecalho=cab, linhas=rows))
        doc.add(sec_acoes)

    # Signature
    doc.add(LinhaHorizontal())
    doc.add(Assinatura(
        nome=responsavel,
        cargo="Secretário(a) de Reunião",
        local=local_r,
        mostrar_data=True,
    ))

    return doc


@registrar_template("ficha_tecnica", descricao="Ficha técnica de produto ou projeto")
def _ficha_tecnica(dados: dict):
    from docschema import (
        Documento, Secao, Titulo, Paragrafo, Tabela, Lista, ItemLista,
        Texto, Negrito, Badge, DataHora, LinhaHorizontal, Imagem,
    )
    from docschema.elements.block import CelulaTabela

    nome       = dados.get("nome",       "Produto/Projeto")
    versao     = dados.get("versao",     "1.0")
    status     = dados.get("status",     "Em desenvolvimento")
    descricao  = dados.get("descricao",  "")
    specs      = dados.get("specs",      {})   # {"Chave": "Valor"}
    recursos   = dados.get("recursos",   [])
    tecnologias = dados.get("tecnologias", [])
    imagem     = dados.get("imagem",     "")
    autor      = dados.get("autor",      "")

    _STATUS_TIPOS = {
        "Em desenvolvimento": "warning",
        "Ativo": "success",
        "Descontinuado": "danger",
        "Planejado": "info",
    }
    status_tipo = _STATUS_TIPOS.get(status, "default")

    doc = Documento(
        titulo=f"Ficha Técnica: {nome}",
        autor=autor,
        format_options={"html": {"css_class": "ficha-tecnica"}},
    )

    # Header
    sec_h = Secao(id="header")
    sec_h.add(Paragrafo([Negrito(nome), Texto("  "), Badge(f"v{versao}", tipo="primary"), Texto("  "), Badge(status, tipo=status_tipo)]))
    if autor:
        sec_h.add(Paragrafo([Texto("Responsável: "), Negrito(autor)]))
    sec_h.add(Paragrafo([Texto("Data de emissão: "), DataHora(formato="%d/%m/%Y")]))
    doc.add(sec_h)

    # Image
    if imagem:
        doc.add(Imagem(src=imagem, alt=nome, legenda=f"Figura 1 — {nome}"))

    # Description
    if descricao:
        sec_desc = Secao(titulo=Titulo([Texto("Descrição")], nivel=2), id="descricao")
        sec_desc.add(Paragrafo([Texto(descricao)]))
        doc.add(sec_desc)

    # Specs table
    if specs:
        sec_specs = Secao(titulo=Titulo([Texto("Especificações")], nivel=2), id="especificacoes")
        cab  = [CelulaTabela("Propriedade", negrito=True), CelulaTabela("Valor", negrito=True)]
        rows = [[k, v] for k, v in specs.items()]
        sec_specs.add(Tabela(cabecalho=cab, linhas=rows))
        doc.add(sec_specs)

    # Features
    if recursos:
        sec_rec = Secao(titulo=Titulo([Texto("Recursos")], nivel=2), id="recursos")
        lst = Lista()
        for r in recursos:
            lst.add(ItemLista([Texto(str(r))]))
        sec_rec.add(lst)
        doc.add(sec_rec)

    # Tech stack
    if tecnologias:
        sec_tech = Secao(titulo=Titulo([Texto("Tecnologias")], nivel=2), id="tecnologias")
        sec_tech.add(Paragrafo([Texto("Stack utilizado: ")]
                               + [Badge(t, tipo="primary") for t in tecnologias]))
        doc.add(sec_tech)

    return doc


@registrar_template("email_formal", descricao="E-mail formal como documento")
def _email_formal(dados: dict):
    from docschema import (
        Documento, Paragrafo, Titulo, LinhaHorizontal, Espaco, Assinatura,
        Texto, Negrito, Italico, Lista, ItemLista,
    )

    para      = dados.get("para",      "")
    de        = dados.get("de",        "")
    assunto   = dados.get("assunto",   "")
    saudacao  = dados.get("saudacao",  f"Prezado(a) {para},")
    corpo     = dados.get("corpo",     "")
    itens     = dados.get("itens",     [])
    encerramento = dados.get("encerramento", "Atenciosamente,")
    cargo     = dados.get("cargo",     "")
    empresa   = dados.get("empresa",   "")

    doc = Documento(
        titulo=f"E-mail: {assunto}",
        format_options={"txt": {"line_width": 72}},
    )

    doc.add(Paragrafo([Negrito("Para: "), Texto(para)]))
    doc.add(Paragrafo([Negrito("De: "), Texto(de)]))
    doc.add(Paragrafo([Negrito("Assunto: "), Texto(assunto)]))
    doc.add(LinhaHorizontal())
    doc.add(Espaco(1))
    doc.add(Paragrafo([Texto(saudacao)]))
    doc.add(Espaco(1))

    if corpo:
        for linha in corpo.split("\n\n"):
            doc.add(Paragrafo([Texto(linha.strip())]))

    if itens:
        lst = Lista()
        for item in itens:
            lst.add(ItemLista([Texto(str(item))]))
        doc.add(lst)

    doc.add(Espaco(1))
    doc.add(Paragrafo([Texto(encerramento)]))
    doc.add(Assinatura(
        nome=de,
        cargo=cargo,
        mostrar_data=False,
        mostrar_local=False,
    ))
    if empresa:
        doc.add(Paragrafo([Italico(empresa)]))

    return doc


@registrar_template("proposta_comercial", descricao="Proposta comercial com tabela de preços e condições")
def _proposta_comercial(dados: dict):
    from docschema import (
        Documento, Secao, Titulo, Paragrafo, Tabela, Lista, ItemLista,
        LinhaHorizontal, Assinatura, Texto, Negrito, Badge,
        Espaco, DataHora, TabelaConteudo,
    )
    from docschema.elements.block import CelulaTabela

    titulo       = dados.get("titulo",        "Proposta Comercial")
    empresa_para = dados.get("empresa_para",  "")
    empresa_de   = dados.get("empresa_de",    "")
    responsavel  = dados.get("responsavel",   "")
    cargo        = dados.get("cargo",         "")
    validade     = dados.get("validade",      "30 dias")
    itens_prop   = dados.get("itens",         [])  # [{"desc": ..., "qtd": ..., "unit": ..., "total": ...}]
    total        = dados.get("total",         "")
    condicoes    = dados.get("condicoes",     [])
    obs          = dados.get("observacoes",   "")

    doc = Documento(
        titulo=titulo,
        autor=responsavel,
        format_options={"html": {"css_class": "proposta"}, "docx": {"toc": True}},
    )

    # Cover
    capa = Secao(id="capa")
    if empresa_de:
        capa.add(Paragrafo([Negrito(empresa_de)]))
    capa.add(Paragrafo([Texto("Para: "), Negrito(empresa_para or "")]))
    capa.add(Paragrafo([Texto("Data: "), DataHora(formato="%d/%m/%Y")]))
    capa.add(Paragrafo([Texto("Validade: "), Badge(validade, tipo="warning")]))
    doc.add(capa)

    doc.add(TabelaConteudo(titulo="Sumário", show_levels=2))

    # Items
    if itens_prop:
        sec_itens = Secao(titulo=Titulo([Texto("Itens da Proposta")], nivel=1), id="itens-proposta")
        cab = [
            CelulaTabela("Descrição",      align="left",  negrito=True),
            CelulaTabela("Qtd",            align="center", negrito=True),
            CelulaTabela("Valor unitário", align="right",  negrito=True),
            CelulaTabela("Total",          align="right",  negrito=True),
        ]
        rows = []
        for it in itens_prop:
            rows.append([
                CelulaTabela(it.get("desc", "")),
                CelulaTabela(str(it.get("qtd", 1)), align="center"),
                CelulaTabela(str(it.get("unit", "")), align="right"),
                CelulaTabela(str(it.get("total", "")), align="right"),
            ])
        if total:
            rows.append([
                CelulaTabela("", colspan=3),
                CelulaTabela(f"Total: {total}", align="right", negrito=True),
            ])
        sec_itens.add(Tabela(cabecalho=cab, linhas=rows))
        doc.add(sec_itens)

    # Conditions
    if condicoes:
        sec_cond = Secao(titulo=Titulo([Texto("Condições Comerciais")], nivel=1), id="condicoes")
        lst = Lista(ordenada=True)
        for c in condicoes:
            lst.add(ItemLista([Texto(str(c))]))
        sec_cond.add(lst)
        doc.add(sec_cond)

    # Observations
    if obs:
        sec_obs = Secao(titulo=Titulo([Texto("Observações")], nivel=1), id="observacoes")
        sec_obs.add(Paragrafo([Texto(obs)]))
        doc.add(sec_obs)

    # Signature
    doc.add(LinhaHorizontal())
    doc.add(Assinatura(
        nome=responsavel,
        cargo=cargo,
        mostrar_data=True,
    ))

    return doc
