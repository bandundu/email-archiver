import os
import logging
from config.config import config
from models.models import Base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Create a database engine and session
engine = create_engine(config.DATABASE_URL, pool_size=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_database():
    if not os.path.exists(config.DATABASE_URL):
        logging.info("Creating data directory")
        if not os.path.exists(config.DATBASE_DIR):
            os.makedirs(config.DATBASE_DIR)

        logging.debug("Database does not exist. Creating database..")

        # Create tables based on the defined models
        Base.metadata.create_all(bind=engine)

        # Create full-text search index
        with engine.connect() as connection:
            connection.execute(
                text(
                    'CREATE VIRTUAL TABLE IF NOT EXISTS emails_fts USING fts5(subject, sender, recipients, body, content="emails", content_rowid="id")'
                )
            )
            connection.execute(
                text(
                    "INSERT INTO emails_fts(rowid, subject, sender, recipients, body) SELECT id, subject, sender, recipients, body FROM emails"
                )
            )

        logging.info("Database initialized successfully.")
    else:
        logging.debug("Database already exists.")
