"""
docschema.elements.block  (v2)
================================
All block-level elements.

New in v2:
  TabelaConteudo  — auto-generated table of contents
  CelulaTabela    — advanced table cell (align, colspan)
  Tabela          — updated: accepts CelulaTabela or str in cells
  NotaRodape      — standalone footnote definition block
  Formulario      — simple form with CampoFormulario fields
  CampoFormulario — individual form field
  Se              — conditional block (bool or callable(ctx))
  Para            — loop/repetition block
  Assinatura      — signature block with optional name, cargo, local, date
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Union, TYPE_CHECKING

from docschema.elements.base import (
    BlockElement,
    InlineElement,
    BlockContent,
    InlineContent,
    FormatOptions,
    FallbackMap,
    Metadata,
)

if TYPE_CHECKING:
    from docschema.renderers.base import BaseRenderer


def _inline(value: Union[str, InlineContent]) -> InlineContent:
    from docschema.elements.inline import Texto
    if isinstance(value, str):
        return [Texto(value)] if value else []
    return list(value)


# ── Heading ───────────────────────────────────────────────────────────────────

class Titulo(BlockElement):
    """
    Section heading.  nivel=1..6 maps to h1..h6 semantics.
    Supports Ancora inline for cross-reference targets.
    """
    def __init__(self, children: Union[str, InlineContent], nivel: int = 1, *,
                 metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: InlineContent = _inline(children)
        self.nivel: int = nivel
    def accept(self, r): return r.visit_titulo(self)

    def texto_puro(self) -> str:
        """Extract plain text for TOC generation."""
        from docschema.elements.inline import Texto, Negrito, Italico, Sublinhado, Ancora
        parts = []
        def _extract(els):
            for el in els:
                if isinstance(el, Texto):
                    parts.append(el.conteudo)
                elif isinstance(el, (Negrito, Italico, Sublinhado)):
                    _extract(el.children)
                elif isinstance(el, Ancora):
                    pass  # skip anchors
                # skip other inline elements
        _extract(self.children)
        return "".join(parts)


class Subtitulo(Titulo):
    """Convenience alias for Titulo(nivel=2..3)."""
    def __init__(self, children, nivel: int = 2, *, metadata=None, format_options=None, fallback=None):
        super().__init__(children, nivel=nivel, metadata=metadata,
                         format_options=format_options, fallback=fallback)
    def accept(self, r): return r.visit_titulo(self)


# ── Paragraph ─────────────────────────────────────────────────────────────────

class Paragrafo(BlockElement):
    def __init__(self, children: InlineContent, estilo: str = "", *,
                 metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: InlineContent = list(children)
        self.estilo: str = estilo
    def accept(self, r): return r.visit_paragrafo(self)


# ── Section ───────────────────────────────────────────────────────────────────

class Secao(BlockElement):
    def __init__(self, children=None, titulo=None, id: str = "", *,
                 metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: BlockContent    = list(children) if children else []
        self.titulo:   Optional[Titulo] = titulo
        self.id:       str             = id

    def add(self, element: BlockElement) -> "Secao":
        self.children.append(element)
        return self

    def accept(self, r): return r.visit_secao(self)


# ── Lists ─────────────────────────────────────────────────────────────────────

class ItemLista(BlockElement):
    def __init__(self, children: InlineContent, *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: InlineContent = list(children)
    def accept(self, r): return r.visit_item_lista(self)


class Lista(BlockElement):
    def __init__(self, children=None, ordenada: bool = False, *,
                 metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: List[ItemLista] = list(children) if children else []
        self.ordenada: bool = ordenada

    def add(self, item: ItemLista) -> "Lista":
        self.children.append(item)
        return self

    def accept(self, r): return r.visit_lista(self)


# ── Table (updated with CelulaTabela support) ─────────────────────────────────

class CelulaTabela:
    """
    Advanced table cell.  Can be used in Tabela.linhas and Tabela.cabecalho.

    Usage:
        CelulaTabela("Nome",   align="left",   colspan=1)
        CelulaTabela("Total",  align="right",  colspan=3, negrito=True)
        CelulaTabela([Texto("Status"), Badge("OK", tipo="success")])
    """
    def __init__(
        self,
        valor: Union[str, InlineContent],
        align:   str = "left",   # "left" | "center" | "right"
        colspan: int = 1,
        rowspan: int = 1,
        negrito: bool = False,
    ):
        self.valor   = valor  # str or List[InlineElement]
        self.align   = align
        self.colspan = colspan
        self.rowspan = rowspan
        self.negrito = negrito

    def texto_puro(self) -> str:
        if isinstance(self.valor, str):
            return self.valor
        parts = []
        for el in self.valor:
            if hasattr(el, "conteudo"):
                parts.append(el.conteudo)
        return "".join(parts)

    def inline_content(self) -> InlineContent:
        from docschema.elements.inline import Texto, Negrito
        if isinstance(self.valor, str):
            content: InlineContent = [Texto(self.valor)] if self.valor else []
        else:
            content = list(self.valor)
        if self.negrito:
            return [Negrito(content)]
        return content


class Tabela(BlockElement):
    """
    Data table.  cabecalho and linhas accept str or CelulaTabela.

    Backward compatible: List[str] and List[List[str]] still work.

    Advanced:
        Tabela(
            cabecalho=[
                CelulaTabela("Nome",  align="left"),
                CelulaTabela("Total", align="right"),
            ],
            linhas=[
                [CelulaTabela("Alpha", negrito=True), CelulaTabela("R$ 100", align="right")],
                [CelulaTabela("Total", colspan=1, negrito=True), "R$ 100"],
            ],
        )
    """
    def __init__(self, cabecalho, linhas, legenda: str = "", *,
                 metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.cabecalho = cabecalho   # List[str | CelulaTabela]
        self.linhas    = linhas      # List[List[str | CelulaTabela]]
        self.legenda   = legenda

    def _cel_texto(self, cel) -> str:
        if isinstance(cel, CelulaTabela):
            return cel.texto_puro()
        return str(cel)

    def cabecalho_texto(self) -> List[str]:
        return [self._cel_texto(c) for c in self.cabecalho]

    def linhas_texto(self) -> List[List[str]]:
        return [[self._cel_texto(c) for c in row] for row in self.linhas]

    def accept(self, r): return r.visit_tabela(self)


# ── NEW: TabelaConteudo ───────────────────────────────────────────────────────

class TabelaConteudo(BlockElement):
    """
    Auto-generated table of contents from document headings.

    Placed at the position in the document where the TOC should appear.
    The renderer traverses the document tree to collect Titulo elements.

    Usage:
        doc.add(TabelaConteudo(titulo="Sumário", show_levels=3))

    Options:
        show_levels — max heading level to include (1=only h1, 2=h1+h2, etc.)
        titulo      — heading text above the TOC
        numerado    — show numbering (1., 1.1, etc.)
    """
    def __init__(
        self,
        titulo:      str = "Sumário",
        show_levels: int = 3,
        numerado:    bool = False,
        *,
        metadata=None, format_options=None, fallback=None,
    ):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.titulo      = titulo
        self.show_levels = show_levels
        self.numerado    = numerado
    def accept(self, r): return r.visit_tabela_conteudo(self)


# ── NEW: NotaRodape block ─────────────────────────────────────────────────────

class NotaRodape(BlockElement):
    """
    Standalone footnote definition placed at the end of the document.
    Paired with MarcadorRodape inline element.

    When using MarcadorRodape, the renderer auto-collects them.
    NotaRodape can also be placed explicitly for manual footnotes.

    Usage:
        NotaRodape(numero=1, children=[Texto("Fonte: IBGE 2024.")])
    """
    def __init__(self, numero: int, children: InlineContent, *,
                 metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.numero:   int           = numero
        self.children: InlineContent = list(children)
    def accept(self, r): return r.visit_nota_rodape(self)


# ── Image ─────────────────────────────────────────────────────────────────────

class Imagem(BlockElement):
    def __init__(self, src="", alt="", titulo="", legenda="", largura=None, altura=None, *,
                 metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.src, self.alt, self.titulo = src, alt, titulo
        self.legenda, self.largura, self.altura = legenda, largura, altura
    def accept(self, r): return r.visit_imagem(self)


# ── Layout helpers ────────────────────────────────────────────────────────────

class Espaco(BlockElement):
    def __init__(self, linhas: int = 1, *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.linhas = linhas
    def accept(self, r): return r.visit_espaco(self)


class QuebraPagina(BlockElement):
    def __init__(self, *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
    def accept(self, r): return r.visit_quebra_pagina(self)


class LinhaHorizontal(BlockElement):
    def __init__(self, *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
    def accept(self, r): return r.visit_linha_horizontal(self)


# ── Rich block elements ───────────────────────────────────────────────────────

class BlocoDestaque(BlockElement):
    """Callout / admonition block with optional title."""
    def __init__(self, children=None, titulo="", tipo="info", *,
                 metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: BlockContent = list(children) if children else []
        self.titulo = titulo
        self.tipo   = tipo
    def add(self, el): self.children.append(el); return self
    def accept(self, r): return r.visit_bloco_destaque(self)


class Nota(BlockElement):
    """Inline note / annotation block (info, warning, tip, danger)."""
    def __init__(self, children: InlineContent, tipo="info", *,
                 metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: InlineContent = list(children)
        self.tipo = tipo
    def accept(self, r): return r.visit_nota(self)


class Citacao(BlockElement):
    """Block quotation with optional authorship attribution."""
    def __init__(self, children: InlineContent, autoria="", *,
                 metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: InlineContent = list(children)
        self.autoria = autoria
    def accept(self, r): return r.visit_citacao(self)


class Codigo(BlockElement):
    """Code block with language hint for syntax highlighting."""
    def __init__(self, conteudo="", linguagem="text", *,
                 metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.conteudo  = conteudo
        self.linguagem = linguagem
    def accept(self, r): return r.visit_codigo(self)


# ── NEW: Formulario ───────────────────────────────────────────────────────────

class CampoFormulario(BlockElement):
    """
    Individual form field.
    tipo: "text" | "email" | "number" | "date" | "select" | "textarea" | "checkbox" | "radio"

    Usage:
        CampoFormulario("nome",   tipo="text",   label="Nome completo", obrigatorio=True)
        CampoFormulario("email",  tipo="email",  label="E-mail")
        CampoFormulario("status", tipo="select", label="Status",
                        opcoes=["Ativo", "Inativo", "Pendente"])
    """
    def __init__(
        self,
        nome:        str,
        tipo:        str = "text",
        label:       str = "",
        obrigatorio: bool = False,
        placeholder: str = "",
        valor:       str = "",
        opcoes:      Optional[List[str]] = None,
        *,
        metadata=None, format_options=None, fallback=None,
    ):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.nome        = nome
        self.tipo        = tipo
        self.label       = label or nome
        self.obrigatorio = obrigatorio
        self.placeholder = placeholder
        self.valor       = valor
        self.opcoes: List[str] = opcoes or []
    def accept(self, r): return r.visit_campo_formulario(self)


class Formulario(BlockElement):
    """
    Simple form with CampoFormulario fields.

    HTML renders a real <form>. TXT/MD renders as fill-in-the-blank.
    Clipboard renders as a compact list of field names.

    Usage:
        form = Formulario(titulo="Contato", acao="/contato", metodo="post")
        form.add(CampoFormulario("nome",  label="Nome", obrigatorio=True))
        form.add(CampoFormulario("email", tipo="email", label="E-mail"))
        form.add(CampoFormulario("msg",   tipo="textarea", label="Mensagem"))
    """
    def __init__(
        self,
        campos:  Optional[List[CampoFormulario]] = None,
        titulo:  str = "",
        acao:    str = "",
        metodo:  str = "post",
        *,
        metadata=None, format_options=None, fallback=None,
    ):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.campos: List[CampoFormulario] = list(campos) if campos else []
        self.titulo  = titulo
        self.acao    = acao
        self.metodo  = metodo

    def add(self, campo: CampoFormulario) -> "Formulario":
        self.campos.append(campo)
        return self

    def accept(self, r): return r.visit_formulario(self)


# ── NEW: Se (conditional block) ───────────────────────────────────────────────

class Se(BlockElement):
    """
    Conditional block. Renders 'sim' if condicao is true, 'nao' otherwise.

    condicao can be:
      - bool        → evaluated directly
      - callable    → called with context dict: condicao(ctx) -> bool
      - str         → key looked up in context: ctx.get(condicao, False)

    Usage:
        Se(True, sim=[Paragrafo([Texto("Sempre visível")])]),

        Se(lambda ctx: ctx["ativo"],
           sim=[Paragrafo([Badge("ATIVO", tipo="success")])],
           nao=[Paragrafo([Badge("INATIVO", tipo="danger")])]),

        Se("mostrar_rodape", sim=[Assinatura(nome="Dr. Fulano")]),
    """
    def __init__(
        self,
        condicao,
        sim:  Optional[BlockContent] = None,
        nao:  Optional[BlockContent] = None,
        *,
        metadata=None, format_options=None, fallback=None,
    ):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.condicao = condicao
        self.sim:  BlockContent = list(sim)  if sim  else []
        self.nao:  BlockContent = list(nao)  if nao  else []

    def avaliar(self, contexto: Dict[str, Any]) -> bool:
        c = self.condicao
        if callable(c):
            return bool(c(contexto))
        if isinstance(c, str):
            return bool(contexto.get(c, False))
        return bool(c)

    def accept(self, r): return r.visit_se(self)


# ── NEW: Para (loop/repetition block) ─────────────────────────────────────────

class Para(BlockElement):
    """
    Loop/repetition block.  Expands a list of items through a template function.

    itens:    list  | callable(ctx) -> list
    template: callable(item, ctx) -> List[BlockElement]

    Usage:
        # Static list
        Para(
            itens=produtos,
            template=lambda p, ctx: [
                Titulo([Texto(p["nome"])], nivel=3),
                Paragrafo([Texto(f'Preço: R$ {p["valor"]:.2f}')]),
            ]
        )

        # Dynamic list from context
        Para(
            itens=lambda ctx: ctx["contratos"],
            template=lambda c, ctx: [
                Titulo([Texto(c["numero"])], nivel=3),
                Paragrafo([Texto(f'Status: {c["status"]}')]),
            ]
        )
    """
    def __init__(
        self,
        itens,                        # list | callable(ctx) -> list
        template: Callable,           # (item, ctx) -> List[BlockElement]
        separador: Optional[BlockElement] = None,
        *,
        metadata=None, format_options=None, fallback=None,
    ):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.itens     = itens
        self.template  = template
        self.separador = separador   # optional separator between items

    def accept(self, r): return r.visit_para(self)


# ── NEW: Assinatura ───────────────────────────────────────────────────────────

class Assinatura(BlockElement):
    """
    Signature block — rendered as a signature line with optional fields below.

    HTML/PDF: styled box with underscore line.
    TXT: _____________________\\nNome: X\\nCargo: Y\\nData: Z

    Options:
        nome          — signer name (below line)
        cargo         — title/position
        data          — date string or DataHora element (None = auto today)
        local         — location
        largura       — line width (chars for TXT, px hint for HTML)
        mostrar_data  — include date field (default True)
        mostrar_local — include location field (default True if local set)
        linhas        — number of signature lines (e.g. 2 for co-signers)

    Usage:
        Assinatura(nome="Dr. João", cargo="Diretor", local="São Paulo/SP")
        Assinatura()   # blank signature line
        Assinatura(nome="", cargo="Responsável Técnico", mostrar_data=True)
    """
    def __init__(
        self,
        nome:         str = "",
        cargo:        str = "",
        data          = None,       # str | DataHora | None (auto today)
        local:        str = "",
        largura:      int = 40,
        mostrar_data: bool = True,
        mostrar_local: bool = True,
        linhas:       int = 1,
        *,
        metadata=None, format_options=None, fallback=None,
    ):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.nome          = nome
        self.cargo         = cargo
        self.data          = data
        self.local         = local
        self.largura       = largura
        self.mostrar_data  = mostrar_data
        self.mostrar_local = mostrar_local
        self.linhas        = linhas

    def data_formatada(self) -> str:
        import datetime
        from docschema.elements.inline import DataHora
        if self.data is None:
            return datetime.date.today().strftime("%d/%m/%Y")
        if isinstance(self.data, DataHora):
            return self.data.renderizado()
        return str(self.data)

    def accept(self, r): return r.visit_assinatura(self)
