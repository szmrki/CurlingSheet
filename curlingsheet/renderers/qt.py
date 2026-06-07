# -*- coding: utf-8 -*-
"""PyQt6 の QPainter でシート spec を描くレンダラ。

円・ラインの座標は従来 ``paintEvent`` / ``painter.py`` が行っていた
整数演算(直径//2 による左上算出)をそのまま再現するため、
描画結果は従来とピクセル単位で一致する。
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPen

from ..primitives import Circle, Line, Rect


def _qcolor(c) -> "QColor | None":
    return None if c is None else QColor(c.r, c.g, c.b, c.a)


def _set_pen(painter, color, width) -> None:
    if color is None:
        painter.setPen(Qt.PenStyle.NoPen)
    else:
        painter.setPen(QPen(_qcolor(color), width))


def _set_brush(painter, fill) -> None:
    if fill is None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
    else:
        painter.setBrush(QBrush(_qcolor(fill)))


def _draw_rect(item: Rect, painter) -> None:
    _set_pen(painter, item.stroke, item.stroke_w)
    _set_brush(painter, item.fill)
    painter.drawRect(round(item.x), round(item.y), round(item.w), round(item.h))


def _draw_circle(item: Circle, painter) -> None:
    _set_pen(painter, item.stroke, item.stroke_w)
    _set_brush(painter, item.fill)
    # 従来の drawEllipse(cx - diameter//2, cy - diameter//2, diameter, diameter) を再現
    d = round(item.r * 2)
    rad = d // 2
    left = round(item.cx) - rad
    top = round(item.cy) - rad
    painter.drawEllipse(left, top, d, d)


def _draw_line(item: Line, painter) -> None:
    _set_pen(painter, item.color, item.width)
    painter.drawLine(round(item.x1), round(item.y1), round(item.x2), round(item.y2))


def render_qt(spec, painter) -> None:
    """spec(プリミティブのリスト)を QPainter で描画する。"""
    for item in spec:
        if isinstance(item, Rect):
            _draw_rect(item, painter)
        elif isinstance(item, Circle):
            _draw_circle(item, painter)
        elif isinstance(item, Line):
            _draw_line(item, painter)
