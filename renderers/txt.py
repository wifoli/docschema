"""
docschema.renderers.txt  (v2)
================================
Plain-text renderer.
"""
from __future__ import annotations

import textwrap
from typing import Any, Dict, Generator, List, Optional

from docschema.renderers.base import BaseRenderer

_DEFAULT_LINE_WIDTH = 80


class TxtRenderer(BaseRenderer):
    FORMAT_NAME = "txt"

    def __init__(self, document_config=None, **kwargs):
        super().__init__(document_config, **kwargs)
        self._line_width = _DEFAULT_LINE_WIDTH

    # ── Document ──────────────────────────────────────────────────────────────

    def render_document(self, doc) -> str:
        self._doc       = doc
        self._doc_cfg   = doc.get_format_config(self.FORMAT_NAME)
        self._context   = getattr(doc, "_render_context", {})
        self._footnotes = []
        self._line_width = int(self._doc_cfg.get("line_width", _DEFAULT_LINE_WIDTH))

        parts: List[str] = []
        if doc.titulo:
            parts.append(doc.titulo.upper())
            parts.append("=" * min(len(doc.titulo), self._line_width))
        if doc.autor:
            parts.append(f"Autor: {doc.autor}")
        if parts:
            parts.append("")

        body = self.render_block_list(doc.children)
        parts.append(body)

        footnotes = self.render_footnotes()
        if footnotes:
            parts.append(footnotes)

        return "\n".join(p for p in parts if p is not None)

    def render_document_stream(self, doc) -> Generator[str, None, None]:
        self._doc       = doc
        self._doc_cfg   = doc.get_format_config(self.FORMAT_NAME)
        self._context   = getattr(doc, "_render_context", {})
        self._footnotes = []
        self._line_width = int(self._doc_cfg.get("line_width", _DEFAULT_LINE_WIDTH))

        if doc.titulo:
            yield doc.titulo.upper() + "\n"
            yield "=" * min(len(doc.titulo), self._line_width) + "\n"
        if doc.autor:
            yield f"Autor: {doc.autor}\n"
        yield "\n"

        for child in doc.children:
            result = child.accept(self)
            if result and str(result).strip():
                yield str(result) + "\n"

        footnotes = self.render_footnotes()
        if footnotes:
            yield footnotes

    def render_footnotes(self) -> str:
        if not self._footnotes:
            return ""
        rule = "-" * self._line_width
        lines = [f"\n{rule}"]
        for i, fn in enumerate(self._footnotes, 1):
            content = self.render_inline_list(fn.children)
            lines.append(f"[{i}] {content}")
        return "\n".join(lines)

    # ── Inline ────────────────────────────────────────────────────────────────

    def visit_texto(self, el): return el.conteudo
    def visit_negrito(self, el): return f"*{self.render_inline_list(el.children)}*"
    def visit_italico(self, el): return f"_{self.render_inline_list(el.children)}_"
    def visit_sublinhado(self, el): return f"_{self.render_inline_list(el.children)}_"
    def visit_link(self, el):
        text = self.render_inline_list(el.children)
        return f"{text} ({el.url})" if el.url else text
    def visit_quebra_linha(self, el): return "\n"
    def visit_span(self, el): return self.render_inline_list(el.children)
    def visit_emoji(self, el): return el.simbolo

    def visit_badge(self, el):
        sym = el._TXT_SYMBOLS.get(el.tipo, "")
        txt = self.render_inline_list(el.children)
        return f"[{sym}{txt}]" if sym else f"[{txt}]"

    def visit_data_hora(self, el):
        return el.renderizado()

    def visit_local(self, el):
        return el.renderizado()

    def visit_ancora(self, el): return ""  # invisible in TXT

    def visit_ref_cruzada(self, el):
        label = self.resolve_option(el, "label_format", "{texto} (ver {id})")
        return label.format(texto=el.texto, id=el.ancora_id)

    def visit_marcador_rodape(self, el):
        self._footnotes.append(el)
        n = len(self._footnotes)
        return f"[{n}]"

    def visit_variavel(self, el):
        return str(self._context.get(el.nome, el.padrao))

    # ── Block ─────────────────────────────────────────────────────────────────

    def visit_titulo(self, el):
        text  = self.render_inline_list(el.children)
        nivel = el.nivel
        lw    = self._line_width
        if nivel == 1:
            return f"\n{text.upper()}\n{'=' * min(len(text), lw)}"
        if nivel == 2:
            return f"\n{text}\n{'-' * min(len(text), lw)}"
        prefix = "#" * nivel + " "
        return f"\n{prefix}{text}"

    def visit_paragrafo(self, el):
        text   = self.render_inline_list(el.children)
        prefix = self.resolve_option(el, "prefix", "")
        if self.resolve_option(el, "uppercase", False):
            text = text.upper()
        wrapped = textwrap.fill(text, width=self._line_width)
        return f"{prefix}{wrapped}" if prefix else wrapped

    def visit_secao(self, el):
        parts: List[str] = []
        if el.titulo:
            parts.append(el.titulo.accept(self))
        parts.append(self.render_block_list(el.children))
        return "\n".join(p for p in parts if p)

    def visit_lista(self, el):
        bullet = self.resolve_option(el, "bullet", "-")
        parts: List[str] = []
        for i, item in enumerate(el.children, 1):
            content = self.render_inline_list(item.children)
            marker  = f"{i}." if el.ordenada else bullet
            parts.append(f"  {marker} {content}")
        return "\n".join(parts)

    def visit_item_lista(self, el): return self.render_inline_list(el.children)

    def visit_tabela(self, el):
        if el.has_fallback(self.FORMAT_NAME):
            return str(el.get_fallback_value(self.FORMAT_NAME))
        strategy = self.resolve_option(el, "fallback_strategy", "columns")
        return self._tabela_as_list(el) if strategy == "list" else self._tabela_as_columns(el)

    def _cel_render(self, cel) -> str:
        from docschema.elements.block import CelulaTabela
        if isinstance(cel, CelulaTabela):
            return self.render_inline_list(cel.inline_content())
        return str(cel)

    def _tabela_as_columns(self, el):
        cab_txt  = [self._cel_render(c) for c in el.cabecalho]
        lin_txt  = [[self._cel_render(c) for c in row] for row in el.linhas]
        min_w    = int(self.resolve_option(el, "min_column_width", 12))
        all_rows = [cab_txt] + lin_txt
        widths   = [
            max(max(len(r[c]) for r in all_rows if c < len(r)) + 2, min_w)
            for c in range(len(cab_txt))
        ]
        def fmt(row):
            return "| " + " | ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)) + " |"
        sep   = "|-" + "-+-".join("-" * w for w in widths) + "-|"
        lines = [fmt(cab_txt), sep] + [fmt(r) for r in lin_txt]
        if el.legenda:
            lines.append(f"\n  {el.legenda}")
        return "\n".join(lines)

    def _tabela_as_list(self, el):
        cab = [self._cel_render(c) for c in el.cabecalho]
        rows = [
            "  - " + ", ".join(f"{cab[i]}: {self._cel_render(v)}" for i, v in enumerate(row))
            for row in el.linhas
        ]
        if el.legenda:
            rows.append(f"\n  {el.legenda}")
        return "\n".join(rows)

    def visit_tabela_conteudo(self, el):
        if self._doc is None:
            return ""
        titulos = self.collect_titulos(self._doc.children, el.show_levels)
        if not titulos:
            return ""
        parts = [f"\n{el.titulo.upper()}\n{'=' * len(el.titulo)}"]
        counters: Dict[int, int] = {}
        for t in titulos:
            nivel = t.nivel
            counters[nivel] = counters.get(nivel, 0) + 1
            # reset lower levels
            for k in list(counters.keys()):
                if k > nivel:
                    counters[k] = 0
            indent = "  " * (nivel - 1)
            text   = t.texto_puro()
            if el.numerado:
                num = ".".join(str(counters.get(i, 0)) for i in range(1, nivel + 1))
                parts.append(f"{indent}{num}. {text}")
            else:
                bullet = "-" if nivel > 1 else "•"
                parts.append(f"{indent}{bullet} {text}")
        return "\n".join(parts)

    def visit_nota_rodape(self, el):
        content = self.render_inline_list(el.children)
        return f"[{el.numero}] {content}"

    def visit_imagem(self, el):
        if el.has_fallback(self.FORMAT_NAME):
            return str(el.get_fallback_value(self.FORMAT_NAME))
        lines = [f"[Imagem: {el.alt}]"]
        if el.titulo:
            lines.append(f"  Título:  {el.titulo}")
        if el.legenda:
            lines.append(f"  Legenda: {el.legenda}")
        return "\n".join(lines)

    def visit_espaco(self, el): return "\n" * el.linhas

    def visit_quebra_pagina(self, el):
        if el.has_fallback(self.FORMAT_NAME):
            return str(el.get_fallback_value(self.FORMAT_NAME))
        return f"\n{'-' * self._line_width}\n"

    def visit_linha_horizontal(self, el): return "-" * self._line_width

    def visit_bloco_destaque(self, el):
        label   = self.resolve_option(el, "label", f"[{el.tipo.upper()}]")
        border  = self.resolve_option(el, "border", False)
        parts   = []
        if el.titulo:
            parts.append(f"{label} {el.titulo}")
        else:
            parts.append(label)
        parts.append(self.render_block_list(el.children))
        content = "\n".join(p for p in parts if p)
        if border:
            rule = "-" * self._line_width
            return f"{rule}\n{content}\n{rule}"
        return content

    def visit_nota(self, el):
        _labels = {"info": "[INFO]", "warning": "[ATENÇÃO]", "tip": "[DICA]", "danger": "[PERIGO]"}
        label   = self.resolve_option(el, "label", _labels.get(el.tipo, "[NOTA]"))
        content = self.render_inline_list(el.children)
        border  = self.resolve_option(el, "border", False)
        text    = f"{label} {content}"
        if border:
            rule = "-" * self._line_width
            return f"{rule}\n{text}\n{rule}"
        return text

    def visit_citacao(self, el):
        indent  = int(self.resolve_option(el, "indent", 4))
        content = self.render_inline_list(el.children)
        pad     = " " * indent
        wrapped = textwrap.indent(textwrap.fill(content, self._line_width - indent), pad)
        if el.autoria:
            wrapped += f"\n{pad}— {el.autoria}"
        return wrapped

    def visit_codigo(self, el):
        indent   = int(self.resolve_option(el, "indent", 2))
        indented = textwrap.indent(el.conteudo, " " * indent)
        if el.linguagem and el.linguagem != "text":
            return f"[{el.linguagem.upper()}]\n{indented}"
        return indented

    # ── v2 block ──────────────────────────────────────────────────────────────

    def visit_formulario(self, el):
        parts = []
        if el.titulo:
            parts.append(f"\n{el.titulo}\n{'-' * len(el.titulo)}")
        for campo in el.campos:
            parts.append(campo.accept(self))
        return "\n".join(parts)

    def visit_campo_formulario(self, el):
        req    = " *" if el.obrigatorio else ""
        linhas = int(self.resolve_option(el, "field_width", 30))
        line   = "_" * linhas
        if el.tipo == "checkbox":
            return f"  [ ] {el.label}{req}"
        if el.tipo == "select" and el.opcoes:
            opts = " / ".join(el.opcoes)
            return f"  {el.label}{req}: [ {opts} ]"
        if el.tipo == "textarea":
            return f"  {el.label}{req}:\n  {line}\n  {line}\n  {line}"
        return f"  {el.label}{req}: {line}"

    def visit_se(self, el):
        ramo = el.sim if el.avaliar(self._context) else el.nao
        return self.render_block_list(ramo) if ramo else ""

    def visit_para(self, el):
        itens  = el.itens(self._context) if callable(el.itens) else el.itens
        partes = []
        for item in itens:
            elementos = el.template(item, self._context)
            rendered  = self.render_block_list(elementos)
            if rendered.strip():
                partes.append(rendered)
                if el.separador and item is not itens[-1]:
                    partes.append(el.separador.accept(self))
        return "\n".join(partes)

    def visit_assinatura(self, el):
        lw    = self._line_width
        linha = "_" * min(el.largura, lw)
        parts = ["", linha]
        if el.nome:
            parts.append(f"Nome:  {el.nome}")
        if el.cargo:
            parts.append(f"Cargo: {el.cargo}")
        if el.mostrar_data:
            parts.append(f"Data:  {el.data_formatada()}")
        if el.mostrar_local and el.local:
            parts.append(f"Local: {el.local}")
        return "\n".join(parts)
