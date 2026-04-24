# -*- coding: utf-8 -*-
import sys
import os
from importlib.resources import files


def resource_path(filename: str) -> str:
    """アイコン等のリソースファイルへのパスを返す。
    PyInstaller (_MEIPASS) とインストール済みパッケージの両方に対応。"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    ref = files('curlingsheet')
    for part in filename.replace('\\', '/').split('/'):
        ref = ref.joinpath(part)
    return str(ref)
