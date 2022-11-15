from typing import *
import os
from core.utils.references import ServerRef, DBRef


class MDReposLoader:
    """
    config file:
    ip
    user
    password
    port
    db_name
    """
    DEFAULT_PATH: str = 'resource/metadata_storage'  #'../../resource/metadata_storage'
    METADATA_REPOS_NAME: str = 'Metadata repository'

    @staticmethod
    def read_configs(path: Optional[str]) -> DBRef:
        if path is None:
            path = MDReposLoader.DEFAULT_PATH

        if not (os.path.exists(path) and os.path.isfile(path)):
            raise Exception('Incorrect path to configuration file: %s' % path)

        with open(path, 'r') as f:
            lines = f.readlines()

        lines = [line.replace('\n', '') for line in lines]

        try:
            server_ref = ServerRef(*lines[: 3], MDReposLoader.METADATA_REPOS_NAME, lines[3])
        except Exception:
            raise Exception('Invalid format of configuration file')

        return DBRef(server_ref, lines[-1])

