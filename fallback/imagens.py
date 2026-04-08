"""
docschema/fallback/imagens.py
==============================
Fallbacks pré-definidos para Imagem por formato.

Problema que resolve:
    PDF e DOCX podem mostrar a imagem real.
    TXT e Clipboard não suportam imagens — o que mostrar no lugar?
    HTML pode querer uma tag diferente da padrão.

Como usar:
    from docschema.fallback.imagens import fallback_imagem, FALLBACK_GRAFICO, FALLBACK_FOTO_PERFIL
    from docschema import Imagem

    # Usando preset pronto:
    img = Imagem(
        src="relatorio/grafico_vendas.png",
        alt="Gráfico de vendas",
        legenda="Figura 3 — Vendas mensais 2025",
        fallback=FALLBACK_GRAFICO,
    )

    # Usando helper com texto customizado:
    img = Imagem(
        src="logo.png",
        alt="Logo da empresa",
        fallback=fallback_imagem(
            txt="[Logo: Acme Corp — acme.com.br]",
            clipboard="Acme Corp",
        ),
    )
"""
from typing import Any, Dict


# ── Tipo ──────────────────────────────────────────────────────────────────────

FallbackImagem = Dict[str, Any]


# ── Helper principal ──────────────────────────────────────────────────────────

def fallback_imagem(
    txt:       str = "",
    clipboard: str = "",
    markdown:  str = "",
    html:      str = "",
) -> FallbackImagem:
    """
    Monta um dict de fallbacks para Imagem com os formatos especificados.
    Formatos não fornecidos ficam sem fallback (o renderer decide o padrão).

    Exemplo:
        fallback=fallback_imagem(
            txt="[Ver gráfico em: https://dash.acme.com/grafico-3]",
            clipboard="grafico-vendas-2025",
        )
    """
    result: FallbackImagem = {}
    if txt:
        result["txt"]       = txt
    if clipboard:
        result["clipboard"] = clipboard
    if markdown:
        result["markdown"]  = markdown
    if html:
        result["html"]      = html
    return result


# ── Presets prontos ───────────────────────────────────────────────────────────

FALLBACK_GRAFICO: FallbackImagem = {
    "txt":       "[GRÁFICO — disponível na versão HTML/PDF deste relatório]",
    "clipboard": "[gráfico]",
    "markdown":  "*[Gráfico disponível na versão visual]*",
}
"""
Fallback padrão para gráficos.
Claramente avisa que o gráfico existe, mas não está disponível no formato atual.
"""

FALLBACK_FOTO_PERFIL: FallbackImagem = {
    "txt":       "[Foto de perfil]",
    "clipboard": "",  # omite completamente no clipboard
    "markdown":  "*[Foto de perfil]*",
}
"""
Fallback para fotos de perfil/avatares.
Clipboard omite completamente (string vazia = elemento ignorado).
"""

FALLBACK_DIAGRAMA: FallbackImagem = {
    "txt": (
        "[DIAGRAMA — descrição textual abaixo]\n"
        "Este diagrama está disponível apenas na versão visual do documento."
    ),
    "clipboard": "[ver diagrama na versão visual]",
    "markdown":  "*Ver diagrama na versão HTML ou PDF.*",
}
"""
Fallback para diagramas técnicos.
TXT inclui aviso de que há descrição alternativa a seguir.
"""

FALLBACK_LOGO: FallbackImagem = {
    "txt":       "",   # Logo não faz sentido em TXT — omite
    "clipboard": "",   # Omite no clipboard também
    "markdown":  "",   # Omite no markdown inline
}
"""
Fallback para logotipos.
Em todos os formatos de texto, o logo simplesmente não aparece
(é decorativo, não informativo).
"""

FALLBACK_ASSINATURA_IMAGEM: FallbackImagem = {
    "txt":       "[ Assinado digitalmente ]",
    "clipboard": "[ass. digital]",
    "markdown":  "*[Assinatura digital anexada ao documento original]*",
}
"""
Fallback para imagem de assinatura manuscrita digitalizada.
"""


# ── Factory por tipo de imagem ────────────────────────────────────────────────

def fallback_por_tipo(tipo: str, nome: str = "") -> FallbackImagem:
    """
    Retorna um fallback adequado com base no tipo semântico da imagem.

    Tipos reconhecidos:
        "grafico"   → FALLBACK_GRAFICO
        "foto"      → FALLBACK_FOTO_PERFIL
        "diagrama"  → FALLBACK_DIAGRAMA
        "logo"      → FALLBACK_LOGO
        "assinatura"→ FALLBACK_ASSINATURA_IMAGEM
        outro       → fallback genérico com o nome

    Exemplo:
        Imagem(src="organograma.png", alt="Organograma",
               fallback=fallback_por_tipo("diagrama", "Organograma Departamental"))
    """
    _MAP = {
        "grafico":    FALLBACK_GRAFICO,
        "foto":       FALLBACK_FOTO_PERFIL,
        "diagrama":   FALLBACK_DIAGRAMA,
        "logo":       FALLBACK_LOGO,
        "assinatura": FALLBACK_ASSINATURA_IMAGEM,
    }
    preset = _MAP.get(tipo.lower())
    if preset:
        return preset

    # Tipo desconhecido: fallback genérico com o nome
    label = f"[{nome or tipo}]"
    return {
        "txt":       label,
        "clipboard": label,
        "markdown":  f"*{label}*",
    }
