# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QMouseEvent

WHITE = QColor(255,255,255)
BLACK = QColor(0,0,0)
RED = QColor(255,0,0)
YELLOW = QColor(255,255,0)

class Stone:
    def __init__(self, config) -> None:
        self.x = int(config[0])
        self.y = int(config[1])
        self.team = config[2]
        self.radius = 9
    
    def draw(self, painter) -> None:
        pen = painter.pen()
        painter.setPen(QPen(BLACK, 1))
        painter.setBrush(self.__color(self.team))
        painter.drawEllipse(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)
        painter.setPen(pen) #ペン設定を元に戻す

    def __color(self, team) -> None:
        if team in (0, "red", RED):
            return RED
        elif team in(1, "yellow", YELLOW):
            return YELLOW
        else: pass

    def contains(self, px, py) -> bool:
        # マウス座標(px, py)がこのストーンの中にあるか判定
        dx = px - self.x
        dy = py - self.y
        return dx * dx + dy * dy <= self.radius * self.radius

#QPainterにメソッドを追加
class QPainter2(QPainter):
    def drawHouse(self, center_x, center_y, color12, color4) -> None:
        # 円サイズ（直径）
        ft12 = self.__setcolor(color12)
        ft4 = self.__setcolor(color4)
        house_sizes = [
            (239, ft12),   # 12ft 外円
            (159, WHITE),     # 8ft
            (79, ft4),   # 4ft
            (25, WHITE)      # ボタン
        ]

        for diameter, color in house_sizes:
            radius = diameter // 2
            self.setBrush(QBrush(color))
            self.drawEllipse(center_x - radius, center_y - radius, diameter, diameter)
    
    def drawPochi(self, x, y) -> None:
        diameter = 4; radius = diameter // 2
        self.setBrush(QBrush(BLACK))
        self.drawEllipse(x - radius, y - radius, diameter, diameter)

    def __setcolor(self, idx) -> QColor:
        if idx == 0:
            return QColor(255, 0, 0, 80)
        elif idx == 1:
            return QColor(0, 0, 255, 80)
        elif idx == 2:
            return QColor(0, 64, 0, 80)
        else: pass

class Sheet(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(300, 600)
        self.color12 = 2 #緑　1が青
        self.color4 = 0 #赤
        self.stones = [] #ストーンを格納するリスト
        self.is_MD = False #ルール変更
        self.is_PPL = False
        self.is_PPR = False
        self.md_place = 5

    def paintEvent(self, event) -> None:
        painter = QPainter2(self)

        #背景
        painter.fillRect(self.rect(), WHITE)
        #基本のペン
        line_pen = QPen(BLACK, 1)
        painter.setPen(line_pen)
        # 外枠
        painter.drawRect(0, 0, 299, 599)

        # === ハウスの描画 ===
        center_x = 149
        center_y = 159
        painter.drawHouse(center_x, center_y, self.color12, self.color4)
    
        # センターライン
        painter.drawLine(149, 0, 149, 600)
        # バックライン
        painter.drawLine(0, 40, 299, 40)
        # ティーライン
        painter.drawLine(0, 159, 299, 159)
        # ホグライン
        painter.drawLine(0, 580, 299, 580)

        #3ぽち
        painter.drawPochi(center_x, 370)
        painter.drawPochi(center_x-72, 370)
        painter.drawPochi(center_x+72, 370)

        #2ぽち
        painter.drawPochi(center_x, 430)
        painter.drawPochi(center_x-70, 430)
        painter.drawPochi(center_x+70, 430)

        #1ぽち
        painter.drawPochi(center_x, 490)
        painter.drawPochi(center_x-68, 490)
        painter.drawPochi(center_x+68, 490)

        for stone in self.stones:
            stone.draw(painter)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        px = event.position().x()
        py = event.position().y()
        self.selected_stone = None
        for stone in reversed(self.stones):
            if stone.contains(px,py):
                self.selected_stone = stone
                self.offset_x = stone.x - int(px)
                self.offset_y = stone.y - int(py)
                break
            
    def mouseMoveEvent(self, event: QMouseEvent) -> None: 
        px = event.position().x()
        py = event.position().y()
        if self.selected_stone:
            new_x = int(px) + self.offset_x
            new_y = int(py) + self.offset_y

            r = self.selected_stone.radius
            w = self.width(); h = self.height()

            #xy座標の範囲制限
            new_x = max(r, min(new_x, w-r))
            new_y = max(r, min(new_y,h-r))

            # ストーンの重なりを防ぐチェック
            self.check_stone_overlap(new_x, new_y, r,w,h)
        
            self.update()
        else: pass

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.selected_stone:
            r = self.selected_stone.radius
            w = self.width()
            if self.selected_stone.x in (r, w - r): #サイドの壁に当たっていたら消す
                self.stones.remove(self.selected_stone)
                self.update()
            self.selected_stone = None

    def check_stone_overlap(self, new_x, new_y, r, w, h) -> None:
        MAX_ITER = 100; lcount = 0
        for _ in range(MAX_ITER):
            overlap_found = False
            for stone in reversed(self.stones):
                if stone == self.selected_stone:
                    continue
                dx = new_x - stone.x
                dy = new_y - stone.y
                dist = (dx**2 + dy**2)**0.5
                min_dist = r + stone.radius
                if dist < min_dist:
                    overlap_found = True
                    # 重なっているので、現在のstoneから外側に押し出すベクトルを計算
                    if dist == 0:
                        # 完全に重なっている場合は右に半径分ずらす    
                        tmp_x = stone.x + min_dist
                        if tmp_x <= w - r:
                            dx = min_dist
                        else: # 右にずらせない場合は左に石と重ならないようにずらす
                            lcount += 1
                            dx = -min_dist*lcount   
                        dy = 0
                        dist = min_dist
                    push_x = dx / dist * min_dist
                    push_y = dy / dist * min_dist
                    # 新しい位置を調整（stoneの位置から半径分離れた位置）
                    new_x = int(stone.x + push_x)
                    new_y = int(stone.y + push_y)

                    # 範囲内に戻す
                    new_x = max(r, min(new_x, w - r))
                    new_y = max(r, min(new_y, h - r))
            if not overlap_found: break

        self.selected_stone.x = new_x
        self.selected_stone.y = new_y

    def add_stone(self, stones_list: list[tuple[float,float,object]]) -> None: 
        #stones_listは各要素が(x,y,team)のリスト
        for stone in stones_list:
            over = tuple(n >= self.max_stones() for n in self.count_stones())
            if all(over):
                break
            elif any(over):
                false_indice = [i for i, val in enumerate(over) if not val][0] #最大個数の石の色を取得
                if stone[2] == false_indice:
                    self.stones.append(Stone(stone))
            else:    
                self.stones.append(Stone(stone))    
        self.update() #再描画

    def clear_stones(self) -> None:
        self.stones.clear()
        self.update()

    def count_stones(self) -> tuple[int, int]:
        team0 = 0; team1 = 0
        for stone in self.stones:
            if stone.team in (0, "red", RED):
                team0 += 1
            elif stone.team in (1, "yellow", YELLOW):
                team1 += 1
            else: pass        
        return team0, team1
    
    def max_stones(self) -> int:
        if self.is_MD: return 6
        else: return 8

    def init_MD(self) -> None:
        self.clear_stones()
        center_x = 149; housex = 80; 
        housey = 169; foot8 = 130
        p3b = 360; p3f = 380; p2b = 420; p2f = 440
        p1b = 480; p1f = 500; f = 0; l = 1
        if self.is_PPL:
            if self.md_place == 5:
                self.add_stone({
                    (center_x-housex, housey, l),
                    (center_x-72, p3b, f)
                })
            elif self.md_place == 4:
                self.add_stone({
                    (center_x-housex, housey, l),
                    (center_x-72, p3f, f)
                })
            elif self.md_place == 3:
                self.add_stone({
                    (center_x-housex, housey, l),
                    (center_x-70, p2b, f)
                })
            elif self.md_place == 2:
                self.add_stone({
                    (center_x-housex, housey, l),
                    (center_x-70, p2f, f)
                })
            elif self.md_place == 1:
                self.add_stone({
                    (center_x-housex, housey, l),
                    (center_x-68, p1b, f)
                })
            elif self.md_place == 0:
                self.add_stone({
                    (center_x-housex, housey, l),
                    (center_x-68, p1f, f)
                })
        elif self.is_PPR:
            if self.md_place == 5:
                self.add_stone({
                    (center_x+housex, housey, l),
                    (center_x+72, p3b, f)
                })
            elif self.md_place == 4:
                self.add_stone({
                    (center_x+housex, housey, l),
                    (center_x+72, p3f, f)
                })
            elif self.md_place == 3:
                self.add_stone({
                    (center_x+housex, housey, l),
                    (center_x+70, p2b, f)
                })
            elif self.md_place == 2:
                self.add_stone({
                    (center_x+housex, housey, l),
                    (center_x+70, p2f, f)
                })
            elif self.md_place == 1:
                self.add_stone({
                    (center_x+housex, housey, l),
                    (center_x+68, p1b, f)
                })
            elif self.md_place == 0:
                self.add_stone({
                    (center_x+housex, housey, l),
                    (center_x+68, p1f, f)
                })
        else:
            if self.md_place == 5:
                self.add_stone([
                    (center_x, foot8, l),
                    (center_x, p3b, f),
                ])
            elif self.md_place == 4:
                self.add_stone({
                    (center_x, foot8, l),
                    (center_x, p3f, f)
                })
            elif self.md_place == 3:
                self.add_stone({
                    (center_x, foot8, l),
                    (center_x, p2b, f)
                })
            elif self.md_place == 2:
                self.add_stone({
                    (center_x, foot8, l),
                    (center_x, p2f, f)
                })
            elif self.md_place == 1:
                self.add_stone({
                    (center_x, foot8, l),
                    (center_x, p1b, f)
                })
            elif self.md_place == 0:
                self.add_stone({
                    (center_x, foot8, l),
                    (center_x, p1f, f)
                })
        self.update()