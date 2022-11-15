from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QSize
from core.utils.references import ServerRef


class RecordWidget(QWidget):
    MAX_STR_IN_ENUM = 4

    def __init__(self, server_ref: ServerRef, databases: list[str], func_remove: callable, parent=None):
        super().__init__(parent)
        self.server_ref = server_ref
        self._create_content(server_ref, databases, func_remove)

    def _create_content(self, server_ref: ServerRef, databases: list[str], func_remove: callable):
        main_l = QVBoxLayout(self)
        self.setLayout(main_l)
        fr = QFrame(self, objectName='fram')
        main_l.addWidget(fr)
        fr.setFrameShape(QFrame.StyledPanel)
        fr.setFrameShadow(QFrame.Raised)
        grid = QGridLayout(fr)
        fr.setLayout(grid)
        name_l = QLabel(server_ref.name, fr, objectName='name')
        #name_l.setFont(QFont('Arial', 20))

        grid.addWidget(
            name_l, 0, 0
        )
        grid.addWidget(
            QLabel(server_ref.user, fr), 0, 1
        )
        grid.addWidget(
            QLabel('%s:%s' % (server_ref.address, server_ref.port), fr), 0, 2
        )
        grid.addWidget(
            remove_btn := QPushButton('', fr, objectName='close'), 0, 3
        )
        size = QSize(25, 25)
        remove_btn.setMaximumSize(size)
        remove_btn.setMinimumSize(size)
        remove_btn.clicked.connect(func_remove)

        grid.addWidget(
            QLabel(self.__list_to_str(databases), fr), 1, 0, 1, -1
        )

    @staticmethod
    def __list_to_str(strings: list[str]):
        content = ', '.join(strings[: min(RecordWidget.MAX_STR_IN_ENUM, len(strings))])
        if len(strings) > RecordWidget.MAX_STR_IN_ENUM:
            content += ' и др.'
        return content

    @staticmethod
    def create_no_server_message(parent=None) -> QWidget:
        return QLabel('Здесь пока нет серверов...', parent)

