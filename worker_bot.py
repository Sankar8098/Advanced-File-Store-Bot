import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from database import get_movie_by_stream_id, verify_url_token
from datetime import datetime, timedelta
from config import Config
import secrets

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Store verified users and their access tokens
verified_users = {}

def generate_access_token():
    """Generate a random access token."""
    return secrets.token_urlsafe(32)

async def handle_worker_verification(update: Update, context: CallbackContext) -> None:
    """Handle URL verification and provide download/stream options in worker bot."""
    try:
        message = update.message
        if not message.text or not (message.text.startswith('http://') or message.text.startswith('https://')):
            await message.reply_text(
                "Please send a verified shortened URL from the main bot."
            )
            return

        url = message.text.strip()
        user_id = update.effective_user.id
        
        # Verify the URL and get stream_id
        verification = verify_url_token(url)
        if not verification:
            await message.reply_text(
                "❌ Invalid or expired URL.\n"
                "Please get a new link from the main bot."
            )
            return
        
        stream_id = verification['stream_id']
        movie = get_movie_by_stream_id(stream_id)
        
        if not movie:
            await message.reply_text(
                "Movie not found. Please get a new link from the main bot."
            )
            return
        
        # Generate temporary access token
        access_token = generate_access_token()
        verified_users[user_id] = {
            'token': access_token,
            'stream_id': stream_id,
            'expires': datetime.now() + timedelta(minutes=30)
        }
        
        # Create keyboard with download and stream options
        keyboard = [
            [InlineKeyboardButton("📥 Download", callback_data=f"dl_{access_token}")],
            [InlineKeyboardButton("▶️ Stream", callback_data=f"str_{access_token}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            f"✅ URL Verified Successfully!\n\n"
            f"🎥 *{movie['title']}*\n"
            f"📝 {movie.get('description', 'No description available')}\n"
            f"📅 Year: {movie.get('year', 'N/A')}\n"
            f"🎭 Genre: {movie.get('genre', 'N/A')}\n\n"
            f"⚠️ Links expire in 30 minutes!\n"
            f"Choose your preferred option:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in worker verification: {e}")
        await message.reply_text("An error occurred. Please try again later.")

async def handle_download_stream_options(update: Update, context: CallbackContext) -> None:
    """Handle download and stream button clicks."""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        if user_id not in verified_users:
            await query.answer("Please verify the URL first!")
            return
            
        user_data = verified_users[user_id]
        if datetime.now() > user_data['expires']:
            await query.answer("Access token expired! Please verify again.")
            del verified_users[user_id]
            return
            
        action, token = query.data.split('_')
        if token != user_data['token']:
            await query.answer("Invalid access token!")
            return
            
        movie = get_movie_by_stream_id(user_data['stream_id'])
        if not movie:
            await query.answer("Movie not found!")
            return
            
        # Send file with protection and auto-delete
        if action == 'dl':
            sent_message = await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=movie['file_url'],
                caption=f"🎥 {movie['title']}",
                protect_content=True,  # Prevent forwarding
                reply_to_message_id=query.message.message_id
            )
        else:
            sent_message = await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=movie['file_url'],
                caption=f"🎥 {movie['title']}",
                protect_content=True,  # Prevent forwarding
                reply_to_message_id=query.message.message_id
            )
        
        # Schedule auto-deletion after 30 minutes
        context.job_queue.run_once(
            delete_movie_file,
            1800,  # 30 minutes in seconds
            data={
                'chat_id': update.effective_chat.id,
                'message_id': sent_message.message_id
            }
        )
        
        await query.answer("File sent! It will be automatically deleted in 30 minutes.")
            
    except Exception as e:
        logger.error(f"Error handling download/stream options: {e}")
        await query.answer("Error processing your request. Please try again.")

async def delete_movie_file(context: CallbackContext) -> None:
    """Delete movie file after 30 minutes."""
    job = context.job
    try:
        await context.bot.delete_message(
            chat_id=job.data['chat_id'],
            message_id=job.data['message_id']
        )
        await context.bot.send_message(
            chat_id=job.data['chat_id'],
            text="⚠️ The movie file has been automatically deleted for security reasons."
        )
    except Exception as e:
        logger.error(f"Error deleting movie file: {e}")

def main():
    """Start the bot."""
    try:
        application = Application.builder().token(Config.WORKER_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_worker_verification))
        application.add_handler(CallbackQueryHandler(handle_download_stream_options))
        
        # Start the bot
        application.run_polling()
        logger.info("Worker bot started successfully!")
        
    except Exception as e:
        logger.error(f"Error starting worker bot: {e}")

if __name__ == '__main__':
    main()