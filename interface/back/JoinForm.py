from dataclasses import dataclass
from enum import Enum


class JoinType(Enum):
    inner = 'INNER'
    left = 'LEFT'
    right = 'RIGHT'


@dataclass#(frozen=True)
class JoinForm:
    #table_to_join_path: str
    left_column: str
    right_column: str
    type: JoinType


