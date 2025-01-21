from typing import Optional, Dict, List
import logging
from datetime import datetime
from pymongo import MongoClient
import os
from urllib.parse import quote_plus, urlparse, parse_qs
import certifi
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_mongodb_uri() -> str:
    """Get MongoDB URI from environment variable with proper encoding."""
    try:
        uri = os.getenv('MONGODB_URI')
        if not uri:
            raise ValueError("MONGODB_URI environment variable is not set")
            
        # Clean the URI
        uri = uri.strip().strip('"\'')
        
        # Parse URI components
        parsed = urlparse(uri)
        
        # Validate URI scheme
        if parsed.scheme not in ('mongodb', 'mongodb+srv'):
            raise ValueError(f"Invalid MongoDB URI scheme: {parsed.scheme}")
        
        # Extract and validate components
        username = parsed.username or ''
        password = parsed.password or ''
        hostname = parsed.hostname
        
        if not hostname:
            raise ValueError("MongoDB URI missing hostname")
            
        if not username or not password:
            raise ValueError("MongoDB URI missing credentials")
        
        # URL encode username and password
        safe_username = quote_plus(username)
        safe_password = quote_plus(password)
        
        # Reconstruct the URI with encoded credentials
        if parsed.port:
            base_uri = f"{parsed.scheme}://{safe_username}:{safe_password}@{hostname}:{parsed.port}"
        else:
            base_uri = f"{parsed.scheme}://{safe_username}:{safe_password}@{hostname}"
        
        # Add database name and query parameters
        query_params = {
            'retryWrites': 'true',
            'w': 'majority',
            'authSource': 'admin',
            'ssl': 'true'
        }
        
        # Add existing query parameters
        if parsed.query:
            existing_params = parse_qs(parsed.query)
            query_params.update({k: v[0] for k, v in existing_params.items()})
            
        # Build query string
        query_string = '&'.join(f"{k}={v}" for k, v in query_params.items())
            
        # Construct final URI
        final_uri = f"{base_uri}/movie?{query_string}"
            
        logger.info("MongoDB URI processed successfully")
        return final_uri
        
    except Exception as e:
        logger.error(f"Error processing MongoDB URI: {str(e)}")
        raise

try:
    # Get MongoDB URI with validation
    MONGODB_URI = get_mongodb_uri()
    logger.info("Got MongoDB URI")
    
    # Create MongoDB client with robust settings
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        tlsCAFile=certifi.where(),
        retryWrites=True,
        maxPoolSize=50,
        minPoolSize=10,
        maxIdleTimeMS=50000,
        waitQueueTimeoutMS=5000
    )
    logger.info("Created MongoDB client")
    
    # Test connection
    client.admin.command('ping')
    logger.info("Successfully pinged MongoDB server")
    
    # Get database
    db = client.movie  # Use the database name directly
    logger.info(f"Connected to database: {db.name}")
    
    # Collections
    users = db.users
    movies = db.movies
    files = db.files
    statistics = db.statistics
    
    # Create indexes
    users.create_index("telegram_id", unique=True)
    movies.create_index("stream_id", unique=True)
    movies.create_index("title")
    files.create_index("stream_id", unique=True)
    
    logger.info("Successfully initialized all collections and indexes")
    
except Exception as e:
    logger.error(f"MongoDB connection error: {str(e)}")
    raise

# Model schemas (for reference)
USER_SCHEMA = {
    "telegram_id": str,
    "is_admin": bool,
    "is_banned": bool,
    "joined_date": datetime,
    "last_search": datetime
}

MOVIE_SCHEMA = {
    "title": str,
    "description": str,
    "year": int,
    "genre": str,
    "stream_id": str,
    "file_url": str,
    "file_size": float,
    "duration": int,
    "views": int,
    "created_at": datetime,
    "uploader_id": str,
    "short_url_get2short": str,
    "short_url_modijiurl": str
}