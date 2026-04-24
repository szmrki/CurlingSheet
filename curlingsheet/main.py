# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QApplication
from .main_window import MainWindow
import sys


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
