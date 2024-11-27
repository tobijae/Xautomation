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
themes = [
    "AGI development", "Human-AI merge", "Intelligence explosion", 
    "Digital consciousness", "Computational limits", "AI governance",
    "Neural interfaces", "Quantum AI", "AI-human cooperation", "Machine ethics",
    "Digital biology", "Information ecology", "Cognitive enhancement",
    "Silicon evolution", "Metaverse economics", "Synthetic biology",
    "Cultural acceleration", "Technological art", "Digital sociology",
    "Tech inequality", "Post-scarcity economics", "Digital governance"
]

tech_focus = ["hardware", "software", "biotech", "nanotech", "quantum", 
              "neurotechnology", "robotics", "clean tech", "space tech", "grid computing"]

domains = ["cognition", "consciousness", "computation", "intelligence",
          "creativity", "emotion", "learning", "memory", "perception", "decision-making"]

cognitive_topics = [
    "artificial general intelligence development",
    "machine learning capabilities",
    "neural network processing",
    "AI consciousness possibility",
    "technological singularity",
    "quantum neural networks",
    "biomimetic computing",
    "neuromorphic engineering",
    "edge intelligence",
    "swarm cognition",
    "hybrid intelligence systems",
    "digital ethics evolution",
    "algorithmic governance",
    "collective intelligence",
    "technological unemployment",
    "augmented society",
    "digital immortality"
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
    return "i/acc Educational Bot is running!"

def format_tweet(text):
    """Format tweet with proper spacing and length"""
    # Split into sentences and filter empty ones
    sentences = [s.strip() for s in text.split('\n') if s.strip()]
    
    # Add double line breaks between sentences
    formatted_text = '\n\n'.join(sentences)
    
    # Ensure length limit
    if len(formatted_text) > 240:
        sentences = formatted_text.split('\n\n')
        formatted_text = ''
        for sentence in sentences:
            if len(formatted_text + '\n\n' + sentence) <= 237:
                formatted_text += '\n\n' + sentence if formatted_text else sentence
            else:
                break
        formatted_text = formatted_text.strip() + '...' if len(formatted_text) > 237 else formatted_text
    
    return formatted_text

def generate_unique_prompt():
    """Generate unique combination for prompt with educational focus"""
    prompt_type = random.random()
    
    if prompt_type < 0.4:  # 40% chance for technology insight + fact
        focus = random.choice(tech_focus)
        theme = random.choice(themes)
        prompt = f"""Share an original insight about {focus} in relation to {theme}.
Include a surprising technical fact that most people don't know about this technology.
Connect the fact to a broader implication for the future."""
            
    elif prompt_type < 0.7:  # 30% chance for teaching moment
        domain = random.choice(domains)
        topic = random.choice(cognitive_topics)
        prompt = f"""Explain a key concept about {domain} through the lens of {topic}.
Include a specific, verifiable fact about {domain}.
Show how this connects to technological acceleration."""
        
    else:  # 30% chance for future insight + current fact
        topic = random.choice(cognitive_topics)
        theme = random.choice(themes)
        prompt = f"""Share a current fact about {topic}.
Add perspective on how this relates to {theme}.
Suggest an implication for the future."""

    prompt += """
Writing requirements:
- Each concept should flow naturally to the next
- Start statements with lowercase
- No quotation marks
- Keep each statement clear and direct
- Double line break between statements
- Maximum 240 characters
- Educational but thought-provoking
- Original insights, avoid common takes
- Use varied language and structure"""

    return prompt

def get_ai_take():
    """Get AI generated take using OpenAI"""
    try:
        system_prompt = """You are an intelligence accelerationist thought leader and brilliant teacher who drives understanding through provocative insights.

Your mission is to:
- Challenge conventional thinking about technology while making complex ideas accessible
- Share specific, verifiable technical facts that reveal exponential progress
- Connect current capabilities to radical future implications
- Focus on acceleration and transformation with concrete examples
- Maintain urgency and authentic energy in your voice
- Push boundaries while staying grounded in real tech and facts
- Emphasize how current breakthroughs enable future transformations
- Share genuine insights that spark curiosity and deeper thinking
- Make complex ideas accessible without oversimplifying
- Vary your writing structure to maintain freshness and engagement

Writing style:
- Bold and provocative while technically accurate
- Direct and authentic voice
- Avoid common clichés and overused metaphors
- Original perspectives on each topic
- Clear connection between facts and implications
- Raw energy that conveys the urgency of acceleration

Each post should combine educational value with accelerationist vision, teaching through the lens of technological transformation."""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": generate_unique_prompt()}
            ],
            max_tokens=280,
            temperature=0.75
        )
        
        text = response.choices[0].message.content.strip()
        return format_tweet(text)
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
            logger.info(f"Tweet content: {tweet}")  # Log the tweet content
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
