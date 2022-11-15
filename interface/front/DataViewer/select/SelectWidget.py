from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class SelectWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.label_info = None
        self.make_ui()

    def make_ui(self):
        main_l = QVBoxLayout()
        self.setLayout(main_l)

        main_frame = QFrame(self, objectName='fram')
        main_l.addWidget(main_frame)
        select_lay = QVBoxLayout()
        main_frame.setLayout(select_lay)

        self.label_info = QLabel(main_frame)
        select_lay.addWidget(self.label_info)
        select_lay.addWidget(scr := QScrollArea(main_frame))

        scr.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scr.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scr.setWidgetResizable(True)
        scr.setWidget(self.label_info)

    def set_text(self, text: str):
        self.label_info.setText(text)
