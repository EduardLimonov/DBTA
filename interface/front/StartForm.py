from __future__ import annotations
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import sys

from core.utils.ServerManager import ServerManager
from interface.front.start_props.RecordWidget import RecordWidget
from core.md_repos.MDRepos import MDRepos
from core.utils.references import ServerRef
import mysql.connector


class StartForm(QWidget):
    def __init__(self, md_repos: MDRepos, master: AppRunner):
        super().__init__()
        self.available_servers = None
        self.serv_lay = None
        self.md_repos = md_repos
        self.master = master
        self.setGeometry(300, 100, 800, 600)
        self.setFixedSize(self.geometry().size())
        self.fram = QFrame(self)
        self.servers_widget = QWidget(self.fram)
        self.create_ui()

    def create_ui(self):
        self.setWindowTitle("DBTA - professional edition")
        lay = QHBoxLayout()
        self.setLayout(lay)
        self.serv_lay = self._create_serv_lay()
        self.servers_widget.setLayout(self.serv_lay)
        self.serv_lay.setAlignment(Qt.AlignTop)
        #self.servers_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scr = QScrollArea(self.fram)
        scr.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scr.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scr.setWidgetResizable(True)
        scr.setWidget(self.servers_widget)

        btn_lay = self._create_btn_space()
        btn_lay.setAlignment(Qt.AlignVCenter)
        lay.addWidget(self.fram)
        lay.addWidget(scr)
        #lay.addLayout(self.serv_lay)
        lay.addLayout(btn_lay)
        self.check_servers()

    def update_servers(self):
        for record in self.records:
            record.hide()
        self.__create_records()
        self._fill(self.serv_lay, self.records)
        for record in self.records:
            record.show()
            record.update()
        self.update()
        self.showNormal()
        self.master.repaint_app()
        self.check_servers()

    def __create_records(self):
        servers: list[tuple[str, ServerRef]] = self.md_repos.get_available_servers()
        db_for_each_server = {serv_ref: self.md_repos.get_available_databases(sid) for sid, serv_ref in servers}
        for k in db_for_each_server:
            # serv_ref: list[db_names]
            db_for_each_server[k] = [_props[0] for _props in db_for_each_server[k]]

        rm_func_for_each_server = {serv_ref: lambda rm, sr=serv_ref: (self.md_repos.remove_server(sr),
                                                                      print(sr), self.update_servers())
                                   for serv_ref in db_for_each_server}

        self.records = [RecordWidget(ref, db_for_each_server[ref], rm_func_for_each_server[ref], self)
                        for ref in db_for_each_server]
        if len(self.records) == 0:
            self.records = [RecordWidget.create_no_server_message(self.servers_widget)]

    def _create_serv_lay(self) -> QVBoxLayout:
        res = QVBoxLayout()
        self.__create_records()
        res.addWidget(QLabel('Доступные подключения:', self, objectName='name'))
        StartForm._fill(res, self.records)

        return res

    def _create_btn_space(self) -> QVBoxLayout:
        res = QVBoxLayout()
        res.addWidget(
            check := QPushButton('Проверить подключения')
        )
        res.addWidget(
            add := QPushButton('Добавить сервер...')
        )
        res.addWidget(
            query := QPushButton('Запрос...')
        )

        check.clicked.connect(lambda e, self=self: self.check_servers(True))
        add.clicked.connect(lambda e, self=self: self.master.add_server())
        query.clicked.connect(lambda e, self=self: self.make_query())

        return res

    def make_query(self):
        self.master.make_query()

    @staticmethod
    def _fill(layout: QLayout, widgets: list[QWidget]) -> None:
        for w in widgets:
            layout.addWidget(w)

    def check_servers(self, show_ok=False):
        errors = []
        self.available_servers = []
        for r in self.records:
            if not (type(r) == RecordWidget):
                continue
            ref = r.server_ref
            try:
                ServerManager(ref)
                self.available_servers.append(ref.name)
            except mysql.connector.errors.DatabaseError:
                errors.append(ref.name)

        if len(errors):
            QMessageBox.about(self, "Внимание", "Не удается выполнить подключение: %s" % ', '.join(errors))
        elif show_ok:
            QMessageBox.about(self, "Внимание", "Все подключения доступны ")


if __name__ == '__main__':
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)


    sys.excepthook = except_hook

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    #sys.exit(app.exec_())

