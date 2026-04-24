# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QWidget, QPushButton, QRadioButton, QButtonGroup,
                              QVBoxLayout, QHBoxLayout, QFileDialog,
                              QGroupBox, QCheckBox, QDialog, QToolButton, QMenu,
                              QLabel)
from PyQt6.QtGui import QImage, QIcon, QAction
import cv2
import numpy as np
import pandas as pd
import os, sys

from sheet import Sheet
from dialogs import ColorDialog
import sheet2pos as sp

resource_path = lambda p: os.path.join(getattr(sys, '_MEIPASS', os.getcwd()), p)
icon_path      = resource_path("icon/icon.ico")
hammer_red     = resource_path("icon/hammer_red.ico")
hammer_yellow  = resource_path("icon/hammer_yellow.ico")


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CurlingSheet")
        self.setWindowIcon(QIcon(icon_path))

        self.sheet = Sheet()

        # --- ボタン類 ---
        self.button_change_color    = self._push("ハウスの色の変更",         self.change_color)
        self.button_add_red_stone   = self._push("赤ストーンを追加",          self.add_red_stone_from_button)
        self.button_add_yellow_stone= self._push("黄ストーンを追加",          self.add_yellow_stone_from_button)
        self.button_save            = self._push("画像のエクスポート",         self.save_fig)
        self.button_import_img      = self._push("画像のインポート",           self.import_fig)
        self.button_export_stones   = self._push("ストーン配置のエクスポート", self.export_stones)
        self.button_import_stones   = self._push("ストーン配置のインポート",   self.import_stones)
        self.button_clear_stones    = self._push("クリア",                    self.sheet.clear_stones)

        self.button_normal = self._radio("4人制", self.normal_rules)
        self.button_md     = self._radio("MD",    self.md_rules)
        self.button_3b = self._radio("3b", self.set_3b)
        self.button_3f = self._radio("3f", self.set_3f)
        self.button_2b = self._radio("2b", self.set_2b)
        self.button_2f = self._radio("2f", self.set_2f)
        self.button_1b = self._radio("1b", self.set_1b)
        self.button_1f = self._radio("1f", self.set_1f)

        self.button_ppl = self._check("PP-Left",  self.set_ppl)
        self.button_ppr = self._check("PP-Right", self.set_ppr)

        rule_buttons  = [self.button_normal, self.button_md]
        place_buttons = [self.button_3b, self.button_3f,
                         self.button_2b, self.button_2f,
                         self.button_1b, self.button_1f]

        self._button_group(rule_buttons,  self.button_normal)
        self._button_group(place_buttons, self.button_3b)

        self.button_hammer = self._tool_button()
        rule_buttons.append(self.button_hammer)

        # MDの詳細設定パネル
        self.detail = QGroupBox("MDの詳細設定")
        detail_layout = QVBoxLayout()
        detail_layout.addLayout(self._hbox([self.button_ppl, self.button_ppr]))
        detail_layout.addWidget(QLabel("初期配置 (b: 後  f: 前)"))
        detail_layout.addLayout(self._hbox(place_buttons))
        self.detail.setLayout(detail_layout)
        self.detail.setVisible(False)

        # 全体レイアウト
        layout = QVBoxLayout()
        layout.addLayout(self._hbox(rule_buttons))
        layout.addWidget(self.detail)
        layout.addWidget(self.sheet)
        layout.addWidget(self.button_change_color)
        layout.addLayout(self._hbox([self.button_add_red_stone, self.button_add_yellow_stone]))
        layout.addLayout(self._hbox([self.button_save, self.button_import_img]))
        layout.addWidget(self.button_export_stones)
        layout.addWidget(self.button_import_stones)
        layout.addWidget(self.button_clear_stones)
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

        self.sheet.clear_stones()

    # --- ウィジェットファクトリ ---
    def _push(self, title, method) -> QPushButton:
        btn = QPushButton(title)
        btn.clicked.connect(method)
        return btn

    def _radio(self, title, method) -> QRadioButton:
        btn = QRadioButton(title)
        btn.toggled.connect(method)
        return btn

    def _check(self, title, method) -> QCheckBox:
        btn = QCheckBox(title)
        btn.toggled.connect(method)
        return btn

    def _button_group(self, buttons: list, default: QRadioButton) -> None:
        group = QButtonGroup(self)
        for btn in buttons:
            group.addButton(btn)
        default.setChecked(True)

    def _hbox(self, widgets: list) -> QHBoxLayout:
        layout = QHBoxLayout()
        for w in widgets:
            layout.addWidget(w)
        return layout

    def _tool_button(self) -> QToolButton:
        btn = QToolButton()
        btn.setIcon(QIcon(hammer_red))
        btn.setText("")
        menu = QMenu()
        action_red    = QAction("赤", self)
        action_yellow = QAction("黄", self)
        menu.addAction(action_red)
        menu.addAction(action_yellow)
        btn.setMenu(menu)
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        action_red.triggered.connect(   lambda: self._select_hammer(btn, 0))
        action_yellow.triggered.connect(lambda: self._select_hammer(btn, 1))
        return btn

    # --- ハンマー選択 ---
    def _select_hammer(self, button, color: int) -> None:
        if color == 0:
            self.sheet.f, self.sheet.l = 1, 0
            button.setIcon(QIcon(hammer_red))
        elif color == 1:
            self.sheet.f, self.sheet.l = 0, 1
            button.setIcon(QIcon(hammer_yellow))
        if self.sheet.is_MD:
            self.sheet.init_MD()

    # --- ダイアログ ---
    def change_color(self) -> None:
        dialog = ColorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.sheet.color12 = dialog.combo12.currentIndex()
            self.sheet.color4  = dialog.combo4.currentIndex()
            self.sheet.update()

    # --- ストーン追加 ---
    def _add_stone_at(self, x, y, team) -> None:
        self.sheet.add_stone([(x, y, team)])
        self.sheet.selected_stone = self.sheet.stones[-1]
        s = self.sheet.selected_stone
        self.sheet.check_stone_overlap(s.x, s.y, s.radius,
                                       self.sheet.width(), self.sheet.height())
        self.sheet.selected_stone = None
        self.sheet.update()

    def add_red_stone_from_button(self)    -> None: self._add_stone_at(11,  11, 0)
    def add_yellow_stone_from_button(self) -> None: self._add_stone_at(288, 11, 1)

    # --- ファイルI/O ---
    def save_fig(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "画像のエクスポート",
                                              "output.png", "PNG画像 (*.png)")
        if path:
            self.sheet.grab().save(path)

    def import_fig(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "画像のインポート",
                                              "", "PNG画像 (*.png)")
        if path:
            pos = sp.get_stones_pos(img_path=path)[["x", "y", "team"]]
            self.sheet.clear_stones()
            self.sheet.add_stone([tuple(row) for row in pos.values])

    def export_stones(self) -> None:
        pixmap  = self.sheet.grab()
        qimage  = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        ptr     = qimage.bits()
        ptr.setsize(qimage.sizeInBytes())
        img = np.array(ptr, dtype=np.uint8).reshape((qimage.height(), qimage.width(), 4))
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

        pos = sp.get_stones_pos(img=img)
        if not pos.empty:
            pos  = sp.curlit_to_dc3(pos)
            path, _ = QFileDialog.getSaveFileName(self, "ストーン配置のエクスポート",
                                                  "output.json", "JSON Files (*.json)")
            if path:
                sp.df_to_json(pos, path)

    def import_stones(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "ストーン配置のインポート",
                                              "", "JSON Files (*.json)")
        if path:
            df = pd.read_json(path, orient="records")
            if not df.empty:
                df = sp.dc3_to_curlit(df)
            self.sheet.clear_stones()
            self.sheet.add_stone([tuple(row) for row in df.values])

    # --- ルール切替 ---
    def normal_rules(self, checked) -> None:
        if checked:
            self.sheet.is_MD = self.sheet.is_PPL = self.sheet.is_PPR = False
            self.button_ppl.setChecked(False)
            self.button_ppr.setChecked(False)
            self.sheet.clear_stones()

    def md_rules(self, checked) -> None:
        self.detail.setVisible(checked)
        if checked:
            self.sheet.is_MD = True
            self.sheet.init_MD()

    def set_ppl(self, checked) -> None:
        self.sheet.is_PPL = checked
        if checked:
            self.button_ppr.setChecked(False)
        self.sheet.init_MD()

    def set_ppr(self, checked) -> None:
        self.sheet.is_PPR = checked
        if checked:
            self.button_ppl.setChecked(False)
        self.sheet.init_MD()

    def set_3b(self, checked) -> None:
        if checked: self.sheet.md_place = 5; self.sheet.init_MD()

    def set_3f(self, checked) -> None:
        if checked: self.sheet.md_place = 4; self.sheet.init_MD()

    def set_2b(self, checked) -> None:
        if checked: self.sheet.md_place = 3; self.sheet.init_MD()

    def set_2f(self, checked) -> None:
        if checked: self.sheet.md_place = 2; self.sheet.init_MD()

    def set_1b(self, checked) -> None:
        if checked: self.sheet.md_place = 1; self.sheet.init_MD()

    def set_1f(self, checked) -> None:
        if checked: self.sheet.md_place = 0; self.sheet.init_MD()
