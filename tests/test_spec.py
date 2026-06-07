# -*- coding: utf-8 -*-
"""spec 層のテスト(PyQt6 非依存・高速)。"""
from collections import Counter

from curlingsheet import build_sheet_spec, SheetOptions, Circle, RED, YELLOW


def _counts(spec):
    return Counter(type(p).__name__ for p in spec)


def test_default_counts():
    c = _counts(build_sheet_spec(SheetOptions()))
    assert c["Circle"] == 13   # ハウス4 + ポチ9
    assert c["Line"] == 4      # センター/バック/ティー/ホグ
    assert c["Rect"] == 2      # 背景 + 外枠


def test_all_toggles_off():
    spec = build_sheet_spec(SheetOptions(show_pochi=False, show_frame=False,
                                         show_background=False))
    c = _counts(spec)
    assert c["Circle"] == 4    # ハウスのみ
    assert c["Line"] == 4
    assert c.get("Rect", 0) == 0


def test_pochi_toggle():
    on = _counts(build_sheet_spec(SheetOptions(show_pochi=True)))["Circle"]
    off = _counts(build_sheet_spec(SheetOptions(show_pochi=False)))["Circle"]
    assert on - off == 9       # ポチは9個


def test_default_omitted_equals_default_options():
    assert build_sheet_spec() == build_sheet_spec(SheetOptions())


def test_stone_team_colors():
    class S:
        def __init__(self, x, y, team):
            self.x, self.y, self.team = x, y, team

    spec = build_sheet_spec(SheetOptions(), [S(0, 0, "red"), S(0, 0, 1)])
    stones = [p for p in spec if isinstance(p, Circle)][-2:]
    assert stones[0].fill == RED
    assert stones[1].fill == YELLOW
