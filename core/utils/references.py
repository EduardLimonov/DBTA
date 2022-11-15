from __future__ import annotations
from typing import *

from dataclasses import dataclass

from core.utils.MDStructures import MDServer


@dataclass(frozen=True)
class ServerRef:
    address: str
    user: str
    password: str
    name: Optional[str] = None
    port: str = '3306'

    @staticmethod
    def create_server_ref(server_md: MDServer) -> ServerRef:
        return ServerRef(server_md.address, server_md.user, server_md.passwd, server_md.name, server_md.port)


@dataclass
class DBRef:
    serverRef: ServerRef
    dbname: str


ServerId = DBId = str
