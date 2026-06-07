# -*- coding: utf-8 -*-
"""描画器に依存しない図形プリミティブ。

このモジュールは PyQt6 や matplotlib などの特定の描画ライブラリに依存しない。
``spec.build_sheet_spec`` がここで定義された図形のリストを生成し、
各レンダラ(``renderers.qt`` / ``renderers.mpl`` / 利用者独自の描画器)が
それを消費して実際に描画する。

座標系は画面座標系(原点は左上、y は下向き)。単位は px。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RGBA:
    """0-255 の RGBA 色。"""
    r: int
    g: int
    b: int
    a: int = 255


@dataclass(frozen=True)
class Circle:
    """中心 (cx, cy)、半径 r の円。

    fill / stroke が None の場合はそれぞれ塗り / 枠線を描かない。
    """
    cx: float
    cy: float
    r: float
    fill: "RGBA | None" = None
    stroke: "RGBA | None" = None
    stroke_w: float = 1


@dataclass(frozen=True)
class Line:
    """(x1, y1) から (x2, y2) への直線。"""
    x1: float
    y1: float
    x2: float
    y2: float
    color: "RGBA | None" = None
    width: float = 1


@dataclass(frozen=True)
class Rect:
    """左上 (x, y)、幅 w、高さ h の矩形。"""
    x: float
    y: float
    w: float
    h: float
    fill: "RGBA | None" = None
    stroke: "RGBA | None" = None
    stroke_w: float = 1


# よく使う色
WHITE = RGBA(255, 255, 255)
BLACK = RGBA(0, 0, 0)
RED = RGBA(255, 0, 0)
YELLOW = RGBA(255, 255, 0)
