# -*- coding: utf-8 -*-
"""matplotlib の Axes へシート spec を描くレンダラ。

matplotlib は必須依存ではないため、import はこの関数内で遅延して行う。
利用例::

    import matplotlib.pyplot as plt
    from curlingsheet.spec import build_sheet_spec, SheetOptions
    from curlingsheet.renderers.mpl import render_matplotlib

    fig, ax = plt.subplots()
    spec = build_sheet_spec(SheetOptions(show_pochi=False), stones)
    render_matplotlib(spec, ax)
    plt.show()
"""
from .. import geometry as g
from ..primitives import Circle, Line, Rect


def _mpl_color(c):
    if c is None:
        return "none"
    return (c.r / 255, c.g / 255, c.b / 255, c.a / 255)


def render_matplotlib(spec, ax, *, set_view: bool = True, invert_yaxis: bool = True):
    """spec を matplotlib の Axes へ描画する。

    ax           : 描画先の Axes
    set_view     : 表示範囲・アスペクト比・軸非表示をこの関数で設定するか
    invert_yaxis : 画面座標系(下向き y)に合わせて y 軸を反転するか

    戻り値は ax。
    """
    from matplotlib import patches

    for z, item in enumerate(spec):
        if isinstance(item, Rect):
            ax.add_patch(patches.Rectangle(
                (item.x, item.y), item.w, item.h,
                facecolor=_mpl_color(item.fill),
                edgecolor=_mpl_color(item.stroke),
                linewidth=item.stroke_w, zorder=z))
        elif isinstance(item, Circle):
            ax.add_patch(patches.Circle(
                (item.cx, item.cy), item.r,
                facecolor=_mpl_color(item.fill),
                edgecolor=_mpl_color(item.stroke),
                linewidth=item.stroke_w, zorder=z))
        elif isinstance(item, Line):
            ax.plot([item.x1, item.x2], [item.y1, item.y2],
                    color=_mpl_color(item.color), linewidth=item.width, zorder=z)

    if set_view:
        ax.set_xlim(0, g.SHEET_W)
        ax.set_ylim(0, g.SHEET_H)
        ax.set_aspect("equal")
        if invert_yaxis:
            ax.invert_yaxis()
        ax.axis("off")
    return ax
