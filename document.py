"""
docschema.document
===================
The Documento class is the root of every document tree.
It is not itself an Element — it is the entry point for rendering.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from docschema.elements.base import BlockElement, BlockContent, FormatOptions, Metadata

if TYPE_CHECKING:
    from docschema.renderers.base import BaseRenderer


class Documento:
    """
    Root document node.

    Carries:
      • titulo, autor, idioma  — document-level metadata
      • metadata               — arbitrary key/value annotations
      • format_options         — per-format global configuration
        e.g. format_options={"html": {"show_toc": True}, "txt": {"line_width": 88}}
      • children               — ordered list of block elements

    Builder-style:
        doc = Documento(titulo="…")
        doc.add(Titulo([…], nivel=1))
        doc.add(Paragrafo([…]))
    """

    def __init__(
        self,
        children:       Optional[BlockContent]  = None,
        titulo:         str                     = "",
        autor:          str                     = "",
        idioma:         str                     = "pt-BR",
        id:             str                     = "",
        metadata:       Optional[Metadata]      = None,
        format_options: Optional[FormatOptions] = None,
    ) -> None:
        self.children:       BlockContent  = list(children) if children else []
        self.titulo:         str           = titulo
        self.autor:          str           = autor
        self.idioma:         str           = idioma
        self.id:             str           = id
        self.metadata:       Metadata      = metadata       or {}
        self.format_options: FormatOptions = format_options or {}

    # ── Builder ────────────────────────────────────────────────────────────────

    def add(self, element: BlockElement) -> "Documento":
        """Append a block element.  Returns self for chaining."""
        self.children.append(element)
        return self

    # ── Config ─────────────────────────────────────────────────────────────────

    def get_format_option(self, fmt: str, key: str, default: Any = None) -> Any:
        return self.format_options.get(fmt, {}).get(key, default)

    def get_format_config(self, fmt: str) -> Dict[str, Any]:
        """Return the full config dict for a given format."""
        return dict(self.format_options.get(fmt, {}))

    # ── Visitor entry point ────────────────────────────────────────────────────

    def accept(self, renderer: "BaseRenderer") -> Any:
        return renderer.render_document(self)

    def __repr__(self) -> str:
        return f"Documento(titulo={self.titulo!r}, children={len(self.children)})"
