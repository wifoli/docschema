"""
docschema/fallback/format_options.py
=====================================
format_options reutilizáveis para elementos comuns.

Problema que resolve:
    Você descobre que todas as suas Citacoes precisam de indent=6 no TXT
    e tag="blockquote" no HTML — e tem 30 delas.
    Em vez de repetir format_options={...} em cada uma, você importa
    um preset e passa em todas.

Como usar:
    from docschema.fallback.format_options import (
        FO_CITACAO_FORMAL,
        FO_NOTA_DESTAQUE,
        FO_CODIGO_DARK,
        FO_PARAGRAFO_LEAD,
    )
    from docschema import Citacao, Nota, Codigo, Paragrafo, Texto

    q = Citacao(
        [Texto("A excelência não é um ato, é um hábito.")],
        autoria="Aristóteles",
        format_options=FO_CITACAO_FORMAL,
    )
"""
from typing import Any, Dict


# ── Tipo ──────────────────────────────────────────────────────────────────────

FormatOptions = Dict[str, Dict[str, Any]]


# ── Citação ───────────────────────────────────────────────────────────────────

FO_CITACAO_FORMAL: FormatOptions = {
    "txt": {
        "indent": 6,
        "prefix": "> ",     # mesmo estilo que markdown
    },
    "html": {
        "tag": "blockquote",
        "css_class": "quote quote-formal",
    },
}
"""Citação com recuo generoso e marcador de quote no TXT."""

FO_CITACAO_CURTA: FormatOptions = {
    "txt":  {"indent": 2},
    "html": {"tag": "q", "css_class": "quote quote-inline"},
}
"""Citação curta — tag <q> inline no HTML, recuo mínimo no TXT."""


# ── Notas / alertas ───────────────────────────────────────────────────────────

FO_NOTA_DESTAQUE: FormatOptions = {
    "txt":      {"border": True, "label": ">>> ATENÇÃO <<<"},
    "html":     {"css_class": "note note-warning note-highlight"},
    "markdown": {"prefix": "> ⚠️ "},
}
"""Nota de atenção com borda no TXT e destaque visual no HTML."""

FO_NOTA_SUTIL: FormatOptions = {
    "txt":      {"border": False},
    "html":     {"css_class": "note note-info note-subtle"},
    "markdown": {"prefix": "> 💬 "},
}
"""Nota informacional discreta — sem bordas no TXT."""


# ── Código ────────────────────────────────────────────────────────────────────

FO_CODIGO_INLINE: FormatOptions = {
    "txt":  {"indent": 0},  # sem recuo — leitura em linha
    "html": {"css_class": "code-inline"},
}
"""Bloco de código pequeno, sem recuo no TXT."""

FO_CODIGO_DESTACADO: FormatOptions = {
    "txt":  {"indent": 4},
    "html": {"css_class": "code-block code-highlighted hljs"},
}
"""Bloco de código com recuo maior e hint para highlight.js no HTML."""

FO_CODIGO_TERMINAL: FormatOptions = {
    "txt":  {"indent": 2, "prefix": "$ "},
    "html": {"css_class": "code-block code-terminal language-bash"},
}
"""Código de terminal/shell — prefixo $ no TXT."""


# ── Parágrafo ─────────────────────────────────────────────────────────────────

FO_PARAGRAFO_LEAD: FormatOptions = {
    "txt":  {"prefix": "  "},   # leve recuo para parágrafo de abertura
    "html": {"css_class": "lead"},
}
"""Parágrafo de abertura/introdução — maior e com destaque no HTML."""

FO_PARAGRAFO_AVISO: FormatOptions = {
    "txt":  {"prefix": "! ", "uppercase": False},
    "html": {"css_class": "text-warning"},
}
"""Parágrafo de aviso — prefixo '!' no TXT, cor warning no HTML."""

FO_PARAGRAFO_LEGAL: FormatOptions = {
    "txt":  {"indent": 0},
    "html": {"css_class": "legal-text text-sm"},
}
"""Texto jurídico/legal — fonte menor no HTML."""


# ── Lista ─────────────────────────────────────────────────────────────────────

FO_LISTA_CHECKLIST: FormatOptions = {
    "txt":      {"bullet": "[ ]"},
    "html":     {"css_class": "list-checklist"},
    "markdown": {},   # renderiza como - mas não muda comportamento
}
"""Lista com estilo de checklist — '[ ]' como bullet no TXT."""

FO_LISTA_COMPACTA: FormatOptions = {
    "txt":      {"bullet": "·"},
    "html":     {"css_class": "list-compact"},
}
"""Lista compacta com bullet minimalista."""


# ── BlocoDestaque ─────────────────────────────────────────────────────────────

FO_BLOCO_IMPORTANTE: FormatOptions = {
    "txt":  {"border": True, "label": "[ IMPORTANTE ]"},
    "html": {"css_class": "callout callout-danger"},
}
"""Bloco de destaque para informações críticas — com borda no TXT."""

FO_BLOCO_DICA: FormatOptions = {
    "txt":  {"border": False, "label": "💡 Dica:"},
    "html": {"css_class": "callout callout-tip"},
}
"""Bloco de dica com ícone no TXT."""


# ── Factory para casos customizados ──────────────────────────────────────────

def fo_campo_largura(largura_txt: int = 30) -> FormatOptions:
    """
    format_options para campos de formulário com largura customizada.

    Exemplo:
        CampoFormulario("obs", tipo="textarea", label="Observações",
                        format_options=fo_campo_largura(50))
    """
    return {
        "txt": {"field_width": largura_txt},
    }


def fo_citacao_com_fonte(url: str) -> FormatOptions:
    """
    format_options que adiciona URL da fonte ao final da citação.

    Exemplo:
        Citacao(
            [Texto("...")],
            autoria="IBGE",
            format_options=fo_citacao_com_fonte("https://ibge.gov.br/..."),
        )
    """
    return {
        "txt":  {"indent": 4},
        "html": {"tag": "blockquote", "css_class": "quote", "source_url": url},
    }
