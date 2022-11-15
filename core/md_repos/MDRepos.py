from __future__ import annotations

from core.md_repos.MDReposLoader import MDReposLoader
from core.utils.MDStructures import MDServer, AbstractMD
from core.utils.references import DBRef, ServerRef, DBId
from core.utils.ServerManager import ServerManager
import core.utils.query as q
from core.utils.schema.DBSchema import Node
from core.utils.schema.SchemaBuilder import SchemaBuilder
from typing import *
from mysql.connector import MySQLConnection
from core.md_extractor.MDExtractor import MDExtractor
from PyQt5.QtWidgets import *

from interface.back.LoadCommutator import LoadCommutator


class MDRepos:
    from core.utils.schema.DBSchema import DBSchema

    db_repos: DBRef
    server_manager: ServerManager
    connection: MySQLConnection

    def __init__(self, path: Optional = None):
        self.db_repos = MDReposLoader.read_configs(path)
        self.server_manager = ServerManager(self.db_repos.serverRef, database=self.db_repos.dbname)
        self.__check_repos_connection()

    def __check_repos_connection(self) -> None:
        self.connection = self.server_manager.get_connection()
        with self.connection.cursor():
            pass

    def get_available_servers(self) -> list[tuple[str, ServerRef]]:
        # id, ServerRef(ip, user, passwd, name)
        query = q.sql_get_servers
        results = self.server_manager.make_select(query)
        return [(r[0], ServerRef(*r[1:])) for r in results]

    def get_available_databases(self, server_id: str) -> list[tuple[str, str, str]]:
        query = q.sql_get_databases(server_id)
        results = self.server_manager.make_select(query)  # db_name, db_id, server_id
        return results

    def get_schema(self, db_id: DBId) -> DBSchema:
        return SchemaBuilder.build_by_md(self, db_id)

    def store_schema(self, server_id: str, schema: DBSchema) -> None:
        self.__insert_every_child(server_id, [schema.root])

    def __insert_every_child(self, parent_id: str, children: list[Node]):
        for child in children:
            child_id = self.insert_and_get_id(child.name, parent_id, SchemaBuilder.level_to_abstract(child.level))
            self.__insert_every_child(child_id, child.children)

    def insert_and_get_id(self, name: str, parent_id: str, table: Type[AbstractMD]) -> str:
        query = q.sql_insert_record(name, parent_id, table)
        return self.server_manager.execute_transaction(query)

    def reconnect(self) -> None:
        self.server_manager.close_connection()
        self.server_manager = ServerManager(self.db_repos.serverRef, database=self.db_repos.dbname)
        self.__check_repos_connection()

    def add_server(self, server_ref: ServerRef, commutator: LoadCommutator, reconnect: bool = False) -> None:
        if reconnect:
            self.reconnect()
        if self.has_server(server_ref.name):
            raise Exception('Server "%s" already exists' % server_ref.name)

        server_id = self.server_manager.execute_transaction(q.sql_insert_server(server_ref))
        extractor = MDExtractor(server_ref)
        schemas = [extractor.get_schema(db_name) for db_name in extractor.get_databases()]

        cnt = 0

        for schema in schemas:
            if reconnect:
                self.reconnect()
            self.store_schema(server_id, schema)
            cnt += 1
            commutator.get_message(int(100 * cnt / len(schemas)))

    def remove_server(self, server_ref: ServerRef) -> None:
        if not self.has_server(server_ref.name):
            raise Exception("Server '%s' don't exists" % server_ref.name)

        self.server_manager.execute_transaction(q.sql_delete_record(MDServer, server_ref.name))

    def has_server(self, server_name: str) -> bool:
        return len(self.server_manager.make_select(q.sql_server_exists(server_name))) > 0

    def get_server_by_name(self, name: str) -> MDServer:
        query = q.sql_get_server_by_name(name)
        res = self.server_manager.make_select(query)[0]  # list[(id, ip, username, passwd, name, port)][0]
        return q.record_to_server(res)
