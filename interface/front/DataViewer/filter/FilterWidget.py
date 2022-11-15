from collections import deque

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize

from interface.back.Filter import Filter, Relation
from interface.back.PathManager import PathManager
from core.utils.schema.DBSchema import Level
from interface.front.DataViewer.filter.FilterField import FilterField


class FilterWidget(QWidget):
    def __init__(self, path_manager: PathManager, available_attrs: list[str], parent=None):
        super().__init__(parent)
        self.filters_lay = None
        self.button_add = None
        #self.frame = None
        #self.frame_layout = None
        self.filter_main_widget = None
        self.filter_widgets: list[FilterField] = []
        self.path_manager = path_manager
        self.filters: list[Filter] = self.__init_filters()
        self.available_attrs = available_attrs
        self.create_ui()

    def __init_filters(self) -> list[Filter]:
        # TODO
        return []

    def create_ui(self):
        main_l = QVBoxLayout()
        #main_l.setAlignment(Qt.AlignTop)
        self.setLayout(main_l)
        frame = QFrame(self, objectName='fram')
        main_l.addWidget(frame)
        frame_layout = QHBoxLayout()
        frame.setLayout(frame_layout)
        frame_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        frame_layout.addWidget(l := QLabel('Фильтры:', frame, objectName='name'))
        #l.setFixedSize(100, 40)

        filters_frame = QFrame(frame)
        filters_lay = QVBoxLayout()
        filters_lay.setAlignment(Qt.AlignTop)
        filters_frame.setLayout(filters_lay)
        self.filter_main_widget = QWidget(filters_frame)
        #self.filter_main_widget.setMaximumHeight(140)
        filters_lay.addWidget(self.filter_main_widget)
        filters_lay.addWidget(scr := QScrollArea(filters_frame))

        scr.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scr.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scr.setWidgetResizable(True)
        scr.setWidget(self.filter_main_widget)
        # scr.setMaximumHeight(100)

        self.filters_lay = QHBoxLayout()
        self.filters_lay.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.filter_main_widget.setLayout(self.filters_lay)

        #frame_layout.addLayout(filters_lay)
        frame_layout.addWidget(filters_frame)
        for f in self.filters:
            self.__add_filter_field(f)

        frame_layout.addWidget(
            bt := QPushButton('Добавить', frame)
        )
        self.button_add = bt
        bt.clicked.connect(self.__clicked_add_filter)
        #bt.setFixedSize(80, 30)
        self.path_manager.changed_path.connect(self.changed_path)
        self.changed_path()

    def __add_filter_field(self, _filter: Filter):
        av_at = self._get_avail_attr()
        av_rel = self._get_avail_rel()

        new = FilterField(self.__filter_close, av_at, av_rel, self.filter_main_widget, _filter)
        self.filter_widgets.append(new)
        self.filters_lay.addWidget(new)
        self.__update_geom()

    def _get_avail_attr(self) -> list[str]:
        attrs = self.available_attrs  #self.path_manager.get_list_of_children(full=True)
        '''        
        TODO ???
        serv, path = self.path_manager.get_str_state()

        collisions = self.find_collisions(attrs)
        for indices_tuple in collisions:
            for index in indices_tuple:
                # составим полный путь к attrs[index]
                full_path = '%s (%s -> %s)' % (attrs[index], serv, ' -> '.join(path))'''

        return attrs

    @staticmethod
    def find_collisions(lst: list) -> set[set[int]]:
        if len(lst) == len(set(lst)):
            return set()

        def findall(e, tlst, ignore):
            return {i for i in range(len(tlst)) if tlst[i] == e and tlst[i] not in ignore}

        res = set()
        ignore = set()
        i = 0
        while len(lst):
            #e = lst.pop(-1)
            all_elems = findall(lst[i], lst, ignore)
            if len(all_elems):
                res.add({i}.union(all_elems))
        return res

    @staticmethod
    def _get_avail_rel() -> list[str]:
        return [r.value for r in Relation]

    def __clicked_add_filter(self):
        _filter = self.__init_default_filter()
        self.__add_filter_field(_filter)
        self.update()

    def __filter_close(self, _filter: FilterField):
        self.filter_widgets.remove(_filter)
        self.filters = [f for f in self.filters if f != _filter.get_filter()]
        self.__update_geom()
        _filter.hide()

    def __init_default_filter(self) -> Filter:
        pass

    def set_filter_list(self, lst: list[Filter]):
        self.filters = lst.copy()
        for w in self.filter_widgets:
            w.hide()
        self.filter_widgets = []
        for _f in lst:
            self.__add_filter_field(_f)
        self.update()
        self.__update_geom()

    def clear_filters(self):
        self.set_filter_list([])

    def changed_path(self):
        #self.set_filter_list([])
        if self.path_manager.level == Level.attr:
            self.setEnabled(True)
            self.available_attrs = self.path_manager.get_list_of_children(full=True)
        else:
            self.setEnabled(False)

    def get_filters(self) -> list[Filter]:
        return [ff.get_filter() for ff in self.filter_widgets]

    def __update_geom(self):
        if len(self.filter_widgets):
            self.setMinimumHeight(200)
        else:
            self.setMinimumHeight(0)

    def set_available_attributes(self, av_at):
        self.available_attrs = av_at



