from flask_sqlalchemy import SQLAlchemy

# This file is used to initialize the database with the Flask app.
# There is most likely a better solution,
# but there was way too many circular dependencies otherwise
db = SQLAlchemy()


def initialize_db(app) -> SQLAlchemy:
    """Initialize the database with the Flask app."""

    db.init_app(app)

    with app.app_context():
        # db.drop_all()  # Drop all tables if they exist
        db.create_all()
    return db
