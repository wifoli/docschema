"""
docschema.renderers.base  (v2)
================================
Abstract base for all renderers.

New in v2:
  - render context (_context: dict) for Se/Para/Variavel
  - footnote collection (_footnotes list) for MarcadorRodape
  - render_document_stream() for streaming output
  - new abstract visit_* for all v2 elements
"""
from __future__ import annotations

import io
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from docschema.document import Documento
    from docschema.elements.inline import *
    from docschema.elements.block import *


class BaseRenderer(ABC):
    """
    Abstract Visitor that renders a Documento into a target format.

    Config resolution chain (resolve_option):
        1. element.format_options[FORMAT_NAME][key]
        2. document.format_options[FORMAT_NAME][key]
        3. caller-supplied default

    Context (for Se/Para/Variavel):
        Stored in self._context dict; set via gerar(doc, fmt, contexto={…})
    """

    FORMAT_NAME: str = ""

    def __init__(self, document_config: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._doc_cfg:  Dict[str, Any] = document_config or {}
        self._context:  Dict[str, Any] = {}
        self._footnotes: List[Any]     = []  # collected MarcadorRodape elements
        self._doc: Optional[Any]       = None

    # ── Config resolution ──────────────────────────────────────────────────────

    def resolve_option(self, element: Any, key: str, default: Any = None) -> Any:
        elem_val = element.get_format_option(self.FORMAT_NAME, key)
        if elem_val is not None:
            return elem_val
        doc_val = self._doc_cfg.get(key)
        if doc_val is not None:
            return doc_val
        return default

    # ── Context helpers ────────────────────────────────────────────────────────

    def ctx(self, key: str, default: Any = None) -> Any:
        return self._context.get(key, default)

    # ── Composition helpers ────────────────────────────────────────────────────

    def render_inline_list(self, children: List[Any]) -> str:
        return "".join(str(el.accept(self)) for el in children)

    def render_block_list(self, children: List[Any]) -> str:
        parts = [el.accept(self) for el in children]
        return "\n".join(str(p) for p in parts if p is not None and str(p).strip() != "")

    def render_footnotes(self) -> str:
        """Render collected footnotes.  Called by render_document after body."""
        return ""  # default: no footnotes section

    # ── TOC helper ─────────────────────────────────────────────────────────────

    def collect_titulos(self, children: List[Any], max_nivel: int = 6) -> List[Any]:
        """Walk doc tree and collect Titulo elements up to max_nivel."""
        from docschema.elements.block import Titulo, Secao, BlocoDestaque, Lista
        result = []
        for el in children:
            if isinstance(el, Titulo) and el.nivel <= max_nivel:
                result.append(el)
            elif isinstance(el, (Secao, BlocoDestaque)):
                result.extend(self.collect_titulos(el.children, max_nivel))
        return result

    # ── Document entry point ──────────────────────────────────────────────────

    @abstractmethod
    def render_document(self, doc: "Documento") -> Any: ...

    def render_document_stream(self, doc: "Documento") -> Generator[str, None, None]:
        """
        Streaming version.  Default: yield render_document() in one chunk.
        Subclasses can override to yield chunks incrementally.
        """
        result = self.render_document(doc)
        if isinstance(result, (bytes, bytearray)):
            yield result
        else:
            yield str(result)

    # ── Inline visitors (abstract) ────────────────────────────────────────────

    @abstractmethod
    def visit_texto(self, el) -> str: ...
    @abstractmethod
    def visit_negrito(self, el) -> str: ...
    @abstractmethod
    def visit_italico(self, el) -> str: ...
    @abstractmethod
    def visit_sublinhado(self, el) -> str: ...
    @abstractmethod
    def visit_link(self, el) -> str: ...
    @abstractmethod
    def visit_quebra_linha(self, el) -> str: ...
    @abstractmethod
    def visit_span(self, el) -> str: ...
    @abstractmethod
    def visit_emoji(self, el) -> str: ...

    # v2 inline
    @abstractmethod
    def visit_badge(self, el) -> str: ...
    @abstractmethod
    def visit_data_hora(self, el) -> str: ...
    @abstractmethod
    def visit_local(self, el) -> str: ...
    @abstractmethod
    def visit_ancora(self, el) -> str: ...
    @abstractmethod
    def visit_ref_cruzada(self, el) -> str: ...
    @abstractmethod
    def visit_marcador_rodape(self, el) -> str: ...
    @abstractmethod
    def visit_variavel(self, el) -> str: ...

    # ── Block visitors (abstract) ─────────────────────────────────────────────

    @abstractmethod
    def visit_titulo(self, el) -> str: ...
    @abstractmethod
    def visit_paragrafo(self, el) -> str: ...
    @abstractmethod
    def visit_secao(self, el) -> str: ...
    @abstractmethod
    def visit_lista(self, el) -> str: ...
    @abstractmethod
    def visit_item_lista(self, el) -> str: ...
    @abstractmethod
    def visit_tabela(self, el) -> str: ...
    @abstractmethod
    def visit_imagem(self, el) -> str: ...
    @abstractmethod
    def visit_espaco(self, el) -> str: ...
    @abstractmethod
    def visit_quebra_pagina(self, el) -> str: ...
    @abstractmethod
    def visit_linha_horizontal(self, el) -> str: ...
    @abstractmethod
    def visit_bloco_destaque(self, el) -> str: ...
    @abstractmethod
    def visit_nota(self, el) -> str: ...
    @abstractmethod
    def visit_citacao(self, el) -> str: ...
    @abstractmethod
    def visit_codigo(self, el) -> str: ...

    # v2 block
    @abstractmethod
    def visit_tabela_conteudo(self, el) -> str: ...
    @abstractmethod
    def visit_nota_rodape(self, el) -> str: ...
    @abstractmethod
    def visit_formulario(self, el) -> str: ...
    @abstractmethod
    def visit_campo_formulario(self, el) -> str: ...
    @abstractmethod
    def visit_se(self, el) -> str: ...
    @abstractmethod
    def visit_para(self, el) -> str: ...
    @abstractmethod
    def visit_assinatura(self, el) -> str: ...
