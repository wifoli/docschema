"""
docschema/fallback/tabelas.py
==============================
Fallbacks e format_options pré-definidos para Tabela por contexto.

Problema que resolve:
    Uma tabela financeira (com totais, alinhamento right) precisa de uma
    estratégia diferente de uma tabela de dados genérica.
    Em TXT e Clipboard, a estratégia padrão "columns" pode não ser ideal.

Como usar:
    from docschema.fallback.tabelas import (
        opts_tabela_financeira,
        opts_tabela_dados,
        opts_tabela_simples,
    )
    from docschema import Tabela

    tabela = Tabela(
        cabecalho=["Item", "Qtd", "Valor"],
        linhas=[["Produto A", "5", "R$ 250"]],
        format_options=opts_tabela_financeira(),
    )
"""
from typing import Any, Dict, Optional


# ── Tipo ──────────────────────────────────────────────────────────────────────

FormatOptionsTabela = Dict[str, Dict[str, Any]]


# ── Helpers ───────────────────────────────────────────────────────────────────

def opts_tabela_financeira(
    min_column_width: int = 14,
    clipboard_strategy: str = "list",
) -> FormatOptionsTabela:
    """
    format_options para tabelas financeiras.

    TXT:       colunas ASCII com largura mínima generosa
    Clipboard: lista chave:valor (mais legível ao colar em e-mail/chat)
    HTML:      classe CSS "table-financial"
    PDF:       repetição de cabeçalho em todas as páginas

    Exemplo:
        Tabela(
            cabecalho=["Descrição", "Quantidade", "Valor Unit.", "Total"],
            linhas=[...],
            format_options=opts_tabela_financeira(),
        )
    """
    return {
        "txt": {
            "fallback_strategy": "columns",
            "min_column_width":  min_column_width,
        },
        "clipboard": {
            "fallback_strategy": clipboard_strategy,  # "list" = item por item
        },
        "html": {
            "css_class": "table table-financial",
        },
        "markdown": {
            # nada especial — usa padrão GFM
        },
    }


def opts_tabela_dados(
    txt_strategy: str = "columns",
    min_column_width: int = 10,
) -> FormatOptionsTabela:
    """
    format_options para tabelas de dados genéricas.

    TXT:  colunas ASCII padrão, coluna mínima menor
    HTML: classe "table table-data table-striped"
    """
    return {
        "txt": {
            "fallback_strategy": txt_strategy,
            "min_column_width":  min_column_width,
        },
        "clipboard": {
            "fallback_strategy": "list",
        },
        "html": {
            "css_class": "table table-data table-striped",
        },
    }


def opts_tabela_simples() -> FormatOptionsTabela:
    """
    format_options mínimo — apenas garante comportamento previsível
    sem customizar muito cada formato.
    """
    return {
        "txt":       {"fallback_strategy": "columns", "min_column_width": 10},
        "clipboard": {"fallback_strategy": "list"},
        "html":      {"css_class": "table"},
    }


def opts_tabela_comparativa(
    destacar_colunas: Optional[int] = None,
) -> FormatOptionsTabela:
    """
    format_options para tabelas de comparação (features A vs B vs C).

    TXT:  colunas side-by-side com largura generosa
    Clipboard: lista detalhada
    HTML:  classe "table table-compare"

    Argumento:
        destacar_colunas — índice da coluna a destacar (ex: coluna do plano recomendado)
    """
    opts = {
        "txt": {
            "fallback_strategy": "columns",
            "min_column_width":  16,
        },
        "clipboard": {
            "fallback_strategy": "list",
        },
        "html": {
            "css_class": "table table-compare",
        },
    }
    if destacar_colunas is not None:
        opts["html"]["highlight_col"] = destacar_colunas
    return opts


# ── Presets completos (format_options + fallback dict) ────────────────────────

def tabela_sem_suporte_txt(mensagem: str = "[Tabela disponível apenas na versão visual]") -> Dict[str, Any]:
    """
    Retorna o argumento `fallback=` para uma Tabela que não deve
    ser renderizada em TXT/Clipboard — apenas mostra uma mensagem.

    Uso:
        Tabela(
            cabecalho=[...],
            linhas=[...],
            fallback=tabela_sem_suporte_txt("Ver tabela no PDF/HTML"),
        )
    """
    return {
        "txt":       mensagem,
        "clipboard": "[tabela — ver versão visual]",
    }
