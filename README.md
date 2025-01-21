# Advanced File Store Bot 🚀

A powerful Telegram bot for storing and streaming large files up to 4GB with advanced features.

## 🌟 Features

- 📁 Store and share files up to 4GB
- 🎥 Stream videos directly in Telegram
- 🔐 Secure file sharing with access control
- 🎯 Force channel subscription
- 📊 Detailed statistics and analytics
- 🔄 Auto-delete expired files
- 🎨 Customizable messages and UI
- 🚀 High performance with MongoDB
- 🔍 Advanced file search
- 👥 Admin management system

## 🛠️ Requirements

- Python 3.9 or higher
- MongoDB database
- Telegram Bot Token (2 tokens needed)
- API ID and Hash from my.telegram.org

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and set these variables:

### Required Variables

```bash
# Bot Settings
TELEGRAM_BOT_TOKEN=your_bot_token_here
WORKER_BOT_TOKEN=your_worker_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
OWNER_ID=your_telegram_id_here
CHANNEL_ID=-100xxxxxxxx

# Database Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.xxxxx.mongodb.net/filestore
```

### Optional Variables

```bash
# Channel Settings
FORCE_SUB_CHANNEL=0
FORCE_SUB_MESSAGE="⚠️ Please join our channel to use this bot!"
JOIN_REQUEST_ENABLED=False

# Customization
START_MESSAGE="👋 Welcome to our File Store Bot!"
START_PIC=https://graph.org/file/29c1cf05d61f49ed3aa0b.jpg
RANDOM_START_PIC=True
CUSTOM_CAPTION={filename}\n\nShared via @YourBotUsername

# Admin Settings
ADMINS=123456789 987654321
NOTIFY_ON_JOIN=True
LOG_CHANNEL=-100xxxxxxxx
```

## 🚀 Deployment Methods

### Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

1. Click the deploy button
2. Fill in the required environment variables
3. Deploy and start the bot

### Local Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/file-store-bot.git
   cd file-store-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

### Docker Deployment

1. Build the image:
   ```bash
   docker build -t file-store-bot .
   ```

2. Run the container:
   ```bash
   docker-compose up -d
   ```

## 📝 Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/stats` - Show bot statistics (admin only)
- `/broadcast` - Broadcast message to users (admin only)
- `/ban` - Ban a user (admin only)
- `/unban` - Unban a user (admin only)
- `/users` - List all users (admin only)

## 🔒 Security Features

- File access control with expiring links
- Protected content forwarding
- Rate limiting
- User banning system
- Secure file storage
- MongoDB authentication
- Input validation

## 🗄️ Database Structure

### Users Collection
```javascript
{
  "telegram_id": String,
  "is_admin": Boolean,
  "is_banned": Boolean,
  "joined_date": DateTime,
  "last_search": DateTime
}
```

### Movies Collection
```javascript
{
  "title": String,
  "description": String,
  "year": Number,
  "genre": String,
  "stream_id": String,
  "file_url": String,
  "file_size": Number,
  "duration": Number,
  "views": Number,
  "created_at": DateTime,
  "uploader_id": String
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- Create an [Issue](https://github.com/yourusername/file-store-bot/issues)
- Join our [Telegram Channel](https://t.me/your_channel)
- Contact [@YourUsername](https://t.me/your_username)

## ⭐ Credits

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [MongoDB](https://www.mongodb.com/)
- [Heroku](https://www.heroku.com/)

## 📊 Statistics

- Total Users: Growing daily
- Files Stored: Unlimited
- Uptime: 99.9%
- Response Time: <2s

## 🔄 Updates

Stay tuned for regular updates and new features! Star ⭐ the repository to receive notifications.