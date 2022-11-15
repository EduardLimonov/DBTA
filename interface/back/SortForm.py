from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class SortType(Enum):
    asc = 'по возрастанию'
    desc = 'по убыванию'


@dataclass(frozen=True)
class SortForm:
    attr: str
    sort_type: SortType

    def __str__(self) -> str:
        return '%s|%s' % (self.attr, self.sort_type.value)

    @staticmethod
    def from_str(string: str) -> SortForm:
        a, st = string.split('|')
        return SortForm(a, SortType(st))
