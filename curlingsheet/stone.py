# -*- coding: utf-8 -*-
from PyQt6.QtGui import QPen, QColor

WHITE  = QColor(255, 255, 255)
BLACK  = QColor(0, 0, 0)
RED    = QColor(255, 0, 0)
YELLOW = QColor(255, 255, 0)


class Stone:
    def __init__(self, config) -> None:
        self.x      = int(config[0])
        self.y      = int(config[1])
        self.team   = config[2]
        self.radius = 9

    def draw(self, painter) -> None:
        pen = painter.pen()
        painter.setPen(QPen(BLACK, 1))
        painter.setBrush(self._color(self.team))
        painter.drawEllipse(self.x - self.radius, self.y - self.radius,
                            self.radius * 2, self.radius * 2)
        painter.setPen(pen)

    def _color(self, team) -> QColor:
        if team in (0, "red", RED):
            return RED
        elif team in (1, "yellow", YELLOW):
            return YELLOW

    def contains(self, px, py) -> bool:
        dx = px - self.x
        dy = py - self.y
        return dx * dx + dy * dy <= self.radius * self.radius
