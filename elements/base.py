"""
docschema.elements.base
========================
Abstract base classes for all document elements.

Design patterns:
  - Composite   : BlockElement can contain other BlockElements
  - Visitor     : accept(renderer) dispatches to the renderer's visit_* method
  - Template    : resolve_option() implements the 3-level config chain
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from docschema.renderers.base import BaseRenderer

# ── Type aliases ─────────────────────────────────────────────────────────────

FormatOptions = Dict[str, Dict[str, Any]]   # {"html": {"css_class": "..."}, ...}
Metadata      = Dict[str, Any]              # arbitrary key/value annotations
FallbackMap   = Dict[str, Any]              # format_name -> fallback string/strategy
InlineContent = List["InlineElement"]
BlockContent  = List["BlockElement"]


# ── Base ─────────────────────────────────────────────────────────────────────

class Element(ABC):
    """
    Root of every document element.

    Config resolution order (highest → lowest priority):
        1. element.format_options[fmt][key]
        2. document.format_options[fmt][key]   (injected by renderer)
        3. renderer hard-coded default
    """

    def __init__(
        self,
        *,
        metadata:       Optional[Metadata]      = None,
        format_options: Optional[FormatOptions] = None,
        fallback:       Optional[FallbackMap]   = None,
    ) -> None:
        self.metadata:       Metadata      = metadata       or {}
        self.format_options: FormatOptions = format_options or {}
        self.fallback:       FallbackMap   = fallback       or {}

    # ── Config helpers ────────────────────────────────────────────────────────

    def get_format_option(self, fmt: str, key: str, default: Any = None) -> Any:
        """Return element-level format option or *default*."""
        return self.format_options.get(fmt, {}).get(key, default)

    def has_fallback(self, fmt: str) -> bool:
        return fmt in self.fallback

    def get_fallback_value(self, fmt: str) -> Optional[Any]:
        return self.fallback.get(fmt)

    # ── Visitor ───────────────────────────────────────────────────────────────

    @abstractmethod
    def accept(self, renderer: "BaseRenderer") -> Any:
        """Dispatch to the correct visit_* method on *renderer*."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class BlockElement(Element, ABC):
    """Block-level element (paragraph, section, table, …)."""


class InlineElement(Element, ABC):
    """Inline element (text, bold, link, …)."""
