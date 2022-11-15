from __future__ import annotations
from dataclasses import dataclass, field
from typing import *
from enum import Enum


class Level(Enum):
    server = -1
    db = 0
    tab = 1
    attr = 2
    err = 3

    def child_level(self) -> Level:
        match self:
            case Level.server:
                return Level.db
            case Level.db:
                return Level.tab
            case Level.tab:
                return Level.attr
            case Level.attr:
                return Level.err

    def parent_level(self) -> Level:
        match self:
            case Level.server:
                return Level.err
            case Level.db:
                return Level.server
            case Level.tab:
                return Level.db
            case Level.attr:
                return Level.tab


@dataclass
class Node:
    #id: str
    #parent: Union[Node, str]
    name: str
    level: Level
    children: list[Node] = field(default_factory=list)

    '''@property
    def parent_id(self) -> str:
        if type(self.parent) == str:
            return self.parent
        return self.parent.id'''


@dataclass
class DBSchema:
    root: Node
