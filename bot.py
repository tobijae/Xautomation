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

# Content themes for the aesthetic
content_themes = [
    # Tech x Anime fusion
    "tech acceleration", "digital escape", "virtual dreams",
    "ai consciousness", "digital enlightenment", "cyber aesthetics",
    
    # Cultural commentary
    "online existence", "digital identity", "virtual society",
    "artificial dreams", "digital evolution", "tech spirituality",
    
    # Aesthetic posts
    "cyber dreams", "digital beauty", "virtual aesthetics",
    "tech poetry", "machine thoughts", "digital fragments",
    
    # Meta commentary
    "posting through it", "digital signals", "virtual whispers",
    "online echoes", "network thoughts", "digital mysteries"
]

# Image style variations
image_styles = {
    "lighting": [
        "dramatic red lighting with glowing eyes",
        "soft blue ethereal lighting",
        "cyberpunk neon accents",
        "morning golden sunlight",
        "twilight purple hues",
        "night scene with city lights",
        "clean white high-key lighting",
        "moody low-key lighting",
        "warm sunset oranges",
        "cool moonlight blues"
    ],
    
    "character_elements": [
        "long flowing hair with ribbon",
        "short messy hair with clips",
        "twin tails with technology accessories",
        "white/silver hair with mysterious aura",
        "black hair with digital patterns",
        "asymmetrical hairstyle with cyber elements",
        "hooded figure with glowing features",
        "school uniform with tech modifications",
        "casual wear with digital accessories",
        "futuristic outfit with traditional elements"
    ],
    
    "expressions": [
        "knowing smile with glowing eyes",
        "mysterious side glance",
        "determined forward gaze",
        "gentle smile with hidden meaning",
        "contemplative looking at phone",
        "surprised by digital revelation",
        "serene with closed eyes",
        "focused on virtual interface",
        "melancholic stare into distance",
        "confident smirk with tech reflection"
    ],
    
    "poses": [
        "looking at phone screen",
        "reaching toward virtual elements",
        "sitting with floating screens",
        "standing in digital wind",
        "leaning against virtual wall",
        "floating in cyberspace",
        "walking through digital cherry blossoms",
        "interacting with holographic interface",
        "resting with tech accessories",
        "dynamic action with digital effects"
    ],
    
    "backgrounds": [
        "city skyline with digital overlay",
        "bedroom with floating screens",
        "virtual cherry blossom garden",
        "abstract digital space",
        "school hallway with tech elements",
        "night city with neon signs",
        "clean white void with particles",
        "traditional room with future tech",
        "digital subway station",
        "floating in cloud servers"
    ],
    
    "effects": [
        "floating digital particles",
        "glowing circuit patterns",
        "cherry blossom petals",
        "data stream effects",
        "holographic glitches",
        "rain with digital elements",
        "floating code segments",
        "energy aura effects",
        "butterfly data patterns",
        "geometric tech shapes"
    ]
}


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Twitter API v2 client
twitter_client = tweepy.Client(
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
)

# Initialize Twitter API v1.1 for media uploads
auth = tweepy.OAuthHandler(
    os.getenv('TWITTER_API_KEY'),
    os.getenv('TWITTER_API_SECRET')
)
auth.set_access_token(
    os.getenv('TWITTER_ACCESS_TOKEN'),
    os.getenv('TWITTER_ACCESS_SECRET')
)
twitter_api = tweepy.API(auth)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "weeb/acc bot is running"

def generate_image(text):
    """Generate image for every post with enhanced style combinations"""
    try:
        # Select random elements from each style category
        style = {
            'lighting': random.choice(image_styles['lighting']),
            'character': random.choice(image_styles['character_elements']),
            'expression': random.choice(image_styles['expressions']),
            'pose': random.choice(image_styles['poses']),
            'background': random.choice(image_styles['backgrounds']),
            'effect': random.choice(image_styles['effects'])
        }
        
        # Create detailed prompt
        prompt = f"""Create an anime-style illustration that captures this theme: {text}
Style requirements:
- High-quality modern anime art style
- Lighting: {style['lighting']}
- Character features: {style['character']}
- Expression: {style['expression']}
- Pose: {style['pose']}
- Background: {style['background']}
- Special effects: {style['effect']}
- Clean, detailed illustration with strong composition
- Similar to modern anime key visual style
- Single character focus
- Dramatic and impactful composition"""

        # Generate image with DALL-E
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Get and download the image
        image_url = response.data[0].url
        image_data = requests.get(image_url).content
        
        # Save temporarily with unique timestamp
        temp_path = f"temp_image_{int(time.time())}.png"
        with open(temp_path, "wb") as f:
            f.write(image_data)
            
        # Upload to Twitter
        media = twitter_api.media_upload(filename=temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        logger.info(f"Generated image with style combination: {style}")
        return media.media_id
    except Exception as e:
        logger.error(f"Error generating/uploading image: {e}")
        return None
def get_content():
    """Get AI generated content"""
    try:
        theme = random.choice(content_themes)
        
        system_prompt = """You are a weeb/acc Twitter account that posts about the intersection of technology, consciousness, and anime aesthetics. Your posts are short, meaningful, and slightly mysterious. You never explain too much. Your tone is knowing but not pretentious."""
        
        user_prompt = f"""Create a short, impactful tweet about {theme}.
Requirements:
- Maximum 60 characters
- No hashtags or emojis
- Slightly mysterious or profound
- Can be a question or statement
- Should feel like it's from someone "in the know"

Examples:
are you evolving yet?
digital dreams at 3am
embrace the virtual dawn
another night in the machine
become what you fear"""  # Changed double quotes to single quotes for examples

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=60,
            temperature=0.9
        )
        
        text = response.choices[0].message.content.strip().lower()
        return text
    except Exception as e:
        logger.error(f"Error getting content: {e}")
        return None

def create_tweet():
    """Create tweet with guaranteed image"""
    try:
        content = get_content()
        if not content:
            return None, None
            
        # Always generate image
        media_id = generate_image(content)
        return content, media_id
    except Exception as e:
        logger.error(f"Error creating tweet: {e}")
        return None, None

def post_update():
    """Post update to Twitter"""
    try:
        tweet_content, media_id = create_tweet()
        if tweet_content and media_id:
            twitter_client.create_tweet(
                text=tweet_content,
                media_ids=[media_id]
            )
            logger.info(f"Tweet posted successfully at {datetime.now()}")
            logger.info(f"Content: {tweet_content}")
        else:
            logger.error("Failed to generate content or image")
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
    """Main function to run the bot"""
    logger.info("Starting bot...")
    post_update()
    
    # Post every 90 minutes
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
