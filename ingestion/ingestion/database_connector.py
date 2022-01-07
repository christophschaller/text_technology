import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker


class DatabaseConnector:

    def __init__(self, user: str, password: str, host: str, port: str, database: str):
        self.engine = None
        self.session = None

        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        self._connect()

    def _connect(self):
        self.engine = sa.create_engine(
            f"mariadb+mariadbconnector://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )

        session = sessionmaker(self.engine)
        # session.configure(bind=self.engine)
        self.session = session()

    def database_exists(self):
        existing_databases = [db[0] for db in self.engine.execute("SHOW DATABASES;")]
        return self.database in existing_databases

    def insert(self, element):
        self.session.add(element)
        self.session.commit()

    def bulk_insert(self, elements):
        self.session.add_all(elements)
        self.session.commit()
