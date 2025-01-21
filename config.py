import os
from dotenv import load_dotenv
import logging
from typing import List, Optional
from pathlib import Path

# Configure logging with more detailed format
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def validate_token(token: Optional[str], name: str) -> str:
    """Validate Telegram bot token format."""
    if not token:
        raise ValueError(f"{name} is not set")
    if not token.strip():
        raise ValueError(f"{name} cannot be empty")
    if not token.count(':') == 1:
        raise ValueError(f"{name} format is invalid")
    return token.strip()

def validate_api_credentials() -> tuple:
    """Validate API credentials."""
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    
    if not api_id or not api_hash:
        raise ValueError("API_ID and API_HASH must be set")
    
    try:
        api_id = int(api_id)
    except ValueError:
        raise ValueError("API_ID must be a number")
        
    if not isinstance(api_hash, str) or len(api_hash) != 32:
        raise ValueError("API_HASH must be a 32-character string")
        
    return api_id, api_hash

def parse_admin_list(admins_str: Optional[str]) -> List[int]:
    """Parse admin list from environment variable."""
    if not admins_str:
        return []
    try:
        return [int(x.strip()) for x in admins_str.split() if x.strip().isdigit()]
    except ValueError:
        logger.warning("Invalid admin ID found in ADMINS list")
        return []

class Config:
    """Configuration class with enhanced validation and features."""
    
    # Bot Settings
    TELEGRAM_BOT_TOKEN = validate_token(os.getenv('TELEGRAM_BOT_TOKEN'), 'TELEGRAM_BOT_TOKEN')
    WORKER_BOT_TOKEN = validate_token(os.getenv('WORKER_BOT_TOKEN'), 'WORKER_BOT_TOKEN')
    
    # API Settings
    API_ID, API_HASH = validate_api_credentials()
    
    # User Settings
    OWNER_ID = int(os.getenv('OWNER_ID', '0'))
    if OWNER_ID == 0:
        logger.warning("OWNER_ID not set! Some features may be limited")
    
    CHANNEL_ID = int(os.getenv('CHANNEL_ID', '0'))
    if CHANNEL_ID == 0:
        logger.warning("CHANNEL_ID not set! Channel features will be disabled")
    
    # Database Settings
    MONGODB_URI = os.getenv('MONGODB_URI')
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is not set")
    
    # Performance Settings
    MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS', '100'))
    CONNECTION_TIMEOUT = int(os.getenv('CONNECTION_TIMEOUT', '5000'))
    
    # Channel and Subscription Settings
    FORCE_SUB_CHANNEL = int(os.getenv('FORCE_SUB_CHANNEL', '0'))
    FORCE_SUB_MESSAGE = os.getenv(
        'FORCE_SUB_MESSAGE',
        '<b>⚠️ Please join our channel to use this bot!</b>\n\n'
        'Click the button below to join:'
    )
    JOIN_REQUEST_ENABLED = os.getenv('JOIN_REQUEST_ENABLED', 'False').lower() == 'true'
    
    # Bot Customization
    START_MESSAGE = os.getenv(
        'START_MESSAGE',
        '<b>👋 Welcome to our File Store Bot!</b>\n\n'
        '<i>I can help you store and share files securely. '
        'Send me any file to get started!</i>'
    )
    
    START_PIC = os.getenv('START_PIC', 'https://graph.org/file/29c1cf05d61f49ed3aa0b.jpg')
    RANDOM_START_PIC = os.getenv('RANDOM_START_PIC', 'True').lower() == 'true'
    
    CUSTOM_CAPTION = os.getenv(
        'CUSTOM_CAPTION',
        '{filename}\n\n'
        '💾 Size: {filesize}\n'
        '👤 Shared by: @{username}\n\n'
        '🤖 @YourBotUsername'
    )
    
    BOT_STATS_TEXT = os.getenv(
        'BOT_STATS_TEXT',
        '📊 <b>Bot Statistics</b>\n\n'
        '👥 Users: {total_users:,}\n'
        '📁 Files: {total_files:,}\n'
        '💾 Storage: {storage_used}\n'
        '⚡️ Uptime: {uptime}'
    )
    
    USER_REPLY_TEXT = os.getenv(
        'USER_REPLY_TEXT',
        '👋 Hello!\n\n'
        'Use /help to see available commands.\n'
        'Use /start to restart the bot.'
    )
    
    # Admin Settings
    ADMINS: List[int] = parse_admin_list(os.getenv('ADMINS'))
    if OWNER_ID != 0 and OWNER_ID not in ADMINS:
        ADMINS.append(OWNER_ID)
    
    NOTIFY_ON_JOIN = os.getenv('NOTIFY_ON_JOIN', 'True').lower() == 'true'
    LOG_CHANNEL = int(os.getenv('LOG_CHANNEL', '0'))
    if LOG_CHANNEL == 0:
        logger.warning("LOG_CHANNEL not set! Logging to channel will be disabled")
    
    # URL Shortener Settings
    GET2SHORT_API_KEY = os.getenv('GET2SHORT_API_KEY', '')
    MODIJIURL_API_KEY = os.getenv('MODIJIURL_API_KEY', '')
    
    # File Settings
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', str(2 * 1024 * 1024 * 1024)))  # 2GB default
    ALLOWED_MIME_TYPES = {
        'video': ['video/mp4', 'video/x-matroska', 'video/webm'],
        'audio': ['audio/mpeg', 'audio/mp4', 'audio/ogg'],
        'document': ['application/pdf', 'application/zip', 'application/x-rar-compressed']
    }
    
    # Cache Settings
    CACHE_TIME = int(os.getenv('CACHE_TIME', '300'))  # 5 minutes default
    CACHE_SIZE = int(os.getenv('CACHE_SIZE', '1000'))
    
    @classmethod
    def get_allowed_mime_types(cls) -> List[str]:
        """Get flat list of all allowed MIME types."""
        return [mime for types in cls.ALLOWED_MIME_TYPES.values() for mime in types]
    
    @classmethod
    def is_mime_type_allowed(cls, mime_type: str) -> bool:
        """Check if a MIME type is allowed."""
        return mime_type in cls.get_allowed_mime_types()
    
    @classmethod
    def get_file_type(cls, mime_type: str) -> Optional[str]:
        """Get file type category from MIME type."""
        for file_type, mime_types in cls.ALLOWED_MIME_TYPES.items():
            if mime_type in mime_types:
                return file_type
        return None