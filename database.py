from typing import Optional, Dict, Any
import logging
from models import db, movies

logger = logging.getLogger(__name__)

class URLVerificationError(Exception):
    """Exception for URL verification failures."""
    pass

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