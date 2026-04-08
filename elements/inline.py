"""
docschema.elements.inline  (v2)
================================
All inline-level elements.

New in v2:
  Badge          — colored label/tag
  DataHora       — formatted datetime (static or live)
  Local          — city/state/country with formatter
  Ancora         — invisible anchor for cross-references
  RefCruzada     — cross-reference link to an Ancora
  MarcadorRodape — footnote marker (renderer collects content)
  Variavel       — template placeholder resolved from render context
"""
from __future__ import annotations

import datetime
from typing import Any, List, Optional, Union, TYPE_CHECKING

from docschema.elements.base import (
    InlineElement,
    InlineContent,
    FormatOptions,
    FallbackMap,
    Metadata,
)

if TYPE_CHECKING:
    from docschema.renderers.base import BaseRenderer


def _to_inline(value: Union[str, InlineContent, None]) -> InlineContent:
    if value is None:
        return []
    if isinstance(value, str):
        return [Texto(value)] if value else []
    return list(value)


# ── Primitives ────────────────────────────────────────────────────────────────

class Texto(InlineElement):
    def __init__(self, conteudo: str = "", *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.conteudo = conteudo
    def accept(self, r): return r.visit_texto(self)
    def __repr__(self): return f"Texto({self.conteudo!r})"


class Emoji(InlineElement):
    def __init__(self, simbolo: str = "", *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.simbolo = simbolo
    def accept(self, r): return r.visit_emoji(self)


class QuebraLinha(InlineElement):
    def __init__(self, *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
    def accept(self, r): return r.visit_quebra_linha(self)


# ── Formatting ────────────────────────────────────────────────────────────────

class Negrito(InlineElement):
    def __init__(self, conteudo: Union[str, InlineContent] = "", *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: InlineContent = _to_inline(conteudo)
    def accept(self, r): return r.visit_negrito(self)


class Italico(InlineElement):
    def __init__(self, conteudo: Union[str, InlineContent] = "", *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: InlineContent = _to_inline(conteudo)
    def accept(self, r): return r.visit_italico(self)


class Sublinhado(InlineElement):
    def __init__(self, conteudo: Union[str, InlineContent] = "", *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: InlineContent = _to_inline(conteudo)
    def accept(self, r): return r.visit_sublinhado(self)


class Link(InlineElement):
    def __init__(self, conteudo: Union[str, InlineContent] = "", *, url: str = "", metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: InlineContent = _to_inline(conteudo)
        self.url = url
    def accept(self, r): return r.visit_link(self)


class Span(InlineElement):
    def __init__(self, children: InlineContent, *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: InlineContent = list(children)
    def accept(self, r): return r.visit_span(self)


# ── NEW: Badge ────────────────────────────────────────────────────────────────

class Badge(InlineElement):
    """
    Colored inline label/tag.  Accepts str or InlineContent (e.g. Variavel).
    tipo: "default" | "info" | "success" | "warning" | "danger" | "primary"

    Examples:
        Badge("ATIVO", tipo="success")
        Badge(Variavel("status"), tipo="info")
    """
    _CSS_COLORS = {
        "default": "#888",
        "info":    "#2196F3",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "danger":  "#F44336",
        "primary": "#673AB7",
    }
    _TXT_SYMBOLS = {
        "info": "ℹ", "success": "✓", "warning": "⚠",
        "danger": "✗", "primary": "★",
    }

    def __init__(self, conteudo, tipo: str = "default", *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        if isinstance(conteudo, str):
            self.children: InlineContent = [Texto(conteudo)] if conteudo else []
        elif isinstance(conteudo, InlineElement):
            self.children = [conteudo]
        else:
            self.children = list(conteudo)
        self.tipo = tipo

    @property
    def texto(self) -> str:
        parts = []
        for c in self.children:
            if hasattr(c, "conteudo"):
                parts.append(c.conteudo)
        return "".join(parts)

    def accept(self, r): return r.visit_badge(self)
    def __repr__(self): return f"Badge({self.children!r}, tipo={self.tipo!r})"


# ── NEW: DataHora ─────────────────────────────────────────────────────────────

class DataHora(InlineElement):
    """
    Inline date/time.  If valor=None, uses current datetime at render time.

    Examples:
        DataHora()                                   # now, default format
        DataHora(formato="%d/%m/%Y")                 # date only
        DataHora(valor=datetime(2025,3,15))
        DataHora(valor="2025-01-01", formato="%B %Y")
    """
    DEFAULT_FORMATO = "%d/%m/%Y %H:%M"

    def __init__(self, valor=None, formato: str = DEFAULT_FORMATO, *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self._valor  = valor
        self.formato = formato

    @property
    def valor(self) -> datetime.datetime:
        v = self._valor
        if v is None:
            return datetime.datetime.now()
        if isinstance(v, datetime.datetime):
            return v
        if isinstance(v, datetime.date):
            return datetime.datetime(v.year, v.month, v.day)
        if isinstance(v, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
                try:
                    return datetime.datetime.strptime(v, fmt)
                except ValueError:
                    pass
        raise ValueError(f"DataHora: não consegui parsear '{v}'")

    def renderizado(self) -> str:
        return self.valor.strftime(self.formato)

    def accept(self, r): return r.visit_data_hora(self)


# ── NEW: Local ────────────────────────────────────────────────────────────────

class Local(InlineElement):
    """
    Inline location with flexible format string.

    Examples:
        Local(cidade="Umuarama", estado="PR")
        Local(cidade="São Paulo", estado="SP", pais="Brasil", formato="{cidade}-{estado}, {pais}")
        Local(endereco="Av. Brasil 100", cidade="Curitiba", cep="80000-000")
    """
    DEFAULT_FORMATO = "{cidade}/{estado}"

    def __init__(self, cidade="", estado="", pais="", endereco="", cep="",
                 formato: str = DEFAULT_FORMATO, *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.cidade   = cidade
        self.estado   = estado
        self.pais     = pais
        self.endereco = endereco
        self.cep      = cep
        self.formato  = formato

    def renderizado(self) -> str:
        try:
            result = self.formato.format(
                cidade=self.cidade, estado=self.estado, pais=self.pais,
                endereco=self.endereco, cep=self.cep,
            )
            return result.strip(" /,")
        except KeyError:
            return self.cidade or self.estado or self.pais or self.endereco

    def accept(self, r): return r.visit_local(self)


# ── NEW: Ancora + RefCruzada ──────────────────────────────────────────────────

class Ancora(InlineElement):
    """
    Invisible anchor point for cross-references.

    Example:
        Titulo([Texto("Metodologia"), Ancora(id="sec-met")], nivel=2)
        # later:
        RefCruzada("sec-met", "ver Metodologia")
    """
    def __init__(self, id: str, *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.id = id
    def accept(self, r): return r.visit_ancora(self)


class RefCruzada(InlineElement):
    """
    Cross-reference link to an Ancora.
    texto defaults to ancora_id if not provided.
    """
    def __init__(self, ancora_id: str, texto: str = "", *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.ancora_id = ancora_id
        self.texto     = texto or ancora_id
    def accept(self, r): return r.visit_ref_cruzada(self)


# ── NEW: MarcadorRodape ───────────────────────────────────────────────────────

class MarcadorRodape(InlineElement):
    """
    Inline footnote marker.  Renderer collects all footnotes and appends them
    at the end of the document (or the section, depending on format).

    Example:
        Paragrafo([
            Texto("Conforme regulamentação vigente"),
            MarcadorRodape("Lei 12.345/2021, art. 7º."),
            Texto("."),
        ])
    """
    def __init__(self, conteudo: Union[str, InlineContent], *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.children: InlineContent = _to_inline(conteudo)
    def accept(self, r): return r.visit_marcador_rodape(self)


# ── NEW: Variavel ─────────────────────────────────────────────────────────────

class Variavel(InlineElement):
    """
    Template placeholder resolved from render context.

    Example:
        Variavel("empresa")               # ctx["empresa"] or ""
        Variavel("periodo", "Q1 2025")    # with fallback default

    Context passed via:
        gerar(doc, "html", contexto={"empresa": "Acme"})
    """
    def __init__(self, nome: str, padrao: str = "", *, metadata=None, format_options=None, fallback=None):
        super().__init__(metadata=metadata, format_options=format_options, fallback=fallback)
        self.nome   = nome
        self.padrao = padrao
    def accept(self, r): return r.visit_variavel(self)
    def __repr__(self): return f"Variavel({self.nome!r})"
