from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Relation(Enum):
    eq = '='
    less = '<'
    greater = '>'
    le = '<='
    ge = '>='
    ne = '!='


@dataclass(frozen=True)
class Filter:
    at1: str = None
    at2: str = None
    relation: Relation = None

    def __str__(self) -> str:
        return '%s|%s|%s' % (self.at1, self.at2, self.relation.value)

    @staticmethod
    def from_str(string: str) -> Filter:
        a1, a2, r = string.split('|')
        return Filter(a1, a2, Relation(r))

