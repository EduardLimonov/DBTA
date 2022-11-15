from typing import Iterable

from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal

from interface.back.Filter import Filter
from interface.back.PathManager import PathManager
from interface.back.SortForm import SortForm
from interface.back.SqlWriter import SqlWriter
from core.md_repos.MDRepos import MDRepos
from core.utils import query as q
from core.utils.MDStructures import MDServer
from core.utils.ServerManager import ServerManager
from core.utils.references import ServerRef
from interface.front.DataViewer.join.JoinWidget import JoinWidget
from interface.front.DataViewer.select.SelectWidget import SelectWidget
from interface.front.DataViewer.filter.FilterWidget import FilterWidget
from interface.front.DataViewer.navigator.Navigator import NavigatorWidget
from interface.front.DataViewer.sort.SortWidget import SortWidget
from interface.front.DataViewer.table.TableWidget import TableWidget
import mysql.connector


class DataViewer(QWidget):
    FILTER = 'filter'
    SORT = 'sort'

    close_signal = pyqtSignal()

    def __init__(self, repos: MDRepos, available_connections: list[str], state_dict=None, parent=None):
        super().__init__(parent)
        if state_dict is None:
            state_dict = {DataViewer.FILTER: {}, DataViewer.SORT: {}}

        self.state_dict = state_dict
        self.select = None
        self.table = None
        self.sort = None
        self.filter = None
        self.navigator = None
        self.join = None
        self.repos = repos
        self.available_connections = available_connections
        self.path_manager = PathManager(repos)
        self.create_ui()

    def create_ui(self):
        main_l = QHBoxLayout()
        self.setLayout(main_l)

        content_widget = QWidget(self)
        main_l.addWidget(content_widget)
        lay = QVBoxLayout()
        #lay.setAlignment(Qt.AlignTop)
        content_widget.setLayout(lay)

        self.navigator = NavigatorWidget(self.path_manager, self.find_action, self.available_connections, content_widget)
        self.join = JoinWidget(self.path_manager, self.available_connections, content_widget)
        self.filter = FilterWidget(self.path_manager, [], content_widget)
        #self.filter.setMinimumHeight(200)
        self.sort = SortWidget(self.path_manager, [], content_widget)
        #self.sort.setMinimumHeight(200)
        self.select = SelectWidget(content_widget)
        self.table = TableWidget(content_widget)

        self.join.changed_join_signal.connect(self.__update_filter_and_sort)
        self.navigator.path_manager.changed_path.connect(self.__update_filter_and_sort)

        lay.addWidget(self.navigator)
        lay.addWidget(self.join)
        lay.addWidget(self.filter)
        lay.addWidget(self.sort)
        lay.addWidget(self.select)
        lay.addWidget(self.table)
        lay.addWidget(QLabel('© 2021-2022 Honfate Inc', self))

        self.setWindowTitle('Извлечение данных')
        self.setWindowState(QtCore.Qt.WindowMaximized)

        scr = QScrollArea(self)
        main_l.addWidget(scr)
        scr.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scr.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scr.setWidgetResizable(True)
        scr.setWidget(content_widget)

    @staticmethod
    def __extract_elements_by_keys(dictionary: dict[tuple[str, ...], list[str]], my_keys: Iterable[str]) -> list[str]:
        # извлечь из dictionary все строки всех списков, для которых ключ словаря полностью содержится в my_keys

        def check_key(_tuple_key: tuple[str], _my_keys: Iterable[str]) -> bool:
            for k in _tuple_key:
                if k not in _my_keys:
                    return False

            return True

        res = []
        for dict_key in dictionary:
            if check_key(dict_key, my_keys):
                res += dictionary[dict_key]

        return list(dict.fromkeys(res))

    def __get_filters_and_sorts(self) -> tuple[list[Filter], list[SortForm]]:
        actual_table_paths = tuple(self.join.get_path_tables())

        filter_strings = self.__extract_elements_by_keys(self.state_dict[DataViewer.FILTER], actual_table_paths)
        sort_strings = self.__extract_elements_by_keys(self.state_dict[DataViewer.SORT], actual_table_paths)

        filters = [Filter.from_str(s) for s in filter_strings]
        sorts = [SortForm.from_str(s) for s in sort_strings]

        return filters, sorts

    def __update_filter_and_sort(self):
        av_at = self.join.get_full_attribute_list()
        self.filter.set_available_attributes(av_at)
        self.sort.set_available_attributes(av_at)

        filters, sorts = self.__get_filters_and_sorts()

        self.filter.set_filter_list(filters)
        self.sort.set_sort_list(sorts)

    def __save_filter_and_sort(self):
        actual_table_paths = tuple(self.join.get_path_tables())
        filters, sorts = self.filter.get_filters(), self.sort.get_sorts()
        self.state_dict[DataViewer.FILTER][actual_table_paths] = [str(f) for f in filters]
        self.state_dict[DataViewer.SORT][actual_table_paths] = [str(s) for s in sorts]

    def find_action(self, a):
        server_name, path = self.path_manager.get_str_state()
        joins = self.join.get_joins()
        filters = self.filter.get_filters()
        sorts = self.sort.get_sorts()
        columns = None  # TODO choose columns

        server_data: MDServer = self.path_manager.repos.get_server_by_name(server_name)
        server_ref: ServerRef = ServerRef.create_server_ref(server_data)

        query_prepare, query_select, new_table_names = SqlWriter.make_select_text(
            server_name, path, joins, filters, sorts, self.get_db_create_code, server_ref, columns
        )
        print("Prepared FEDERATED tables: %s" % '\n'.join(query_prepare), end='\n\n\n')
        print("Query text: % s" % query_select)
        print("New names: %s" % str(new_table_names))

        self.select.set_text(query_select)
        server_manager = ServerManager(server_ref)

        server_manager.execute_transaction(query_prepare)
        result = []
        try:
            result = server_manager.make_select(query_select)
        except mysql.connector.errors.ProgrammingError as e:
            print(e)
            QMessageBox.about(self, "Ошибка выполнения", "Во время выполнения запроса произошла ошибка")

        server_manager.execute_transaction(
            [SqlWriter.remove_table_statement(tab_name) for tab_name in new_table_names]
        )
        #print("Result: %s" % result)

        if not (columns is None):
            names = columns
        else:
            names = self.join.get_full_attribute_list()  #self.path_manager.get_list_of_children() + self.
        self.table.set_vals(result, names)
        self.__save_filter_and_sort()

    def closeEvent(self, event):
        self.close_signal.emit()
        super().closeEvent(event)

    def get_db_create_code(self, server: str, tname: str) -> str:
        server_data: MDServer = self.path_manager.repos.get_server_by_name(server)
        server_ref: ServerRef = ServerRef.create_server_ref(server_data)
        server_manager = ServerManager(server_ref)

        return server_manager.make_select(q.sql_get_table_create_code(tname))[-1][-1]


