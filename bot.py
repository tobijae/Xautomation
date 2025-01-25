import discord
import openai
import tweepy
import requests
import os
import logging
import asyncio
from threading import Thread

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Discord Setup ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
discord_client = discord.Client(intents=intents)

# --- Twitter Setup ---
twitter_client = tweepy.Client(
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
)

# --- Constants ---
MIDJOURNEY_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
MIDJOURNEY_BOT_ID = 936929561302675456  # MidJourney bot ID
OPENAI_PROMPT_TEMPLATE = "Generate a creative image prompt about futuristic politics:"

# --- Global Variables ---
latest_image_url = None

# ============================================
# Core Functions
# ============================================

def generate_prompt():
    """Generate a MidJourney prompt using OpenAI"""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=OPENAI_PROMPT_TEMPLATE,
            max_tokens=50
        )
        prompt_text = response.choices[0].text.strip()
        return f"/imagine {prompt_text} --v 6"  # Generates 4 images by default
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return None

async def post_to_midjourney(prompt):
    """Send prompt to MidJourney Discord channel"""
    channel = discord_client.get_channel(MIDJOURNEY_CHANNEL_ID)
    await channel.send(prompt)

@discord_client.event
async def on_ready():
    logger.info(f'Discord bot logged in as {discord_client.user}')
    asyncio.create_task(midjourney_loop())

@discord_client.event
async def on_message(message):
    global latest_image_url
    if message.author.id == MIDJOURNEY_BOT_ID and message.attachments:
        # Capture first image from the 4 generated
        latest_image_url = message.attachments[0].url
        logger.info(f"Captured image URL: {latest_image_url}")

async def midjourney_loop():
    """Automation loop (runs every 1.5 hours)"""
    while True:
        try:
            # Generate and send prompt
            prompt = generate_prompt()
            if not prompt:
                await asyncio.sleep(60)
                continue

            await post_to_midjourney(prompt)
            logger.info(f"Sent to MidJourney: {prompt}")

            # Wait for images (3 minutes max)
            for _ in range(18):  # 18 * 10s = 3 minutes
                await asyncio.sleep(10)
                if latest_image_url:
                    break

            if latest_image_url:
                # Download and post to X
                response = requests.get(latest_image_url)
                media = twitter_client.media_upload(filename="ai_image.jpg", file=response.content)
                twitter_client.create_tweet(text="New AI-generated artwork!", media_ids=[media.media_id])
                logger.info("Posted to X/Twitter!")
                latest_image_url = None  # Reset

            # Wait exactly 1.5 hours (5400 seconds)
            await asyncio.sleep(5400)

        except Exception as e:
            logger.error(f"Loop error: {e}")
            await asyncio.sleep(60)

# ============================================
# Run the Bot
# ============================================
if __name__ == "__main__":
    discord_client.run(os.getenv('DISCORD_BOT_TOKEN'))
