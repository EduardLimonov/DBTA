import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from threading import Thread


class TableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tableView = None
        self.model = None
        self.init_ui()

    def init_ui(self):
        self.setMinimumHeight(950)
        main_l = QHBoxLayout()
        self.setLayout(main_l)
        self.model = QStandardItemModel(self)
        main_frame = QFrame(self, objectName='fram')
        main_l.addWidget(main_frame)
        lay = QHBoxLayout()
        main_frame.setLayout(lay)
        self.tableView = QTableView(main_frame)
        lay.addWidget(self.tableView)
        self.tableView.setModel(self.model)
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def set_vals(self, values: list[tuple[str, ...]], column_names: list[str]):
        self.model.clear()
        if len(values):
            self.model.setColumnCount(len(values[0]))

        self.model.setHorizontalHeaderLabels(column_names)

        Thread(target=lambda: self.__insert_vals(values)).start()
        self.tableView.resizeRowsToContents()
        #self.tableView.resizeColumnsToContents()

        self.update()

    def __insert_vals(self, values):
        for _tuple in values:
            new = [QStandardItem(str(val)) for val in _tuple]
            self.model.appendRow(new)

        self.tableView.resizeRowsToContents()
        self.tableView.resizeColumnsToContents()
        self.update()


