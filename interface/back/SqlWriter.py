from interface.back.Filter import Filter
from interface.back.JoinForm import JoinForm
from interface.back.SortForm import SortForm, SortType
from core.utils.query import Query
import core.utils.query as q
from core.utils.references import ServerRef


class SqlWriter:
    @staticmethod
    def __extract_path(path: list[str]) -> str:
        return '.'.join(path)

    @staticmethod
    def __correct_name(server_name: str, main_db_name: str, full_path: str) -> str:
        path_list = full_path.split('.')
        if ("'" in full_path or '"' in full_path) and len(path_list) == 1:
            return path_list[0]
        if path_list[0] == server_name:
            return '.'.join(path_list[1:])
        else:
            return '%s.%s.%s' % (main_db_name, SqlWriter.__create_table_name(path_list), path_list[-1])

    @staticmethod
    def __extract_filters(server_name: str, db_name: str, filters: list[Filter | None]) -> str:
        filters = list(dict.fromkeys(filters))
        if len(filters) == 0:
            return ''

        res = 'WHERE '
        sentences = ['%s %s %s' % (SqlWriter.__correct_name(server_name, db_name, f.at1),
                                   f.relation.value,
                                   SqlWriter.__correct_name(server_name, db_name, f.at2)) for f in filters]
        res += ' AND '.join(sentences)
        return res

    @staticmethod
    def __sort_type_to_sql(sort_type: SortType) -> str:
        match sort_type:
            case SortType.desc:
                return 'DESC'
            case SortType.asc:
                return 'ASC'

    @staticmethod
    def __extract_sort(server_name: str, db_name: str, sorts: list[SortForm | None]) -> str:
        sorts = list(dict.fromkeys(sorts))
        if len(sorts) == 0:
            return ''

        res = 'ORDER BY '
        sentences = ['%s %s ' % (SqlWriter.__correct_name(server_name, db_name, f.attr),
                                 SqlWriter.__sort_type_to_sql(f.sort_type)) for f in sorts]
        res += ', '.join(sentences)
        return res

    @staticmethod
    def __extract_columns(columns: list[str] | None = None) -> str:
        if columns is None:
            return '*'
        return ', '.join(columns)

    @staticmethod
    def __create_table_name(path: list[str]) -> str:
        # если path = сервер.бд.таблица.атрибут
        if len(path) == 4:
            path = path[: -1]
        res = '_'.join(path)
        if len(res) > 64:
            res = '%s_%s' % (path[0], path[-1])
        if len(res) > 64:
            res = '%s_%s' % (str(hash(res)), path[-1])
        if len(res) > 64:
            h = str(hash(res))[:4]
            res = '%s_%s' % (h, res[: 64 - 7])
        return res

    @staticmethod
    def __prepare_fed_tables(db_name, joins: list[JoinForm], get_db_create_func: callable, server_ref: ServerRef) \
            -> tuple[list[Query], list[str]]:
        server_name = server_ref.name
        if len(joins) == 0:
            return [], []
        res = [q.sql_use_database(db_name)]
        new_table_names = []
        for join in joins:
            right_path = join.right_column.split('.')
            if right_path[0] != server_name:
                create_tab: str = get_db_create_func(right_path[0], '.'.join(right_path[1:-1]))
                i = create_tab.find('ENGINE=')
                i_start = i + len('ENGINE=')
                i_end = create_tab.find(' ', i_start)

                #i_table_name_start = len('CREATE TABLE `')
                #i_table_name_end = create_tab.find()
                new_table_name = '%s.%s' % (db_name, SqlWriter.__create_table_name(right_path))
                remote_db_name, remote_table_name = right_path[-3: -1]
                connection_info = "\nCONNECTION='mysql://%s:%s@%s:%s/%s/%s'" % \
                                  (server_ref.user, server_ref.password, server_ref.address, server_ref.port,
                                   remote_db_name, remote_table_name)

                res.append(create_tab.replace(create_tab[i_start: i_end], 'FEDERATED', 1)
                           .replace(right_path[-2], new_table_name, 1).replace('`', '', 2) + connection_info)
                new_table_names.append(new_table_name)

                join.right_column = '%s.%s' % (new_table_name, right_path[-1])

            # возможно, что левый атрибут является атрибутом из ранее присоединенной таблицы с другого сервера
            # (но мы ранее добавили ее FEDERATED представление => нужно поменять имя таблицы на новое FEDERATED имя)
            left_path = join.left_column.split('.')
            if left_path[0] != server_name:
                left_name = '%s.%s.%s' % (db_name, SqlWriter.__create_table_name(left_path), left_path[-1])
                join.left_column = left_name
                left_path = join.left_column.split('.')

            right_path = join.right_column.split('.')
            if len(right_path) == 4:  # содержит имя сервера
                join.right_column = '.'.join(right_path[1:])
            if len(left_path) == 4:  # содержит имя сервера
                join.left_column = '.'.join(left_path[1:])

        return res, new_table_names

    @staticmethod
    def __extract_joins(joins: list[JoinForm]) -> str:
        if len(joins) == 0:
            return ''
        res = ''
        for join in joins:
            join_table = join.right_column.split('.')[: - 1]
            res += '\n\t%s JOIN %s ON %s = %s' % \
                   (join.type.value, '.'.join(join_table), join.left_column, join.right_column)

        return res

    @staticmethod
    def make_select_text(server_name: str, path: list[str], joins: list[JoinForm], filters: list[Filter | None],
                         sorts: list[SortForm | None], get_db_create_func: callable, server_ref: ServerRef,
                         columns: list[str] = None) \
            -> tuple[list[Query], Query, list[str]]:
        # prepare: list of statements to create federated tables
        # res -- select query
        # new_table_names -- list of names of new tables, which are creating in prepare list
        prepare, new_table_names = SqlWriter.__prepare_fed_tables(path[0], joins, get_db_create_func, server_ref)
        res = "SELECT %s FROM %s " % (SqlWriter.__extract_columns(columns), SqlWriter.__extract_path(path))

        db_name = path[0]
        if len(joins):
            res += '%s' % SqlWriter.__extract_joins(joins)
        if len(filters):
            res += '\n%s' % SqlWriter.__extract_filters(server_name, db_name, filters)
        if len(sorts):
            res += '\n%s' % SqlWriter.__extract_sort(server_name, db_name, sorts)

        return prepare, res, new_table_names

    @staticmethod
    def remove_table_statement(table_name: str) -> Query:
        # table_name -- db.table
        return 'DROP TABLE %s' % table_name
