from __future__ import annotations
from typing import *

from core.utils.schema.DBSchema import DBSchema
from core.utils.MDStructures import *
from core.utils.schema.DBSchema import Node, Level
import core.utils.query as q


class SchemaBuilder:

    @staticmethod
    def build_by_md(md_repos: MDRepos, db_id: str) -> DBSchema:
        root = SchemaBuilder.__record_to_node(
            md_repos.server_manager.make_select_text(q.sql_get_full_record(db_id, MDDB))[0]
        )
        SchemaBuilder.__add_children(root, md_repos)
        return DBSchema(root)

    @staticmethod
    def __record_to_node(record: tuple[str, str, str], level: Level = None) -> Node:
        if level is None:
            level = Level.db
        return Node(record[2], level)

    @staticmethod
    def level_to_abstract(level: Level) -> Type[AbstractMD]:
        match level:
            case Level.db:
                return MDDB
            case Level.tab:
                return MDTable
            case Level.attr:
                return MDAttribute

    @staticmethod
    def __add_children(node: Node, node_id: str, md_repos: MDRepos) -> None:
        """
        Рекурсивная процедура поиска потомков node в базе данных и добавления их в node.children
        (для потомков также ищутся свои потомки)
        """
        if node.level == Level.attr:
            return
        else:
            child_level = node.level.child_level()
            assert child_level != Level.err

            child_records = md_repos.server_manager.make_select_text(
                q.sql_get_children(node_id, SchemaBuilder.level_to_abstract(child_level))
            )

            node.children = [SchemaBuilder.__record_to_node(record, child_level) for record in child_records]
            child_ids = [record[0] for record in child_records]
            for i in range(len(node.children)):
                SchemaBuilder.__add_children(node.children[i], child_ids[i], md_repos)
