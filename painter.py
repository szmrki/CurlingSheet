# -*- coding: utf-8 -*-
from PyQt6.QtGui import QPainter, QBrush, QColor
from stone import BLACK, WHITE


class QPainter2(QPainter):
    def drawHouse(self, center_x, center_y, color12, color4) -> None:
        house_sizes = [
            (239, self._house_color(color12)),
            (159, WHITE),
            (79,  self._house_color(color4)),
            (25,  WHITE),
        ]
        for diameter, color in house_sizes:
            radius = diameter // 2
            self.setBrush(QBrush(color))
            self.drawEllipse(center_x - radius, center_y - radius, diameter, diameter)

    def drawPochi(self, x, y) -> None:
        diameter = 4
        radius = diameter // 2
        self.setBrush(QBrush(BLACK))
        self.drawEllipse(x - radius, y - radius, diameter, diameter)

    def _house_color(self, idx) -> QColor:
        colors = {
            0: QColor(255, 0, 0, 80),
            1: QColor(0, 0, 255, 80),
            2: QColor(0, 64, 0, 80),
        }
        return colors.get(idx, QColor(0, 0, 0, 0))
