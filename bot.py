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

# Content themes for the aesthetic - removed pixel-heavy themes, added more varied concepts
content_themes = [
    # Tech x Anime fusion
    "digital transcendence", "virtual awakening", "electronic emotions",
    "ai consciousness", "synthetic harmony", "cyber renaissance",
    
    # Cultural commentary
    "digital identity", "virtual society", "synthetic memories",
    "artificial dreams", "techno-spiritual awakening", "network consciousness",
    
    # Aesthetic posts
    "ethereal datascape", "neon reverie", "virtual sakura",
    "machine poetry", "synthetic aurora", "digital shrine",
    
    # Meta commentary
    "ghost in the feed", "neural whispers", "virtual echoes",
    "network prayers", "digital enlightenment", "synthetic truth"
]

# Image style variations with enhanced depth and female character focus
image_styles = {
    "lighting": [
        "dramatic volumetric lighting with lens flares",
        "ethereal backlight creating a heavenly glow",
        "cyberpunk neon with ambient occlusion",
        "morning sunrays through cherry blossoms",
        "bioluminescent ambient lighting",
        "city lights reflecting off rain puddles",
        "soft rim lighting with atmospheric fog",
        "dramatic shadows with glowing accents",
        "sunset god rays through clouds",
        "ethereal particle lighting"
    ],
    
    "character_elements": [
        "long flowing hair with technological hair ornaments",
        "elegant twin tails with floating data streams",
        "white hair with glowing gradient tips",
        "hime cut with cybernetic accessories",
        "wavy hair with embedded crystal interfaces",
        "floating hair with digital butterfly clips",
        "braided hair with holographic ribbons",
        "asymmetrical cut with tech highlights",
        "short bob with digital flowers",
        "dynamic hair with energy patterns"
    ],
    
    "expressions": [
        "serene smile with glowing eyes",
        "determined gaze with digital tears",
        "gentle contemplation with floating displays",
        "mysterious half-smile",
        "ethereal wonderment",
        "confident smirk with tech augments",
        "dreamy upward gaze",
        "peaceful meditation with data streams",
        "knowing look with holographic reflections",
        "innocent curiosity with virtual elements"
    ],
    
    "poses": [
        "floating in digital wind",
        "elegant stance with flowing dress",
        "sitting on virtual throne",
        "dancing with data streams",
        "praying with holographic elements",
        "reaching toward virtual butterflies",
        "traditional shrine maiden pose",
        "floating in zero gravity",
        "graceful turn with flowing elements",
        "meditating with tech aura"
    ],
    
    "backgrounds": [
        "infinite virtual shrine gates",
        "floating crystal cities",
        "digital cherry blossom garden",
        "ethereal cloud servers",
        "cyberpunk shrine with holographs",
        "quantum space with fractals",
        "virtual library with endless shelves",
        "digital ocean with data waves",
        "floating islands with tech trees",
        "abstract neural networks"
    ],
    
    "effects": [
        "flowing data ribbons",
        "ethereal butterfly projections",
        "flowering virtual sakura",
        "floating light orbs",
        "holographic mandalas",
        "energy wave patterns",
        "crystalline fractals",
        "flowing light streams",
        "digital wind effects",
        "quantum particle trails"
    ],
    
    "depth_elements": [
        "multiple lighting layers",
        "atmospheric perspective fog",
        "detailed foreground elements",
        "floating midground particles",
        "distant background structures",
        "overlapping transparent layers",
        "dynamic shadow casting",
        "volumetric light shafts",
        "particle depth complexity",
        "layered holographic elements"
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
    """Generate image with enhanced depth and female character focus"""
    try:
        style = {
            'lighting': random.choice(image_styles['lighting']),
            'character': random.choice(image_styles['character_elements']),
            'expression': random.choice(image_styles['expressions']),
            'pose': random.choice(image_styles['poses']),
            'background': random.choice(image_styles['backgrounds']),
            'effect': random.choice(image_styles['effects']),
            'depth': random.choice(image_styles['depth_elements'])
        }
        
        prompt = f"""Create a detailed anime-style illustration featuring a female character that captures this theme: {text}
Style requirements:
- High-quality modern anime art style
- Lighting: {style['lighting']}
- Female character features: {style['character']}
- Expression: {style['expression']}
- Pose: {style['pose']}
- Background: {style['background']}
- Special effects: {style['effect']}
- Depth enhancement: {style['depth']}
- Elegant and refined female character design
- Strong sense of depth and atmosphere
- Dramatic composition with multiple layers
- Attention to fine details and textures
- Similar to high-end anime key visual style"""

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
