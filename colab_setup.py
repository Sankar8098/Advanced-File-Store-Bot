import os
import subprocess
import requests
from IPython.display import HTML, display
from pyngrok import ngrok

def setup_colab():
    """Set up the bot environment in Google Colab."""
    print("🚀 Setting up File Store Bot in Google Colab...")
    
    # Install required packages
    print("\n📦 Installing dependencies...")
    subprocess.run(["pip", "install", "-r", "requirements.txt"])
    
    # Set up environment variables
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # Start ngrok tunnel
    print("\n🌐 Starting ngrok tunnel...")
    public_url = ngrok.connect(8443)
    os.environ['PUBLIC_URL'] = public_url.public_url
    
    print(f"\n✅ Setup complete! Public URL: {public_url.public_url}")
    
    # Display setup instructions
    display(HTML("""
    <div style='background-color: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0;'>
        <h2 style='color: #2c3e50;'>🚀 Setup Instructions</h2>
        <ol style='color: #34495e;'>
            <li>Set your environment variables in the next cell:
                <pre style='background-color: #fff; padding: 10px; border-radius: 5px;'>
import os
os.environ['TELEGRAM_BOT_TOKEN'] = 'your_bot_token'
os.environ['WORKER_BOT_TOKEN'] = 'your_worker_token'
os.environ['API_ID'] = 'your_api_id'
os.environ['API_HASH'] = 'your_api_hash'
os.environ['OWNER_ID'] = 'your_telegram_id'
os.environ['CHANNEL_ID'] = 'your_channel_id'</pre>
            </li>
            <li>Start the bot:
                <pre style='background-color: #fff; padding: 10px; border-radius: 5px;'>!python bot.py</pre>
            </li>
        </ol>
    </div>
    """))

if __name__ == "__main__":
    setup_colab()