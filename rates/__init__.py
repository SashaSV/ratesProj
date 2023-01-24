from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
migrate = Migrate()
marshmallow = Marshmallow()

def create_app():
    from sqlalchemy import create_engine
    from sqlalchemy_utils import database_exists, create_database

    engine = create_engine("postgresql://postgres:111111@localhost:5432/convertor_test")
    if not database_exists(engine.url):
        create_database(engine.url)

    app = Flask(__name__)
    app.config['SECRET_KEY'] = "my key"
    app.config["SQLALCHEMY_DATABASE_URI"] = engine.url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        migrate.init_app(app, db)
        marshmallow.init_app(app)
    return app
