from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from interface.back.JoinForm import JoinType, JoinForm
from interface.back.PathManager import PathManager
from core.utils.schema.DBSchema import Level
from interface.front.DataViewer.navigator.Navigator import NavigatorWidget


class JoinField(QWidget):
    change_join_signal = pyqtSignal()

    def __init__(self, parent, available_attrs: list[str], available_connections: list[str],
                 right_path_manager: PathManager, close_action: callable):
        super().__init__(parent)
        self.status = JoinType.inner
        self.c2 = None
        self.c1 = None
        self.condition_frame = None
        self.nav = None
        self.available_attrs = available_attrs
        #self.left_path_manager = left_path_manager
        self.right_path_manager = right_path_manager
        self.close_action = close_action
        self.available_connections = available_connections

        #self.left_path_manager.changed_path.connect(self.change_path)
        self.right_path_manager.changed_path.connect(self.change_path)
        self.make_ui()
        self.change_join_signal.emit()

    def make_ui(self):
        main_l = QVBoxLayout()
        self.setLayout(main_l)
        frame = QFrame(self, objectName='fram')
        main_l.addWidget(frame)

        frame_l = QGridLayout()
        frame_l.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        frame.setLayout(frame_l)
        self.nav = NavigatorWidget(self.right_path_manager, None, self.available_connections, frame, False, )
        frame_l.addWidget(self.nav, 0, 0)

        frame_l.addWidget(close := QPushButton('', frame, objectName='close'), 0, 2)
        close.clicked.connect(lambda e, self=self: (self.close_action(self), self.change_join_signal.emit()))
        size = QSize(25, 25)
        close.setMinimumSize(size)
        close.setMaximumSize(size)

        self.condition_frame = condition_frame = QFrame(frame, objectName='fram')
        frame_l.addWidget(condition_frame, 1, 0, 1, -1)
        condition_lay = QHBoxLayout()
        condition_frame.setLayout(condition_lay)
        condition_lay.addWidget(QLabel('условие: ', condition_frame))
        condition_lay.addWidget(c1 := QComboBox(condition_frame))
        condition_lay.addWidget(eq := QLabel('=', condition_frame))
        eq.setAlignment(Qt.AlignCenter)
        condition_lay.addWidget(c2 := QComboBox(condition_frame))

        self.c1 = c1
        self.c2 = c2
        c1.addItems(self.available_attrs)

        w = QWidget(frame)
        b0, b1, b2 = self._create_radio_btn(w)
        l = QVBoxLayout()
        w.setLayout(l)
        l.addWidget(b0)
        l.addWidget(b1)
        l.addWidget(b2)
        frame_l.addWidget(w, 0, 1)
        l.setAlignment(Qt.AlignTop)

        self.change_path()

    def _create_radio_btn(self, parent):
        radio_button_0 = QRadioButton(JoinType.inner.value, parent)
        radio_button_0.setChecked(True)

        radio_button_1 = QRadioButton(JoinType.left.value, parent)

        radio_button_2 = QRadioButton(JoinType.right.value, parent)

        button_group = QButtonGroup(parent)
        button_group.addButton(radio_button_0)
        button_group.addButton(radio_button_1)
        button_group.addButton(radio_button_2)

        button_group.buttonClicked.connect(self._on_radio_button_clicked)

        return radio_button_0, radio_button_1, radio_button_2

    def _on_radio_button_clicked(self, button):
        self.status = button.text()
        self.change_join_signal.emit()

    def change_path(self):
        self.change_join_signal.emit()

        if self.right_path_manager.level == Level.attr:
            self.condition_frame.setEnabled(True)
            self.c2.clear()
            self.c2.addItems(self.right_path_manager.get_list_of_children())
        else:
            self.condition_frame.setEnabled(False)

    def is_done(self) -> bool:
        return self.right_path_manager.level == Level.attr

    def get_joined_attributes(self):
        return self.right_path_manager.get_list_of_children()

    def get_join_form(self) -> JoinForm | None:
        if not self.is_done():
            return None
        server, path = self.right_path_manager.get_str_state()
        return JoinForm(self.c1.currentText(), '%s.%s.%s' % (server, '.'.join(path), self.c2.currentText()),
                        JoinType(self.status))

