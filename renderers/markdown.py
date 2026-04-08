"""
docschema.renderers.markdown  (v2)
====================================
Markdown / GFM renderer.
"""
from __future__ import annotations

from typing import Dict, Generator, List, Optional

from docschema.renderers.base import BaseRenderer

_ALIGN_MAP = {"left": ":---", "center": ":---:", "right": "---:"}


class MarkdownRenderer(BaseRenderer):
    FORMAT_NAME = "markdown"

    def render_document(self, doc) -> str:
        self._doc       = doc
        self._doc_cfg   = doc.get_format_config(self.FORMAT_NAME)
        self._context   = getattr(doc, "_render_context", {})
        self._footnotes = []

        parts: List[str] = []
        if doc.titulo:
            parts.append(f"# {doc.titulo}\n")
        if doc.autor:
            parts.append(f"*Autor: {doc.autor}*\n")

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

        if doc.titulo:
            yield f"# {doc.titulo}\n\n"
        if doc.autor:
            yield f"*Autor: {doc.autor}*\n\n"

        for child in doc.children:
            result = child.accept(self)
            if result and str(result).strip():
                yield str(result) + "\n"

        footnotes = self.render_footnotes()
        if footnotes:
            yield "\n" + footnotes

    def render_footnotes(self) -> str:
        if not self._footnotes:
            return ""
        lines = ["\n---"]
        for i, fn in enumerate(self._footnotes, 1):
            content = self.render_inline_list(fn.children)
            lines.append(f"[^{i}]: {content}")
        return "\n".join(lines)

    # ── Inline ────────────────────────────────────────────────────────────────

    def visit_texto(self, el): return el.conteudo
    def visit_negrito(self, el): return f"**{self.render_inline_list(el.children)}**"
    def visit_italico(self, el): return f"*{self.render_inline_list(el.children)}*"
    def visit_sublinhado(self, el): return f"<u>{self.render_inline_list(el.children)}</u>"
    def visit_link(self, el):
        text = self.render_inline_list(el.children)
        return f"[{text}]({el.url})" if el.url else text
    def visit_quebra_linha(self, el): return "  \n"
    def visit_span(self, el): return self.render_inline_list(el.children)
    def visit_emoji(self, el): return el.simbolo

    def visit_badge(self, el):
        # GitHub-flavored markdown doesn't have native badges; render as bold label
        sym = el._TXT_SYMBOLS.get(el.tipo, "")
        txt = self.render_inline_list(el.children)
        return f"**`{sym}{txt}`**" if sym else f"**`{txt}`**"

    def visit_data_hora(self, el): return el.renderizado()
    def visit_local(self, el): return el.renderizado()
    def visit_ancora(self, el): return f'<a id="{el.id}"></a>'
    def visit_ref_cruzada(self, el): return f"[{el.texto}](#{el.ancora_id})"

    def visit_marcador_rodape(self, el):
        self._footnotes.append(el)
        n = len(self._footnotes)
        return f"[^{n}]"

    def visit_variavel(self, el):
        return str(self._context.get(el.nome, el.padrao))

    # ── Block ─────────────────────────────────────────────────────────────────

    def visit_titulo(self, el):
        text = self.render_inline_list(el.children)
        return f"{'#' * el.nivel} {text}"

    def visit_paragrafo(self, el):
        prefix  = self.resolve_option(el, "prefix", "")
        content = self.render_inline_list(el.children)
        return f"{prefix}{content}"

    def visit_secao(self, el):
        parts: List[str] = []
        if el.titulo:
            parts.append(el.titulo.accept(self))
        parts.append(self.render_block_list(el.children))
        return "\n".join(p for p in parts if p)

    def visit_lista(self, el):
        parts: List[str] = []
        for i, item in enumerate(el.children, 1):
            content = self.render_inline_list(item.children)
            marker  = f"{i}." if el.ordenada else "-"
            parts.append(f"{marker} {content}")
        return "\n".join(parts)

    def visit_item_lista(self, el): return self.render_inline_list(el.children)

    def visit_tabela(self, el):
        if el.has_fallback(self.FORMAT_NAME):
            return str(el.get_fallback_value(self.FORMAT_NAME))

        cab  = [self._cel_md(c) for c in el.cabecalho]
        rows = [[self._cel_md(c) for c in row] for row in el.linhas]
        aligns = [self._cel_align(c) for c in el.cabecalho]

        header = "| " + " | ".join(cab) + " |"
        sep    = "| " + " | ".join(aligns) + " |"
        body   = "\n".join("| " + " | ".join(row) + " |" for row in rows)
        parts  = [header, sep, body]
        if el.legenda:
            parts.append(f"\n*{el.legenda}*")
        return "\n".join(parts)

    def _cel_md(self, cel) -> str:
        from docschema.elements.block import CelulaTabela
        if isinstance(cel, CelulaTabela):
            content = self.render_inline_list(cel.inline_content())
            return content
        return str(cel)

    def _cel_align(self, cel) -> str:
        from docschema.elements.block import CelulaTabela
        if isinstance(cel, CelulaTabela):
            return _ALIGN_MAP.get(cel.align, ":---")
        return ":---"

    def visit_tabela_conteudo(self, el):
        if self._doc is None:
            return ""
        titulos = self.collect_titulos(self._doc.children, el.show_levels)
        if not titulos:
            return ""
        parts = [f"## {el.titulo}\n"]
        counters: Dict[int, int] = {}
        for t in titulos:
            nivel = t.nivel
            counters[nivel] = counters.get(nivel, 0) + 1
            for k in list(counters.keys()):
                if k > nivel:
                    counters[k] = 0
            indent = "  " * (nivel - 1)
            text   = t.texto_puro()
            anchor = text.lower().replace(" ", "-")
            if el.numerado:
                num = ".".join(str(counters.get(i, 0)) for i in range(1, nivel + 1))
                parts.append(f"{indent}{num}. [{text}](#{anchor})")
            else:
                parts.append(f"{indent}- [{text}](#{anchor})")
        return "\n".join(parts)

    def visit_nota_rodape(self, el):
        content = self.render_inline_list(el.children)
        return f"[^{el.numero}]: {content}"

    def visit_imagem(self, el):
        if el.has_fallback(self.FORMAT_NAME):
            return str(el.get_fallback_value(self.FORMAT_NAME))
        size = ""
        if el.largura or el.altura:
            w = el.largura or ""
            h = el.altura or ""
            size = f' ={w}x{h}'
        md = f"![{el.alt}]({el.src}{size})"
        if el.legenda:
            return f"{md}\n*{el.legenda}*"
        return md

    def visit_espaco(self, el): return "\n" * el.linhas

    def visit_quebra_pagina(self, el):
        if el.has_fallback(self.FORMAT_NAME):
            return str(el.get_fallback_value(self.FORMAT_NAME))
        return self.resolve_option(el, "fallback", "\n---\n")

    def visit_linha_horizontal(self, el): return "\n---\n"

    def visit_bloco_destaque(self, el):
        prefix = self.resolve_option(el, "prefix", "> ")
        parts  = []
        if el.titulo:
            _labels = {"info":"ℹ️","warning":"⚠️","tip":"💡","danger":"🚨"}
            sym = _labels.get(el.tipo, "")
            parts.append(f"{prefix}**{sym} {el.titulo}**")
        body = self.render_block_list(el.children)
        for line in body.split("\n"):
            parts.append(f"{prefix}{line}")
        return "\n".join(parts)

    def visit_nota(self, el):
        _labels = {"info":"ℹ️","warning":"⚠️","tip":"💡","danger":"🚨"}
        prefix  = self.resolve_option(el, "prefix", "> ")
        sym     = _labels.get(el.tipo, "")
        content = self.render_inline_list(el.children)
        return f"{prefix}{sym} **{el.tipo.capitalize()}:** {content}"

    def visit_citacao(self, el):
        prefix  = self.resolve_option(el, "prefix", "> ")
        content = self.render_inline_list(el.children)
        lines   = [f"{prefix}{line}" for line in content.split("\n")]
        if el.autoria:
            lines.append(f"{prefix}— *{el.autoria}*")
        return "\n".join(lines)

    def visit_codigo(self, el):
        lang = el.linguagem if el.linguagem != "text" else ""
        return f"```{lang}\n{el.conteudo}\n```"

    def visit_formulario(self, el):
        parts = []
        if el.titulo:
            parts.append(f"### {el.titulo}\n")
        for campo in el.campos:
            parts.append(campo.accept(self))
        return "\n".join(parts)

    def visit_campo_formulario(self, el):
        req = " \\*" if el.obrigatorio else ""
        if el.tipo == "checkbox":
            return f"- [ ] **{el.label}**{req}"
        if el.tipo == "select" and el.opcoes:
            opts = " / ".join(f"`{o}`" for o in el.opcoes)
            return f"**{el.label}**{req}: {opts}"
        if el.tipo == "textarea":
            return f"**{el.label}**{req}:\n\n> *(campo de texto longo)*"
        return f"**{el.label}**{req}: `__________________________`"

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
        linha = f"{'_' * el.largura}"
        parts = [f"\n{linha}"]
        if el.nome:
            parts.append(f"**{el.nome}**")
        if el.cargo:
            parts.append(f"*{el.cargo}*")
        sub = []
        if el.mostrar_data:
            sub.append(el.data_formatada())
        if el.mostrar_local and el.local:
            sub.append(el.local)
        if sub:
            parts.append(" | ".join(sub))
        return "\n\n".join(parts)
