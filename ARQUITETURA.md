# docschema — Arquitetura de Geração de Documentos Multiformato

## Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura de Pastas](#estrutura-de-pastas)
3. [Padrões de Projeto](#padrões-de-projeto)
4. [Modelo Intermediário](#modelo-intermediário)
5. [Cadeia de Resolução de Configuração](#cadeia-de-resolução-de-configuração)
6. [Estratégia de Fallback](#estratégia-de-fallback)
7. [Renderizadores](#renderizadores)
8. [Motor Central](#motor-central)
9. [Exemplos de Uso](#exemplos-de-uso)
10. [Extensibilidade](#extensibilidade)
11. [Trade-offs e Decisões](#trade-offs-e-decisões)

---

## Visão Geral

O `docschema` é um sistema para definir um documento **uma única vez** e
renderizá-lo em qualquer formato de saída sem reescrever o conteúdo.

```
  Autor escreve          Motor seleciona         Formato gerado
 ┌──────────────┐       ┌──────────────────┐    ┌────────────────┐
 │  Documento   │──────▶│ DocumentEngine   │───▶│  PDF           │
 │  (modelo     │       │                  │───▶│  DOCX          │
 │   neutro)    │       │  gerar(doc, fmt) │───▶│  HTML          │
 └──────────────┘       └──────────────────┘───▶│  Markdown      │
                                                 │  TXT           │
                                                 │  Clipboard     │
                                                 └────────────────┘
```

O modelo intermediário não conhece nenhum formato de saída. Cada
renderizador converte o mesmo modelo de forma independente.

---

## Estrutura de Pastas

```
docschema/
├── __init__.py               # Exports públicos: todos os elementos + gerar()
│
├── document.py               # Documento — raiz do modelo
│
├── elements/
│   ├── __init__.py
│   ├── base.py               # Element, BlockElement, InlineElement (ABCs)
│   ├── inline.py             # Texto, Negrito, Italico, Sublinhado, Link,
│   │                         # QuebraLinha, Span, Emoji
│   └── block.py              # Titulo, Subtitulo, Paragrafo, Secao, Lista,
│                             # ItemLista, Tabela, Imagem, Espaco,
│                             # QuebraPagina, LinhaHorizontal, BlocoDestaque,
│                             # Nota, Citacao, Codigo
│
├── renderers/
│   ├── __init__.py
│   ├── base.py               # BaseRenderer (Visitor abstrato)
│   ├── txt.py                # TxtRenderer
│   ├── markdown.py           # MarkdownRenderer
│   ├── html.py               # HtmlRenderer
│   ├── clipboard.py          # ClipboardRenderer (extends TxtRenderer)
│   ├── pdf.py                # PdfRenderer (requer reportlab)
│   └── docx_renderer.py      # DocxRenderer (requer python-docx)
│
├── engine.py                 # DocumentEngine + gerar() convenience function
│
└── examples/
    ├── receita.py            # Exemplo 1 — documento declarativo completo
    └── relatorio_cliente.py  # Exemplo 2 — autoria imperativa + dados dinâmicos
```

---

## Padrões de Projeto

### Composite — hierarquia de elementos

`Secao`, `Lista`, `BlocoDestaque` e `Documento` são nós compostos. Eles
implementam `.add(child)` e mantêm `children: List[Element]`. Elementos
folha (Texto, Negrito, etc.) não têm filhos.

Isso permite árvores arbitrariamente profundas:

```
Documento
└── Secao("ingredientes")
    ├── Titulo("Ingredientes", nivel=2)
    ├── Subtitulo("Massa", nivel=3)
    ├── Lista(ordenada=False)
    │   ├── ItemLista([Texto("3 cenouras")])
    │   └── ItemLista([Texto("4 ovos")])
    └── BlocoDestaque("Substituições")
        └── Paragrafo([Texto("..."), Negrito("cacau 50%")])
```

### Visitor — despacho de renderização

Cada elemento implementa `accept(renderer)`, que chama `renderer.visit_<tipo>(self)`.
O renderizador recebe o controle sem que o elemento precise conhecer os formatos.

```python
# No elemento:
def accept(self, renderer: "BaseRenderer") -> Any:
    return renderer.visit_paragrafo(self)

# No renderizador TXT:
def visit_paragrafo(self, el: Paragrafo) -> str:
    return self.render_inline_list(el.children) + "\n"

# No renderizador HTML:
def visit_paragrafo(self, el: Paragrafo) -> str:
    css = self.resolve_option(el, "css_class", "")
    cls = f' class="{css}"' if css else ""
    return f"<p{cls}>{self.render_inline_list(el.children)}</p>"
```

Adicionar um novo formato = implementar uma nova classe com todos os métodos
`visit_*`. Adicionar um novo elemento = adicionar `visit_novo` em cada
renderizador existente.

### Strategy — renderizadores intercambiáveis

Cada renderizador é uma estratégia de saída independente com a mesma
interface (`render(doc) -> str | bytes`). O motor simplesmente seleciona
a estratégia certa e a executa.

### Registry — mapeamento formato → renderizador

`DocumentEngine` mantém um dicionário `_registry: Dict[str, Type[BaseRenderer]]`.
O registro padrão é preenchido na inicialização, mas pode ser estendido por
qualquer código externo:

```python
engine = DocumentEngine()
engine.register("latex", LatexRenderer)
resultado = gerar(doc, "latex")
```

### Template Method — resolução de configuração

`BaseRenderer.resolve_option(el, key, default)` implementa a cadeia de
prioridade em 3 níveis como um template fixo reutilizado por todos os
renderizadores.

### Façade — função `gerar()`

`gerar(doc, fmt, **kwargs)` oculta toda a inicialização do motor, seleção
do renderizador e chamada de render. Um import e uma chamada bastam.

---

## Modelo Intermediário

### Hierarquia de classes

```
Element (ABC)
├── BlockElement (ABC)           — ocupa uma linha/bloco próprio
│   ├── Titulo
│   ├── Subtitulo
│   ├── Paragrafo
│   ├── Secao                   ← nó composto
│   ├── Lista                   ← nó composto
│   ├── ItemLista
│   ├── Tabela
│   ├── Imagem
│   ├── Espaco
│   ├── QuebraPagina
│   ├── LinhaHorizontal
│   ├── BlocoDestaque           ← nó composto
│   ├── Nota
│   ├── Citacao
│   └── Codigo
│
└── InlineElement (ABC)          — vive dentro de um bloco
    ├── Texto
    ├── Negrito
    ├── Italico
    ├── Sublinhado
    ├── Link
    ├── QuebraLinha
    ├── Span
    └── Emoji
```

### Campos comuns (Element)

```python
@dataclass
class Element:
    id:             Optional[str]       = None
    metadata:       Dict[str, Any]      = field(default_factory=dict)
    format_options: Dict[str, Any]      = field(default_factory=dict)
    fallback:       Dict[str, Any]      = field(default_factory=dict)

    def accept(self, renderer) -> Any: ...           # Visitor dispatch
    def resolve_option(self, fmt, key, default): ... # lê format_options[fmt][key]
    def get_fallback_value(self, fmt): ...           # lê fallback[fmt]
```

`format_options` é um dicionário de dicionários: a chave externa é o nome
do formato, a chave interna é o nome da opção.

`fallback` guarda representações alternativas por formato. Pode ser uma
string pronta (fallback direto) ou uma string de estratégia que o
renderizador interpreta (ex: `"list"`, `"columns"`).

### Elementos de bloco — campos específicos

| Classe          | Campos principais                                       |
|-----------------|--------------------------------------------------------|
| `Titulo`        | `children: List[InlineElement]`, `nivel: int`          |
| `Paragrafo`     | `children: List[InlineElement]`, `estilo: str`         |
| `Secao`         | `titulo: Titulo`, `children: List[BlockElement]`       |
| `Lista`         | `children: List[ItemLista]`, `ordenada: bool`          |
| `ItemLista`     | `children: List[InlineElement]`                        |
| `Tabela`        | `cabecalho`, `linhas`, `legenda`                       |
| `Imagem`        | `src`, `alt`, `titulo`, `legenda`, `largura`, `altura` |
| `BlocoDestaque` | `titulo`, `children`, `tipo`                           |
| `Nota`          | `children`, `tipo` (info/warning/tip/danger)           |
| `Citacao`       | `children`, `autoria`                                  |
| `Codigo`        | `conteudo`, `linguagem`                                |

### Elementos inline — campos específicos

| Classe      | Campos principais                     |
|-------------|---------------------------------------|
| `Texto`     | `conteudo: str`                       |
| `Negrito`   | `conteudo: str \| List[InlineElement]`|
| `Link`      | `texto: str`, `url: str`              |
| `Span`      | `children: List[InlineElement]`       |
| `Emoji`     | `simbolo: str`                        |

---

## Cadeia de Resolução de Configuração

Implementada em `BaseRenderer.resolve_option()`:

```
1º  element.format_options[fmt][key]   ← máxima prioridade (elemento específico)
2º  document.format_options[fmt][key]  ← prioridade intermediária (doc global)
3º  default do renderizador            ← menor prioridade (fallback do sistema)
```

Exemplo prático:

```python
# Documento define line_width global
doc = Documento(format_options={"txt": {"line_width": 88}})

# Parágrafo sobrescreve só para ele
par = Paragrafo([...], format_options={"txt": {"line_width": 60}})

# TxtRenderer.render_inline_list() chama:
width = self.resolve_option(el, "line_width", 72)
# → para `par`: retorna 60  (elemento vence)
# → para outro Paragrafo sem format_options: retorna 88  (doc vence)
# → sem nada: retorna 72  (default do renderer)
```

---

## Estratégia de Fallback

### Por que modelo híbrido?

| Abordagem              | Vantagem                         | Desvantagem                             |
|------------------------|----------------------------------|-----------------------------------------|
| Embutido no elemento   | Portável, auto-documentado       | Mistura dado + apresentação             |
| Embutido no renderer   | Centralizado, coerente           | Acoplado ao renderer, difícil sobrescrever |
| Registry/Policy        | Ultra-flexível                   | Complexidade extra, over-engineering    |
| **Híbrido** ✓          | Flexível + coerente + simples    | Requer documentação clara               |

O modelo híbrido combina três camadas:

#### Camada 1 — Fallback direto no elemento (maior prioridade)

O autor do documento fornece a representação final pronta:

```python
Imagem(
    src="foto.jpg",
    alt="Bolo de cenoura",
    fallback={
        "txt": "[Imagem: Bolo de cenoura com cobertura de chocolate.]",
        "clipboard": "Bolo de cenoura: foto ilustrativa.",
    }
)
```

O renderer chama `el.get_fallback_value("txt")` e usa o valor diretamente,
sem executar lógica própria.

#### Camada 2 — Fallback por estratégia (formato híbrido)

O autor indica uma estratégia, o renderer a implementa:

```python
Tabela(
    ...,
    format_options={"txt": {"fallback_strategy": "columns"}},
    fallback={"clipboard": "list"},
)
```

O renderer TXT detecta `fallback_strategy == "columns"` e executa o
algoritmo de colunas ASCII. O renderer clipboard detecta `"list"` e
transforma a tabela em itens de lista.

#### Camada 3 — Fallback padrão do renderer (menor prioridade)

Quando não há fallback definido, cada `visit_*` tem comportamento sensato:

- `visit_imagem` em TXT → `[Imagem: {alt}]`
- `visit_tabela` em clipboard → lista de pares chave:valor
- `visit_quebra_pagina` em HTML → `<hr class="page-break">`
- `visit_sublinhado` em TXT → `_texto_`

Nenhum elemento é silenciosamente descartado.

---

## Renderizadores

### BaseRenderer

```python
class BaseRenderer(ABC):
    format_name: str                      # "txt", "html", etc.
    _doc: Optional[Documento]             # referência ao documento

    def render(self, doc: Documento) -> Any: ...
    def render_inline_list(self, items) -> str: ...
    def render_block_list(self, items) -> str: ...
    def resolve_option(self, el, key, default): ...  # cadeia 3 níveis
```

### TxtRenderer

Saída em texto puro com formatação ASCII.

- **Títulos**: sublinhados com `=` (nível 1) ou `-` (nível 2+)
- **Negrito/itálico**: marcadores `*texto*` e `_texto_`
- **Tabela**: colunas com `|` e separador `+-`; estratégia `columns` usa
  largura configurável
- **Imagem**: `[Imagem: {alt}]` ou fallback do elemento
- **Quebra de página**: linha de `-` ou fallback configurado
- **Nota/Destaque**: borda ASCII com label (ex: `[DICA]`)

### MarkdownRenderer

Saída em Markdown CommonMark/GFM.

- **Títulos**: `#` a `######`
- **Ênfase**: `**negrito**`, `*itálico*`, `<u>sublinhado</u>`
- **Links**: `[texto](url)`
- **Tabela**: pipe tables com alinhamento por coluna
- **Código**: fence ` ```linguagem ```
- **Citação/Nota**: `> texto`
- **Prefix configurável**: qualquer bloco pode ter `prefix` em format_options

### HtmlRenderer

Saída em HTML5 semântico.

- **Documento**: `<article>` com `class` opcional
- **Seção**: `<section>`, título como `<h2>`–`<h6>`
- **Links**: `<a href>` com `target="_blank"` opcional
- **Tabela**: `<table>` com `<thead>` / `<tbody>` / `<caption>`
- **Imagem**: `<figure>` + `<img>` + `<figcaption>`; atributos `loading`,
  `class` via format_options
- **TOC**: gerado automaticamente quando `show_toc: True` no Documento
- **`css_class`**: aplicada em qualquer elemento via format_options

### ClipboardRenderer (estende TxtRenderer)

Versão compacta para copiar/colar.

- Herda todo TxtRenderer
- Modo `compact`: sem cabeçalho do documento, sem quebras de página
- Tabela → lista de pares por padrão
- Remove ornamentos desnecessários

### PdfRenderer (requer `reportlab`)

```bash
pip install reportlab
```

- Usa `SimpleDocTemplate` + `Paragraph`, `Table`, `Image` do ReportLab
- Estilos mapeados de elementos para `ParagraphStyle`
- Retorna `filepath` (string) em vez de string de conteúdo

### DocxRenderer (requer `python-docx`)

```bash
pip install python-docx
```

- Usa `python-docx` para criar `Document` Word
- Títulos → `heading` com nível
- Listas → `ListBullet` / `ListNumber`
- Tabelas → `Table` com cabeçalho
- Retorna `filepath` (string)

---

## Motor Central

```python
class DocumentEngine:
    _registry: Dict[str, Type[BaseRenderer]]

    def register(self, fmt: str, cls: Type[BaseRenderer]) -> None: ...
    def render(self, doc: Documento, fmt: str, **kwargs) -> Any: ...

def gerar(doc: Documento, formato: str, **kwargs) -> Any:
    return DocumentEngine().render(doc, formato, **kwargs)
```

O motor instancia o renderizador, injeta o `Documento` e chama `.render()`.
Parâmetros extras (ex: `output_path`) são passados ao construtor do
renderizador via `**kwargs`.

---

## Exemplos de Uso

### API declarativa (documento como valor)

```python
from docschema import (
    Documento, Secao, Titulo, Paragrafo, Lista, ItemLista,
    Texto, Negrito, Italico, Link, gerar,
)

doc = Documento(
    titulo="Meu Documento",
    format_options={
        "html": {"show_toc": True},
        "txt": {"line_width": 80},
    },
    children=[
        Titulo([Texto("Introdução")], nivel=1),
        Paragrafo([
            Texto("Este documento foi escrito "),
            Negrito("uma única vez"),
            Texto(" e exportado em vários formatos."),
        ]),
        Lista(ordenada=False, children=[
            ItemLista([Link("Site", url="https://exemplo.com")]),
            ItemLista([Texto("Texto simples")]),
        ]),
    ]
)

txt  = gerar(doc, "txt")
md   = gerar(doc, "markdown")
html = gerar(doc, "html")
clip = gerar(doc, "clipboard")
pdf  = gerar(doc, "pdf",  output_path="saida.pdf")
docx = gerar(doc, "docx", output_path="saida.docx")
```

### API imperativa (dados dinâmicos)

```python
doc = Documento(titulo="Relatório")
doc.add(Titulo([Texto("Relatório")], nivel=1))

sec = Secao(titulo=Titulo([Texto("Dados")], nivel=2))
for item in dados:
    sec.add(Paragrafo([Texto(item["nome"]), Texto(": "), Negrito(item["valor"])]))

doc.add(sec)
resultado = gerar(doc, "markdown")
```

### Personalização por formato

```python
Paragrafo(
    [Texto("Resumo executivo")],
    format_options={
        "html":      {"css_class": "lead"},
        "markdown":  {"prefix": "> "},
        "txt":       {"uppercase": True},
        "clipboard": {},
    }
)
```

### Fallback de imagem

```python
Imagem(
    src="diagrama.png",
    alt="Fluxo de aprovação em 5 etapas",
    legenda="Figura 1 — Processo de aprovação",
    format_options={
        "html": {"css_class": "diagram", "loading": "lazy"},
    },
    fallback={
        # string direta — o renderer usa tal qual
        "txt":       "[Diagrama] Fluxo de aprovação em 5 etapas. Ver Figura 1.",
        "clipboard": "Fluxo de aprovação: 5 etapas (ver diagrama).",
    }
)
```

### Fallback de tabela

```python
Tabela(
    cabecalho=["Produto", "Preço", "Estoque"],
    linhas=[["Café", "R$ 12,00", "200"], ["Chá", "R$ 8,00", "150"]],
    format_options={
        # renderer TXT executa algoritmo de colunas com largura mínima
        "txt": {"fallback_strategy": "columns", "min_column_width": 14},
        # renderer clipboard transforma em lista de itens
        "clipboard": {"fallback_strategy": "list"},
    }
)
```

### Quebra de página com fallback por formato

```python
QuebraPagina(
    format_options={
        "html":     {"fallback": "<!-- page-break -->"},
        "markdown": {"fallback": "\n---\n"},
        "txt":      {"fallback": "\n" + ("-" * 60) + "\n"},
    }
)
# PDF/DOCX: quebra de página real
# HTML: comentário semântico
# Markdown: separador ---
# TXT: linha de hifens
```

---

## Extensibilidade

### Adicionar novo formato (ex: LaTeX)

```python
from docschema.renderers.base import BaseRenderer
from docschema.elements.block import Titulo, Paragrafo
from docschema.document import Documento

class LatexRenderer(BaseRenderer):
    format_name = "latex"

    def render(self, doc: Documento) -> str:
        body = self.render_block_list(doc.children)
        return f"\\documentclass{{article}}\n\\begin{{document}}\n{body}\\end{{document}}\n"

    def visit_titulo(self, el: Titulo) -> str:
        cmds = {1: "section", 2: "subsection", 3: "subsubsection"}
        cmd = cmds.get(el.nivel, "paragraph")
        return f"\\{cmd}{{{self.render_inline_list(el.children)}}}\n"

    def visit_paragrafo(self, el: Paragrafo) -> str:
        return self.render_inline_list(el.children) + "\n\n"

    # ... demais visit_*

# Registro
from docschema.engine import DocumentEngine
engine = DocumentEngine()
engine.register("latex", LatexRenderer)

resultado = engine.render(doc, "latex")
```

### Adicionar novo elemento inline (ex: Codigo Inline)

```python
# 1. Definir a classe
from docschema.elements.base import InlineElement

class CodigoInline(InlineElement):
    conteudo: str
    def __init__(self, conteudo: str, **kwargs):
        super().__init__(**kwargs)
        self.conteudo = conteudo
    def accept(self, renderer):
        return renderer.visit_codigo_inline(self)

# 2. Adicionar visit_codigo_inline em BaseRenderer (default)
def visit_codigo_inline(self, el: CodigoInline) -> str:
    return f"`{el.conteudo}`"

# 3. Sobrescrever nos renderers que precisam de comportamento diferente:
# TxtRenderer:
def visit_codigo_inline(self, el) -> str:
    return f"[{el.conteudo}]"

# HtmlRenderer:
def visit_codigo_inline(self, el) -> str:
    return f"<code>{el.conteudo}</code>"
```

### Adicionar novo elemento de bloco (ex: Aviso)

```python
# 1. Definir a classe
from docschema.elements.base import BlockElement

class Aviso(BlockElement):
    children: List[InlineElement]
    nivel: str  # "baixo" | "medio" | "alto"

    def accept(self, renderer):
        return renderer.visit_aviso(self)

# 2. Implementar visit_aviso em todos os renderers
# TxtRenderer:
def visit_aviso(self, el: Aviso) -> str:
    labels = {"baixo": "[INFO]", "medio": "[ATENÇÃO]", "alto": "[CRÍTICO]"}
    label = labels.get(el.nivel, "[AVISO]")
    return f"{label} {self.render_inline_list(el.children)}\n"

# HtmlRenderer:
def visit_aviso(self, el: Aviso) -> str:
    return f'<div class="aviso aviso-{el.nivel}">{self.render_inline_list(el.children)}</div>'
```

### Adicionar nova regra de fallback

Há três pontos de extensão, em ordem de prioridade:

```python
# 1. No elemento (mais específico):
minha_tabela = Tabela(..., fallback={"meu_formato": "lista"})

# 2. No renderizador (padrão do formato):
class MeuRenderer(BaseRenderer):
    def visit_tabela(self, el: Tabela) -> str:
        fb = el.get_fallback_value(self.format_name)
        if fb:
            return str(fb)
        # lógica padrão ...

# 3. Registro de fallback externo (máxima flexibilidade):
from docschema.fallback import FallbackRegistry
FallbackRegistry.register("meu_formato", Tabela, minha_funcao_fallback)
```

---

## Trade-offs e Decisões

### Por que Visitor e não método polimórfico?

Com polimorfismo direto (`el.render_txt()`), o elemento precisaria conhecer
todos os formatos. Adicionar um novo formato forçaria mudanças em todas as
classes de elemento. O Visitor inverte essa dependência: o elemento só
implementa `accept()`, e toda a lógica de saída fica no renderizador.

### Por que `dataclass` nos elementos?

- Autocomplete completo no IDE
- `__repr__` automático para debug
- `field(default_factory=dict)` evita mutabilidade compartilhada
- Fortemente tipado com `Optional`, `List`, `Dict`

### Por que `children: list` no construtor e `.add()`?

As duas APIs cobrem casos distintos:

- **`children=[...]`**: documento como valor (declarativo, imutável, ideal para
  arquivos de configuração e templates)
- **`.add()`**: construção imperativa a partir de dados dinâmicos (loops,
  condicionais, vinda de banco)

Ambas produzem o mesmo modelo intermediário.

### Por que ClipboardRenderer estende TxtRenderer?

Clipboard é TXT com restrições extras (sem cabeçalho, sem ornamentos, tabelas
sempre em lista). Reusar TxtRenderer via herança evita duplicação, e os
poucos métodos diferentes são sobrescritos. Se as diferenças crescerem muito,
pode se tornar uma subclasse com maior divergência ou uma classe independente.

### Por que PDF e DOCX retornam filepath e não string?

Esses formatos são binários. Retornar `bytes` forçaria o caller a lidar com
I/O sempre. Retornar filepath é mais ergonômico para o caso de uso mais comum
(salvar em disco). Para usar em memória, basta passar um `BytesIO` como
`output_path`.

### Quando usar fallback no elemento vs. no renderer?

| Caso                              | Onde definir              |
|-----------------------------------|---------------------------|
| Conteúdo específico do documento  | `fallback={}` no elemento |
| Regra genérica para o tipo        | `visit_*` no renderer     |
| Política reutilizável entre docs  | `FallbackRegistry`        |

O modelo híbrido maximiza flexibilidade sem criar um sistema de registro
complexo para casos simples.

---

## Dependências

| Formato   | Dependência          | Instalação                  |
|-----------|----------------------|-----------------------------|
| TXT       | nenhuma              | —                           |
| Markdown  | nenhuma              | —                           |
| HTML      | nenhuma              | —                           |
| Clipboard | nenhuma              | —                           |
| PDF       | `reportlab`          | `pip install reportlab`     |
| DOCX      | `python-docx`        | `pip install python-docx`   |

O núcleo do pacote (elementos + TXT/MD/HTML/clipboard) não tem dependências
externas. PDF e DOCX são opcionais e falham com `ImportError` amigável.
