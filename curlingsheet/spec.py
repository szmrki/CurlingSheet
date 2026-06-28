# -*- coding: utf-8 -*-
"""シートを描画器非依存のプリミティブ列へ変換する層。

``build_sheet_spec`` はオプションとストーン列から ``primitives`` の
図形リストを生成する。生成されたリストは PyQt6 でも matplotlib でも、
あるいは利用者独自の描画器でも消費できる(``primitives`` 参照)。

このモジュールは PyQt6 に依存しないため、Qt を読み込まずに
レイアウトの生成・検査・他ライブラリでの描画が可能。
"""
from dataclasses import dataclass

from . import geometry as g
from .primitives import Circle, Line, Rect, RGBA, WHITE, BLACK, RED, YELLOW

# ハウスの色インデックス -> RGBA(半透明)
_HOUSE_COLORS = {
    0: RGBA(255, 0,   0,   80),
    1: RGBA(0,   0,   255, 80),
    2: RGBA(0,   64,  0,   80),
}


def _house_color(idx) -> RGBA:
    return _HOUSE_COLORS.get(idx, RGBA(0, 0, 0, 0))


def _team_color(team) -> "RGBA | None":
    """ストーンの team 値(0/"red"/1/"yellow" 等)を塗り色へ解決する。"""
    if team in (0, "red"):
        return RED
    if team in (1, "yellow"):
        return YELLOW
    return None


@dataclass
class SheetOptions:
    """シート描画のオプション。

    show_pochi      : MD ポイント(ポチ)を描くか
    show_frame      : 外枠を描くか
    show_background : 背景(白塗り)を描くか
    color12         : 12 フィートサークルの色インデックス
    color4          : 4 フィートサークルの色インデックス
    """
    show_pochi: bool = True
    show_frame: bool = True
    show_background: bool = True
    color12: int = 2
    color4: int = 0


def _house_items(color12, color4) -> list:
    cx, cy = g.CENTER_X, g.TEE_LINE_Y
    palette = {"c12": _house_color(color12), "white": WHITE, "c4": _house_color(color4)}
    return [
        Circle(cx, cy, diameter / 2, fill=palette[key], stroke=BLACK, stroke_w=1)
        for diameter, key in g.HOUSE_RINGS
    ]


def _line_items() -> list:
    cx = g.CENTER_X
    return [
        Line(cx, 0, cx, g.SHEET_H, BLACK, 1),                            # センターライン
        Line(0, g.BACK_LINE_Y, g.LINE_X_END, g.BACK_LINE_Y, BLACK, 1),   # バックライン
        Line(0, g.TEE_LINE_Y, g.LINE_X_END, g.TEE_LINE_Y, BLACK, 1),     # ティーライン
        Line(0, g.HOG_LINE_Y, g.LINE_X_END, g.HOG_LINE_Y, BLACK, 1),     # ホグライン
    ]


def _pochi_items() -> list:
    r = g.POCHI_DIAMETER / 2
    return [
        Circle(x, y, r, fill=BLACK, stroke=BLACK, stroke_w=1)
        for x, y in g.POCHI_POSITIONS
    ]


def _stone_item(stone) -> Circle:
    """x / y / team(と任意で radius)属性を持つストーンを円へ変換する。"""
    radius = getattr(stone, "radius", g.STONE_RADIUS)
    return Circle(stone.x, stone.y, radius,
                  fill=_team_color(stone.team), stroke=BLACK, stroke_w=1)


def build_sheet_spec(options: "SheetOptions | None" = None, stones=()) -> list:
    """シート全体を描画プリミティブのリストへ変換する。

    options : SheetOptions(None ならデフォルト)
    stones  : x / y / team 属性を持つストーンの反復可能オブジェクト

    戻り値のリストは描画順(背景→外枠→ハウス→ライン→ポチ→ストーン)。
    """
    o = options or SheetOptions()
    items: list = []

    if o.show_background:
        items.append(Rect(0, 0, g.SHEET_W, g.SHEET_H, fill=WHITE))
    if o.show_frame:
        x, y, w, h = g.FRAME
        items.append(Rect(x, y, w, h, stroke=BLACK, stroke_w=1))

    items += _house_items(o.color12, o.color4)
    items += _line_items()
    if o.show_pochi:
        items += _pochi_items()
    items += [_stone_item(s) for s in stones]
    return items
