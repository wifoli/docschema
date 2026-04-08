"""
docschema.renderers.clipboard  (v2)
=====================================
Clipboard renderer — compact TXT variant.
Extends TxtRenderer with simpler output for copy-paste.
"""
from __future__ import annotations

from typing import Generator, List

from docschema.renderers.txt import TxtRenderer


class ClipboardRenderer(TxtRenderer):
    FORMAT_NAME = "clipboard"

    def render_document(self, doc) -> str:
        self._doc       = doc
        self._doc_cfg   = doc.get_format_config(self.FORMAT_NAME)
        self._context   = getattr(doc, "_render_context", {})
        self._footnotes = []
        self._line_width = int(self._doc_cfg.get("line_width", 80))
        mode = self._doc_cfg.get("mode", "normal")

        parts: List[str] = []

        if mode != "compact" and doc.titulo:
            parts.append(doc.titulo)
            parts.append("")

        parts.append(self.render_block_list(doc.children))

        footnotes = self.render_footnotes()
        if footnotes:
            parts.append(footnotes)

        return "\n".join(p for p in parts if p is not None)

    def render_document_stream(self, doc) -> Generator[str, None, None]:
        self._doc       = doc
        self._doc_cfg   = doc.get_format_config(self.FORMAT_NAME)
        self._context   = getattr(doc, "_render_context", {})
        self._footnotes = []
        self._line_width = int(self._doc_cfg.get("line_width", 80))
        mode = self._doc_cfg.get("mode", "normal")

        if mode != "compact" and doc.titulo:
            yield doc.titulo + "\n\n"

        for child in doc.children:
            result = child.accept(self)
            if result and str(result).strip():
                yield str(result) + "\n"

        footnotes = self.render_footnotes()
        if footnotes:
            yield footnotes

    # ── Overrides for compact clipboard output ────────────────────────────────

    def visit_quebra_pagina(self, el):
        return ""  # No page breaks in clipboard

    def visit_tabela(self, el):
        # Always use list format in clipboard
        strategy = self.resolve_option(el, "fallback_strategy", "list")
        if el.has_fallback(self.FORMAT_NAME):
            return str(el.get_fallback_value(self.FORMAT_NAME))
        return self._tabela_as_list(el) if strategy == "list" else self._tabela_as_columns(el)

    def visit_assinatura(self, el):
        # Compact: just name/cargo/date on one line
        parts = []
        if el.nome:
            parts.append(el.nome)
        if el.cargo:
            parts.append(el.cargo)
        if el.mostrar_data:
            parts.append(el.data_formatada())
        if el.mostrar_local and el.local:
            parts.append(el.local)
        return " | ".join(parts) if parts else "_____"

    def visit_formulario(self, el):
        # Compact: just field names
        parts = []
        if el.titulo:
            parts.append(f"[Formulário: {el.titulo}]")
        for campo in el.campos:
            req = "*" if campo.obrigatorio else ""
            parts.append(f"  {campo.label}{req}: ____")
        return "\n".join(parts)

    def visit_badge(self, el):
        # No symbols in clipboard, just brackets
        return f"[{self.render_inline_list(el.children)}]"

    def visit_ancora(self, el): return ""

    def visit_ref_cruzada(self, el): return el.texto

    def visit_marcador_rodape(self, el):
        self._footnotes.append(el)
        return ""  # In clipboard, footnote markers are invisible; content appended at end
