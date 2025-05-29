from sheet import Sheet
from PyQt6.QtWidgets import (QWidget, QPushButton, QRadioButton, QButtonGroup,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QApplication,
                             QGroupBox, QCheckBox, QDialog, QDialogButtonBox,
                             QComboBox, QLabel, QToolButton, QMenu)
from PyQt6.QtGui import QImage, QIcon, QAction
from PyQt6.QtCore import Qt
import cv2
import sheet2pos as sp
import numpy as np
import sys
import pandas as pd
import os

#exeファイル用
resource_path = lambda p: os.path.join(getattr(sys, '_MEIPASS', os.getcwd()), p)
icon_path = resource_path("icon/icon.ico")
hammer_red = resource_path("icon/hammer_red.ico")
hammer_yellow = resource_path("icon/hammer_yellow.ico")

# ハウスカラー変更用ダイアログ
class ColorDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("ハウスの色の変更")
        self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(300, 120)

        layout = QVBoxLayout()

        layout12, self.combo12 = self.__set_combo_layout("12-foot color", parent.sheet.color12)
        layout4, self.combo4 = self.__set_combo_layout("4-foot color", parent.sheet.color4)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)  #OKコードで閉じる

        layout.addLayout(layout12)
        layout.addLayout(layout4)
        layout.addWidget(buttons, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        #メインウィンドウに重ねるように表示
        parent_geom = parent.geometry()
        x = parent_geom.x() + (parent_geom.width() - self.width()) // 2
        y = parent_geom.y() + (parent_geom.height() - self.height()) // 2
        self.move(x, y)

    def __set_combo_layout(self, label_name, default) -> QHBoxLayout:
        label = QLabel(label_name)
        combo = QComboBox()
        combo.addItems(["赤", "青", "緑"])
        combo.setCurrentIndex(default)
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(combo)
        return layout, combo

class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CurlingSheet")
        self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(322, 830)

        self.sheet = Sheet()
        self.button_change_color = self.__set_push_button("ハウスの色の変更", self.change_color)
        self.button_add_red_stone = self.__set_push_button("赤ストーンを追加", self.add_red_stone_from_button)
        self.button_add_yellow_stone = self.__set_push_button("黄ストーンを追加", self.add_yellow_stone_from_button)
        self.button_save = self.__set_push_button("画像として保存", self.save_fig)
        self.button_export_stones = self.__set_push_button("ストーン配置のエクスポート", self.export_stones)
        self.button_import_stones = self.__set_push_button("ストーン配置のインポート", self.import_stones)
        self.button_clear_stones = self.__set_push_button("クリア", self.sheet.clear_stones)

        self.button_normal = self.__set_radio_button("4人制", self.normal_rules)
        self.button_md = self.__set_radio_button("MD", self.md_rules)
        self.button_3b = self.__set_radio_button("3b", self.set_3b)
        self.button_3f = self.__set_radio_button("3f", self.set_3f)
        self.button_2b = self.__set_radio_button("2b", self.set_2b)
        self.button_2f = self.__set_radio_button("2f", self.set_2f)
        self.button_1b = self.__set_radio_button("1b", self.set_1b)
        self.button_1f = self.__set_radio_button("1f", self.set_1f)
        rule_buttons = [self.button_normal, self.button_md]
        place_buttons = [self.button_3b, self.button_3f,
                         self.button_2b, self.button_2f,
                         self.button_1b, self.button_1f
                         ]

        self.button_ppl = self.__set_check_box("PP-Left", self.set_ppl)
        self.button_ppr = self.__set_check_box("PP-Right", self.set_ppr)
   
        self.__set_button_group(rule_buttons, self.button_normal)
        self.__set_button_group(place_buttons, self.button_3b)

        self.button_hammer = self.__set_tool_button()
        rule_buttons.append(self.button_hammer)
        
        #MDの詳細設定について
        self.detail = QGroupBox("MDの詳細設定")
        detail_layout = QVBoxLayout()
        pp_layout = self.__set_qhbox([self.button_ppl, self.button_ppr])
        detail_layout.addLayout(pp_layout)
        detail_layout.addWidget(QLabel("初期配置 (b: 後  f: 前)"))
        place_layout = self.__set_qhbox(place_buttons)
        detail_layout.addLayout(place_layout)
        self.detail.setLayout(detail_layout)
        self.detail.setVisible(False) #最初は非表示

        radio_layout = self.__set_qhbox(rule_buttons)
        button_layout = self.__set_qhbox([self.button_add_red_stone, self.button_add_yellow_stone])

        #全体のレイアウト
        layout = QVBoxLayout()
        layout.addLayout(radio_layout)
        layout.addWidget(self.detail)
        layout.addWidget(self.sheet)
        layout.addWidget(self.button_change_color)
        layout.addLayout(button_layout)
        layout.addWidget(self.button_save)
        layout.addWidget(self.button_export_stones)
        layout.addWidget(self.button_import_stones)
        layout.addWidget(self.button_clear_stones)
        
        self.setLayout(layout)
        self.sheet.clear_stones() #初期化

    def __set_push_button(self, title, method) -> QPushButton:
        button = QPushButton(title)
        button.clicked.connect(method)
        return button
    
    def __set_radio_button(self, title, method) -> QRadioButton:
        button = QRadioButton(title)
        button.toggled.connect(method)
        return button
    
    def __set_check_box(self, title, method) -> QCheckBox:
        button = QCheckBox(title)
        button.toggled.connect(method)
        return button
    
    def __set_button_group(self, buttons: list, init_button: QRadioButton) -> None:
        group = QButtonGroup(self)
        for button in buttons:
            group.addButton(button)
        init_button.setChecked(True)

    def __set_qhbox(self, buttons: list) -> QHBoxLayout:
        layout = QHBoxLayout()
        for button in buttons:
            layout.addWidget(button)
        return layout
    
    def __set_tool_button(self) -> QToolButton:
        button = QToolButton()

        button.setIcon(QIcon(hammer_red))
        button.setText("") # テキストを表示しない

        menu = QMenu()
        action_red = QAction("赤", self)
        action_yellow = QAction("黄", self)

        menu.addAction(action_red)
        menu.addAction(action_yellow)

        #ボタンにメニューを設定
        button.setMenu(menu)
        button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        # アクションを選んだときの処理
        action_red.triggered.connect(lambda: self.__select_option(button, 0))
        action_yellow.triggered.connect(lambda: self.__select_option(button, 1))

        return button
    
    def __select_option(self, button, color: int) -> None:
        #print(f"選ばれた色：{color}")
        if color == 0: #赤
            self.sheet.f = 1
            self.sheet.l = 0
            button.setIcon(QIcon(hammer_red))
        elif color == 1: #黄
            self.sheet.f = 0
            self.sheet.l = 1
            button.setIcon(QIcon(hammer_yellow))
        else: pass
        if self.sheet.is_MD:
            self.sheet.init_MD()

    def change_color(self) -> None:
        dialog = ColorDialog(self)
        result = dialog.exec()  # モーダルで表示
        if result == QDialog.DialogCode.Accepted:
            self.sheet.color12 = dialog.combo12.currentIndex() #色と対応するインデックスを取得
            self.sheet.color4 = dialog.combo4.currentIndex()
            self.sheet.update()
        else: pass

    def add_red_stone_from_button(self) -> None:
        self.sheet.add_stone([(11, 11, 0)])
        self.sheet.selected_stone = self.sheet.stones[-1]
        self.sheet.check_stone_overlap(self.sheet.selected_stone.x, 
                                       self.sheet.selected_stone.y,
                                       self.sheet.selected_stone.radius,
                                       self.sheet.width(),
                                       self.sheet.height())
        self.sheet.selected_stone = None
        self.sheet.update()

    def add_yellow_stone_from_button(self) -> None:
        self.sheet.add_stone([(288, 11, 1)])
        self.sheet.selected_stone = self.sheet.stones[-1]
        self.sheet.check_stone_overlap(self.sheet.selected_stone.x, 
                                       self.sheet.selected_stone.y,
                                       self.sheet.selected_stone.radius,
                                       self.sheet.width(),
                                       self.sheet.height())
        self.sheet.selected_stone = None
        self.sheet.update()

    def save_fig(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "画像の保存",
            "output.png",
            "PNG画像 (*.png);;JPEG画像 (*.jpg *.jpeg)"
        )
        if file_path:
            pixmap = self.sheet.grab()
            pixmap.save(file_path)
        else: pass

    def export_stones(self) -> None:
        pixmap = self.sheet.grab()
        qimage = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits() #ピクセルデータへのポインタ
        ptr.setsize(qimage.sizeInBytes()) #サイズを明示
        img = np.array(ptr, dtype=np.uint8).reshape((height, width, 4))
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR) #透明度を無視

        pos = sp.get_stones_pos(img=img)
        if not pos.empty:
            pos = sp.curlit_to_dc3(pos)
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "ストーン配置のエクスポート",
                "output.json",
                "JSON Files (*.json)"
            )
            if file_path:
                sp.df_to_json(pos, file_path)
            else: pass

    def import_stones(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "ストーン配置のインポート", 
            "", 
            "JSON Files (*.json)"
        )
        if file_path:
            df = pd.read_json(file_path, orient="records")
            if not df.empty:
                df = sp.dc3_to_curlit(df)
            stones = [tuple(row) for row in df.values]
            self.sheet.clear_stones()
            self.sheet.add_stone(stones)
        else: pass

    def normal_rules(self, checked) -> None:
        if checked:
            self.setFixedHeight(830)
            self.sheet.is_MD = False
            self.sheet.is_PPL = False
            self.sheet.is_PPR = False
            self.button_ppl.setChecked(False)
            self.button_ppr.setChecked(False)
            self.sheet.clear_stones()
    
    def md_rules(self, checked) -> None:
        self.detail.setVisible(checked)
        if checked:
            self.setFixedHeight(945)
            self.sheet.is_MD = True
            self.sheet.init_MD()

    def set_ppl(self, checked) -> None:
        if checked:
            self.sheet.is_PPL = True
            self.button_ppr.setChecked(False)
        else:
            self.sheet.is_PPL = False
        self.sheet.init_MD()

    def set_ppr(self, checked) -> None:
        if checked:
            self.sheet.is_PPR = True
            self.button_ppl.setChecked(False)
        else:
            self.sheet.is_PPR = False
        self.sheet.init_MD()

    def set_3b(self, checked) -> None:
        if checked:
            self.sheet.md_place = 5
            self.sheet.init_MD()

    def set_3f(self, checked) -> None:
        if checked:
            self.sheet.md_place = 4
            self.sheet.init_MD()
    def set_2b(self, checked) -> None:
        if checked:
            self.sheet.md_place = 3
            self.sheet.init_MD()

    def set_2f(self, checked) -> None:
        if checked:
            self.sheet.md_place = 2
            self.sheet.init_MD()

    def set_1b(self, checked) -> None:
        if checked:
            self.sheet.md_place = 1
            self.sheet.init_MD()

    def set_1f(self, checked) -> None:
        if checked:
            self.sheet.md_place = 0
            self.sheet.init_MD()
 
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())