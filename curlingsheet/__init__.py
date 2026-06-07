# -*- coding: utf-8 -*-
__version__ = "0.1.0"

# 描画器非依存の公開 API(PyQt6 を読み込まずに使用可能)
from .primitives import RGBA, Circle, Line, Rect, WHITE, BLACK, RED, YELLOW
from .spec import build_sheet_spec, SheetOptions

__all__ = [
    "__version__",
    "RGBA", "Circle", "Line", "Rect",
    "WHITE", "BLACK", "RED", "YELLOW",
    "build_sheet_spec", "SheetOptions",
]
