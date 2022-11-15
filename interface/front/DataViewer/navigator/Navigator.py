from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from interface.back.PathManager import PathManager
from core.utils.schema.DBSchema import Level
from interface.front.DataViewer.navigator.MoveWidget import MoveWidget


class NavigatorWidget(QWidget):
    def __init__(self, path_manager: PathManager, find_action: callable, available_connections: list[str], parent=None,
                 add_find: bool = True):
        super().__init__(parent)
        self.find_bttn = None
        self.label_path = None
        self.move_widget = None
        self.path_manager = path_manager
        self.find_action = find_action
        self.available_connections = available_connections
        self.create_ui(add_find)

    def create_ui(self, add_find):
        main_l = QGridLayout()
        self.setLayout(main_l)
        main_l.setAlignment(Qt.AlignTop)
        info_frame = QFrame(qq := QWidget(self), objectName='fram')

        qq.setLayout(ll := QVBoxLayout())
        ll.addWidget(info_frame)
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setFrameShadow(QFrame.Raised)
        info_frame.setLayout(l := QHBoxLayout())
        #ll.setAlignment(Qt.AlignTop)

        main_l.addWidget(qq, 0, 0)
        self.label_path = QLabel('', info_frame)
        l.addWidget(self.label_path)
        #main_l.addWidget(self.label_path)

        self.move_widget = MoveWidget(self.path_manager, self.available_connections, self.update_path, self)
        main_l.addWidget(self.move_widget, 1, 0)

        if add_find:
            main_l.addWidget(find_btn := QPushButton('Найти', self, objectName='evilButton'), 0, 1, -1, 1)
            find_btn.clicked.connect(self.find_action)
            self.find_bttn = find_btn
            self.path_manager.changed_path.connect(self.update_path)

        self.update_path()

    @staticmethod
    def __to_label_text(path: tuple[str, list[str]] | None) -> str:
        if path is None:
            return ''
        else:
            return '%s -> %s' % (path[0], ' -> '.join(path[1]))

    def update_path(self):
        self.label_path.setText('Путь: %s' % self.__to_label_text(self.path_manager.get_str_state()))
        self.update()

        if self.find_bttn is None:
            return
        if self.path_manager.level == Level.attr:
            self.find_bttn.setEnabled(True)
        else:
            self.find_bttn.setEnabled(False)

