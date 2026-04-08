"""
docschema.renderers.pdf  (v2)
===============================
PDF renderer using ReportLab.
pip install reportlab

v2 additions:
  - output_path accepts BytesIO
  - TabelaConteudo, Assinatura, Badge, Formulario, Se, Para
  - Footnotes collected and printed at end
"""
from __future__ import annotations

import io
from typing import Any, Dict, Generator, List, Optional

from docschema.renderers.base import BaseRenderer

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, KeepTogether,
    )
    from reportlab.platypus.tableofcontents import TableOfContents
    _RL_AVAILABLE = True
except ImportError:
    _RL_AVAILABLE = False


class PdfRenderer(BaseRenderer):
    FORMAT_NAME = "pdf"

    def __init__(self, output_path=None, **kwargs):
        super().__init__(**kwargs)
        if not _RL_AVAILABLE:
            raise ImportError("PdfRenderer requires reportlab. Run: pip install reportlab")
        self._output_path = output_path or "output.pdf"

    # ── Document ──────────────────────────────────────────────────────────────

    def render_document(self, doc) -> Any:
        self._doc       = doc
        self._doc_cfg   = doc.get_format_config(self.FORMAT_NAME)
        self._context   = getattr(doc, "_render_context", {})
        self._footnotes = []

        styles = getSampleStyleSheet()
        self._styles = {
            "h1":      ParagraphStyle("H1",    parent=styles["Heading1"], fontSize=18, spaceAfter=8),
            "h2":      ParagraphStyle("H2",    parent=styles["Heading2"], fontSize=15, spaceAfter=6),
            "h3":      ParagraphStyle("H3",    parent=styles["Heading3"], fontSize=13, spaceAfter=4),
            "body":    ParagraphStyle("Body",  parent=styles["Normal"],   fontSize=11, leading=16),
            "bold":    ParagraphStyle("Bold",  parent=styles["Normal"],   fontSize=11, leading=16),
            "code":    ParagraphStyle("Code",  parent=styles["Code"],     fontSize=9,  fontName="Courier"),
            "quote":   ParagraphStyle("Quote", parent=styles["Normal"],   leftIndent=24, rightIndent=24, textColor=colors.grey),
            "caption": ParagraphStyle("Cap",   parent=styles["Normal"],   fontSize=9,  textColor=colors.grey),
            "fn":      ParagraphStyle("FN",    parent=styles["Normal"],   fontSize=9,  textColor=colors.grey),
            "sig":     ParagraphStyle("Sig",   parent=styles["Normal"],   fontSize=11),
        }

        story = []
        for child in doc.children:
            result = child.accept(self)
            if result is not None:
                if isinstance(result, list):
                    story.extend(r for r in result if r is not None)
                else:
                    story.append(result)

        # Append footnotes
        if self._footnotes:
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
            for i, fn in enumerate(self._footnotes, 1):
                content = self._inline_text(fn.children)
                story.append(Paragraph(f"[{i}] {content}", self._styles["fn"]))

        # Output
        path = self._output_path
        if isinstance(path, (str,)):
            buf = path
        else:
            buf = path  # BytesIO accepted directly

        doc_rl = SimpleDocTemplate(
            buf,
            pagesize=A4,
            title=doc.titulo or "",
            author=doc.autor or "",
            rightMargin=2*cm, leftMargin=2*cm, topMargin=2.5*cm, bottomMargin=2*cm,
        )
        doc_rl.build(story)

        if isinstance(path, str):
            return path
        if hasattr(path, "getvalue"):
            return path.getvalue()
        return path

    def render_document_stream(self, doc) -> Generator[bytes, None, None]:
        buf = io.BytesIO()
        original = self._output_path
        self._output_path = buf
        self.render_document(doc)
        self._output_path = original
        yield buf.getvalue()

    # ── Inline helpers ────────────────────────────────────────────────────────

    def _inline_text(self, children) -> str:
        """Convert inline elements to ReportLab-compatible HTML string."""
        parts = []
        for el in children:
            parts.append(str(el.accept(self)))
        return "".join(parts)

    def visit_texto(self, el): return el.conteudo
    def visit_negrito(self, el): return f"<b>{self._inline_text(el.children)}</b>"
    def visit_italico(self, el): return f"<i>{self._inline_text(el.children)}</i>"
    def visit_sublinhado(self, el): return f"<u>{self._inline_text(el.children)}</u>"
    def visit_link(self, el):
        text = self._inline_text(el.children)
        return f'<a href="{el.url}" color="blue">{text}</a>' if el.url else text
    def visit_quebra_linha(self, el): return "<br/>"
    def visit_span(self, el): return self._inline_text(el.children)
    def visit_emoji(self, el): return el.simbolo

    def visit_badge(self, el):
        sym = el._TXT_SYMBOLS.get(el.tipo, "")
        txt = self._inline_text(el.children)
        return f"<b>[{sym}{txt}]</b>"

    def visit_data_hora(self, el): return el.renderizado()
    def visit_local(self, el): return el.renderizado()
    def visit_ancora(self, el): return ""
    def visit_ref_cruzada(self, el): return el.texto  # PDF: no internal anchor links

    def visit_marcador_rodape(self, el):
        self._footnotes.append(el)
        n = len(self._footnotes)
        return f"<super><font size='7'>[{n}]</font></super>"

    def visit_variavel(self, el):
        return str(self._context.get(el.nome, el.padrao))

    # ── Block helpers ─────────────────────────────────────────────────────────

    def visit_titulo(self, el):
        text  = self._inline_text(el.children)
        style = self._styles.get(f"h{el.nivel}", self._styles["h3"])
        return Paragraph(text, style)

    def visit_paragrafo(self, el):
        text = self._inline_text(el.children)
        return Paragraph(text, self._styles["body"])

    def visit_secao(self, el):
        result = []
        if el.titulo:
            t = el.titulo.accept(self)
            if t: result.append(t)
        for child in el.children:
            r = child.accept(self)
            if r:
                result.extend(r) if isinstance(r, list) else result.append(r)
        return result

    def visit_lista(self, el):
        result = []
        for i, item in enumerate(el.children, 1):
            content = self._inline_text(item.children)
            marker  = f"{i}." if el.ordenada else "•"
            result.append(Paragraph(f"<para leftIndent='20'>{marker} {content}</para>",
                                    self._styles["body"]))
        return result

    def visit_item_lista(self, el): return Paragraph(self._inline_text(el.children), self._styles["body"])

    def visit_tabela(self, el):
        from reportlab.platypus import Table as RLTable
        cab  = [self._cel_pdf(c) for c in el.cabecalho]
        rows = [[self._cel_pdf(c) for c in row] for row in el.linhas]
        data = [cab] + rows
        style = TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2E75B6")),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F5F5F5")]),
            ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ])
        t = RLTable(data, hAlign="LEFT", style=style, repeatRows=1)
        result = [t]
        if el.legenda:
            result.append(Paragraph(el.legenda, self._styles["caption"]))
        return result

    def _cel_pdf(self, cel):
        from docschema.elements.block import CelulaTabela
        if isinstance(cel, CelulaTabela):
            return self._inline_text(cel.inline_content())
        return str(cel)

    def visit_tabela_conteudo(self, el):
        # Simple TOC: list of headings
        if self._doc is None:
            return []
        titulos = self.collect_titulos(self._doc.children, el.show_levels)
        result  = [Paragraph(el.titulo, self._styles["h2"])]
        for t in titulos:
            text   = t.texto_puro()
            indent = 20 * (t.nivel - 1)
            p = Paragraph(f"<para leftIndent='{indent}'>{'·'*(t.nivel)} {text}</para>",
                          self._styles["body"])
            result.append(p)
        return result

    def visit_nota_rodape(self, el):
        content = self._inline_text(el.children)
        return Paragraph(f"[{el.numero}] {content}", self._styles["fn"])

    def visit_imagem(self, el):
        if el.has_fallback(self.FORMAT_NAME):
            return Paragraph(str(el.get_fallback_value(self.FORMAT_NAME)), self._styles["body"])
        try:
            from reportlab.platypus import Image
            w = (el.largura or 400) * 0.75
            h = (el.altura or 300) * 0.75
            img = Image(el.src, width=w, height=h)
            result = [img]
            if el.legenda:
                result.append(Paragraph(el.legenda, self._styles["caption"]))
            return result
        except Exception:
            return Paragraph(f"[Imagem: {el.alt}]", self._styles["body"])

    def visit_espaco(self, el): return Spacer(1, el.linhas * 6 * mm)
    def visit_quebra_pagina(self, el): return PageBreak()
    def visit_linha_horizontal(self, el): return HRFlowable(width="100%", thickness=0.5, color=colors.grey)

    def visit_bloco_destaque(self, el):
        _colors = {"info": "#E3F2FD", "warning": "#FFF8E1", "tip": "#E8F5E9", "danger": "#FFEBEE"}
        bg = colors.HexColor(_colors.get(el.tipo, "#F5F5F5"))
        result = []
        if el.titulo:
            result.append(Paragraph(f"<b>{el.titulo}</b>", self._styles["body"]))
        for child in el.children:
            r = child.accept(self)
            if r:
                result.extend(r) if isinstance(r, list) else result.append(r)
        table = Table([[result]], style=TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), bg),
            ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 12),
        ]))
        return table

    def visit_nota(self, el):
        _labels = {"info":"ℹ️","warning":"⚠️","tip":"💡","danger":"🚨"}
        icon    = _labels.get(el.tipo, "")
        content = self._inline_text(el.children)
        return Paragraph(f"{icon} {content}", self._styles["body"])

    def visit_citacao(self, el):
        content = self._inline_text(el.children)
        result  = [Paragraph(f"<i>{content}</i>", self._styles["quote"])]
        if el.autoria:
            result.append(Paragraph(f"— {el.autoria}", self._styles["caption"]))
        return result

    def visit_codigo(self, el):
        return Paragraph(el.conteudo.replace("\n", "<br/>"), self._styles["code"])

    def visit_formulario(self, el):
        result = []
        if el.titulo:
            result.append(Paragraph(el.titulo, self._styles["h3"]))
        for campo in el.campos:
            r = campo.accept(self)
            if r:
                result.extend(r) if isinstance(r, list) else result.append(r)
        return result

    def visit_campo_formulario(self, el):
        req = " *" if el.obrigatorio else ""
        if el.tipo == "checkbox":
            return Paragraph(f"☐ {el.label}{req}", self._styles["body"])
        return Paragraph(f"{el.label}{req}: _________________", self._styles["body"])

    def visit_se(self, el):
        ramo = el.sim if el.avaliar(self._context) else el.nao
        if not ramo:
            return []
        result = []
        for child in ramo:
            r = child.accept(self)
            if r:
                result.extend(r) if isinstance(r, list) else result.append(r)
        return result

    def visit_para(self, el):
        itens  = el.itens(self._context) if callable(el.itens) else el.itens
        result = []
        for item in itens:
            for child in el.template(item, self._context):
                r = child.accept(self)
                if r:
                    result.extend(r) if isinstance(r, list) else result.append(r)
        return result

    def visit_assinatura(self, el):
        w = el.largura * 0.3 * cm
        parts = []
        parts.append(HRFlowable(width=w, thickness=1, color=colors.black))
        if el.nome:
            parts.append(Paragraph(f"<b>{el.nome}</b>", self._styles["sig"]))
        if el.cargo:
            parts.append(Paragraph(f"<i>{el.cargo}</i>", self._styles["sig"]))
        sub = []
        if el.mostrar_data:
            sub.append(el.data_formatada())
        if el.mostrar_local and el.local:
            sub.append(el.local)
        if sub:
            parts.append(Paragraph(" | ".join(sub), self._styles["caption"]))
        return parts
