from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from interface.back.SortForm import SortForm, SortType


class SortField(QWidget):
    def __init__(self, close_action: callable, available_attr: list[str], parent=None, sort_form: SortForm = None):
        super().__init__(parent)
        self.attr = None

        if sort_form is None:
            # доступные атрибуты есть всегда
            sort_form = SortForm(available_attr[0], SortType.asc)

        self.sort_form = sort_form
        self.close_action = close_action
        self.available_attr = available_attr
        self.create_ui()

    def create_ui(self):
        main_l = QHBoxLayout()
        main_l.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setLayout(main_l)
        frame = QFrame(self, objectName='fram')
        main_l.addWidget(frame)

        grid = QGridLayout()
        frame.setLayout(grid)
        grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        grid.addWidget(QLabel('атрибут', frame), 0, 0)
        grid.addWidget(c := QComboBox(frame), 1, 0)
        self.attr = c
        c.addItems(self.available_attr)
        c.setCurrentText(self.sort_form.attr)

        r1, r2 = self._create_radio_btn(frame)
        grid.addWidget(r1, 0, 1)
        grid.addWidget(r2, 1, 1)

        grid.addWidget(close := QPushButton('', frame, objectName='close'), 0, 2)
        close.clicked.connect(lambda e, self=self: self.close_action(self))
        size = QSize(25, 25)
        close.setMinimumSize(size)
        close.setMaximumSize(size)

    def _create_radio_btn(self, parent):
        radio_button_1 = QRadioButton(SortType.asc.value, parent)
        #radio_button_1.setChecked(True)

        radio_button_2 = QRadioButton(SortType.desc.value, parent)

        if self.sort_form.sort_type == SortType.asc:
            radio_button_1.setChecked(True)
        else:
            radio_button_2.setChecked(True)

        button_group = QButtonGroup(parent)
        button_group.addButton(radio_button_1)
        button_group.addButton(radio_button_2)

        button_group.buttonClicked.connect(self._on_radio_button_clicked)

        return radio_button_1, radio_button_2

    def _on_radio_button_clicked(self, button):
        self.sort_form = SortForm(self.attr.currentText(), SortType(button.text()))

    def get_sort_form(self) -> SortForm | None:
        if len(self.available_attr) == 0:
            return None
        self.sort_form = SortForm(self.attr.currentText(), SortType(self.sort_form.sort_type))
        return self.sort_form
