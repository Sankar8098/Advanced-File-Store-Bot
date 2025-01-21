import os
import logging
import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram.error import TelegramError
from database import get_db, get_movie_by_stream_id, search_movies, increment_movie_views
from datetime import datetime, timedelta
from config import Config
import secrets
import time

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def rate_limit(user_id: int) -> bool:
    """Simple rate limiting."""
    return True  # Implement proper rate limiting if needed

async def check_force_sub(update: Update, context: CallbackContext) -> bool:
    """Check if user has joined the required channel."""
    return True  # Implement force sub check if needed

async def start(update: Update, context: CallbackContext) -> None:
    """Handle /start command."""
    user_id = update.effective_user.id
    
    if not rate_limit(user_id):
        await update.message.reply_text("Please wait a minute before making more requests.")
        return
        
    if not await check_force_sub(update, context):
        return
        
    try:
        # Get start picture URL
        start_pic_url = Config.START_PIC
        if Config.RANDOM_START_PIC:
            start_pic = random.choice(list(Config.START_PICTURES.values()))
            start_pic_url = start_pic['url']
            
        # Create welcome buttons
        keyboard = []
        if hasattr(Config, 'WELCOME_BUTTONS'):
            for row in Config.WELCOME_BUTTONS:
                keyboard_row = []
                for button in row:
                    if isinstance(button, list) and len(button) == 2:
                        keyboard_row.append(InlineKeyboardButton(button[0], callback_data=button[1]))
                keyboard.append(keyboard_row)
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        # Send welcome message with picture
        await update.message.reply_photo(
            photo=start_pic_url,
            caption=Config.START_MESSAGE,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        # Log new user if enabled
        if Config.NOTIFY_ON_JOIN and Config.LOG_CHANNEL:
            await context.bot.send_message(
                chat_id=Config.LOG_CHANNEL,
                text=f"New user joined!\nID: {user_id}\nName: {update.effective_user.full_name}"
            )
            
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        # Fallback to text-only message if image fails
        await update.message.reply_text(
            Config.START_MESSAGE,
            parse_mode='HTML'
        )

def main():
    """Start the bot."""
    try:
        updater = Updater(Config.TELEGRAM_BOT_TOKEN)
        dispatcher = updater.dispatcher
        
        # Add handlers
        dispatcher.add_handler(CommandHandler("start", start))
        
        # Start the bot
        updater.start_polling()
        logger.info("Bot started successfully!")
        updater.idle()
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()