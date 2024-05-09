import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    DATBASE_DIR = os.getenv("DATABASE_DIR")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    # Add more configuration variables as needed

config = Config()