# Text Technology

This project is part of the Text Technology course at IMS.  
We plan to build a system to ingest XML corpora into a DB.  
Any corpus stored in the Database should then be explorable using a small webapp.


## Participants

 - ### [Kazem Abdi Dehnoei]()
 - ### [Dojun Park]()
 - ### [Chris Schaller]()


## Segments

#### [Ingestion / ETL Pipeline](./ingestion/README.md)
Microservice to extract TEI formatted xml corpora, transform them to sql objects 
and load them into a database.

#### [App](/app)
Webapp to explore the stored corpora.


## Quickstart

### With SQLite (Default)
1. Make sure all dependencies are installed according to the requirement files: 
[ingestion requirements](/ingestion/requirements.txt),
   [webapp requirements](/app/requirements.txt).
1. Place the **Two Gentlemen of Verona** TEI corpus (default filename _corpus.xml_) 
   in the path _/data/corpus.xml_ 
1. Run [local_parse.py](/ingestion/local_parse.py) to parse the corpus into the db.
1. Run `flask run` from the root directory to run the webapp.

### With MariaDB
1. Make sure all required env vars are available through the .env files defined in 
   [docker-compose.yaml](./docker-compose.yaml)
1. Run `docker-compose up` to start mariadb and ingestion service.  
   The webapp is not yet compatible integrated in the docker-compose setup.
1. Pass the **Two Gentlemen of Verona** TEI corpus as file or raw text to the 
   _/ingest_ endpoint of the ingestion service available at port 8080.
1. Run `flask run` from the [app](/app) directory to also start the webapp.   