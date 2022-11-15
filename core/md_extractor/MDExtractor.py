from __future__ import annotations
from core.utils.MDStructures import MDDB, MDTable
from core.utils.ServerManager import ServerManager
from core.utils.references import ServerRef
from mysql.connector import MySQLConnection
from core.utils.schema.DBSchema import DBSchema, Node, Level
import core.utils.query as q


class MDExtractor:
    server_manager: ServerManager
    connection: MySQLConnection

    def __init__(self, server_ref: ServerRef):
        self.server_manager = ServerManager(server_ref)
        self.connection = self.server_manager.get_connection()

    def get_databases(self) -> list[str]:
        # список названий доступных БД
        query = q.sql_show_dbs
        return [r[0] for r in self.server_manager.make_select(query)]

    def get_schema(self, db_name: str) -> DBSchema:
        root = Node(db_name, Level.db)
        self.__find_every_child(root)
        return DBSchema(root)

    def __find_every_child(self, node: Node) -> None:
        base_name = node.name
        for table in self.server_manager.make_select(q.sql_show_children(node.name, MDDB)):
            child_table = Node(table[0], Level.tab)
            node.children.append(child_table)
            full_name = '%s.%s' % (base_name, child_table.name)

            for attr in self.server_manager.make_select(q.sql_show_children(full_name, MDTable)):
                child_attr = Node(attr[0], Level.attr)
                child_table.children.append(child_attr)


