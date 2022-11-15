from typing import Type
from PyQt5.QtCore import QObject, pyqtSignal
from core.md_repos.MDRepos import MDRepos
from core.utils.MDStructures import AbstractMD, abstract_to_level, level_to_abstract, MDServer
from core.utils.schema.DBSchema import Level
import core.utils.query as q


class PathManager(QObject):
    state: list[AbstractMD]
    level: Level  # уровень, на котором ищутся потомки (на 1 ниже уровня нашего взгляда)
    repos: MDRepos
    actual_children: list[AbstractMD]
    deprecated_paths: list[str]

    changed_path = pyqtSignal()

    def __init__(self, repos: MDRepos, deprecated_paths: list[str] = None):
        super().__init__()
        if deprecated_paths is None:
            deprecated_paths = []
        self.state = []
        self.deprecated_paths = deprecated_paths
        self.level = Level.server
        self.repos = repos
        self.__update_children()

    def __find_child_by_name(self, name: str) -> AbstractMD:
        for ch in self.actual_children:
            if ch.name == name:
                return ch

    def move_up(self):
        if self.level != Level.server:
            self.state.pop(len(self.state) - 1)
            self.level = self.level.parent_level()
            self.__update_children()
            self.changed_path.emit()

    def move_down(self, where: str):
        child = self.__find_child_by_name(where)
        self.level = self.level.child_level()
        self.state.append(child)
        self.__update_children()
        self.changed_path.emit()

    def get_full_path(self) -> str:
        return '.'.join([s.name for s in self.state])

    def get_list_of_children(self, full=False) -> list[str]:
        full_path = self.get_full_path()
        if full:
            return [
                '%s.%s' % ('.'.join((s.name for s in self.state)), ch.name) for ch in self.actual_children
                if '%s.%s' % (full_path, ch.name) not in self.deprecated_paths
            ]
        return [ch.name for ch in self.actual_children if '%s.%s' % (full_path, ch.name) not in self.deprecated_paths]

    def get_level(self) -> Level:
        return self.level

    def get_str_state(self) -> tuple[str, list[str]] | None:
        if self.level == Level.server:
            return None
        else:
            path = [] if len(self.state) == 1 else self.state[1:]
            return self.state[0].name, [p.name for p in path]

    def __update_children(self):
        if len(self.state):
            parent_id = self.state[-1].id
            child_type: Type[AbstractMD] = level_to_abstract(self.level)
            query = q.sql_get_children(parent_id, child_type)
            res = self.repos.server_manager.make_select(query)  # list[(id, id_parent, name)]

            self.actual_children = [child_type(child_type.tname, *record) for record in res]
        else:
            query = q.sql_get_servers
            res = self.repos.server_manager.make_select(query)  # list[(id, ip, username, passwd, name, port)]
            self.actual_children = [
                q.record_to_server(record) for record in res
            ]
