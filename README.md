# Advanced File Store Bot 🚀

A powerful Telegram bot for storing and streaming large files up to 4GB with advanced features.

## 🚀 Quick Deploy to Heroku
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## ⚙️ Mandatory Variables

Before deploying, make sure you have:

1. `TELEGRAM_BOT_TOKEN`: Get from [@BotFather](https://t.me/BotFather)
2. `WORKER_BOT_TOKEN`: Create another bot with [@BotFather](https://t.me/BotFather)
3. `API_ID` and `API_HASH`: Get from [my.telegram.org](https://my.telegram.org)
4. `OWNER_ID`: Your Telegram User ID
5. `CHANNEL_ID`: Your Channel ID (e.g., -100xxxxxxxx)
6. `MONGODB_URI`: Your MongoDB connection string

### 📝 How to Get MongoDB URI

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account and sign in
3. Create a new cluster (free tier is sufficient)
4. Click "Connect" on your cluster
5. Choose "Connect your application"
6. Copy the connection string
7. Replace `<password>` with your database password
8. Add database name at the end of URI (before parameters)
9. Your URI should look like:
   ```
   mongodb+srv://username:password@cluster.xxxxx.mongodb.net/filestore?retryWrites=true&w=majority
   ```
   
   ⚠️ Important:
   - Replace `username` and `password` with your actual values
   - Keep `filestore` as the database name
   - If your password contains special characters, they will be automatically escaped

## 🌟 Features
[Rest of README content remains the same...]