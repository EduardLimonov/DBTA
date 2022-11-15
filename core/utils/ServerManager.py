from core.utils.references import ServerRef
from mysql.connector import connect, MySQLConnection
import core.utils.query as q


class ServerManager:
    server_ref: ServerRef
    connection: MySQLConnection

    def __init__(self, server_ref: ServerRef, **kwargs):
        self.connection = None
        self.server_ref = server_ref
        self.connect(**kwargs)
        '''if federated:
            self.connect(**kwargs, option_files=['C:\\ProgramData\\MySQL\\MySQL Server 8.0\\my.ini'])
        else:
            self.connect(**kwargs)
            print(self.make_select("SHOW ENGINES"))'''

    def connect(self, **kwargs) -> None:
        self.connection = connect(
            host=self.server_ref.address,
            user=self.server_ref.user,
            password=self.server_ref.password,
            port=self.server_ref.port,
            **kwargs
        )

    def make_select(self, query: str) -> list[tuple] | list[str]:
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        return list(results)

    def execute_transaction(self, query: q.Query | list[q.Query]) -> str:
        # возвращает id последней вставленной записи
        if type(query) == q.Query:
            statements = [query]
        else:
            statements = query
        with self.connection.cursor() as cursor:
            for s in statements:
                cursor.execute(s)
            cursor.execute(q.sql_last_inserted_id)
            results = cursor.fetchall()
            self.connection.commit()

        return results[0][0]

    def get_connection(self) -> MySQLConnection:
        return self.connection

    def close_connection(self) -> None:
        if not (self.connection is None):
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close_connection()


if __name__ == '__main__':
    print('')
