# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QWidget, QPushButton, QRadioButton, QButtonGroup,
                              QVBoxLayout, QHBoxLayout, QFileDialog,
                              QGroupBox, QCheckBox, QDialog, QToolButton, QMenu,
                              QLabel, QApplication)
from PyQt6.QtGui import QImage, QIcon, QAction, QCloseEvent
from PyQt6.QtCore import Qt
import cv2
import numpy as np
import pandas as pd

from .sheet import Sheet
from .dialogs import ColorDialog
from . import sheet2pos as sp
from .resources import resource_path

icon_path     = resource_path("icon/icon.ico")
hammer_red    = resource_path("icon/hammer_red.ico")
hammer_yellow = resource_path("icon/hammer_yellow.ico")


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CurlingSheet")
        self.setWindowIcon(QIcon(icon_path))

        self.sheet = Sheet()

        self.button_change_color     = self._push("ハウスの色の変更",         self.change_color)
        self.button_add_red_stone    = self._push("赤ストーンを追加",          self.add_red_stone_from_button)
        self.button_add_yellow_stone = self._push("黄ストーンを追加",          self.add_yellow_stone_from_button)
        self.button_save             = self._push("画像のエクスポート",         self.save_fig)
        self.button_copy             = self._push("画像をコピー",               self.copy_fig)
        self.button_import_img       = self._push("画像のインポート",           self.import_fig)
        self.button_export_stones    = self._push("ストーン配置のエクスポート", self.export_stones)
        self.button_import_stones    = self._push("ストーン配置のインポート",   self.import_stones)
        self.button_clear_stones     = self._push("クリア",                    self.sheet.clear_stones)

        self.button_normal = self._radio("4人制", self.normal_rules)
        self.button_md     = self._radio("MD",    self.md_rules)
        # 既にMD選択中にもう一度MDを押したときは toggled が発火しない
        # (状態が変わらないため)。clicked を併用し、閉じた詳細ウィンドウを
        # 再度開けるようにする。
        self.button_md.clicked.connect(self.show_detail)
        self.button_3b = self._radio("3b", self.set_3b)
        self.button_3f = self._radio("3f", self.set_3f)
        self.button_2b = self._radio("2b", self.set_2b)
        self.button_2f = self._radio("2f", self.set_2f)
        self.button_1b = self._radio("1b", self.set_1b)
        self.button_1f = self._radio("1f", self.set_1f)

        self.button_ppl   = self._check("PP-Left",  self.set_ppl)
        self.button_ppr   = self._check("PP-Right", self.set_ppr)
        self.button_pochi = self._check("MDポイントを表示", self.toggle_pochi)
        self.button_pochi.setChecked(True)
        self.button_frame = self._check("外枠を表示", self.toggle_frame)
        self.button_frame.setChecked(True)

        rule_buttons: list[QWidget] = [self.button_normal, self.button_md]
        place_buttons = [self.button_3b, self.button_3f,
                         self.button_2b, self.button_2f,
                         self.button_1b, self.button_1f]

        self._button_group(rule_buttons,  self.button_normal)
        self._button_group(place_buttons, self.button_3b)

        self.button_hammer = self._tool_button()
        rule_buttons.append(self.button_hammer)

        # MDの詳細設定は独立した非モーダルウィンドウにする。
        # Qt.WindowType.Window を親付きで指定すると、メインの上に重ならず
        # 別ウィンドウとして表示でき、かつメイン側も操作し続けられる
        # (非モーダル)。設定を変えながらシートの結果を確認できる。
        self.detail = QWidget(self, Qt.WindowType.Window)
        self.detail.setWindowTitle("MDの詳細設定")
        self.detail.setWindowIcon(QIcon(icon_path))
        detail_layout = QVBoxLayout()
        detail_layout.addLayout(self._hbox([self.button_ppl, self.button_ppr]))
        detail_layout.addWidget(QLabel("初期配置 (b: 後  f: 前)"))
        detail_layout.addLayout(self._hbox(place_buttons))
        self.detail.setLayout(detail_layout)
        self.detail.setVisible(False)

        # 左カラム: シート本体のみ(表示専用)。
        # ルール選択や詳細設定はすべて右カラム/別ウィンドウへ移し、
        # 「左=表示 / 右=操作」と役割を分離した。
        left = QVBoxLayout()
        left.addWidget(self.sheet)
        left.addStretch()  # シートを上寄せにし、余白を下に集める

        # 右カラム: 各種操作ボタンを機能ごとにグループ化して縦に並べる。
        # 以前はシートの下に縦積みしていたため全体が縦長(約945px)になっていたが、
        # シート横の余白に寄せることでウィンドウ高さをシート(600px)程度に抑える。
        # 各グループの間に addStretch を入れ、シート高さいっぱいに均等に散らす。
        group_rule = self._groupbox("ルール", [
            self._hbox(rule_buttons),
        ])
        group_stone = self._groupbox("ストーン操作", [
            self._hbox([self.button_add_red_stone, self.button_add_yellow_stone]),
            self.button_clear_stones,
        ])
        group_image = self._groupbox("画像", [
            self.button_save,
            self.button_copy,
            self.button_import_img,
        ])
        group_data = self._groupbox("ストーン配置データ", [
            self.button_export_stones,
            self.button_import_stones,
        ])
        group_view = self._groupbox("表示設定", [
            self.button_change_color,
            self._hbox([self.button_pochi, self.button_frame]),
        ])

        right = QVBoxLayout()
        right.addWidget(group_rule)
        right.addStretch()
        right.addWidget(group_stone)
        right.addStretch()
        right.addWidget(group_image)
        right.addStretch()
        right.addWidget(group_data)
        right.addStretch()
        right.addWidget(group_view)

        # 左右カラムを横並びに配置する
        layout = QHBoxLayout()
        layout.addLayout(left)
        layout.addLayout(right)
        layout.setSizeConstraint(QHBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

        self.sheet.clear_stones()

    def _push(self, title, method) -> QPushButton:
        btn = QPushButton(title)
        btn.clicked.connect(method)
        # 右カラムのボタンが縦に細くならないよう最低高さを確保し、
        # グループ間の余白とあわせて見た目のバランスを整える。
        btn.setMinimumHeight(40)
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

    def _groupbox(self, title: str, rows: list) -> QGroupBox:
        """見出し付きの枠(QGroupBox)に行を縦に並べて返す。

        右カラムのボタン群を機能ごとにまとめて視認性を上げるために使う。

        Args:
            title: グループ枠の見出しテキスト。
            rows: 枠内に上から並べる要素のリスト。各要素は
                ウィジェット(QWidget)単体、またはレイアウト(QLayout)を受け付ける。
                レイアウトを渡すと ``_hbox`` で作った横並びをそのまま1行にできる。

        Returns:
            行を縦に積んだ QGroupBox。
        """
        box    = QGroupBox(title)
        vbox   = QVBoxLayout()
        for row in rows:
            # ウィジェットとレイアウトで追加メソッドが異なるため振り分ける
            if isinstance(row, QWidget):
                vbox.addWidget(row)
            else:
                vbox.addLayout(row)
        box.setLayout(vbox)
        return box

    def _tool_button(self) -> QToolButton:
        btn  = QToolButton()
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

    def _select_hammer(self, button, color: int) -> None:
        if color == 0:
            self.sheet.f, self.sheet.l = 1, 0
            button.setIcon(QIcon(hammer_red))
        elif color == 1:
            self.sheet.f, self.sheet.l = 0, 1
            button.setIcon(QIcon(hammer_yellow))
        if self.sheet.is_MD:
            self.sheet.init_MD()

    def change_color(self) -> None:
        dialog = ColorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.sheet.color12 = dialog.combo12.currentIndex()
            self.sheet.color4  = dialog.combo4.currentIndex()
            self.sheet.update()

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

    def save_fig(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "画像のエクスポート",
                                              "output.png", "PNG画像 (*.png)")
        if path:
            self.sheet.grab().save(path)

    def copy_fig(self) -> None:
        """シートの現在の表示画像をクリップボードへコピーする。

        ファイルに保存する ``save_fig`` と同じく ``self.sheet.grab()`` で
        シートを QPixmap として取得し、それをOSのクリップボードに渡す。
        これにより、保存ファイルを介さずに資料・スライドへ直接貼り付けできる。

        Returns:
            None
        """
        # grab() でシート部分のスクリーンショット(QPixmap)を取得する
        pixmap = self.sheet.grab()
        # アプリ共通のクリップボードオブジェクトを取得する。
        # QApplication が未起動などの場合は None が返り得るためガードする。
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setPixmap(pixmap)

    def import_fig(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "画像のインポート",
                                              "", "PNG画像 (*.png)")
        if path:
            pos = sp.get_stones_pos(img_path=path)[["x", "y", "team"]]
            self.sheet.clear_stones()
            self.sheet.add_stone([tuple(row) for row in pos.values])

    def export_stones(self) -> None:
        pixmap = self.sheet.grab()
        qimage = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        ptr    = qimage.bits()
        assert ptr is not None
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

    def normal_rules(self, checked) -> None:
        if checked:
            self.sheet.is_MD = self.sheet.is_PPL = self.sheet.is_PPR = False
            self.button_ppl.setChecked(False)
            self.button_ppr.setChecked(False)
            self.sheet.clear_stones()

    def md_rules(self, checked) -> None:
        if checked:
            self.sheet.is_MD = True
            self.sheet.init_MD()
            self.show_detail()
        else:
            # MD以外を選んだら詳細設定ウィンドウは閉じる
            self.detail.hide()

    def show_detail(self) -> None:
        """MD詳細設定ウィンドウをメインウィンドウに重ねて表示する。

        MD選択時、および既にMD選択中にMDボタンを再クリックしたときに
        呼ばれる。メインウィンドウの左上から少し内側にずらして配置し、
        手前に重ねて表示する。MD以外を選択中は何もしない。

        Returns:
            None
        """
        # MD以外を選んでいるときは詳細設定を開かない
        if not self.button_md.isChecked():
            return
        # メインウィンドウの左上から少し内側にずらして重ねて表示する
        geom = self.geometry()
        self.detail.move(geom.x() + 40, geom.y() + 40)
        self.detail.show()
        self.detail.raise_()           # 他ウィンドウより手前に出す
        self.detail.activateWindow()   # フォーカスを与える

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

    def toggle_pochi(self, checked) -> None:
        self.sheet.show_pochi = checked

    def toggle_frame(self, checked) -> None:
        self.sheet.show_frame = checked

    def closeEvent(self, event: QCloseEvent) -> None:
        """メインウィンドウを閉じる際の処理。

        MD詳細設定は別ウィンドウのため、メインを閉じても残ってしまう
        ことがある。アプリ全体が確実に終了するよう明示的に閉じる。

        Args:
            event: ウィンドウのクローズイベント。

        Returns:
            None
        """
        self.detail.close()
        super().closeEvent(event)
