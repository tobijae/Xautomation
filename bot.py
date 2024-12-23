import tweepy
import random
from datetime import datetime
import schedule
import time
import os
from dotenv import load_dotenv
from threading import Thread
from flask import Flask
import logging
import requests

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Twitter API v2 client
twitter_client = tweepy.Client(
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
)

# Initialize Flask app
app = Flask(__name__)

# Characters who can narrate the news
narrators = [
    {"name": "Gandalf", "style": "wise and mysterious"},
    {"name": "Yoda", "style": "cryptic and sagely"},
    {"name": "Doctor Strange", "style": "mystical and academic"},
    {"name": "Morpheus", "style": "philosophical and profound"},
    {"name": "Dumbledore", "style": "whimsical and knowing"}
]

def get_grok_news():
    """Get news from Grok API"""
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [{
                "role": "user",
                "content": "What are some big stuff that happened in the last 1.5 hours?"
            }]
        }
        
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Error getting news from Grok: {e}")
        return None

def generate_narrated_news(news):
    """Generate character-narrated news"""
    try:
        narrator = random.choice(narrators)
        
        headers = {
            "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""As {narrator['name']}, narrate this news in your {narrator['style']} style in under 200 characters: {news}"""
        
        data = {
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }
        
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Error generating narration: {e}")
        return None

def post_update():
    """Post update to Twitter"""
    try:
        news = get_grok_news()
        if news:
            narrated_news = generate_narrated_news(news)
            if narrated_news:
                twitter_client.create_tweet(text=narrated_news)
                logger.info(f"Tweet posted successfully at {datetime.now()}")
                logger.info(f"Content: {narrated_news}")
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")

@app.route('/')
def home():
    return "News narrator bot is running"

def keep_alive():
    """Ping the service to keep it active"""
    try:
        url = "https://xautomation.onrender.com"
        response = requests.get(url)
        logger.info(f"Keep-alive ping successful: {datetime.now()}")
    except Exception as e:
        logger.error(f"Keep-alive ping failed: {e}")

def run_bot():
    """Main function to run the bot"""
    logger.info("Starting bot...")
    post_update()
    
    schedule.every(90).minutes.do(post_update)
    schedule.every(10).minutes.do(keep_alive)
    
    logger.info("Bot started. Posts every 1.5 hours")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    try:
        bot_thread = Thread(target=run_bot)
        bot_thread.start()
        
        port = int(os.environ.get("PORT", 8080))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
