from __future__ import annotations
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject, QRegExp
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QRegExpValidator, QValidator
from interface.back.Filter import Filter, Relation


class FilterField(QWidget):
    def __init__(self, close_action: callable, available_attr: list[str], available_rel: list[str],
                 parent=None, _filter: Filter = None):
        super().__init__(parent)
        self.c2 = None
        self.r = None
        self.c1 = None
        self.available_attr = available_attr

        if _filter is None:
            if len(self.available_attr) > 0:
                _filter = Filter(available_attr[0], available_attr[0], Relation(available_rel[0]))

        self._filter = _filter
        self.close_action = close_action
        self.available_rel = available_rel
        self.create_ui()

    def create_ui(self):
        main_l = QHBoxLayout()
        self.setLayout(main_l)
        main_l.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        f = QFrame(self, objectName='fram')
        grid = QGridLayout()
        f.setLayout(grid)
        main_l.addWidget(f)
        grid.addWidget(
            QLabel('атрибут 1', f), 0, 0
        )
        grid.addWidget(
            QLabel('отношение', f), 0, 1
        )
        grid.addWidget(
            QLabel('атрибут 2', f), 0, 2
        )

        grid.addWidget(
            c1 := QComboBox(f), 1, 0
        )
        grid.addWidget(
            r := QComboBox(f), 1, 1
        )
        grid.addWidget(
            c2 := QComboBox(f), 1, 2
        )
        grid.addWidget(
            close := QPushButton('', f, objectName='close'), 0, 3
        )
        size = QSize(25, 25)
        close.setMinimumSize(size)
        close.setMaximumSize(size)
        close.clicked.connect(lambda e, self=self: self.close_action(self))

        self.c1 = c1
        self.c2 = c2
        self.r = r

        c1.addItems(self.available_attr)
        c2.addItems(self.available_attr)
        r.addItems(self.available_rel)

        c2.setEditable(True)
        c2.setValidator(QRegExpValidator(QRegExp('^[\\w\\.]+$')))

        c1.setCurrentText(self._filter.at1)
        c2.setCurrentText(self._filter.at2.replace("'", ""))
        r.setCurrentText(self._filter.relation.value)

    def get_filter(self) -> Filter | None:
        if len(self.available_attr) == 0:
            return None
        if self.c2.validator().validate(self.c2.currentText(), 0)[0] != QValidator.Acceptable:
            self.c2.setCurrentText(self.available_attr[0])

        ct = self.c2.currentText()
        if ct in self.available_attr:
            text = ct
        else:
            text = "'%s'" % ct

        self._filter = Filter(self.c1.currentText(), text, Relation(self.r.currentText()))
        return self._filter

    def set_available_attributes(self, new_av_at):
        pass

