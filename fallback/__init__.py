"""
docschema.fallback
===================
Presets reutilizáveis de fallback e format_options.

Importação rápida:

    from docschema.fallback import (
        fallback_imagem, fallback_por_tipo,
        FALLBACK_GRAFICO, FALLBACK_FOTO_PERFIL, FALLBACK_DIAGRAMA,
        opts_tabela_financeira, opts_tabela_dados,
        FO_CITACAO_FORMAL, FO_NOTA_DESTAQUE, FO_CODIGO_TERMINAL,
    )
"""
from docschema.fallback.imagens import (
    fallback_imagem, fallback_por_tipo,
    FALLBACK_GRAFICO, FALLBACK_FOTO_PERFIL, FALLBACK_DIAGRAMA,
    FALLBACK_LOGO, FALLBACK_ASSINATURA_IMAGEM,
)
from docschema.fallback.tabelas import (
    opts_tabela_financeira, opts_tabela_dados,
    opts_tabela_simples, opts_tabela_comparativa,
    tabela_sem_suporte_txt,
)
from docschema.fallback.format_options import (
    FO_CITACAO_FORMAL, FO_CITACAO_CURTA,
    FO_NOTA_DESTAQUE, FO_NOTA_SUTIL,
    FO_CODIGO_INLINE, FO_CODIGO_DESTACADO, FO_CODIGO_TERMINAL,
    FO_PARAGRAFO_LEAD, FO_PARAGRAFO_AVISO, FO_PARAGRAFO_LEGAL,
    FO_LISTA_CHECKLIST, FO_LISTA_COMPACTA,
    FO_BLOCO_IMPORTANTE, FO_BLOCO_DICA,
    fo_campo_largura, fo_citacao_com_fonte,
)
