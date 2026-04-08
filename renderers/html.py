"""
docschema.renderers.html  (v2)
================================
HTML5 semantic renderer.
"""
from __future__ import annotations

import html as _html
from typing import Dict, Generator, List, Optional

from docschema.renderers.base import BaseRenderer


def _cls(value): return f' class="{value}"' if value else ""
def _esc(text): return _html.escape(str(text))

_BADGE_COLORS = {
    "default": ("#e0e0e0", "#333"),
    "info":    ("#1976D2", "#fff"),
    "success": ("#388E3C", "#fff"),
    "warning": ("#F57C00", "#fff"),
    "danger":  ("#D32F2F", "#fff"),
    "primary": ("#512DA8", "#fff"),
}
_NOTA_ICONS = {"info":"ℹ️","warning":"⚠️","tip":"💡","danger":"🚨"}


class HtmlRenderer(BaseRenderer):
    FORMAT_NAME = "html"

    def render_document(self, doc) -> str:
        self._doc       = doc
        self._doc_cfg   = doc.get_format_config(self.FORMAT_NAME)
        self._context   = getattr(doc, "_render_context", {})
        self._footnotes = []
        css_class       = self._doc_cfg.get("css_class", "")
        show_toc        = self._doc_cfg.get("show_toc", False)

        body     = self.render_block_list(doc.children)
        toc_html = self._build_toc(doc) if show_toc else ""
        fn_html  = self.render_footnotes()

        cls_attr = _cls(css_class)
        return f"<article{cls_attr}>\n{toc_html}{body}{fn_html}\n</article>"

    def render_document_stream(self, doc) -> Generator[str, None, None]:
        self._doc       = doc
        self._doc_cfg   = doc.get_format_config(self.FORMAT_NAME)
        self._context   = getattr(doc, "_render_context", {})
        self._footnotes = []
        css_class       = self._doc_cfg.get("css_class", "")
        show_toc        = self._doc_cfg.get("show_toc", False)

        cls_attr = _cls(css_class)
        yield f"<article{cls_attr}>\n"

        if show_toc:
            yield self._build_toc(doc)

        for child in doc.children:
            result = child.accept(self)
            if result and str(result).strip():
                yield str(result) + "\n"

        footnotes = self.render_footnotes()
        if footnotes:
            yield footnotes
        yield "</article>"

    def _build_toc(self, doc) -> str:
        titulos = self.collect_titulos(doc.children)
        if not titulos:
            return ""
        items: List[str] = []
        for t in titulos:
            text   = self.render_inline_list(t.children)
            anchor = t.texto_puro().lower().replace(" ", "-")
            indent = "  " * (t.nivel - 1)
            items.append(f'{indent}  <li><a href="#{anchor}">{text}</a></li>')
        return "<nav>\n<ul>\n" + "\n".join(items) + "\n</ul>\n</nav>\n"

    def render_footnotes(self) -> str:
        if not self._footnotes:
            return ""
        items = []
        for i, fn in enumerate(self._footnotes, 1):
            content = self.render_inline_list(fn.children)
            items.append(f'  <li id="fn-{i}">{content} <a href="#fnref-{i}">↩</a></li>')
        return '\n<section class="footnotes">\n<hr>\n<ol>\n' + "\n".join(items) + "\n</ol>\n</section>\n"

    # ── Inline ────────────────────────────────────────────────────────────────

    def visit_texto(self, el): return _esc(el.conteudo)
    def visit_negrito(self, el): return f"<strong>{self.render_inline_list(el.children)}</strong>"
    def visit_italico(self, el): return f"<em>{self.render_inline_list(el.children)}</em>"
    def visit_sublinhado(self, el): return f"<u>{self.render_inline_list(el.children)}</u>"
    def visit_link(self, el):
        text   = self.render_inline_list(el.children)
        target = ' target="_blank"' if self.resolve_option(el, "new_tab", False) else ""
        return f'<a href="{_esc(el.url)}"{target}>{text}</a>'
    def visit_quebra_linha(self, el): return "<br>"
    def visit_span(self, el):
        css = el.get_format_option(self.FORMAT_NAME, "css_class")
        return f"<span{_cls(css)}>{self.render_inline_list(el.children)}</span>"
    def visit_emoji(self, el):
        return f'<span role="img" aria-label="emoji">{el.simbolo}</span>'

    def visit_badge(self, el):
        css = el.get_format_option(self.FORMAT_NAME, "css_class") or f"badge badge-{el.tipo}"
        bg, fg = _BADGE_COLORS.get(el.tipo, ("#e0e0e0", "#333"))
        style  = f"background:{bg};color:{fg};padding:1px 6px;border-radius:4px;font-size:.8em;font-weight:600;"
        txt = self.render_inline_list(el.children)
        return f'<span{_cls(css)} style="{style}">{txt}</span>'

    def visit_data_hora(self, el):
        rendered = el.renderizado()
        return f'<time datetime="{el.valor.isoformat()}">{_esc(rendered)}</time>'

    def visit_local(self, el):
        rendered = el.renderizado()
        return f'<address style="display:inline">{_esc(rendered)}</address>'

    def visit_ancora(self, el):
        return f'<span id="{_esc(el.id)}" class="anchor"></span>'

    def visit_ref_cruzada(self, el):
        return f'<a href="#{_esc(el.ancora_id)}">{_esc(el.texto)}</a>'

    def visit_marcador_rodape(self, el):
        self._footnotes.append(el)
        n = len(self._footnotes)
        return f'<sup><a href="#fn-{n}" id="fnref-{n}">[{n}]</a></sup>'

    def visit_variavel(self, el):
        return _esc(str(self._context.get(el.nome, el.padrao)))

    # ── Block ─────────────────────────────────────────────────────────────────

    def visit_titulo(self, el):
        text   = self.render_inline_list(el.children)
        css    = el.get_format_option(self.FORMAT_NAME, "css_class")
        anchor = el.texto_puro().lower().replace(" ", "-")
        id_attr = f' id="{anchor}"'
        return f"<h{el.nivel}{id_attr}{_cls(css)}>{text}</h{el.nivel}>"

    def visit_paragrafo(self, el):
        text = self.render_inline_list(el.children)
        css  = self.resolve_option(el, "css_class", el.estilo or None)
        return f"<p{_cls(css)}>{text}</p>"

    def visit_secao(self, el):
        parts: List[str] = []
        if el.titulo:
            parts.append(el.titulo.accept(self))
        parts.append(self.render_block_list(el.children))
        id_attr = f' id="{_esc(el.id)}"' if el.id else ""
        css     = el.get_format_option(self.FORMAT_NAME, "css_class")
        content = "\n".join(p for p in parts if p)
        return f"<section{id_attr}{_cls(css)}>\n{content}\n</section>"

    def visit_lista(self, el):
        css  = self.resolve_option(el, "css_class", None)
        tag  = "ol" if el.ordenada else "ul"
        rows = "\n".join(
            f"  <li>{self.render_inline_list(item.children)}</li>"
            for item in el.children
        )
        return f"<{tag}{_cls(css)}>\n{rows}\n</{tag}>"

    def visit_item_lista(self, el):
        return f"<li>{self.render_inline_list(el.children)}</li>"

    def visit_tabela(self, el):
        if el.has_fallback(self.FORMAT_NAME):
            return str(el.get_fallback_value(self.FORMAT_NAME))
        css   = self.resolve_option(el, "css_class", None)
        heads = "".join(self._th(c) for c in el.cabecalho)
        thead = f"  <thead><tr>{heads}</tr></thead>"
        body_rows = [
            "    <tr>" + "".join(self._td(c) for c in row) + "</tr>"
            for row in el.linhas
        ]
        tbody = "  <tbody>\n" + "\n".join(body_rows) + "\n  </tbody>"
        table = f"<table{_cls(css)}>\n{thead}\n{tbody}\n</table>"
        if el.legenda:
            table += f"\n<caption>{_esc(el.legenda)}</caption>"
        return table

    def _th(self, cel) -> str:
        from docschema.elements.block import CelulaTabela
        if isinstance(cel, CelulaTabela):
            content = self.render_inline_list(cel.inline_content())
            attrs   = f' style="text-align:{cel.align}"'
            if cel.colspan > 1: attrs += f' colspan="{cel.colspan}"'
            return f"<th{attrs}>{content}</th>"
        return f"<th>{_esc(str(cel))}</th>"

    def _td(self, cel) -> str:
        from docschema.elements.block import CelulaTabela
        if isinstance(cel, CelulaTabela):
            content = self.render_inline_list(cel.inline_content())
            attrs   = f' style="text-align:{cel.align}"'
            if cel.colspan > 1: attrs += f' colspan="{cel.colspan}"'
            if cel.rowspan > 1: attrs += f' rowspan="{cel.rowspan}"'
            return f"<td{attrs}>{content}</td>"
        return f"<td>{_esc(str(cel))}</td>"

    def visit_tabela_conteudo(self, el):
        if self._doc is None:
            return ""
        titulos = self.collect_titulos(self._doc.children, el.show_levels)
        if not titulos:
            return ""
        items: List[str] = []
        counters: Dict[int, int] = {}
        for t in titulos:
            nivel = t.nivel
            counters[nivel] = counters.get(nivel, 0) + 1
            for k in list(counters.keys()):
                if k > nivel:
                    counters[k] = 0
            text   = t.texto_puro()
            anchor = text.lower().replace(" ", "-")
            indent = "  " * (nivel - 1)
            if el.numerado:
                num = ".".join(str(counters.get(i, 0)) for i in range(1, nivel + 1))
                items.append(f'{indent}  <li><a href="#{anchor}">{num}. {_esc(text)}</a></li>')
            else:
                items.append(f'{indent}  <li><a href="#{anchor}">{_esc(text)}</a></li>')
        css = self.resolve_option(el, "css_class", "toc")
        return f'<nav{_cls(css)}>\n  <h2>{_esc(el.titulo)}</h2>\n  <ul>\n' + "\n".join(items) + "\n  </ul>\n</nav>\n"

    def visit_nota_rodape(self, el):
        content = self.render_inline_list(el.children)
        return f'<p class="footnote" id="fn-{el.numero}"><sup>[{el.numero}]</sup> {content}</p>'

    def visit_imagem(self, el):
        if el.has_fallback(self.FORMAT_NAME):
            return str(el.get_fallback_value(self.FORMAT_NAME))
        css     = self.resolve_option(el, "css_class", None)
        loading = self.resolve_option(el, "loading", "eager")
        sizes   = ""
        if el.largura: sizes += f' width="{el.largura}"'
        if el.altura:  sizes += f' height="{el.altura}"'
        img = f'<img src="{_esc(el.src)}" alt="{_esc(el.alt)}"{sizes}{_cls(css)} loading="{loading}">'
        if el.legenda:
            return f"<figure>\n  {img}\n  <figcaption>{_esc(el.legenda)}</figcaption>\n</figure>"
        return img

    def visit_espaco(self, el): return "<br>" * el.linhas

    def visit_quebra_pagina(self, el):
        if el.has_fallback(self.FORMAT_NAME):
            return str(el.get_fallback_value(self.FORMAT_NAME))
        return '<div style="page-break-after: always;"></div>'

    def visit_linha_horizontal(self, el): return "<hr>"

    def visit_bloco_destaque(self, el):
        css     = self.resolve_option(el, "css_class", f"callout callout-{el.tipo}")
        parts: List[str] = []
        if el.titulo:
            icon = _NOTA_ICONS.get(el.tipo, "")
            parts.append(f"  <strong>{icon} {_esc(el.titulo)}</strong>")
        parts.append(self.render_block_list(el.children))
        return f"<div{_cls(css)}>\n" + "\n".join(p for p in parts if p) + "\n</div>"

    def visit_nota(self, el):
        css     = self.resolve_option(el, "css_class", f"note note-{el.tipo}")
        icon    = _NOTA_ICONS.get(el.tipo, "")
        content = self.render_inline_list(el.children)
        return f"<aside{_cls(css)}>{icon} {content}</aside>"

    def visit_citacao(self, el):
        tag     = self.resolve_option(el, "tag", "blockquote")
        content = self.render_inline_list(el.children)
        h       = f"<{tag}>{content}"
        if el.autoria:
            h += f"\n  <cite>— {_esc(el.autoria)}</cite>"
        h += f"</{tag}>"
        return h

    def visit_codigo(self, el):
        css     = self.resolve_option(el, "css_class", f"code-block language-{el.linguagem}")
        return f"<pre{_cls(css)}><code>{_esc(el.conteudo)}</code></pre>"

    # ── v2 block: Formulario ──────────────────────────────────────────────────

    def visit_formulario(self, el):
        acao   = f' action="{_esc(el.acao)}"' if el.acao else ""
        method = f' method="{el.metodo}"'
        css    = el.get_format_option(self.FORMAT_NAME, "css_class") or "form"
        parts  = [f'<form{acao}{method}{_cls(css)}>']
        if el.titulo:
            parts.append(f"  <h3>{_esc(el.titulo)}</h3>")
        for campo in el.campos:
            parts.append("  " + campo.accept(self))
        parts.append('  <button type="submit">Enviar</button>')
        parts.append("</form>")
        return "\n".join(parts)

    def visit_campo_formulario(self, el):
        req   = ' required' if el.obrigatorio else ''
        ph    = f' placeholder="{_esc(el.placeholder)}"' if el.placeholder else ''
        val   = f' value="{_esc(el.valor)}"' if el.valor else ''
        label = f'<label for="{el.nome}">{_esc(el.label)}{"*" if el.obrigatorio else ""}</label>'

        if el.tipo == "textarea":
            return (f'<div class="field">{label}'
                    f'<textarea id="{el.nome}" name="{el.nome}"{ph}{req}></textarea></div>')
        if el.tipo == "select":
            opts = "".join(f'<option value="{_esc(o)}">{_esc(o)}</option>' for o in el.opcoes)
            return f'<div class="field">{label}<select id="{el.nome}" name="{el.nome}"{req}>{opts}</select></div>'
        if el.tipo == "checkbox":
            return f'<div class="field"><input type="checkbox" id="{el.nome}" name="{el.nome}"{val}{req}>{label}</div>'

        return (f'<div class="field">{label}'
                f'<input type="{el.tipo}" id="{el.nome}" name="{el.nome}"{ph}{val}{req}></div>')

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
        css  = self.resolve_option(el, "css_class", "signature-block")
        w    = el.largura * 8  # approx px
        lines = [f'<div{_cls(css)} style="margin:2rem 0;display:inline-block;min-width:{w}px">']
        # multi-line support
        for _ in range(el.linhas):
            lines.append(f'  <div style="border-top:1px solid #333;width:{w}px;margin-bottom:4px"></div>')
        if el.nome:
            lines.append(f'  <p style="margin:2px 0;font-weight:600">{_esc(el.nome)}</p>')
        if el.cargo:
            lines.append(f'  <p style="margin:2px 0;font-style:italic;color:#555">{_esc(el.cargo)}</p>')
        sub = []
        if el.mostrar_data:
            sub.append(_esc(el.data_formatada()))
        if el.mostrar_local and el.local:
            sub.append(_esc(el.local))
        if sub:
            lines.append(f'  <p style="margin:2px 0;font-size:.85em;color:#777">{" &nbsp;|&nbsp; ".join(sub)}</p>')
        lines.append("</div>")
        return "\n".join(lines)
