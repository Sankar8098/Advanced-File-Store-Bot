from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
from models import db, movies, users, statistics
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

class URLVerificationError(Exception):
    """Exception for URL verification failures."""
    pass

class DatabaseError(Exception):
    """Base exception for database operations."""
    pass

def get_db():
    """Get database connection."""
    return db

def verify_url_token(url: str) -> Optional[Dict[str, Any]]:
    """
    Verify shortened URL and return stream_id if valid.
    
    Args:
        url: The URL to verify
        
    Returns:
        Dict containing stream_id and verified status, or None if invalid
        
    Raises:
        URLVerificationError: If URL verification fails
    """
    try:
        if not (url.startswith('https://get2short.com/') or 
                url.startswith('https://modijiurl.com/')):
            return None

        stream_id = url.split('/')[-1]
        movie = movies.find_one({"stream_id": stream_id})

        if not movie:
            return None

        return {
            'stream_id': stream_id,
            'verified': True
        }

    except Exception as e:
        logger.error(f"Error in verify_url_token with URL {url}: {e}")
        raise URLVerificationError("Error verifying URL token") from e

def get_movie_by_stream_id(stream_id: str) -> Optional[Dict]:
    """
    Get movie by stream ID.
    
    Args:
        stream_id: The stream ID to look up
        
    Returns:
        Movie document or None if not found
    """
    try:
        return movies.find_one({"stream_id": stream_id})
    except Exception as e:
        logger.error(f"Error getting movie with stream_id {stream_id}: {e}")
        raise DatabaseError("Error retrieving movie") from e

def search_movies(query: str, limit: int = 10) -> List[Dict]:
    """
    Search movies by title.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List of matching movie documents
    """
    try:
        return list(movies.find(
            {"title": {"$regex": query, "$options": "i"}},
            limit=limit
        ).sort("created_at", -1))
    except Exception as e:
        logger.error(f"Error searching movies with query '{query}': {e}")
        raise DatabaseError("Error searching movies") from e

def increment_movie_views(stream_id: str) -> bool:
    """
    Increment movie view count.
    
    Args:
        stream_id: The stream ID of the movie
        
    Returns:
        True if successful, False otherwise
    """
    try:
        result = movies.update_one(
            {"stream_id": stream_id},
            {"$inc": {"views": 1}}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error incrementing views for stream_id {stream_id}: {e}")
        raise DatabaseError("Error updating view count") from e

def create_movie(title: str, stream_id: str, file_url: str, 
                description: Optional[str] = None, year: Optional[int] = None,
                genre: Optional[str] = None, uploader_id: Optional[str] = None) -> Dict:
    """
    Create a new movie entry.
    
    Args:
        title: Movie title
        stream_id: Unique stream identifier
        file_url: URL to the movie file
        description: Optional movie description
        year: Optional release year
        genre: Optional movie genre
        uploader_id: Optional uploader's ID
        
    Returns:
        Created movie document
        
    Raises:
        DatabaseError: If creation fails
    """
    try:
        movie = {
            "title": title,
            "stream_id": stream_id,
            "file_url": file_url,
            "description": description,
            "year": year,
            "genre": genre,
            "uploader_id": uploader_id,
            "views": 0,
            "created_at": datetime.utcnow()
        }
        
        result = movies.insert_one(movie)
        if not result.inserted_id:
            raise DatabaseError("Failed to insert movie")
            
        return movie
        
    except Exception as e:
        logger.error(f"Error creating movie {title}: {e}")
        raise DatabaseError("Error creating movie") from e

def get_movie_stats() -> Dict[str, Any]:
    """
    Get movie statistics.
    
    Returns:
        Dictionary containing total movies, views, and other stats
    """
    try:
        total_movies = movies.count_documents({})
        total_views = sum(movie.get('views', 0) for movie in movies.find({}, {'views': 1}))
        
        return {
            'total_movies': total_movies,
            'total_views': total_views,
            'last_updated': datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting movie stats: {e}")
        raise DatabaseError("Error retrieving movie statistics") from e