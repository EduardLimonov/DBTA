from PyQt5.QtWidgets import *

from interface.back.PathManager import PathManager
from interface.back.SortForm import SortForm
from core.utils.schema.DBSchema import Level
from interface.front.DataViewer.sort.SortField import SortField
from PyQt5.QtCore import Qt


class SortWidget(QWidget):
    def __init__(self, path_manager: PathManager, available_attrs, parent=None):
        super().__init__(parent)
        self.available_attrs = available_attrs
        self.btn_add = None
        self.sort_layout = None
        self.sort_main_widget = None
        self.sort_forms = self.__init_sort_forms()
        self.sort_widgets: list[SortField] = []
        self.path_manager = path_manager
        self.make_ui()

    def __init_sort_forms(self):
        # TODO
        return []

    def make_ui(self):
        main_l = QHBoxLayout()
        self.setLayout(main_l)
        frame = QFrame(self, objectName='fram')
        #frame.setMaximumHeight(140)
        main_l.addWidget(frame)
        frame_l = QHBoxLayout()
        frame.setLayout(frame_l)

        frame_l.addWidget(QLabel('Сортировать по:', frame, objectName='name'))

        sort_frame = QFrame(frame)
        frame_l.addWidget(sort_frame)
        sort_l = QVBoxLayout()
        sort_frame.setLayout(sort_l)

        self.sort_main_widget = QWidget(sort_frame)
        #self.sort_main_widget.setMaximumHeight(140)

        sort_l.addWidget(self.sort_main_widget)

        sort_l.addWidget(scr := QScrollArea(sort_frame))
        scr.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scr.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scr.setWidgetResizable(True)
        scr.setWidget(self.sort_main_widget)

        self.sort_layout = QHBoxLayout()
        self.sort_main_widget.setLayout(self.sort_layout)
        self.sort_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        for f in self.sort_forms:
            self.__add_sort_field(f)

        frame_l.addWidget(b := QPushButton('Добавить', frame))
        self.btn_add = b
        b.clicked.connect(self.__clicked_add_sort)
        self.path_manager.changed_path.connect(self.changed_path)
        self.changed_path()

    def __add_sort_field(self, f: SortForm | None):
        av_at = self._get_avail_attr()
        new = SortField(self.__sort_close, av_at, self.sort_main_widget, f)
        self.sort_widgets.append(new)
        self.sort_layout.addWidget(new)
        self.__update_geom()

    def _get_avail_attr(self) -> list[str]:
        return self.available_attrs  #self.path_manager.get_list_of_children()

    def __clicked_add_sort(self):
        self.__add_sort_field(None)
        self.update()

    def __sort_close(self, sort_widget: SortField):
        self.sort_widgets.remove(sort_widget)
        self.sort_forms = [f for f in self.sort_forms if f != sort_widget.get_sort_form()]
        sort_widget.hide()
        self.__update_geom()

    def set_sort_list(self, lst: list[SortForm]):
        self.sort_forms = lst.copy()
        for w in self.sort_widgets:
            w.hide()
        self.sort_widgets = []
        for _f in lst:
            self.__add_sort_field(_f)
        self.update()
        self.__update_geom()

    def clear_sorts(self):
        self.set_sort_list([])

    def set_available_attributes(self, av_at):
        self.available_attrs = av_at

    def changed_path(self):
        #self.set_sort_list([])
        if self.path_manager.level == Level.attr:
            self.available_attrs = self.path_manager.get_list_of_children(full=True)
            self.setEnabled(True)
        else:
            self.setEnabled(False)

    def get_sorts(self) -> list[SortForm]:
        return [s.get_sort_form() for s in self.sort_widgets]

    def __update_geom(self):
        if len(self.sort_widgets):
            self.setMinimumHeight(200)
        else:
            self.setMinimumHeight(0)
