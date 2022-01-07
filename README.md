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

#### [Backend]()
Microservice offering endpoints to query the corpora stored in the database.

#### [Frontend]()
Webapp to explore the stored corpora.


## Quickstart
 1. Make sure all required env vars are available through the .env files defined in 
[docker-compose.yaml](./docker-compose.yaml)  
 1. Run `docker-compose up`