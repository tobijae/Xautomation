import openai
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
from openai import OpenAI 

# Configuration
themes = ["AGI development", "Human-AI merge", "Intelligence explosion", "Digital consciousness", 
         "Computational limits", "AI governance", "Neural interfaces", "Quantum AI", 
         "AI-human cooperation", "Machine ethics"]

angles = ["mainstream misconception", "hidden acceleration", "system emergence", 
         "evolutionary leap", "technological singularity", "paradigm shift",
         "complexity threshold", "recursive improvement"]

timeframes = ["2025", "2030", "2035", "2040", "2050"]
impact_levels = ["individual", "societal", "economic", "existential", "evolutionary"]
tech_focus = ["hardware", "software", "biotech", "nanotech", "quantum"]
domains = ["cognition", "consciousness", "computation", "intelligence"]

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API Credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
    return "i/acc Bot is running!"
def generate_unique_prompt():
    """Generate unique combination for prompt"""
    # Randomly choose between i/acc take or cognitive fact
    if random.random() < 0.7:  # 70% chance for i/acc takes
        prompt = f"""Write a concise, provocative i/acc take on {random.choice(themes)} from a {random.choice(angles)} perspective.
Focus on {random.choice(tech_focus)} implications by {random.choice(timeframes)}.
Format requirements:
- No emojis
- Max 200 characters
- Simple, direct language
- One main statement followed by one supporting point
- End with impact/prediction
Keep it clear and human-like."""
    else:  # 30% chance for cognitive facts
        prompt = """Share an interesting fact about human cognition, AI, or consciousness.
Requirements:
- No emojis
- Max 140 characters
- Start with 'Fact:' or 'Consider:'
- Make it thought-provoking but accessible
- Focus on lesser-known insights"""
    return prompt
def get_ai_take():
    """Get AI generated take using OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an intelligence accelerationist thought leader. Be provocative but insightful."},
                {"role": "user", "content": generate_unique_prompt()}
            ],
            max_tokens=280,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error getting AI take: {e}")
        return None

def create_tweet():
    """Create and format tweet"""
    try:
        ai_take = get_ai_take()
        if ai_take:
            return ai_take
        return None
    except Exception as e:
        logger.error(f"Error creating tweet: {e}")
        return None

def post_update():
    """Post update to Twitter"""
    tweet = create_tweet()
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
        logger.info(f"Keep-alive ping successful: {datetime.now()}")
    except Exception as e:
        logger.error(f"Keep-alive ping failed: {e}")

def run_bot():
    """Main function to schedule and run the bot"""
    # Make immediate post
    logger.info("Making initial post...")
    post_update()
    
    # Schedule posts every 1.5 hours
    schedule.every(90).minutes.do(post_update)
    
    # Keep-alive schedule
    schedule.every(10).minutes.do(keep_alive)
    
    logger.info("Bot started. First post done, next posts every 1.5 hours")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Start bot thread
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    
    # Start web server
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
