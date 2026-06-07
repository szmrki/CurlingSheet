# -*- coding: utf-8 -*-
"""matplotlib レンダラのスモークテスト(未インストールなら skip)。"""
import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")


def test_render_matplotlib_smoke():
    import matplotlib.pyplot as plt

    from curlingsheet import build_sheet_spec, SheetOptions
    from curlingsheet.renderers.mpl import render_matplotlib

    class S:
        def __init__(self, x, y, team):
            self.x, self.y, self.team = x, y, team

    spec = build_sheet_spec(SheetOptions(show_pochi=False),
                            [S(149, 159, "red"), S(120, 300, "yellow")])
    fig, ax = plt.subplots()
    render_matplotlib(spec, ax)

    assert len(ax.patches) >= 5   # 背景1 + ハウス4
    assert len(ax.lines) == 4
    plt.close(fig)
