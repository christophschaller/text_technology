# Ingestion Microservice

This subfolder contains the **Ingestion Microservice** defining a ETL pipeline to  
**E**xtract TEI formatted xml corpora, **T**ransform them to sql objects with 
sqlalchemy and **L**oad them into a connected mariadb.

## Completeness
This won't parse the complete information contained in the source XML files.  
It will extract enough information to play around with the characters of the play,
their speeches, the acts etc. but won't capture every detail contained in the source.  
This is done to reduce the complexity of the parser, as this is a toy project.  

Also, the parsing is slow as f**k, this is caused by every item being inserted by 
its own. Which is a lazy and bad decision I made due to not wanting to spent time on 
bulk insertion.

## Quickstart

The prerequisites to develop for this service are the dependencies for [mariadb](https://mariadb.org/) and [sqlalchemy](https://www.sqlalchemy.org/).  
Also if you want to use the optional swaggerUi provided by connexion make sure to  
install connexion with the `connexion[swagger-ui]` flag.  
In this folder python requirements are managed using [poetry](https://python-poetry.org/).

 - [test_parse.py](./test_parse.py) offers a quick way to run the
[TeiXmlParser](./ingestion/tei_xml_parser.py).  
 - [app.py](./app.py) is the python entrypoint for the microservice.
    - When running the microservice locally env vars can be provided in `app.env` in 
      this directory.
      

## Docker

The [Dockerfile](Dockerfile) isn't finished.
