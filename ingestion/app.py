"""
This module connects to a running mariadb service, starts a flask microservice
according to the openapi3 schema defined in $TT_APP_SPEC_DIR/$TT_APP_SPEC_FILE
using connexion.
This service should the offer at least one endpoint to start the ETL pipeline for a
provided TEI xml corpus.
"""
import os

import connexion
from dotenv import load_dotenv

from ingestion.tei_xml_parser import TeiXmlParser
from ingestion.tei_sql_schema import Base

# load env vars from .env file
load_dotenv("app.env")
# get env vars specifying database connection
DB_USER = os.getenv("TT_DB_USER")
DB_PASSWORD = os.getenv("TT_DB_PASSWORD")
DB_HOST = os.getenv("TT_DB_HOST")
DB_PORT = os.getenv("TT_DB_PORT")
DB_NAME = os.getenv("TT_DB_NAME")
# get env vars specifying service
APP_SPEC_DIR = os.getenv("TT_APP_SPEC_DIR", "openapi/")
APP_SPEC_FILE = os.getenv("TT_APP_SPEC_FILE")
APP_PORT = int(os.getenv("TT_APP_PORT"))

# connect to db and initialize parser
PARSER = TeiXmlParser(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)


def ingest(xml_string=None):
    PARSER.parse(xml_string)


if __name__ == '__main__':
    # create defined schema in database
    # this is probably pretty dumb to do on every startup...
    # TODO: only do this when no database is present
    Base.metadata.create_all(PARSER.engine)

    app = connexion.App(
        __name__,
        specification_dir=APP_SPEC_DIR
    )
    app.add_api(APP_SPEC_FILE)
    # TODO: it would probably be great to run this with gunicorn instead of the flask
    #  wsgi
    app.run(port=APP_PORT)
