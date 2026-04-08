"""
examples/receita.py
====================
Receita de Bolo de Cenoura — demonstra todas as funcionalidades do docschema:
  • elementos de bloco e inline compostos
  • format_options por elemento
  • fallback de imagem, tabela e quebra de página
  • geração em TXT, Markdown, HTML e Clipboard
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from docschema import (
    Documento, Secao, Titulo, Subtitulo, Paragrafo,
    Lista, ItemLista, Tabela, Imagem, Espaco, QuebraPagina,
    LinhaHorizontal, BlocoDestaque, Citacao, Codigo, Nota,
    Texto, Negrito, Italico, Sublinhado, Link, QuebraLinha, Span, Emoji,
    gerar,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Definição do documento (única vez — renderizado em múltiplos formatos)
# ═══════════════════════════════════════════════════════════════════════════════

receita = Documento(
    id="receita-bolo-cenoura-cobertura-chocolate",
    titulo="Receita de Bolo de Cenoura com Cobertura de Chocolate",
    autor="Leandro",
    idioma="pt-BR",
    metadata={
        "categoria": "receita",
        "porcoes": 10,
        "tempo_preparo_min": 20,
        "tempo_forno_min": 40,
        "tempo_total_min": 60,
        "dificuldade": "fácil",
        "tags": ["bolo", "cenoura", "sobremesa", "forno", "chocolate"],
    },
    format_options={
        "html": {
            "css_class": "receita receita-bolo",
            "show_toc": True,
        },
        "markdown": {
            "title_as_h1": True,
            "table_style": "pipe",
        },
        "txt": {
            "line_width": 88,
            "section_separator": "=" * 88,
        },
        "clipboard": {
            "mode": "compact",
        },
    },
    children=[
        Titulo(
            [
                Texto("Receita de "),
                Negrito("Bolo de Cenoura"),
                Texto(" com "),
                Italico("Cobertura de Chocolate"),
                Emoji("🥕"),
            ],
            nivel=1,
            metadata={"semantic_role": "recipe_title"},
        ),

        Paragrafo(
            [
                Texto("Uma receita clássica, fofinha e ótima para café da tarde. "),
                Texto("Esta versão foi escrita em um modelo "),
                Negrito("abstrato e multiformato"),
                Texto(", para poder ser exportada para PDF, DOCX, HTML, Markdown, TXT e clipboard."),
            ],
            estilo="lead",
            format_options={
                "html":     {"css_class": "lead receita-resumo"},
                "markdown": {"prefix": "> "},
                "txt":      {"uppercase": False},
            },
        ),

        Nota(
            [
                Negrito("Rendimento: "),
                Texto("aproximadamente 10 fatias"),
                QuebraLinha(),
                Negrito("Tempo total: "),
                Texto("1 hora"),
                QuebraLinha(),
                Negrito("Dificuldade: "),
                Texto("fácil"),
            ],
            tipo="info",
            format_options={
                "html":     {"css_class": "recipe-meta-box"},
                "txt":      {"border": True},
                "markdown": {"style": "blockquote"},
            },
        ),

        LinhaHorizontal(),

        # ── Seção: Ingredientes ────────────────────────────────────────────────
        Secao(
            id="ingredientes",
            titulo=Titulo("Ingredientes", nivel=2),
            metadata={"semantic_role": "ingredients_section"},
            children=[
                Subtitulo("Massa", nivel=3),

                Lista(
                    ordenada=False,
                    children=[
                        ItemLista([Texto("3 cenouras médias picadas")]),
                        ItemLista([Texto("4 ovos")]),
                        ItemLista([Texto("1 xícara de óleo")]),
                        ItemLista([Texto("2 xícaras de açúcar")]),
                        ItemLista([Texto("2 e 1/2 xícaras de farinha de trigo")]),
                        ItemLista([Texto("1 colher de sopa de fermento em pó")]),
                    ],
                    format_options={
                        "txt":      {"bullet": "-"},
                        "markdown": {"bullet": "-"},
                        "html":     {"css_class": "ingredientes-lista"},
                    },
                ),

                Espaco(1),
                Subtitulo("Cobertura", nivel=3),

                Lista(
                    ordenada=False,
                    children=[
                        ItemLista([Texto("4 colheres de sopa de chocolate em pó")]),
                        ItemLista([Texto("2 colheres de sopa de manteiga")]),
                        ItemLista([Texto("1 xícara de leite")]),
                        ItemLista([Texto("1 xícara de açúcar")]),
                    ],
                ),

                Espaco(1),

                BlocoDestaque(
                    titulo="Substituições possíveis",
                    children=[
                        Paragrafo([
                            Texto("Você pode substituir o chocolate em pó por "),
                            Negrito("cacau 50%"),
                            Texto(", ajustando o açúcar se quiser uma cobertura menos intensa."),
                        ]),
                        Paragrafo([
                            Texto("Para uma versão sem lactose, use "),
                            Span(
                                [Texto("bebida vegetal e margarina apropriada")],
                                metadata={"semantic_role": "substituicao"},
                            ),
                            Texto("."),
                        ]),
                    ],
                    tipo="tip",
                    format_options={
                        "html":     {"css_class": "box box-tip"},
                        "markdown": {"title_prefix": "💡 "},
                        "txt":      {"label": "[DICA]"},
                    },
                ),
            ],
        ),

        # ── Quebra de página com fallback explícito por formato ────────────────
        QuebraPagina(
            format_options={
                "html":     {"fallback": "<!-- page-break -->"},
                "markdown": {"fallback": "\n---\n"},
                "txt":      {"fallback": "\n" + ("-" * 60) + "\n"},
            }
        ),

        # ── Seção: Modo de preparo ─────────────────────────────────────────────
        Secao(
            id="modo-de-preparo",
            titulo=Titulo("Modo de preparo", nivel=2),
            metadata={"semantic_role": "instructions_section"},
            children=[
                Subtitulo("Massa", nivel=3),

                Lista(
                    ordenada=True,
                    children=[
                        ItemLista([
                            Texto("Preaqueça o forno a "),
                            Negrito("180°C"),
                            Texto(" e unte uma forma com manteiga e farinha."),
                        ]),
                        ItemLista([
                            Texto("No liquidificador, bata as "),
                            Negrito("cenouras"),
                            Texto(", os "),
                            Negrito("ovos"),
                            Texto(" e o "),
                            Negrito("óleo"),
                            Texto(" até obter uma mistura homogênea."),
                        ]),
                        ItemLista([
                            Texto("Transfira a mistura para uma tigela e adicione o açúcar e a farinha."),
                        ]),
                        ItemLista([
                            Texto("Misture bem e acrescente o "),
                            Negrito("fermento"),
                            Texto(" por último."),
                        ]),
                        ItemLista([
                            Texto("Despeje na forma e asse por "),
                            Negrito("aproximadamente 40 minutos"),
                            Texto("."),
                        ]),
                    ],
                    format_options={
                        "html":     {"css_class": "passos passo-a-passo"},
                        "txt":      {"enumeration_style": "numeric"},
                        "markdown": {"ordered_marker": "1."},
                    },
                ),

                Espaco(1),
                Subtitulo("Cobertura", nivel=3),

                Lista(
                    ordenada=True,
                    children=[
                        ItemLista([Texto("Leve todos os ingredientes ao fogo baixo.")]),
                        ItemLista([Texto("Mexa até engrossar levemente.")]),
                        ItemLista([Texto("Despeje sobre o bolo ainda morno.")]),
                    ],
                ),

                Espaco(1),

                Nota(
                    [
                        Negrito("Teste do palito: "),
                        Texto("espete no centro do bolo; se sair limpo, está pronto."),
                    ],
                    tipo="warning",
                    format_options={
                        "html":     {"css_class": "nota nota-warning"},
                        "markdown": {"prefix": "> **Atenção:** "},
                        "txt":      {"label": "[ATENÇÃO]"},
                    },
                ),
            ],
        ),

        # ── Seção: Tabela nutricional (com fallbacks de tabela) ────────────────
        Secao(
            id="tabela-nutricional-aprox",
            titulo=Titulo("Informações aproximadas por fatia", nivel=2),
            children=[
                Tabela(
                    cabecalho=["Item", "Quantidade"],
                    linhas=[
                        ["Calorias",      "290 kcal"],
                        ["Carboidratos",  "42 g"],
                        ["Proteínas",     "4 g"],
                        ["Gorduras",      "12 g"],
                    ],
                    legenda="Valores aproximados, variando conforme os ingredientes usados.",
                    format_options={
                        "html":      {"css_class": "tabela-nutricional"},
                        "markdown":  {"align": ["left", "right"]},
                        "txt":       {"fallback_strategy": "columns", "min_column_width": 18},
                        "clipboard": {"fallback_strategy": "list"},
                    },
                    fallback={
                        # direct string fallbacks override everything
                        # (not set here — using strategy-based fallback above)
                    },
                ),
            ],
        ),

        # ── Seção: Imagem (com fallbacks de imagem por formato) ───────────────
        Secao(
            id="imagem-referencia",
            titulo=Titulo("Apresentação sugerida", nivel=2),
            children=[
                Imagem(
                    src="images/bolo_cenoura_fatia.jpg",
                    alt="Fatia de bolo de cenoura com cobertura de chocolate brilhante",
                    titulo="Sugestão de apresentação",
                    legenda="Sirva com café fresco.",
                    largura=640,
                    altura=420,
                    metadata={"semantic_role": "hero_image"},
                    format_options={
                        "html":      {"css_class": "img img-receita", "loading": "lazy"},
                        "markdown":  {"use_standard_image_syntax": True},
                        "txt":       {"fallback_strategy": "alt_plus_caption"},
                        "clipboard": {"fallback_strategy": "caption_only"},
                    },
                    fallback={
                        "txt":       "[Imagem: Fatia de bolo de cenoura com cobertura de chocolate brilhante. Sirva com café fresco.]",
                        "clipboard": "Sugestão de apresentação: fatia de bolo de cenoura com cobertura de chocolate brilhante. Sirva com café fresco.",
                    },
                ),
            ],
        ),

        # ── Seção: Observações finais ─────────────────────────────────────────
        Secao(
            id="observacoes-finais",
            titulo=Titulo("Observações finais", nivel=2),
            children=[
                Paragrafo([
                    Texto("Para armazenar, mantenha o bolo em recipiente fechado por até "),
                    Negrito("3 dias"),
                    Texto(" em temperatura ambiente."),
                ]),

                Paragrafo([
                    Texto("Receita adaptável para publicação em "),
                    Link("site",               url="https://exemplo.com/receitas/bolo-cenoura"),
                    Texto(", "),
                    Link("material impresso",  url="urn:export:pdf"),
                    Texto(" e "),
                    Link("compartilhamento rápido", url="urn:export:clipboard"),
                    Texto("."),
                ]),

                Citacao(
                    [Texto("Receita de família: simples, confiável e sempre funciona.")],
                    autoria="Caderno da Casa",
                    format_options={
                        "html":     {"tag": "blockquote"},
                        "markdown": {"prefix": "> "},
                        "txt":      {"indent": 4},
                    },
                ),

                Codigo(
                    linguagem="text",
                    conteudo=(
                        "Dica extra:\n"
                        "  - Massa mais leve: peneire a farinha\n"
                        "  - Cobertura mais brilhante: use fogo baixo\n"
                        "  - Mais úmido: não asse demais"
                    ),
                    format_options={
                        "markdown": {"fence": "```"},
                        "html":     {"css_class": "code-block dicas"},
                        "txt":      {"indent": 2},
                    },
                ),
            ],
        ),
    ],
)


# ═══════════════════════════════════════════════════════════════════════════════
# Renderização em múltiplos formatos
# ═══════════════════════════════════════════════════════════════════════════════

SEPARATOR = "\n" + "═" * 80 + "\n"

if __name__ == "__main__":
    formatos = ["txt", "markdown", "html", "clipboard"]

    for fmt in formatos:
        print(f"{SEPARATOR}[ {fmt.upper()} ]{SEPARATOR}")
        resultado = gerar(receita, fmt)
        print(resultado)
        print()
