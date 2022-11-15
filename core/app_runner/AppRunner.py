from core.utils.references import ServerRef
from interface.front.DataViewer.DataViewer import DataViewer
from interface.front.StartForm import StartForm
from core.md_repos.MDRepos import MDRepos
from PyQt5.QtWidgets import *
from interface.front.start_props.AddServerDialog import *
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
from interface.back.LoadCommutator import LoadCommutator
import mysql.connector
import json
import sys


class AppRunner(QObject):
    STATE_PATH = 'resource/state.json'  #'../../resource/state.json'
    PATH_SEP = '$$$$##$$$$'

    add_quit = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.viewer = None
        self.start_widget = None
        self.dialog = None
        self.state = self.__load_filter_sort_md()
        self.repos = MDRepos()
        self.add_quit.connect(self.end_add_serv_action)
        self.run_application()

    def run_application(self):
        app = QApplication(sys.argv)
        self.start_widget = StartForm(self.repos, self)
        self.start_widget.show()
        app.setStyle('Fusion')
        app.setStyleSheet(self.__read_stylesheet())
        # print(PyQt5.QtWidgets.QStyleFactory.keys())
        sys.exit(app.exec())
        # sys.exit(app.exec_())

    @staticmethod
    def __read_stylesheet():
        with open('resource/stylesheet.qss', 'r') as f:
            return f.read()

    def add_server(self):
        self.dialog = AddServerDialog(self)
        self.start_widget.hide()

    def put_result(self, inputs: dict):
        if len(inputs.keys()):
            if self.repos.has_server(inputs[NAME]):
                QMessageBox.about(self.dialog, "Ошибка",
                                  "Ошибка добавления сервера: \nданные некорректны или сервер с таким "
                                  "именем уже существует")
                return
            else:
                self.__set_status_add_server_window(status_active=False)

                def commutate(msg):
                    self.dialog.pbar.setValue(msg)
                    AppRunner.repaint_app()

                commutator = LoadCommutator(commutate)
                new_server = ServerRef(inputs[IP], inputs[USER], inputs[PASSWORD], inputs[NAME], inputs[PORT])

                try:
                    self.repos.add_server(new_server, commutator)
                    commutator.make_ts = False
                    #q.start()
                    #return
                    #q.wait()

                except mysql.connector.errors.DatabaseError:
                    QMessageBox.about(self.dialog, "Ошибка",
                                      "Не удается подключиться к серверу")
                    self.repos.remove_server(new_server)
                    self.__set_status_add_server_window(status_active=True)
                    return

        self.end_add_serv_action()

    def end_add_serv_action(self):
        self.dialog.hide()
        #self.start_widget.update_servers()
        self.update_start_window()
        #self.start_widget.show()
        #self.start_widget.repaint()

        self.dialog = None

    @staticmethod
    def repaint_app():
        QApplication.instance().processEvents()

    def __set_status_add_server_window(self, status_active: bool):
        if status_active:
            self.dialog.pbar.hide()
            self.dialog.setEnabled(True)
            self.dialog.set_closable(True)
        else:
            self.dialog.setEnabled(False)
            self.dialog.pbar.show()
            self.dialog.pbar.setEnabled(True)
            self.dialog.set_closable(False)

    def update_start_window(self):
        #self.repos.reconnect()
        self.start_widget.hide()
        self.start_widget.update_servers()
        #self.start_widget = StartForm(self.repos, self)
        self.start_widget.show()

    def make_query(self):
        self.start_widget.check_servers()
        self.start_widget.hide()
        self.viewer = DataViewer(repos=self.repos, available_connections=self.start_widget.available_servers,
                                 state_dict=self.state)
        self.viewer.close_signal.connect(self.view_done)
        self.viewer.show()

    def view_done(self):
        self.viewer.hide()
        self.__save_filter_sort_md()
        self.update_start_window()

    def __save_filter_sort_md(self):
        res = dict()
        for _type in (DataViewer.FILTER, DataViewer.SORT):
            res[_type] = dict()
            for tuple_key in self.state[_type]:
                res[_type][AppRunner.PATH_SEP.join(tuple_key)] = self.state[_type][tuple_key]

        with open(AppRunner.STATE_PATH, 'w') as f:
            json.dump(res, f, indent=4)

    @staticmethod
    def __load_filter_sort_md() -> dict:
        with open(AppRunner.STATE_PATH, 'r') as f:
            r = json.load(f)

        res = dict()
        for _type in (DataViewer.FILTER, DataViewer.SORT):
            res[_type] = dict()
            for str_key in r[_type]:
                res[_type][tuple(str_key.split(AppRunner.PATH_SEP))] = r[_type][str_key]
        return res


def run_application():
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)

    sys.excepthook = except_hook

    #import os
    #os.chdir('../../')

    AppRunner()

