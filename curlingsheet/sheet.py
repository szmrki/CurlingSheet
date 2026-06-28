# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter
from .stone import Stone, RED, YELLOW
from . import md_positions as mdp
from .spec import build_sheet_spec, SheetOptions
from .renderers.qt import render_qt


class Sheet(QWidget):
    def __init__(self, show_pochi: bool = True, show_frame: bool = True) -> None:
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
        self._show_pochi    = show_pochi
        self._show_frame    = show_frame

    def options(self) -> SheetOptions:
        return SheetOptions(show_pochi=self._show_pochi, show_frame=self._show_frame,
                            color12=self.color12, color4=self.color4)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        spec = build_sheet_spec(self.options(), self.stones)
        render_qt(spec, painter)

    @property
    def show_pochi(self) -> bool:
        return self._show_pochi

    @show_pochi.setter
    def show_pochi(self, value: bool) -> None:
        self._show_pochi = value
        self.update()

    @property
    def show_frame(self) -> bool:
        return self._show_frame

    @show_frame.setter
    def show_frame(self, value: bool) -> None:
        self._show_frame = value
        self.update()

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
        # メソッド冒頭(L66)で selected_stone が None の場合は早期returnしており、
        # ここに到達する時点では必ず Stone インスタンスである。
        assert self.selected_stone is not None
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
