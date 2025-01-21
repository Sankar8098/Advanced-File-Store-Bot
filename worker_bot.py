import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from database import get_movie_by_stream_id, verify_url_token
from datetime import datetime, timedelta
from config import Config
import secrets
import asyncio
from aiohttp import web

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Store verified users and their access tokens
verified_users = {}

# Store message IDs for auto-deletion
auto_delete_messages = {}

def generate_access_token():
    """Generate a random access token."""
    return secrets.token_urlsafe(32)

async def restrict_user_forwarding(update: Update, context: CallbackContext):
    """Restrict user from forwarding messages."""
    try:
        chat_id = update.effective_chat.id
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False
        )
        await context.bot.restrict_chat_member(chat_id, update.effective_user.id, permissions)
    except Exception as e:
        logger.error(f"Error restricting user forwarding: {e}")

async def schedule_message_deletion(context: CallbackContext, chat_id: int, message_id: int, delay: int = 1800):
    """Schedule message deletion after specified delay."""
    try:
        await asyncio.sleep(delay)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        # Send deletion notification
        notification = await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ File has been automatically deleted for security reasons."
        )
        # Delete notification after 10 seconds
        await asyncio.sleep(10)
        await context.bot.delete_message(chat_id=chat_id, message_id=notification.message_id)
    except Exception as e:
        logger.error(f"Error in scheduled message deletion: {e}")

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
        
        # Send verification message
        verification_msg = await message.reply_text(
            f"✅ URL Verified Successfully!\n\n"
            f"🎥 *{movie['title']}*\n"
            f"📝 {movie.get('description', 'No description available')}\n"
            f"📅 Year: {movie.get('year', 'N/A')}\n"
            f"🎭 Genre: {movie.get('genre', 'N/A')}\n\n"
            f"⚠️ Links expire in 30 minutes!\n"
            f"⚠️ Files will be automatically deleted after 30 minutes!\n"
            f"⚠️ Forwarding is disabled for security!\n\n"
            f"Choose your preferred option:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Schedule verification message deletion
        asyncio.create_task(schedule_message_deletion(
            context, 
            verification_msg.chat_id, 
            verification_msg.message_id
        ))

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
            
        # Restrict forwarding for the user
        await restrict_user_forwarding(update, context)
            
        # Send file with protection
        if action == 'dl':
            sent_message = await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=movie['file_url'],
                caption=f"🎥 {movie['title']}\n\n⚠️ This file will be deleted in 30 minutes!",
                protect_content=True,  # Prevent forwarding
                reply_to_message_id=query.message.message_id,
                disable_notification=True
            )
        else:  # Stream
            sent_message = await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=movie['file_url'],
                caption=f"🎥 {movie['title']}\n\n⚠️ This file will be deleted in 30 minutes!",
                protect_content=True,  # Prevent forwarding
                reply_to_message_id=query.message.message_id,
                disable_notification=True,
                supports_streaming=True
            )
        
        # Schedule file deletion
        asyncio.create_task(schedule_message_deletion(
            context,
            sent_message.chat_id,
            sent_message.message_id
        ))
        
        await query.answer("File sent! It will be automatically deleted in 30 minutes.")
            
    except Exception as e:
        logger.error(f"Error handling download/stream options: {e}")
        await query.answer("Error processing your request. Please try again.")

async def web_app():
    """Create web app for Heroku."""
    app = web.Application()
    return app

async def main():
    """Start the bot."""
    try:
        # Initialize bot application
        application = Application.builder().token(Config.WORKER_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_worker_verification))
        application.add_handler(CallbackQueryHandler(handle_download_stream_options))
        
        # Get port from environment variable
        port = int(os.environ.get('PORT', '8443'))
        
        # Start web app
        webapp = await web_app()
        runner = web.AppRunner(webapp)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        logger.info(f"Web app is listening on port {port}")
        
        # Start the bot
        await application.initialize()
        await application.start()
        await application.run_polling()
        
        logger.info("Worker bot started successfully!")
        
        # Keep the app running
        while True:
            await asyncio.sleep(3600)
            
    except Exception as e:
        logger.error(f"Error starting worker bot: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())