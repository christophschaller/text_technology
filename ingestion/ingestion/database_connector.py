"""
This module contains the DatabaseConnector class to connect and load data into a
    mariadb service using sqlalchemy.
"""
from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from .tei_sql_schema import Base


class DatabaseConnector:
    """
    Class managing the connection to the database.
    """

    def __init__(self, user: str = None, password: str = None, host: str = None,
                 port: str = None, database: str = None):
        """
        Args:
            user: username to connect to the database service
            password: ...
            host: host url
            port: service port
            database: name of the target database
        """
        self.engine = None
        self.session = None

        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        self._connect()

    def _connect(self) -> None:
        """
        Initiate the connection to the database service and populate the necessary
        obj variables
        """
        uri = f"sqlite:///../{self.database}.db"
        if self.host:
            uri = f"mariadb+mariadbconnector://{self.user}:{self.password}" \
                  f"@{self.host}:{self.port}/{self.database}"
        self.engine = sa.create_engine(uri)

        session = sessionmaker(self.engine)
        # session.configure(bind=self.engine)
        self.session = session()

    def database_exists(self) -> bool:
        """
        Check if name of the database is in the list of existing databases.

        Returns: Boolean
        """
        # TODO: I feel like this is not working as I thought... The database seems to
        #  exists even if its schema isn't initialized
        existing_databases = [db[0] for db in self.engine.execute("SHOW DATABASES;")]
        return self.database in existing_databases

    def insert(self, element: Base) -> None:
        """
        Insert a db object.

        Args:
            element: db object inheriting from Base specified in tei_sql_schema
        """
        self.session.add(element)
        self.session.commit()

    def merge(self, element: Base) -> None:
        """
        Insert a db object.

        Args:
            element: db object inheriting from Base specified in tei_sql_schema
        """
        self.session.merge(element)
        self.session.commit()

    def bulk_insert(self, elements: List[Base]) -> None:
        """
        Insert a list of db objects.

        Args:
            elements: list of db objects inheriting from Base specified in
                tei_sql_schema
        """
        self.session.add_all(elements)
        self.session.commit()
