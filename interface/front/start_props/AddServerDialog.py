from __future__ import annotations
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QRegExpValidator, QValidator
from PyQt5.QtCore import QRegExp
from PyQt5 import QtCore

IP, PORT, USER, PASSWORD, NAME = 'IP', 'PORT', 'USER', 'PASSWORD', 'NAME'


class AddServerDialog(QWidget):
    MAX_LEN_USER = 32

    def __init__(self, master: AppRunner):
        super(AddServerDialog, self).__init__()
        self.grid = None
        self.inputs = dict()
        self.master = master
        self.pbar = None
        self._want_to_close = True
        self.create_ui()

    def create_ui(self):
        self.setWindowTitle("Добавление сервера")
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        ipv4_pattern = '^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$'
        self.inputs[IP] = self._add_field(0, 'IP', input_validator=QRegExpValidator(QRegExp(ipv4_pattern)))
        iv = QIntValidator()
        iv.setRange(1, 65535)
        self.inputs[PORT] = self._add_field(1, 'port', input_validator=iv)
        self.inputs[USER] = self._add_field(
            2, 'Имя пользователя',
            input_validator=QRegExpValidator(QRegExp('^[a-zA-Z0-9\\_]{1,%d}$' % AddServerDialog.MAX_LEN_USER))
        )
        self.inputs[PASSWORD] = self._add_field(
            3, 'Пароль', input_validator=QRegExpValidator(QRegExp('^[a-zA-Z0-9\\_]*$')), passwd=True
        )
        self.inputs[NAME] = self._add_field(
            4, 'Имя сервера', input_validator=QRegExpValidator(QRegExp('^[a-zA-Z0-9\\_]+$'))
        )

        self.grid.addWidget(b := QPushButton('Добавить'), 5, 1)
        b.clicked.connect(lambda e, self=self: self._take_result())

        self.pbar = QProgressBar(self)
        self.grid.addWidget(self.pbar, 6, 0, 6, -1)

        self.show()
        self.pbar.hide()

    def _add_field(self, row: int, label: str, input_validator: QValidator = None, input_mask: str = None,
                   passwd: bool = False) -> QLineEdit:
        self.grid.addWidget(QLabel(label, self), row, 0)
        self.grid.addWidget(le := QLineEdit(), row, 1, )

        if passwd:
            le.setEchoMode(QLineEdit.Password)

        if not (input_validator is None):
            le.setValidator(input_validator)
        elif not (input_mask is None):
            le.setInputMask(input_mask)

        return le

    def _take_result(self):
        #text = self.inputs[NAME].text()
        #self.master.put_result({IP: '127.0.0.1', PORT: '3306', USER: 'root', PASSWORD: 'password', NAME: text if text else 'loc1'})
        #return
        res = dict()
        for k in self.inputs:
            if self.inputs[k].validator().validate(self.inputs[k].text(), 0)[0] != QValidator.Acceptable:
                QMessageBox.about(
                    self, "Ошибка", "Некорректный ввод: %s" % self.inputs[k].text()
                )
                return
        for k in self.inputs:
            res[k] = self.inputs[k].text()

        self.master.put_result(res)

    def set_closable(self, closable: bool):
        if closable == False:
            '''self.setWindowFlags(
                QtCore.Qt.Window |
                QtCore.Qt.CustomizeWindowHint |
                QtCore.Qt.WindowTitleHint |
                QtCore.Qt.WindowMinimizeButtonHint
            )'''
            self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            self.show()
            self.master.repaint_app()

        else:
            self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)
            self.show()
            self.master.repaint_app()

        self._want_to_close = closable

    def closeEvent(self, event):
        if self._want_to_close:
            self.master.put_result(dict())
            super().closeEvent(event)
        else:
            event.ignore()

