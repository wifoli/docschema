"""
docschema  (v2)
================
Multi-format document generation from a single content definition.

New in v2:
  Inline: Badge, DataHora, Local, Ancora, RefCruzada, MarcadorRodape, Variavel
  Block:  TabelaConteudo, CelulaTabela, NotaRodape, Formulario, CampoFormulario,
          Se, Para, Assinatura
  Engine: gerar_stream(), gerar_bytes(), contexto support
  Templates: usar_template(), registrar_template(), listar_templates()
"""
# ── Document ──────────────────────────────────────────────────────────────────
from docschema.document import Documento

# ── Block elements ────────────────────────────────────────────────────────────
from docschema.elements.block import (
    Assinatura,
    BlocoDestaque,
    CampoFormulario,
    CelulaTabela,
    Citacao,
    Codigo,
    Espaco,
    Formulario,
    Imagem,
    ItemLista,
    LinhaHorizontal,
    Lista,
    NotaRodape,
    Nota,
    Para,
    Paragrafo,
    QuebraPagina,
    Se,
    Secao,
    Subtitulo,
    TabelaConteudo,
    Tabela,
    Titulo,
)

# ── Inline elements ───────────────────────────────────────────────────────────
from docschema.elements.inline import (
    Ancora,
    Badge,
    DataHora,
    Emoji,
    Italico,
    Link,
    Local,
    MarcadorRodape,
    Negrito,
    QuebraLinha,
    RefCruzada,
    Span,
    Sublinhado,
    Texto,
    Variavel,
)

# ── Engine ────────────────────────────────────────────────────────────────────
from docschema.engine import DocumentEngine, engine, gerar, gerar_stream, gerar_bytes

# ── Renderers ─────────────────────────────────────────────────────────────────
from docschema.renderers.base      import BaseRenderer
from docschema.renderers.txt       import TxtRenderer
from docschema.renderers.markdown  import MarkdownRenderer
from docschema.renderers.html      import HtmlRenderer
from docschema.renderers.clipboard import ClipboardRenderer

# ── Templates ─────────────────────────────────────────────────────────────────
from docschema.templates import (
    Template, TemplateRegistro,
    registrar_template, usar_template, listar_templates,
)

__all__ = [
    # Document
    "Documento",
    # Block elements
    "Assinatura", "BlocoDestaque", "CampoFormulario", "CelulaTabela",
    "Citacao", "Codigo", "Espaco", "Formulario", "Imagem",
    "ItemLista", "LinhaHorizontal", "Lista", "Nota", "NotaRodape",
    "Para", "Paragrafo", "QuebraPagina", "Se", "Secao", "Subtitulo",
    "TabelaConteudo", "Tabela", "Titulo",
    # Inline elements
    "Ancora", "Badge", "DataHora", "Emoji", "Italico", "Link", "Local",
    "MarcadorRodape", "Negrito", "QuebraLinha", "RefCruzada", "Span",
    "Sublinhado", "Texto", "Variavel",
    # Engine
    "gerar", "gerar_stream", "gerar_bytes", "engine", "DocumentEngine",
    # Renderers
    "BaseRenderer", "TxtRenderer", "MarkdownRenderer", "HtmlRenderer", "ClipboardRenderer",
    # Templates
    "Template", "TemplateRegistro",
    "registrar_template", "usar_template", "listar_templates",
]
