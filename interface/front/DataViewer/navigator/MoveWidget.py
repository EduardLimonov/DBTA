from __future__ import annotations
from PyQt5.QtWidgets import *
from interface.back.PathManager import PathManager
from core.utils.schema.DBSchema import Level
from PyQt5.QtCore import Qt


class MoveWidget(QWidget):
    def __init__(self, path_manager: PathManager, available_connections: list[str], update_path_action, parent=None):
        super().__init__(parent)
        self.move_up_bttn = None
        self.move_bttn = None
        self.update_path_action = update_path_action
        self.path_manager = path_manager
        self.combo_box = None
        self.available_connections = available_connections
        #self.parent = parent
        self.create_ui()

    def create_ui(self):
        main_l = QVBoxLayout()
        self.setLayout(main_l)
        fr = QFrame(self, objectName='fram')
        main_l.addWidget(fr)
        fr.setFrameShape(QFrame.StyledPanel)
        fr.setFrameShadow(QFrame.Raised)
        grid = QGridLayout(fr)
        fr.setLayout(grid)
        #grid.setAlignment(Qt.AlignTop)

        grid.addWidget(
            up := QPushButton('Вверх', fr), 0, 2
        )
        up.setFixedSize(100, 30)
        up.clicked.connect(self.__move_up_and_update)
        self.move_up_bttn = up
        grid.addWidget(
            QLabel("Перейти в...", fr), 0, 0,
        )
        grid.addWidget(
            l := QComboBox(fr), 1, 0, 1, 1
        )

        self.combo_box = l
        #self.__update_combo_box()

        grid.addWidget(
            move := QPushButton('Перейти', fr), 1, 2
        )
        self.move_bttn = move
        move.setFixedSize(100, 30)

        move.clicked.connect(lambda b, lst=l, s=self: s.__move_and_update(lst.currentText()))
        self.__update_enable()

    def __update_combo_box(self):
        self.combo_box.clear()

        if self.path_manager.level == Level.server:
            lst_to_show = self.available_connections
        else:
            lst_to_show = self.path_manager.get_list_of_children()
        for d in lst_to_show:
            self.combo_box.addItem(d)
        self.update()

    def __move_up_and_update(self):
        self.path_manager.move_up()
        self.update_path_action()
        self.__update_enable()

    def __move_and_update(self, where: str):
        self.path_manager.move_down(where)
        self.update_path_action()
        self.__update_enable()

    def __update_enable(self):
        if self.path_manager.level == Level.attr:
            self.combo_box.setEnabled(False)
            self.move_bttn.setEnabled(False)
            return
        elif self.path_manager.level == Level.server:
            self.move_up_bttn.setEnabled(False)
        else:
            self.combo_box.setEnabled(True)
            self.move_bttn.setEnabled(True)
            self.move_up_bttn.setEnabled(True)

        self.__update_combo_box()



