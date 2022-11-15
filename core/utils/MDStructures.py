from dataclasses import dataclass
from typing import Type

from core.utils.schema.DBSchema import Level


@dataclass
class AbstractMD:
    tname: str

    id: str = None
    id_parent: str | None = None
    name: str = None


@dataclass
class MDServer(AbstractMD):
    tname: str = '_Server'

    id: str = '%s._id' % tname
    address: str = '%s._address' % tname
    user: str = '%s._user' % tname
    passwd: str = '%s._passwd' % tname
    name: str = '%s._name' % tname
    port: str = '%s._port' % tname

    id_parent = None


@dataclass
class MDDB(AbstractMD):
    tname: str = '_DB'

    id: str = '%s._id' % tname
    id_parent: str = '%s._id_parent' % tname
    name: str = '%s._name' % tname


@dataclass
class MDTable(AbstractMD):
    tname: str = '_Table'

    id: str = '%s._id' % tname
    id_parent: str = '%s._id_parent' % tname
    name: str = '%s._name' % tname


@dataclass
class MDAttribute(AbstractMD):
    tname: str = '_Attribute'

    id: str = '%s._id' % tname
    id_parent: str = '%s._id_parent' % tname
    name: str = '%s._name' % tname


@dataclass
class MDGroup:
    tname: str = '_Group'

    id_group: str = '%s._id_group' % tname
    id_attr: str = '%s._id_attr' % tname


def level_to_abstract(level: Level) -> Type[AbstractMD]:
    match level:
        case Level.db:
            return MDDB
        case Level.tab:
            return MDTable
        case Level.attr:
            return MDAttribute


def abstract_to_level(ab: Type[AbstractMD]) -> Level:
    for level in (Level.server, Level.db, Level.tab, Level.attr):
        if level_to_abstract(level) == ab:
            return level
