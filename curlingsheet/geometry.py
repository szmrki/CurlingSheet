# -*- coding: utf-8 -*-
"""シートの描画寸法を一元管理するモジュール。

これまで ``sheet.paintEvent`` と ``painter.py`` に散在していた寸法
(外枠・各ライン・ハウスの同心円・MD ポイント等)をここへ集約した。
中心線やハウス中心の座標は ``md_positions`` を単一の出典とする。
"""
from .md_positions import CENTER_X

# シート全体のサイズ(QWidget の固定サイズと一致)
SHEET_W = 300
SHEET_H = 600

# 外枠(QPainter.drawRect と同じ left, top, w, h)
FRAME = (0, 0, 299, 599)

# 各ラインの y 座標
BACK_LINE_Y = 40        # バックライン
TEE_LINE_Y = 159     # ティーライン(= ハウス中心 y)
HOG_LINE_Y = 580        # ホグライン
LINE_X_END = 299        # 横ラインの右端

# ハウスの同心円。(直径, 色キー) の外側→内側順。
# 色キー: "c12"=12フィート色, "white"=白, "c4"=4フィート色
HOUSE_RINGS = [
    (239, "c12"),
    (159, "white"),
    (79,  "c4"),
    (25,  "white"),
]

# MD ポイント(ポチ)
POCHI_DIAMETER = 4
POCHI_POSITIONS = [
    (CENTER_X,    370), (CENTER_X - 72, 370), (CENTER_X + 72, 370),
    (CENTER_X,    430), (CENTER_X - 70, 430), (CENTER_X + 70, 430),
    (CENTER_X,    490), (CENTER_X - 68, 490), (CENTER_X + 68, 490),
]

# ストーンの半径
STONE_RADIUS = 9
