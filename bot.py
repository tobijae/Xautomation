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

# Enhanced theme lists for more variety
themes = [
    # Core AI/Tech themes
    "AGI development", "Human-AI merge", "Intelligence explosion", 
    "Digital consciousness", "Computational limits", "AI governance",
    "Neural interfaces", "Quantum AI", "AI-human cooperation", "Machine ethics",
    
    # New diverse themes
    "Digital biology", "Information ecology", "Cognitive enhancement",
    "Silicon evolution", "Metaverse economics", "Synthetic biology",
    "Cultural acceleration", "Technological art", "Digital sociology",
    "Tech inequality", "Post-scarcity economics", "Digital governance"
]

angles = [
    # Original perspectives
    "mainstream misconception", "hidden acceleration", "system emergence",
    "evolutionary leap", "technological singularity", "paradigm shift",
    "complexity threshold", "recursive improvement",
    
    # New perspectives
    "historical parallel", "biological metaphor", "economic impact",
    "cultural transformation", "psychological shift", "philosophical paradox",
    "social consequence", "environmental impact", "political disruption",
    "artistic vision", "educational revolution", "market dynamics"
]

timeframes = ["2025", "2030", "2035", "2040", "2050", "this decade", "next decade"]
impact_levels = ["individual", "societal", "economic", "existential", "evolutionary", 
                "cultural", "psychological", "biological", "political", "environmental"]
tech_focus = ["hardware", "software", "biotech", "nanotech", "quantum", 
              "neurotechnology", "robotics", "clean tech", "space tech", "grid computing"]
domains = ["cognition", "consciousness", "computation", "intelligence",
          "creativity", "emotion", "learning", "memory", "perception", "decision-making"]

cognitive_topics = [
    # AI & Tech (Major Focus)
    "artificial general intelligence development",
    "machine learning capabilities",
    "neural network processing",
    "AI consciousness possibility",
    "technological singularity",
    "AI learning patterns",
    "machine cognition",
    "algorithmic thinking",
    "computational intelligence",
    "AI decision making",
    
    # New Technical Topics
    "quantum neural networks",
    "biomimetic computing",
    "neuromorphic engineering",
    "edge intelligence",
    "swarm cognition",
    "hybrid intelligence systems",
    
    # Human-AI Interface
    "brain-computer interfaces",
    "neural enhancement",
    "cognitive augmentation",
    "mind uploading potential",
    "human-AI convergence",
    "cognitive architectures",
    
    # Societal Impact
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
    return "i/acc Bot is running!"

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
    """Generate unique combination for prompt"""
    prompt_type = random.random()
    
    if prompt_type < 0.4:  # 40% chance for technology focus
        focus = random.choice(tech_focus)
        theme = random.choice(themes)
        timeframe = random.choice(timeframes) if random.random() < 0.3 else None
        prompt = f"""Write a provocative i/acc take about {focus} in relation to {theme}"""
        if timeframe:
            prompt += f" by {timeframe}"
            
    elif prompt_type < 0.7:  # 30% chance for societal impact
        impact = random.choice(impact_levels)
        domain = random.choice(domains)
        prompt = f"""Explore the {impact} implications of accelerating {domain}"""
        
    else:  # 30% chance for cognitive/philosophical
        topic = random.choice(cognitive_topics)
        angle = random.choice(angles)
        prompt = f"""Share an insight about {topic} from a {angle} perspective"""

    prompt += """
Requirements:
- Each statement on new line
- Start with lowercase
- No periods at end
- Raw, authentic style
- Keep under 240 chars total
- Avoid recent themes and metaphors
- Focus on one clear idea"""

    return prompt

def get_ai_take():
    """Get AI generated take using OpenAI"""
    try:
        system_prompt = """You are an intelligence accelerationist thought leader.
        Each response should focus on a single unique aspect rather than trying to cover everything.
        Vary between optimistic and critical perspectives.
        Be provocative but insightful.
        Use concrete examples and specific scenarios when possible."""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": generate_unique_prompt()}
            ],
            max_tokens=280,
            temperature=0.9
        )
        
        # Format the response
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
