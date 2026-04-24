# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout,
                              QHBoxLayout, QComboBox, QLabel)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from .resources import resource_path

icon_path = resource_path("icon/icon.ico")


class ColorDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__()
        self.setWindowTitle("ハウスの色の変更")
        self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(300, 120)

        layout = QVBoxLayout()
        layout12, self.combo12 = self._combo_layout("12-foot color", parent.sheet.color12)
        layout4,  self.combo4  = self._combo_layout("4-foot color",  parent.sheet.color4)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)

        layout.addLayout(layout12)
        layout.addLayout(layout4)
        layout.addWidget(buttons, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        geom = parent.geometry()
        self.move(geom.x() + (geom.width()  - self.width())  // 2,
                  geom.y() + (geom.height() - self.height()) // 2)

    def _combo_layout(self, label_name: str, default: int) -> tuple:
        label = QLabel(label_name)
        combo = QComboBox()
        combo.addItems(["赤", "青", "緑"])
        combo.setCurrentIndex(default)
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(combo)
        return layout, combo
