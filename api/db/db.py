from flask_sqlalchemy import SQLAlchemy

import os

# This file is used to initialize the database with the Flask app.
# There is most likely a better solution,
# but there was way too many circular dependencies otherwise
db = SQLAlchemy()


def initialize_db(app) -> SQLAlchemy:
    """Initialize the database with the Flask app."""

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        os.getenv('DATABASE_URL', 'sqlite:///:memory:'))
    app.config["SQLALCHEMY_ECHO"] = False

    db.init_app(app)

    with app.app_context():
        # db.drop_all()  # Drop all tables if they exist
        db.create_all()
    return db
