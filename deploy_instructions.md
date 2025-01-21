# Deployment Instructions

## Heroku Deployment
1. Install Heroku CLI
2. Run:
```bash
heroku create your-bot-name
heroku stack:set container
git push heroku main
```

## DigitalOcean Deployment
1. Install doctl
2. Run:
```bash
doctl apps create --spec deploy/digitalocean-app.yaml
```

## Render Deployment
1. Connect your GitHub repository
2. Create a new Web Service
3. Use the `render.yaml` configuration

## Google Colab Setup
1. Upload project files to Colab
2. Run:
```python
from colab_setup import setup_colab
setup_colab()
```
3. Set environment variables
4. Run the bot

## Environment Variables Required
```
TELEGRAM_BOT_TOKEN=your_bot_token
WORKER_BOT_TOKEN=your_worker_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
ADMIN_IDS=comma_separated_admin_ids
DATABASE_URL=your_database_url
GET2SHORT_API_KEY=your_get2short_key
MODIJIURL_API_KEY=your_modijiurl_key
```

## Database Setup
1. Create PostgreSQL database
2. Run migrations:
```bash
alembic upgrade head
```

## Adding Movies
1. Use the MovieProcessor class:
```python
processor = MovieProcessor()
result = await processor.process_movie(
    title="Movie Title",
    file_url="https://example.com/movie.mp4",
    platform="direct",
    year=2024,
    genre="Action"
)
```