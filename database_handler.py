from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from config import Config
import logging

logger = logging.getLogger(__name__)

def get_database_connection():
    """Get appropriate database connection based on configuration."""
    try:
        if Config.USE_MONGODB:
            client = MongoClient(Config.MONGODB_URI)
            return client.get_default_database()
        else:
            engine = create_engine(Config.DATABASE_URL)
            SessionLocal = sessionmaker(bind=engine)
            return SessionLocal()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise