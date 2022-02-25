import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .views import main_views, query_views, result_views

# load env vars from .env file
load_dotenv("app.env")
# get env vars specifying database connection
DB_USER = os.getenv("TT_DB_USER")
DB_PASSWORD = os.getenv("TT_DB_PASSWORD")
DB_HOST = os.getenv("TT_DB_HOST")
DB_PORT = os.getenv("TT_DB_PORT")
DB_NAME = os.getenv("TT_DB_NAME")

if __name__ == '__main__':
    db = SQLAlchemy()
    migrate = Migrate()

    app = Flask(__name__)
    app.config.from_object({
        "SQLALCHEMY_DATABASE_URI": f"mariadb+mariadbconnector://{DB_USER}:{DB_PASSWORD}"
                                   f"@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)

    # blueprint
    app.register_blueprint(main_views.bp)
    app.register_blueprint(query_views.bp)
    app.register_blueprint(result_views.bp)
    app.run(port=5050)
