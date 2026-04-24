# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPen
from .stone import Stone, WHITE, BLACK, RED, YELLOW
from .painter import QPainter2
from . import md_positions as mdp


class Sheet(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(300, 600)
        self.color12        = 2
        self.color4         = 0
        self.stones         = []
        self.is_MD          = False
        self.is_PPL         = False
        self.is_PPR         = False
        self.md_place       = 5
        self.f              = 1
        self.l              = 0
        self.selected_stone = None

    def paintEvent(self, event) -> None:
        painter = QPainter2(self)
        painter.fillRect(self.rect(), WHITE)
        painter.setPen(QPen(BLACK, 1))
        painter.drawRect(0, 0, 299, 599)

        cx = mdp.CENTER_X
        painter.drawHouse(cx, mdp.HOUSEY, self.color12, self.color4)

        painter.drawLine(cx, 0,   cx,  600)                    # センターライン
        painter.drawLine(0,  40,  299, 40)                     # バックライン
        painter.drawLine(0,  mdp.HOUSEY, 299, mdp.HOUSEY)      # ティーライン
        painter.drawLine(0,  580, 299, 580)                    # ホグライン

        for x, y in [(cx, 370), (cx-72, 370), (cx+72, 370),
                     (cx, 430), (cx-70, 430), (cx+70, 430),
                     (cx, 490), (cx-68, 490), (cx+68, 490)]:
            painter.drawPochi(x, y)

        for stone in self.stones:
            stone.draw(painter)

    def mousePressEvent(self, event) -> None:
        px = event.position().x()
        py = event.position().y()
        self.selected_stone = None
        for stone in reversed(self.stones):
            if stone.contains(px, py):
                self.selected_stone = stone
                self.offset_x = stone.x - int(px)
                self.offset_y = stone.y - int(py)
                break

    def mouseMoveEvent(self, event) -> None:
        if not self.selected_stone:
            return
        px    = event.position().x()
        py    = event.position().y()
        new_x = int(px) + self.offset_x
        new_y = int(py) + self.offset_y
        r     = self.selected_stone.radius
        w, h  = self.width(), self.height()
        new_x = max(r, min(new_x, w - r))
        new_y = max(r, min(new_y, h - r))
        self.check_stone_overlap(new_x, new_y, r, w, h)
        self.update()

    def mouseReleaseEvent(self, event) -> None:
        if self.selected_stone:
            r = self.selected_stone.radius
            if self.selected_stone.x in (r, self.width() - r):
                self.stones.remove(self.selected_stone)
                self.update()
            self.selected_stone = None

    def check_stone_overlap(self, new_x, new_y, r, w, h) -> None:
        lcount = 0
        for _ in range(100):
            overlap_found = False
            for stone in reversed(self.stones):
                if stone == self.selected_stone:
                    continue
                dx   = new_x - stone.x
                dy   = new_y - stone.y
                dist = (dx**2 + dy**2) ** 0.5
                min_dist = r + stone.radius
                if dist < min_dist:
                    overlap_found = True
                    if dist == 0:
                        tmp_x = stone.x + min_dist
                        if tmp_x <= w - r:
                            dx = min_dist
                        else:
                            lcount += 1
                            dx = -min_dist * lcount
                        dy   = 0
                        dist = min_dist
                    new_x = int(stone.x + dx / dist * min_dist)
                    new_y = int(stone.y + dy / dist * min_dist)
                    new_x = max(r, min(new_x, w - r))
                    new_y = max(r, min(new_y, h - r))
            if not overlap_found:
                break
        self.selected_stone.x = new_x
        self.selected_stone.y = new_y

    def add_stone(self, stones_list) -> None:
        for stone in stones_list:
            over = tuple(n >= self.max_stones() for n in self.count_stones())
            if all(over):
                break
            elif any(over):
                idx = [i for i, v in enumerate(over) if not v][0]
                if stone[2] == idx:
                    self.stones.append(Stone(stone))
            else:
                self.stones.append(Stone(stone))
        self.update()

    def clear_stones(self) -> None:
        self.stones.clear()
        self.update()

    def count_stones(self) -> tuple[int, int]:
        team0 = sum(1 for s in self.stones if s.team in (0, "red",    RED))
        team1 = sum(1 for s in self.stones if s.team in (1, "yellow", YELLOW))
        return team0, team1

    def max_stones(self) -> int:
        return 6 if self.is_MD else 8

    def init_MD(self) -> None:
        self.clear_stones()
        self.add_stone(mdp.get_md_stones(self.md_place, self.is_PPL, self.is_PPR,
                                         self.f, self.l))
        self.update()
