"""
docschema.engine  (v2)
========================
DocumentEngine — Registry + Strategy dispatcher.

v2 additions:
  - gerar_stream()  → Generator[str|bytes]
  - contexto kwarg  → passes context to renderer for Se/Para/Variavel
  - output_path accepts BytesIO for PDF/DOCX
  - gerar_bytes()   → convenience for PDF/DOCX as BytesIO

Usage:
    from docschema import gerar, gerar_stream, gerar_bytes

    # Standard
    txt  = gerar(doc, "txt")
    html = gerar(doc, "html")
    gerar(doc, "pdf", output_path="report.pdf")

    # With render context (for Se/Para/Variavel)
    html = gerar(doc, "html", contexto={"empresa": "Acme", "ativo": True})

    # Streaming
    for chunk in gerar_stream(doc, "html"):
        print(chunk, end="", flush=True)

    # BytesIO output (PDF/DOCX)
    import io
    buf = gerar_bytes(doc, "pdf")        # returns io.BytesIO
    with open("out.pdf", "wb") as f:
        f.write(buf.getvalue())
"""
from __future__ import annotations

import io
from typing import Any, Dict, Generator, Optional, Type

from docschema.document import Documento
from docschema.renderers.base import BaseRenderer


class DocumentEngine:
    """
    Central document rendering engine.

    Maintains a registry of { format_name → RendererClass }.
    New renderers can be added at runtime with .register().
    """

    def __init__(self) -> None:
        self._registry: Dict[str, Type[BaseRenderer]] = {}
        self._register_defaults()

    # ── Registry ──────────────────────────────────────────────────────────────

    def register(self, format_name: str, renderer_class: Type[BaseRenderer]) -> None:
        self._registry[format_name.lower()] = renderer_class

    def _register_defaults(self) -> None:
        from docschema.renderers.txt       import TxtRenderer
        from docschema.renderers.markdown  import MarkdownRenderer
        from docschema.renderers.html      import HtmlRenderer
        from docschema.renderers.clipboard import ClipboardRenderer

        self.register("txt",       TxtRenderer)
        self.register("text",      TxtRenderer)
        self.register("markdown",  MarkdownRenderer)
        self.register("md",        MarkdownRenderer)
        self.register("html",      HtmlRenderer)
        self.register("clipboard", ClipboardRenderer)
        self.register("string",    ClipboardRenderer)

        try:
            from docschema.renderers.pdf import PdfRenderer
            self.register("pdf", PdfRenderer)
        except (ImportError, Exception):
            pass

        try:
            from docschema.renderers.docx_renderer import DocxRenderer
            self.register("docx", DocxRenderer)
        except (ImportError, Exception):
            pass

    @property
    def formatos_disponiveis(self) -> list:
        return sorted(self._registry.keys())

    def get_renderer_class(self, formato: str) -> Type[BaseRenderer]:
        fmt = formato.lower()
        if fmt not in self._registry:
            available = ", ".join(self.formatos_disponiveis)
            raise ValueError(f"Formato desconhecido: '{fmt}'.\nDisponíveis: {available}")
        return self._registry[fmt]

    # ── Rendering ─────────────────────────────────────────────────────────────

    def gerar(
        self,
        documento: Documento,
        formato: str,
        contexto: Optional[Dict[str, Any]] = None,
        **renderer_kwargs: Any,
    ) -> Any:
        """
        Render documento to formato.

        contexto: dict passed to renderer for Se/Para/Variavel resolution.
        Extra kwargs forwarded to renderer constructor (e.g. output_path).
        """
        if contexto:
            documento._render_context = contexto
        renderer_class = self.get_renderer_class(formato)
        renderer       = renderer_class(**renderer_kwargs)
        result         = documento.accept(renderer)
        if contexto:
            try:
                del documento._render_context
            except AttributeError:
                pass
        return result

    def gerar_stream(
        self,
        documento: Documento,
        formato: str,
        contexto: Optional[Dict[str, Any]] = None,
        **renderer_kwargs: Any,
    ) -> Generator:
        """
        Stream render documento to formato.
        Yields str chunks for text formats, bytes chunks for binary formats.
        """
        if contexto:
            documento._render_context = contexto
        renderer_class = self.get_renderer_class(formato)
        renderer       = renderer_class(**renderer_kwargs)
        yield from renderer.render_document_stream(documento)
        if contexto:
            try:
                del documento._render_context
            except AttributeError:
                pass

    def gerar_bytes(
        self,
        documento: Documento,
        formato: str,
        contexto: Optional[Dict[str, Any]] = None,
    ) -> io.BytesIO:
        """
        Render to an in-memory BytesIO buffer.
        Primarily for PDF and DOCX formats.
        Returns an io.BytesIO (seeked to position 0).
        """
        buf = io.BytesIO()
        self.gerar(documento, formato, contexto=contexto, output_path=buf)
        buf.seek(0)
        return buf


# ── Module-level convenience ──────────────────────────────────────────────────

engine = DocumentEngine()


def gerar(
    documento: Documento,
    formato: str,
    contexto: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Any:
    """
    Render documento to formato.

    Examples:
        gerar(doc, "txt")
        gerar(doc, "html", contexto={"empresa": "Acme"})
        gerar(doc, "pdf", output_path="report.pdf")
        gerar(doc, "docx", output_path=io.BytesIO())
    """
    return engine.gerar(documento, formato, contexto=contexto, **kwargs)


def gerar_stream(
    documento: Documento,
    formato: str,
    contexto: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Generator:
    """
    Stream render documento to formato.

    Examples:
        for chunk in gerar_stream(doc, "html"):
            sys.stdout.write(chunk)

        # Collect all chunks:
        content = "".join(gerar_stream(doc, "txt"))
    """
    yield from engine.gerar_stream(documento, formato, contexto=contexto, **kwargs)


def gerar_bytes(
    documento: Documento,
    formato: str,
    contexto: Optional[Dict[str, Any]] = None,
) -> io.BytesIO:
    """
    Render to BytesIO — mainly for PDF/DOCX.

    Example:
        buf = gerar_bytes(doc, "pdf")
        response.write(buf.read())    # HTTP streaming
        buf.seek(0); upload(buf)      # Cloud storage
    """
    return engine.gerar_bytes(documento, formato, contexto=contexto)
