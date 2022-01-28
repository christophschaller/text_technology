"""
This module connects to a running mariadb service, loads a xml TEI corpus and tries to
run the ETL pipeline.
"""
import os

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

# connect to db and initialize parser
PARSER = TeiXmlParser(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

if __name__ == '__main__':
    # create defined schema in database
    # this is probably pretty dumb to do on every startup...
    # TODO: only do this when no database is present
    Base.metadata.create_all(PARSER.engine)

    # load corpus from data dir and initiate parser
    with open("../data/corpus.xml") as file_pointer:
        xml_string = file_pointer.read()
        PARSER.parse(xml_string)
