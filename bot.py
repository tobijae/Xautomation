import tweepy
import requests
from datetime import datetime
import schedule
import time
import os
from dotenv import load_dotenv
from threading import Thread
from flask import Flask
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API Credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
XAI_API_KEY = os.getenv('XAI_API_KEY')

# Initialize Twitter client
twitter_client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET
)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "News Bot is running!"

def get_grok_news():
    """Get news analysis from Grok"""
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You are a news curator. Provide concise, engaging summaries of the most important recent news."},
            {"role": "user", "content": "What's the single most important or viral news story from the last 8 hours? Provide a concise summary in a single tweet (max 140 chars). Be informative and engaging, but avoid hashtags or emojis."}
        ],
        "max_tokens": 140,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            logger.error(f"Error from Grok API: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting news from Grok: {e}")
        return None

def create_news_tweet():
    """Create and format tweet with news"""
    try:
        # Get Grok's news analysis
        news_update = get_grok_news()
        
        if news_update:
            time_now = datetime.now().strftime('%H:%M UTC')
            tweet = f"News Update ({time_now})\n\n{news_update}"
            return tweet
        
        return None
        
    except Exception as e:
        logger.error(f"Error creating tweet: {e}")
        return None

def post_update():
    """Post news update to Twitter"""
    tweet = create_news_tweet()
    if tweet:
        try:
            twitter_client.create_tweet(text=tweet)
            logger.info(f"Tweet posted successfully at {datetime.now()}")
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")

def keep_alive():
    """Ping the service to keep it active"""
    try:
        url = "https://xautomation.onrender.com"
        response = requests.get(url)
        print(f"Keep-alive ping successful: {datetime.now()}")  # Add more visible logging
        logger.info(f"Keep-alive ping successful: {datetime.now()}")
    except Exception as e:
        print(f"Keep-alive ping failed: {e}")  # Add more visible logging
        logger.error(f"Keep-alive ping failed: {e}")

def run_bot():
    """Main function to schedule and run the bot"""
    # Schedule posts every 8 hours
    schedule.every().day.at("06:00").do(post_update)  # 6 AM UTC
    schedule.every().day.at("14:00").do(post_update)  # 2 PM UTC
    schedule.every().day.at("22:00").do(post_update)  # 10 PM UTC
    
    # Add keep-alive schedule to prevent free tier spindown
    schedule.every(10).minutes.do(keep_alive)
    
    logger.info("Bot started. Posts scheduled for 6:00 AM, 2:00 PM, and 10:00 PM UTC")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Start the bot in a separate thread
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    
    # Start the web server
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
