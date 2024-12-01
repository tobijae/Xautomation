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

fact_categories = [
    # Core Cognitive Science
    "human cognition", "memory formation", "decision making",
    "cognitive biases", "learning processes", "attention mechanisms",
    "pattern recognition", "problem solving", "mental models",
    
    # Brain & Neuroscience
    "brain evolution", "neuroplasticity", "neurotransmitters",
    "brain structure", "neural networks", "brain development",
    "consciousness studies", "cognitive neuroscience", "memory systems",
    
    # Intelligence & Learning
    "artificial intelligence", "machine learning", "human intelligence",
    "collective intelligence", "emotional intelligence", "learning theory",
    "cognitive development", "intelligence augmentation", "knowledge acquisition",
    
    # Psychology & Behavior
    "cognitive psychology", "behavioral science", "mental processes",
    "psychological phenomena", "human behavior", "cognitive development",
    "social cognition", "perception", "cognitive load",
    
    # Evolution & Development
    "brain evolution", "cognitive evolution", "child development",
    "evolutionary psychology", "cognitive archaeology", "language evolution",
    "cultural evolution", "mental capabilities", "cognitive adaptation",
    
    # Language & Communication
    "language processing", "cognitive linguistics", "communication patterns",
    "language acquisition", "symbolic thinking", "cognitive semantics",
    "mental representation", "language evolution", "cognitive pragmatics",
    
    # Philosophy of Mind
    "consciousness theories", "philosophy of cognition", "mental philosophy",
    "cognitive science history", "mind theories", "cognitive paradigms",
    "consciousness studies", "cognitive frameworks", "mental models",
    
    # Applied Cognition
    "cognitive enhancement", "brain training", "mental techniques",
    "cognitive tools", "learning strategies", "memory techniques",
    "cognitive optimization", "mental performance", "cognitive applications"
]

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
    return "Did You Know? Bot is running!"

def format_tweet(text):
    """Format tweet with proper spacing and length"""
    if len(text) > 240:
        text = text[:237] + "..."
    return text

def generate_fact_prompt():
    """Generate prompt for interesting facts"""
    category = random.choice(fact_categories)
    
    prompt = f"""Share one fascinating fact about {category} in a casual, natural social media style.
Requirements:
- Write like a real person casually sharing something interesting they learned
- Use natural, conversational language (can include "lol", "ngl", "tbh", etc.)- but not too often!
- Use lowercase for a more casual feel
- The fact must be true and verifiable
- Include specific details but phrase them casually
- Maximum 240 characters
- Must be accurate and up-to-date
- Do NOT use "did you know?" or any formal academic language
- Make it sound like something you'd actually tweet to friends
- Do not use # or emojis

Example formats:
"just learned that our brain is already 80% grown by age 2... wild right?"
"ok but apparently we forget like 60% of new stuff within an hour lol"
"ngl this is crazy - scientists found that just 15min of brain training can actually improve memory"

Remember: Sound natural and casual while keeping the information accurate, and do not overuse phrases!"""

    return prompt

def get_fact():
    """Get AI generated fact using OpenAI"""
    try:
        system_prompt = """You are a casual social media user who loves sharing interesting scientific facts. 
Your style is:
- Natural and conversational, like talking to friends
- Sometimes uses internet slang (lol, ngl, tbh) but not too much
- Often uses lowercase for a casual feel
- Shares accurate information but phrases it conversationally
- Occasionally adds reactions like "wild" or "cant believe this"
- Sounds like a real person who just learned something cool

Never make up facts, but always present them in a natural, casual way."""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": generate_fact_prompt()}
            ],
            max_tokens=280,
            temperature=1.0  # Increased for more variety in expression
        )
        
        text = response.choices[0].message.content.strip()
        return format_tweet(text)
    except Exception as e:
        logger.error(f"Error getting fact: {e}")
        return None

def create_tweet():
    """Create and format tweet"""
    try:
        fact = get_fact()
        if fact:
            # Remove the "did you know?" check since we're going for natural style
            return fact
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
            logger.info(f"Tweet content: {tweet}")
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
    try:
        # Start bot thread
        bot_thread = Thread(target=run_bot)
        bot_thread.start()
        
        # Start web server
        port = int(os.environ.get("PORT", 8080))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
