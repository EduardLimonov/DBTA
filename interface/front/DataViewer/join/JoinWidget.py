from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, pyqtSignal

from interface.back.JoinForm import JoinForm
from interface.back.PathManager import PathManager
from core.md_repos.MDRepos import MDRepos
from core.utils.schema.DBSchema import Level
from interface.front.DataViewer.join.JoinField import JoinField


class JoinWidget(QWidget):
    changed_join_signal = pyqtSignal()

    def __init__(self, path_manager: PathManager, available_connections: list[str], parent=None):
        super().__init__(parent)
        self.bttn_add = None
        self.join_lay = None
        self.join_main_widget = None
        self.join_widgets = []
        self.available_connections = available_connections
        self.add_attributes = []
        self.path_manager = path_manager
        self.create_ui()

    def create_ui(self):
        main_l = QVBoxLayout()
        self.setLayout(main_l)
        main_l.setAlignment(Qt.AlignTop )#| Qt.AlignLeft)

        frame = QFrame(self, objectName='fram')
        main_l.addWidget(frame)
        frame_l = QHBoxLayout()
        frame.setLayout(frame_l)

        frame_l.addWidget(QLabel('JOIN', frame, objectName='name'))
        frame_l.addWidget(join_frame := QFrame(frame))
        join_frame.setLayout(join_l := QVBoxLayout())
        #join_frame.setMinimumHeight(280)

        self.join_main_widget = QWidget(join_frame)
        join_l.addWidget(self.join_main_widget)
        self.join_lay = QHBoxLayout()
        self.join_main_widget.setLayout(self.join_lay)
        self.join_lay.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        join_l.addWidget(scr := QScrollArea(self.join_main_widget))
        scr.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scr.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scr.setWidgetResizable(True)
        scr.setWidget(self.join_main_widget)

        frame_l.addWidget(b := QPushButton('Добавить', frame))
        b.clicked.connect(self.__add_join_field)
        self.bttn_add = b
        self.path_manager.changed_path.connect(self.changed_path)
        self.changed_path()

    def get_full_attribute_list(self) -> list[str]:
        path_attrs = self.path_manager.get_list_of_children(full=True)
        for w in self.join_widgets:
            if w.right_path_manager.level != Level.attr:
                continue
            full_attributes = w.right_path_manager.get_list_of_children(full=True)
            for attr in full_attributes:
                if attr not in path_attrs:
                    path_attrs.append(attr)
        return path_attrs

    def get_path_tables(self, path_attrs=None) -> list[str]:
        if path_attrs is None:
            path_attrs = self.get_full_attribute_list()  # server.db.table.attribute
        return list(set(['.'.join(pa.split('.')[: -1]) for pa in path_attrs]))  # server.db.table

    def __add_join_field(self):
        path_attrs = self.get_full_attribute_list()  # server.db.table.attribute
        path_tables = self.get_path_tables(path_attrs)  # server.db.table

        new = JoinField(self.join_main_widget, path_attrs, self.available_connections,
                        r := PathManager(self.path_manager.repos, deprecated_paths=path_tables), self.__close_widget,)

        r.changed_path.connect(self.__check_add_bttn)
        if len(self.join_widgets):
            self.join_widgets[-1].setEnabled(False)

        self.changed_join_signal.emit()
        new.change_join_signal.connect(lambda self=self: self.changed_join_signal.emit())
        self.join_widgets.append(new)
        self.join_lay.addWidget(new)
        self.__check_add_bttn()
        self.__update_geom()

    def __close_widget(self, widget):
        self.join_widgets.remove(widget)
        widget.hide()
        if len(self.join_widgets):
            self.join_widgets[-1].setEnabled(True)
        self.__check_add_bttn()
        self.__update_geom()

    def changed_path(self):
        for w in self.join_widgets:
            self.__close_widget(w)

        self.setEnabled(self.path_manager.level == Level.attr)

    def __check_add_bttn(self):
        if len(self.join_widgets):
            self.bttn_add.setEnabled(self.join_widgets[-1].is_done())
        else:
            self.bttn_add.setEnabled(True)

    def __update_geom(self):
        if len(self.join_widgets):
            self.setMinimumHeight(420)
        else:
            self.setMinimumHeight(0)

    def get_joins(self) -> list[JoinForm]:
        return [jf.get_join_form() for jf in self.join_widgets if jf.is_done()]

