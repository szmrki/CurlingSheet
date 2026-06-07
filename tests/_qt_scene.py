# -*- coding: utf-8 -*-
"""パリティテスト用の固定シーンを Qt で描画するヘルパー。

参照PNGの生成(tests/data/reference_default.png)と、テストでの再描画の
両方がこの関数を使うことで、シーン定義のズレを防ぐ。pytest には収集
されないよう、ファイル名は ``_`` 始まり・関数名も ``test_`` 以外にする。
"""
import os

# 画面なしで描画する(import より前に設定が必要)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class _Stone:
    def __init__(self, x, y, team):
        self.x, self.y, self.team = x, y, team


# 参照画像に含める固定のストーン配置
SCENE_STONES = [
    _Stone(149, 159, "red"),    # ハウス中心
    _Stone(100, 300, 1),        # 黄(int 指定)
    _Stone(200, 450, 0),        # 赤(int 指定)
]


def render_reference_image():
    """固定シーンを QImage(ARGB32, 300x600)に描画して返す。"""
    from PyQt6.QtGui import QImage, QPainter
    from PyQt6.QtWidgets import QApplication

    from curlingsheet.spec import build_sheet_spec, SheetOptions
    from curlingsheet.renderers.qt import render_qt

    QApplication.instance() or QApplication([])

    image = QImage(300, 600, QImage.Format.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    render_qt(build_sheet_spec(SheetOptions(), SCENE_STONES), painter)
    painter.end()
    return image


def image_bytes(image):
    """QImage を RGBA8888 に正規化してバイト列で返す(比較用)。"""
    from PyQt6.QtGui import QImage

    rgba = image.convertToFormat(QImage.Format.Format_RGBA8888)
    buf = rgba.bits()
    buf.setsize(rgba.sizeInBytes())
    return bytes(buf)
