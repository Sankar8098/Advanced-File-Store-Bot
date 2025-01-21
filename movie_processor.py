import os
import asyncio
import aiohttp
from typing import Optional, Dict
from datetime import datetime
from database import get_db, create_movie
import hashlib
import json

class MovieProcessor:
    def __init__(self):
        self.supported_platforms = {
            'gdrive': self._process_gdrive,
            'mega': self._process_mega,
            'direct': self._process_direct
        }
    
    async def process_movie(self, 
                          title: str,
                          file_url: str,
                          platform: str,
                          description: Optional[str] = None,
                          year: Optional[int] = None,
                          genre: Optional[str] = None) -> Dict:
        """Process movie and generate streaming links."""
        
        if platform not in self.supported_platforms:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Generate unique stream ID
        stream_id = self._generate_stream_id(title, file_url)
        
        # Process the URL based on platform
        processed_url = await self.supported_platforms[platform](file_url)
        
        # Store in database
        with get_db() as db:
            movie = create_movie(
                db=db,
                title=title,
                stream_id=stream_id,
                file_url=processed_url,
                description=description,
                year=year,
                genre=genre,
                uploader_id=0  # System upload
            )
        
        return {
            'stream_id': stream_id,
            'processed_url': processed_url,
            'title': title,
            'year': year
        }
    
    def _generate_stream_id(self, title: str, url: str) -> str:
        """Generate unique stream ID."""
        unique_string = f"{title}{url}{datetime.now().isoformat()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    async def _process_gdrive(self, url: str) -> str:
        """Process Google Drive links."""
        # Add your Google Drive processing logic here
        return url
    
    async def _process_mega(self, url: str) -> str:
        """Process Mega links."""
        # Add your Mega processing logic here
        return url
    
    async def _process_direct(self, url: str) -> str:
        """Process direct links."""
        return url