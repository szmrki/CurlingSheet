# -*- coding: utf-8 -*-
"""Qt レンダラの描画が参照PNGと一致することを確認する(案B: スナップショット)。

参照画像 tests/data/reference_default.png は意図的な描画変更があったときだけ
更新する。更新方法はファイル下部の __main__ を参照。
"""
from pathlib import Path

import pytest

pytest.importorskip("PyQt6")

from tests._qt_scene import render_reference_image, image_bytes  # noqa: E402

REFERENCE = Path(__file__).parent / "data" / "reference_default.png"


def test_render_matches_reference():
    assert REFERENCE.exists(), (
        f"参照画像がありません: {REFERENCE}. "
        "python -m tests.test_qt_parity で生成してください。"
    )
    from PyQt6.QtGui import QImage

    current = render_reference_image()
    reference = QImage(str(REFERENCE))
    assert not reference.isNull(), "参照画像の読み込みに失敗しました"
    assert image_bytes(current) == image_bytes(reference)


if __name__ == "__main__":
    # 参照画像を(再)生成する: python -m tests.test_qt_parity
    REFERENCE.parent.mkdir(parents=True, exist_ok=True)
    render_reference_image().save(str(REFERENCE))
    print(f"wrote {REFERENCE}")
