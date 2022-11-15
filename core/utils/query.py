from core.utils.MDStructures import *
from typing import *

from core.utils.references import ServerRef

Query = str

sql_get_servers = 'SELECT * FROM %s' % MDServer.tname
sql_last_inserted_id = 'SELECT LAST_INSERT_ID()'
sql_show_dbs = 'SHOW DATABASES'


def sql_get_databases(server_id: str) -> Query:
    return 'SELECT %s, %s, %s FROM  %s WHERE %s = %s' % (MDDB.name, MDDB.id, MDDB.id_parent,
                                                         MDDB.tname, MDDB.id_parent, server_id)


def sql_get_children(parent_id: str, child: Type[AbstractMD]) -> Query:
    return 'SELECT * FROM %s WHERE %s = %s' % (child.tname, child.id_parent, parent_id)  # id, id_parent, name


def sql_get_full_record(id_record: str, record_table: Type[AbstractMD]) -> Query:
    return 'SELECT * FROM %s WHERE %s = %s' % (record_table.tname, record_table.id, id_record)


def sql_get_server_by_name(server_name: str) -> Query:
    return 'SELECT * FROM %s WHERE %s = "%s"' % (MDServer.tname, MDServer.name, server_name)


def sql_insert_server(server_ref: ServerRef) -> Query:
    return "INSERT %s (%s, %s, %s, %s, %s) VALUES ('%s', '%s', '%s', '%s', '%s')" % \
           (MDServer.tname, MDServer.address, MDServer.user, MDServer.passwd, MDServer.name, MDServer.port,
            server_ref.address, server_ref.user, server_ref.password, server_ref.name, server_ref.port)


def sql_delete_record(from_table: Type[AbstractMD], name: str) -> Query:
    return 'DELETE FROM %s WHERE %s = "%s"' % \
           (from_table.tname, from_table.name, name)


def sql_server_exists(sname: str) -> Query:
    return 'SELECT * FROM %s WHERE %s = "%s"' % (MDServer.tname, MDServer.name, sname)


def sql_get_server_id(server_ref: ServerRef) -> Query:
    return 'SELECT %s FROM %s WHERE %s = "%s"' % (MDServer.id, MDServer.tname, MDServer.name, server_ref.name)


def sql_insert_record(name: str, parent_id: str, table: Type[AbstractMD]) -> Query:
    return 'INSERT %s (%s, %s) VALUES ("%s", "%s")' % (table.tname, table.id_parent, table.name, parent_id, name)


def sql_show_children(parent_name: str, parent_type: Type[AbstractMD]) -> Query:
    match parent_type.tname:
        case MDDB.tname:
            return 'SHOW TABLES FROM %s' % parent_name
        case MDTable.tname:
            return 'SHOW COLUMNS FROM %s' % parent_name


def sql_get_table_create_code(table_name) -> Query:
    return 'SHOW CREATE TABLE %s' % table_name


def record_to_server(record: tuple[str, ...]) -> MDServer:
    return MDServer(MDServer.tname, record[0], None, record[4], record[1], record[2], record[3], record[5])


def sql_use_database(db_name: str) -> Query:
    return 'USE %s' % db_name
